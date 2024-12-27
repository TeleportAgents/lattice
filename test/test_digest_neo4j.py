import sys
import unittest
from pathlib import Path
import logging

from neo4j import GraphDatabase

root = Path(__file__).parent.parent
props = Path(__file__).parent / "props"
sys.path.append(str(root))

from src.lattice.compiler.digest import (
    neo4j_digest_project,
    neo4j_create_call_shortcuts,
)

logging.basicConfig(level=logging.DEBUG)
neo4j_logger = logging.getLogger("neo4j")
neo4j_logger.setLevel(logging.WARNING)


class TestNeo4jDigest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        uri = "bolt://localhost:7687"
        cls._driver = GraphDatabase.driver(uri, auth=("neo4j", "1234567890"))

        with cls._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def test_digest_project(self):
        neo4j_digest_project(self._driver, str(props), "props")

    def test_create_call_shortcuts(self):
        neo4j_create_call_shortcuts(self._driver, "props")

    @classmethod
    def tearDownClass(cls):
        # Cleanup code that runs once for the entire test suite
        cls._driver.close()


# Custom TestSuite in a specific order
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestNeo4jDigest("test_digest_project"))
    suite.addTest(TestNeo4jDigest("test_create_call_shortcuts"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
