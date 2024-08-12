from typing import Sequence, Generator

import ast
from os import walk, path

import jedi

from .types import Function


def read_from_script(script_path: str, start_line: int, end_line: int) -> str:
    with open(script_path) as f:
        source = f.read()

    return read_from_source(source, start_line, end_line)


def read_from_source(source: str, start_line: int, end_line: int) -> str:
    lines = source.splitlines()[start_line - 1 : end_line]

    return "\n".join(lines)


def extract_definition(script: jedi.Script, name: str) -> str:
    function_definitions = [name for name in script.search(name)]

    if not function_definitions:
        raise ValueError(f"Function '{name}' not found in {script.path}")

    function_definition = function_definitions[0]

    start_line = function_definition.get_definition_start_position()[0]
    end_line = function_definition.get_definition_end_position()[0]

    function_source = read_from_script(script.path, start_line, end_line)

    return function_source


def expand_definition(function_source: str) -> Sequence[str]:
    node = ast.parse(function_source)

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            yield child.func.id


def analyze_function(file_path, function_name):
    # Load the script from the file
    with open(file_path, "r") as f:
        source = f.read()

    # Use Jedi to parse the source code
    script = jedi.Script(source, path=file_path)

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


def iterate_over_functions_script(file_path: str) -> Generator:
    with open(file_path, "r") as file:
        source = file.read()

    tree = ast.parse(source, filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            yield Function(
                name=node.name,
                definition=read_from_source(source, node.lineno, node.end_lineno),
            )


def iterate_over_functions_project(directory: str, deep=True) -> Generator:
    _, directories, files = next(walk(directory))
    for file in files:
        if file.split(".")[-1] == "py":
            file_path = path.join(directory, file)
            for f in iterate_over_functions_script(file_path):
                yield f
    if not deep:
        return

    for child_directory in directories:
        dir_path = path.join(directory, child_directory)
        for f in iterate_over_functions_project(dir_path):
            yield f


# # Example usage
# file_path = 'path_to_your_python_file.py'
# function_name = 'your_function_name'

# try:
#     function_source, function_calls = analyze_function(file_path, function_name)
#     print("Function Source:\n", function_source)
#     print("\nFunction Calls:")
#     for call in function_calls:
#         print(f"Function '{call['name']}' is called and defined in {call['path']}")
# except ValueError as e:
#     print(e)
