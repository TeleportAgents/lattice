To extend the script to include the literal definitions of functions from their respective Python files and add them as data to nodes, we can use the `ast` module to extract the function definitions and `networkx` to create and manipulate the graph. This will allow us to store and visualize the relationships between functions along with their code definitions.

First, you'll need to install the `networkx` library if you haven't already:

```bash
pip install networkx
```

Here’s the updated script:

```python
import ast
import os
import networkx as nx
from typing import Dict, Tuple

class FunctionNode:
    def __init__(self, name: str, module: str, definition: str):
        self.name = name
        self.module = module
        self.definition = definition
        self.calls = []

    def add_call(self, call: Tuple[str, str]):
        self.calls.append(call)

def parse_functions(file_path: str) -> Dict[str, FunctionNode]:
    with open(file_path, 'r') as file:
        source_code = file.read()
        tree = ast.parse(source_code, filename=file_path)

    functions = {}
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract the source code for the function definition
            start_lineno = node.lineno - 1
            end_lineno = node.end_lineno if hasattr(node, 'end_lineno') else node.body[-1].lineno
            function_def = "\n".join(source_code.splitlines()[start_lineno:end_lineno])

            function_node = FunctionNode(node.name, module_name, function_def)
            functions[node.name] = function_node

            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    function_node.add_call((child.func.id, module_name))

    return functions

def find_main_function(project_path: str) -> Tuple[Dict[str, Dict[str, FunctionNode]], Dict[str, FunctionNode]]:
    main_functions = {}
    all_functions = {}

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                functions = parse_functions(file_path)
                all_functions.update(functions)
                if file == 'main.py' and 'main' in functions:
                    main_functions[file_path] = functions

    return main_functions, all_functions

def build_graph(main_functions: Dict[str, Dict[str, FunctionNode]], all_functions: Dict[str, FunctionNode]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for file_path, functions in main_functions.items():
        main_func = functions.get('main')
        if main_func:
            graph.add_node(main_func.name, module=main_func.module, definition=main_func.definition)
            for call, module in main_func.calls:
                if call in all_functions:
                    called_func = all_functions[call]
                    graph.add_node(called_func.name, module=called_func.module, definition=called_func.definition)
                    graph.add_edge(main_func.name, called_func.name)

    return graph

def main(project_path: str):
    main_functions, all_functions = find_main_function(project_path)
    if not main_functions:
        print("No main.py file with a 'main' function found.")
        return

    graph = build_graph(main_functions, all_functions)

    # Print the graph
    for node in graph.nodes(data=True):
        print(f"Function '{node[0]}' in module '{node[1]['module']}':")
        print(node[1]['definition'])
        print("Calls:")
        for successor in graph.successors(node[0]):
            print(f"  - {successor} (Module: {graph.nodes[successor]['module']})")
        print()

if __name__ == "__main__":
    project_path = input("Enter the path to the Python project: ")
    main(project_path)
```

### Explanation

1. **FunctionNode Class:**
   - Now includes a `definition` attribute to store the literal definition of the function.

2. **parse_functions Function:**
   - Extracts the literal source code of each function and stores it in the `definition` attribute of `FunctionNode`.

3. **find_main_function Function:**
   - Traverses the project directory to locate all functions and specifically identifies the `main.py` file and its `main` function.

4. **build_graph Function:**
   - Uses `networkx` to create a directed graph (`DiGraph`), where each node represents a function with its name, module, and definition. Edges represent function calls.

5. **main Function:**
   - Orchestrates the overall process, starting with finding the main functions, then building and printing the graph.

6. **Printing the Graph:**
   - The graph is printed with function names, their corresponding modules, and their literal definitions, along with the functions they call.

This script provides a detailed view of the relationships between functions in the `main.py` file and the functions they call, along with their respective definitions. You can extend this script further to include more details or handle more complex scenarios as needed.