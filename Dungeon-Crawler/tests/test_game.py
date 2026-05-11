"""Testing module for game."""
import os

from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import Mock, patch, PropertyMock
import unittest

from src.game import Game

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class TestGame(unittest.TestCase):

    def setUp(self) -> None:
        self._seed: int = 82605
        self._resolution: tuple[int, int] = (1920, 1080)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @patch('src.game.pygame')
    @patch('src.game.World')
    def test_game_init(self, mock_world, mock_pygame) -> None:
        """test initializing the game"""
        game: Game = Game(self._seed, self._resolution)

        # init game
        game._game_init()

        mock_pygame.init.assert_called_once()
        mock_pygame.display.set_mode.assert_called()
        mock_pygame.mixer.init.assert_called_once()
        mock_world.assert_called_with(game._seed)

        # create a new game while another game is running
        with self.assertRaises(Exception):
            new_game: Game = Game(self._seed)
            new_game._game_init()

        game.reset_game()

    @patch('src.game.pygame')
    @patch('src.game.World')
    def test_game_run(self, mock_world, mock_pygame) -> None:
        """test running the game"""
        game: Game = Game(self._seed)

        # run game by simulating a game loop
        game._game_init()
        for i in range(10):  # 10 frames
            game.event_handler()
            game.on_loop()
            game.on_render()
        game.event_handler()

        game.reset_game()
