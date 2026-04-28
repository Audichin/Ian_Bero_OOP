from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import patch
import unittest

from src.generation import Generation


class TestGeneration(unittest.TestCase):
    @given(some.integers(min_value=1, max_value=100))
    def test_generate_dungeon(self, size):
        with patch('src.generation.random') as mock_random:
            mock_random.randint.return_value = 1
            dungeon = Generation.generate_dungeon(size)  # type:ignore
            self.assertEqual(len(dungeon), size)
            self.assertEqual(len(dungeon[0]), size)
            for row in dungeon:
                for cell in row:
                    self.assertEqual(cell, 1)

    def test_generate_dungeon_with_zero_size(self):
        with self.assertRaises(ValueError):
            Generation.generate_dungeon(0)  # type:ignore


if __name__ == '__main__':
    unittest.main()
