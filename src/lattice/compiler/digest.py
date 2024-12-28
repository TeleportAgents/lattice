from typing import Iterator, Any

import ast
from os import walk, path
from itertools import chain
import logging

import jedi as jd
from neo4j import Driver, Transaction

from .uml_types import Function


logger = logging.getLogger("lattice")


def read_from_script(script_path: str, start_line: int, end_line: int) -> str:
    with open(script_path) as f:
        source = f.read()

    return read_from_source(source, start_line, end_line)


def read_from_source(source: str, start_line: int, end_line: int) -> str:
    lines = source.splitlines()[start_line - 1 : end_line]

    return "\n".join(lines)


def extract_definition(script: jd.Script, name: str) -> str:
    function_definitions = [name for name in script.search(name)]

    if not function_definitions:
        raise ValueError(f"Function '{name}' not found in {script.path}")

    function_definition = function_definitions[0]

    start_line = function_definition.get_definition_start_position()[0]
    end_line = function_definition.get_definition_end_position()[0]

    function_source = read_from_script(script.path, start_line, end_line)

    return function_source


def expand_definition(function_source: str) -> Iterator:
    node = ast.parse(function_source)

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            yield child.func.id


def analyze_function(file_path, function_name):
    # Load the script from the file
    with open(file_path, "r") as f:
        source = f.read()

    # Use Jedi to parse the source code
    script = jd.Script(source, path=file_path)

    # Find the specified function definition
    function_definitions = [name for name in script.search(function_name)]

    if not function_definitions:
        raise ValueError(f"Function '{function_name}' not found in {file_path}")

    function_definition = function_definitions[0]

    # Get the full definition of the function
    start_line = function_definition.line
    end_line = function_definition.get_definition_end_position()[0]

    function_lines = source.splitlines()[start_line - 1 : end_line]
    function_source = "\n".join(function_lines)

    # Analyze function calls within the function
    function_calls = []
    for usage in function_definition.usages():
        if usage.type == "function":
            call_site = usage.parent()
            if call_site:
                definition = call_site.goto()
                if definition:
                    function_calls.append(
                        {
                            "name": usage.name,
                            "path": (
                                definition[0].module_path
                                if definition[0].module_path
                                else file_path
                            ),
                        }
                    )

    return function_source, function_calls


def iterate_over_functions_script(file_path: str) -> Iterator[Function]:
    with open(file_path, "r") as file:
        source = file.read()

    tree = ast.parse(source, filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            yield Function(
                name=node.name,
                definition=read_from_source(source, node.lineno, node.end_lineno),
            )


def iterate_over_functions_project(
    directory: str, deep=True, exclude=[]
) -> Iterator[Function]:
    _, directories, files = next(walk(directory))
    for file in files:
        if file.split(".")[-1] == "py":
            file_path = path.join(directory, file)
            for f in iterate_over_functions_script(file_path):
                yield f
    if not deep:
        return

    for child_directory in directories:
        if child_directory in exclude:
            continue
        dir_path = path.join(directory, child_directory)
        for f in iterate_over_functions_project(dir_path, exclude=exclude):
            yield f


def iterate_over_files(directory: str, deep=True, exclude=[], root="") -> Iterator[str]:
    _, directories, files = next(walk(directory))
    for file in files:
        if file.split(".")[-1] == "py":
            file_path = path.join(root, file)
            yield file_path
    if not deep:
        return

    for child_directory in directories:
        if child_directory in exclude:
            continue
        dir_path = path.join(directory, child_directory)
        root_path = path.join(root, child_directory)
        for filepath in iterate_over_files(dir_path, exclude=exclude, root=root_path):
            yield filepath


def neo4j_insert_ast(driver: Driver, filepath: str, name: str, parent_id: str):
    def add_ast_node(tx: Transaction, node: Any, parent_id: str, **kwargs):
        if isinstance(node, ast.Load):
            return

        node_label = type(node).__name__
        node_properties = {
            k: v
            for k, v in vars(node).items()
            if isinstance(v, (str, int, float, bool))
        }
        node_properties.update(kwargs)

        if len(node_properties) > 0:
            create_node_query = f"CREATE (n:{node_label} {{uuid: randomUUID(), {', '.join(f'{k}: ${k}' for k in node_properties.keys())}}}) RETURN n.uuid"
        else:
            create_node_query = (
                f"CREATE (n:{node_label} {{uuid: randomUUID()}}) RETURN n.uuid"
            )

        node_id = tx.run(create_node_query, **node_properties).single().value()

        create_relationship_query = "MATCH (p), (c) WHERE p.uuid = $parent_id AND c.uuid = $id CREATE (p)-[:HAS_CHILD]->(c)"
        tx.run(create_relationship_query, parent_id=parent_id, id=node_id)

        for child in ast.iter_child_nodes(node):
            add_ast_node(tx, child, node_id)

    with open(filepath, "r") as file:
        source = file.read()

    tree = ast.parse(source)

    with driver.session() as session:
        session.execute_write(
            add_ast_node, tree, parent_id, name=name, filepath=filepath
        )


def neo4j_digest_project(driver: Driver, rootpath: str, project_name: str, exclude=[]):
    def digest_directory(directory: str, parent_id: str):
        _, directories, files = next(walk(directory))

        for file in files:
            file_name, file_extension = file.split(".")
            if file_extension == "py":
                neo4j_insert_ast(
                    driver, path.join(directory, file), file_name, parent_id
                )

        for child_directory in directories:
            if child_directory in exclude:
                continue

            dir_path = path.join(directory, child_directory)
            digest_directory(dir_path, parent_id)

    project = jd.Project(rootpath)
    project.save()

    with driver.session() as session:
        node_id = (
            session.run(
                "CREATE (p:Project {uuid: randomUUID(), rootpath:$rootpath, name:$name}) RETURN p.uuid",
                rootpath=rootpath,
                name=project_name,
            )
            .single()
            .value()
        )

    digest_directory(rootpath, node_id)


def neo4j_create_call_shortcuts(driver: Driver, project_name: str):
    with driver.session() as session:
        get_project_query = """
        MATCH (p:Project {name: $name})
        RETURN p
        """
        project_node = session.run(get_project_query, name=project_name).single(
            strict=True
        )["p"]
        project_node_id = project_node["uuid"]
        project = jd.Project.load(project_node["rootpath"])

        get_funcdefs_query = """
        MATCH (:Project {uuid: $uuid})-[:HAS_CHILD*]->(m:Module)-[:HAS_CHILD*]->(f:FunctionDef)
        RETURN m.filepath, f.name, f.uuid, f.lineno, f.col_offset
        """
        funcdefs_results = session.run(
            get_funcdefs_query, uuid=project_node_id
        ).values()
        for filepath, name, uuid, lineno, col_offset in funcdefs_results:
            with open(filepath, "rb") as file:
                source = file.read()

            script = jd.Script(source, path=filepath, project=project)

            references_iters = []

            references_iters.append(filter(lambda ref: ref.type == 'statement', script.get_references(lineno, col_offset + 4)))

            if name == '__init__':
                get_classdef_query = '''
                MATCH (c:ClassDef)-[:HAS_CHILD]->(f:FunctionDef {uuid: $uuid})
                RETURN c.lineno, c.col_offset
                '''
                classdef_results = session.run(get_classdef_query, uuid=uuid).values()

                for cd_lineno, cd_col_offset in classdef_results:
                    references_iters.append(filter(lambda ref: ref.type == 'statement', script.get_references(cd_lineno, cd_col_offset + 6)))
            
            references = list(map(lambda ref: {'filepath': str(ref.module_path), 'lineno': ref.line}, chain(*references_iters)))

            create_caller_shortcut = """
            MATCH (t:FunctionDef {uuid: $node_id})
            WITH t
            UNWIND $refs AS ref
            MATCH (m:Module {filepath: ref.filepath})-[:HAS_CHILD*]->(h: FunctionDef)
            WHERE h.lineno < ref.lineno AND h.end_lineno >= ref.lineno
            CREATE (h)-[rel:CALLS]->(t)
            RETURN count(rel)
            """
            rel_count = (
                session.run(
                    create_caller_shortcut,
                    node_id=uuid,
                    refs=references
                )
                .single()
                .value()
            )
            print(f"added {rel_count} relations")
