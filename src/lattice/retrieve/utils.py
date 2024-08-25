import ast
from textwrap import dedent
from typing import Tuple

import numpy as np


def separate_docstring_and_code(source_code: str) -> Tuple[str, str]:
    """
    Separates the docstring and code from the given source code.

    Parameters
    ----------
    source_code : str
        The source code containing the function definition.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the docstring and the code as strings.
    """
    # Dedent the source code to ensure correct indentation
    source_code = dedent(source_code)

    # Parse the source code into an AST (Abstract Syntax Tree)
    parsed_code = ast.parse(source_code)

    # Extract the first function definition node
    function_node = parsed_code.body[0]

    # Extract the docstring using AST
    docstring = ast.get_docstring(function_node)

    # Generate the code excluding the docstring
    if docstring:
        docstring_lines = docstring.split('\n')
        # The docstring usually starts with """ or ''' and ends with the same
        if '"""' in source_code or "'''" in source_code:
            start_quote = '"""' if '"""' in source_code else "'''"
            start_line = source_code.find(start_quote)
            end_line = source_code.find(start_quote, start_line + len(start_quote))
            end_line += len(start_quote)  # Include the closing triple quotes
            code_without_docstring = source_code[end_line:].strip()
        else:
            code_without_docstring = source_code.strip()
    else:
        code_without_docstring = source_code.strip()

    return docstring, code_without_docstring
