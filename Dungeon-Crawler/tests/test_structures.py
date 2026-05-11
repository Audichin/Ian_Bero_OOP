import random
from unittest.mock import MagicMock, patch
import unittest

import pygame

from src.structures import Dungeon, Room


class TestStructures(unittest.TestCase):
    def make_empty_dungeon(self):
        """
        Creating basic setup for

        Returns:
            dungeon: full dungeon
        """
        dungeon = Dungeon.__new__(Dungeon)
        dungeon._world = MagicMock()
        dungeon._seed = 1
        dungeon._total_rooms = 0
        dungeon._min_puzzle_rooms = 0
        dungeon._native_size = (256, 160)
        dungeon._rooms = {}
        dungeon._rng = random.Random(1)
        dungeon._generation = MagicMock()
        return dungeon

    def make_room(self, x, y, room_type="empty"):
        """Creates room

        Args:
            x (any): x cord
            y (any): y cord
            room_type (str, optional): room type. Defaults to "empty".

        Returns:
            _type_: _description_
        """
        return Room(MagicMock(), x, y, random.Random(1), room_type)

    def assert_rects_equal(self, rects, expected):
        self.assertEqual([rect for rect in rects], [pygame.Rect(*rect) for rect in expected])

    def test_find_farthest_room(self):
        """
        tests setting of farthest room, should always be boss
        """
        dungeon = self.make_empty_dungeon()
        start = self.make_room(0, 0, "start")
        near = self.make_room(1, 0)
        middle = self.make_room(2, 0)
        farthest = self.make_room(3, 0)
        side = self.make_room(0, 1)

        start.connect(near)
        near.connect(middle)
        middle.connect(farthest)
        start.connect(side)

        self.assertIs(dungeon._find_farthest_room(start), farthest)

    def test_assign_room_types(self):
        """
        tests room type assignment
        """
        dungeon = self.make_empty_dungeon()
        dungeon._min_puzzle_rooms = 2
        dungeon._rng = random.Random(3)

        start = self.make_room(0, 0, "start")
        rooms = [
            start,
            self.make_room(1, 0),
            self.make_room(2, 0),
            self.make_room(3, 0),
            self.make_room(1, 1),
        ]

        rooms[0].connect(rooms[1])
        rooms[1].connect(rooms[2])
        rooms[2].connect(rooms[3])
        rooms[1].connect(rooms[4])
        dungeon._rooms = {(room.x, room.y): room for room in rooms}

        with patch.object(Room, "create_enemy") as mock_create_enemy, \
             patch.object(Room, "init_puzzle_patterns") as mock_init_puzzles, \
             patch.object(Room, "init_enemies") as mock_init_enemies:
            dungeon._assign_room_types()

        boss_room = rooms[3]
        self.assertEqual(start.room_type, "start")
        self.assertEqual(boss_room.room_type, "boss")
        mock_create_enemy.assert_called_once()
        self.assertEqual(mock_create_enemy.call_args.args[0], "Boss")
        self.assertEqual(mock_create_enemy.call_args.args[1], pygame.Vector2(1020, 405))

        assigned_types = [room.room_type for room in rooms]
        self.assertEqual(assigned_types.count("puzzle"), 2)
        self.assertEqual(assigned_types.count("enemy"), 1)
        self.assertEqual(mock_init_puzzles.call_count, 2)
        self.assertEqual(mock_init_enemies.call_count, 1)

        for room in rooms:
            if room.room_type == "puzzle":
                mock_init_puzzles.assert_any_call()
            elif room.room_type == "enemy":
                mock_init_enemies.assert_any_call()
