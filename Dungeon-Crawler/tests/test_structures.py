from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import patch
import unittest

from src.structures import Dungeon


class TestStructures(unittest.TestCase):
    @given(some.text())
    def test_create_structure(self, structure_name):
        with patch('src.structures.print') as mock_print:
            Dungeon.create_structure(structure_name)  # type:ignore
            mock_print.assert_called_with(f"Creating structure: {structure_name}")

    def test_create_structure_with_empty_name(self):
        with patch('src.structures.print') as mock_print:
            Dungeon.create_structure("")  # type:ignore
            mock_print.assert_called_with("Creating structure: ")


if __name__ == '__main__':
    unittest.main()
