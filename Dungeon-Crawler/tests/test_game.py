"""Testing module for game."""
import os

from unittest.mock import patch
import unittest

import pygame
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
    @patch('src.game.sys')
    def test_game_run(self, mock_sys, mock_world, mock_pygame) -> None:
        """test running the game"""
        game: Game = Game(self._seed)

        # run game by simulating a game loop
        game._game_init()
        for i in range(10):  # 10 frames
            game.event_handler()
            game.on_loop()
            game.on_render()
        game.cleanup()

        game.reset_game()

    @patch('src.game.pygame')
    @patch('src.game.World')
    def test_game_events(self, mock_world, mock_pygame) -> None:
        """test event handling in the game"""
        event_get: list[pygame.Event] = [pygame.Event(pygame.QUIT)]
        mock_pygame.event.get.return_value = event_get

        game: Game = Game(self._seed)
        game._game_init()

        game.event_handler()

        event_get = [
            pygame.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})]
        mock_pygame.event.get.return_value = event_get

        game.event_handler()

        game.reset_game()

    @patch('src.game.pygame')
    @patch('src.game.World')
    def test_debug(self, mock_world, mock_pygame) -> None:
        """test opening debug and closing debug"""
        event_get: list[pygame.Event] = [
            pygame.Event(pygame.KEYDOWN, {"key": pygame.K_F1})]
        mock_pygame.event.get.return_value = event_get

        game: Game = Game(self._seed)
        game._game_init()
        game.event_handler()
        game.on_render()
        game.event_handler()

        game.reset_game()
