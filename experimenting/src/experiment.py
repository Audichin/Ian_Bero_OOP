"""
Wrapper module for my simple pygame experiment

This project is intended to help us learn more about pygame, how to work
in with its modules and make developer-friendly, modular, OOD friendly code.
"""
import sys
from typing_extensions import Self

import pygame
import pygame.locals as locals


class Game:
    """singleton obj"""
    _instance = None

    __slots__ = ["_resolution", "_screen", "_running"]

    def __new__(cls) -> Self:
        """simple singleton implementation"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, resolution : tuple[int, int] | None = None) -> None:
        """init fix me"""

        self._resolution : tuple[int, int] = tuple[int, int]()
        if resolution is None:
            self._resolution = (1280, 720)
        else:
            self._resolution = resolution
        self._running : bool = False

    def game_init(self) -> None:
        """fixme"""
        pygame.init()
        self._screen : pygame.Surface = pygame.display.set_mode(self._resolution)
        self._running = True

    def event_handler(self) -> None:
        """fixme"""
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self._running = False
            # sys.exit()

    def gui_render(self) -> None:
        """fixme"""
        self._screen.fill("black")
        pygame.display.flip()

    def run_game(self) -> None:
        """fixme"""
        # run the game

        while self._running:
            self.event_handler()

            self.gui_render()

        pygame.quit()

    @staticmethod
    def main() -> None:
        """do something"""
        game : Game = Game()
        game.game_init()
        game.run_game()

    def dog(self) -> None:
        dog = 20
        print(dog)


if __name__ == "__main__":
    Game.main()
