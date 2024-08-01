import unittest
import jedi

from src.lattice.compiler.digest import (
    analyze_function,
    extract_definition,
    expand_definition,
)


class TestDigest(unittest.TestCase):
    def setUp(self) -> None:
        # Load the script from the file
        with open("test/props/digest_main.py", "r") as f:
            source = f.read()

        # Use Jedi to parse the source code
        self.script = jedi.Script(source, path="test/props/digest_main.py")

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
