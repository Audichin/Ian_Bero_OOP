from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import MagicMock, patch
import unittest

from src.structures import Dungeon


class TestGeneration(unittest.TestCase):
    VALID_ROOM_TYPES = {"boss", "enemy", "puzzle", "start"}

    def make_dungeon(self, seed):
        """Create dungeon with magicMock

        Args:
            seed (any): dungeon seed

        Returns:
            _type_: dungeon class setup
        """
        with patch("src.structures.Room.create_enemy"), \
                patch("src.structures.Room.init_enemies"), \
                patch("src.structures.Room.init_puzzle_patterns"):
            return Dungeon(MagicMock(), seed)

    @given(seed=some.integers(min_value=1, max_value=100))
    def test_room_types(self, seed):
        """
        tests room types being assinged with specific amounts

        Args:
            seed (any): dungeon seed
        """
        dungeon = self.make_dungeon(seed)
        room_types = [room.room_type for room in dungeon.rooms.values()]

        self.assertEqual(len(dungeon.rooms), 12)
        self.assertTrue(all(room_type in self.VALID_ROOM_TYPES for room_type in room_types))
        self.assertEqual(room_types.count("start"), 1)
        self.assertEqual(room_types.count("boss"), 1)
        self.assertEqual(room_types.count("puzzle"), 4)
        self.assertEqual(room_types.count("enemy"), 6)

    @given(seed=some.integers(min_value=1, max_value=100))
    def test_wall_data(self, seed):
        """
        tests wall data

        Args:
            seed (any): dungeon seed
        """
        dungeon = self.make_dungeon(seed)
        room_walls = dungeon._generation.room_walls

        self.assertEqual(len(room_walls), len(dungeon.rooms) * 4)

        for room in dungeon.rooms.values():
            for orientation in ["N", "E", "S", "W"]:
                wall_data = room_walls[(room.x, room.y, orientation)]
                self.assertEqual(wall_data["x"], room.x)
                self.assertEqual(wall_data["y"], room.y)
                self.assertEqual(wall_data["ori"], orientation)
                self.assertIn("hasdoor", wall_data)
                self.assertIn("isopen", wall_data)
                self.assertIn("wall_type", wall_data)
                self.assertIn("sel_img", wall_data)
