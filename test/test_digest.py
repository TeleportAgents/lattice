from pathlib import Path
import unittest
import jedi

from src.lattice.compiler.digest import (
    analyze_function,
    extract_definition,
    expand_definition,
    iterate_over_functions_script,
    iterate_over_functions_project,
    iterate_over_files,
)

props = Path(__file__).parent / "props"


class TestDigest(unittest.TestCase):

    def setUp(self) -> None:
        # Load the script from the file
        with open(props / "digest_main.py", "r") as f:
            source = f.read()

        # Use Jedi to parse the source code
        self.script = jedi.Script(source, path=props / "digest_main.py")

    def test_digest_exceptions(self) -> None:
        with self.assertRaises(ValueError):
            analyze_function("test/props/digest_main.py", "random_name")

        with self.assertRaises(FileNotFoundError):
            analyze_function("test/props/not_there.py", "random_name")

        with self.assertRaises(ValueError):
            extract_definition(self.script, "random_name")

    def test_extract_definition(self) -> None:
        definition = extract_definition(self.script, "main")

        true_definition = "def main(*args):\n    print(sum(args))"
        self.assertEqual(definition, true_definition)

    def test_expand_function(self) -> None:
        definition = "def main(*args):\n    print(sum(args))"

        for child in expand_definition(definition):
            print(child)

    def test_iterate_over_functions_script(self) -> None:
        functions = [
            f for f in iterate_over_functions_script("test/props/digest_main.py")
        ]

        self.assertEqual(len(functions), 1)

        f = functions[0]
        true_name = "main"
        true_definition = "def main(*args):\n    print(sum(args))"
        self.assertEqual(f.name, true_name)
        self.assertEqual(f.definition, true_definition)

    def test_iterate_over_functions_directory(self) -> None:
        true_names = ["analyze_text_reviews", "extract_words", "categorize_words"]
        for f in iterate_over_functions_project("test/props/example_directory"):
            self.assertIn(f.name, true_names)

    def test_iterate_over_files(self) -> None:
        filepaths = []

        for filepath in iterate_over_files(props):
            filepaths.append(filepath)

        self.assertEqual(len(filepaths), 4)
