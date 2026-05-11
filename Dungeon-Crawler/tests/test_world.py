"""Testing module for world"""
import os

from unittest.mock import patch
import unittest

from src.world import World

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class TestWorld(unittest.TestCase):

    def setUp(self) -> None:
        self._seed: int = 82605
        self._delta_time: float = .01667
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @patch('src.world.Player')
    @patch('src.world.UI')
    @patch('src.world.Dungeon')
    @patch('src.world.Room')
    @patch('src.world.SoundManager')
    def test_world(self, mock_sound,
                   mock_room, mock_dungeon,
                   mock_UI, mock_player) -> None:
        """test world methods"""
        world: World = World(self._seed)

        assert world._room_transition == 0
        assert world._transition_state == 0
        assert world._victory is False

        assert world._dungeon_seed == self._seed
        assert world._prev_room_type == 'none'

        assert world._player

        assert world._ui

        assert world._item_slot
        assert len(world._inventory) == 0

        assert len(world._sounds) == 0
        assert world._sound_manager
        assert world._prev_music == [9]
