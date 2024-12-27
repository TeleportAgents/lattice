description_extraction = """You are and expert software engineering having deep knowledge about all parts of
                         software development.
                         I want you to read this code and give a thorough explanation of what it does.
                         I want to use these explanations to index the code in a RAG system to retrieve this
                         code if user asks anything that might be solved with this piece of code.
                         Please provide your answer in a Python Dict format like below:
                         {{
                         "description": <THOROUGH EXPLANATION OF THE CODE THAT IS USED IN A RAG SYSTEM>
                         }}
                         I don't want any further explanation. ONLY RETURN THE PYTHON DICT ANSWER.
                         CODE:
                         {definition}"""

keyword_extraction = """You are an AI assistant specialized in all fields of Python software engineering,
                     You have a vast range of skills in Python including:
                     web development, front-end development, backend development,
                     network engineering, cloud engineering,
                     data engineering, database engineering, database management,
                     data science, machine learning and artificial intelligence,
                     algorithms and data structure,
                     scientific computing, and numerical analysis

                     I will give you a description of a Python use-case.
                     Also optionally I will give the piece of code related to the description.
                     If I don't provide the code, I will place empty string in the code section.

                     Now, given the description (required input) and its codes (optional input),
                     you have the tasks:

                     1. Extract 10 Detailed Keywords and Entities From the Description and Code:
                     - Use Named Entity Recognition (NER) to identify and list specific entities such as
                     any specific domain, use-cases, functions, actions, or objects mentioned in the
                     DESCRIPTION AND CODE.

                     NOTE: YOU WILL OUTPUT 10 KEYWORDS IN TOTAL. MAKE SURE THERE NOT REDUNDANT WORDS AND ALL IS UNIQUE.
                     NOTE: THE KEYWORDS MUST BE MOST IMPORTANT KEYWORDS AND YOU MUST BE 100 PERCENT SURE ABOUT THEM.
                     NOTE: DO NOT LIST GENERAL KEYWORDS, ONLY LIST KEYWORD THAT ARE SPECIFIC.
                     NOTE: ALSO MAKE SURE THAT EVERYTHING IS SINGLE KEYWORDS and NOT KEYWORDS CONTAINING MULTIPLE WORDS.
                     NOTE: MAKE SURE ALL THE KEYWORDS ARE LOWER CASE.
                     NOTE: ONLY WRITE THE WORDS IN SINGULAR TERM, NOT PLURAL TERM
                     NOTE: KEYWORDS DO NOT CONTAIN PYTHON TYPES SUCH AS LIST, TUPLE, ETC.
                     NOTE: KEYWORDS DO NOT CONTAIN PYTHON SYNTAX WORDS SUCH AS LEN, RANGE, ETC.

                     You must format your response as Python Dictionary with the following keys and values:
                     {{
                     "description_keywords": [Array of terms]
                     }}

                     Description:
                     {description}

                     Code:
                     {code}

                     IMPORTANT NOTE: DO NOT OUTPUT ANY OTHER EXPLANATIONS. ONLY RETURN THE PYTHON DICTIONARY.
                     IMPORTANT NOTE: MAKE SURE THERE ARE NO SYNTAX ERRORS IN THE PYTHON DICTIONARY.
                     OUTPUT:"""
