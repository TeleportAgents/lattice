To refine the code to extract the definitions of functions from their respective modules, we need to enhance the graph-building process to include function definitions and their respective modules. This way, we can map each function call back to its definition within the corresponding module. 

Here’s a refined version of the script that extracts function definitions from their respective modules and constructs a more detailed graph:

```python
import ast
import os
from typing import Dict, List, Tuple

class FunctionNode:
    def __init__(self, name: str, module: str):
        self.name = name
        self.module = module
        self.calls = []

    def add_call(self, call: Tuple[str, str]):
        self.calls.append(call)

def parse_functions(file_path: str) -> Dict[str, FunctionNode]:
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)

    functions = {}
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_node = FunctionNode(node.name, module_name)
            functions[node.name] = function_node

            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    function_node.add_call((child.func.id, module_name))

    return functions

def find_main_function(project_path: str) -> Dict[str, Dict[str, FunctionNode]]:
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

def build_graph(main_functions: Dict[str, Dict[str, FunctionNode]], all_functions: Dict[str, FunctionNode]):
    graph = {}

    for file_path, functions in main_functions.items():
        main_func = functions.get('main')
        if main_func:
            graph['main'] = {
                'module': main_func.module,
                'calls': []
            }
            for call, module in main_func.calls:
                if call in all_functions:
                    graph['main']['calls'].append({
                        'name': call,
                        'module': module,
                        'calls': all_functions[call].calls
                    })

    return graph

def main(project_path: str):
    main_functions, all_functions = find_main_function(project_path)
    if not main_functions:
        print("No main.py file with a 'main' function found.")
        return

    graph = build_graph(main_functions, all_functions)
    
    # Print the graph
    for func, details in graph.items():
        print(f"Function '{func}' (Module: {details['module']}) calls:")
        for call in details['calls']:
            print(f"  - {call['name']} (Module: {call['module']}) calls: {', '.join(c[0] for c in call['calls'])}")

if __name__ == "__main__":
    project_path = input("Enter the path to the Python project: ")
    main(project_path)
```

### Explanation

1. **FunctionNode Class:**
   - The `FunctionNode` class now includes a `module` attribute to keep track of which module (file) each function belongs to.

2. **parse_functions Function:**
   - This function parses each file to extract function definitions and their calls, associating each function with its module (file name).

3. **find_main_function Function:**
   - This function traverses the project directory to locate all functions and specifically identifies the `main.py` file and its `main` function. It returns both the `main` function and a dictionary of all functions in the project.

4. **build_graph Function:**
   - This function constructs a graph-like dictionary where each function name maps to its module and the functions it calls, including the modules of those called functions.

5. **main Function:**
   - This function orchestrates the overall process, starting with finding the main functions, then building and printing the graph.

6. **Printing the Graph:**
   - The graph is printed with function names and their corresponding modules, along with the functions they call and the modules of those called functions.

This refined script provides a more detailed view of the relationships between functions in the `main.py` file and the functions they call, along with their respective modules. You can further extend this script to include more details or handle more complex scenarios as needed.