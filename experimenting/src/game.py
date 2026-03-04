"""
Wrapper module for my simple pygame experiment

This project is intended to help us learn more about pygame, how to work
in with its modules and make developer-friendly, modular, OOD friendly code.

As per the tutorial online, a game loop should look like this:

while True:
    event()
    loop()
    render()

We handle events first, then run the next game loop (next frame)
and then render the game to the screen last.

In the render we want to do three things:

def render(self) -> None:
    # clear previous screen
    clear()

    # draw new screen
    draw()

    # play all sounds
    play_sounds()

"""
import sys
from typing_extensions import Self

import pygame
from pygame import locals

from world import World


class Game:
    """singleton obj"""
    _instance = None

    __slots__ = ["_resolution"
                 , "_screen"
                 , "_running"
                 , "_world"]

    def __new__(cls) -> Self:
        """simple singleton implementation"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        else:
            raise Exception("Cannot instantiate new singleton.")
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
        self._screen : pygame.Surface = pygame.display.set_mode(self._resolution, pygame.HWSURFACE)
        self._running = True
        self._world : World = World()

    def event_handler(self) -> None:
        """fixme"""
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self._running = False
            # sys.exit()

    def on_loop(self, x) -> None:
        """do something"""
        pygame.time.delay(1000)
        if x % 2 == 0:
            self._screen.fill("black")
        else:
            self._screen.fill("blue")
        self._world.loop()

    def on_render(self) -> None:
        """fixme"""
        pygame.display.flip()

    def cleanup(self) -> None:
        """clean the game"""
        pygame.display.quit()
        pygame.quit()

    def run_game(self) -> None:
        """fixme"""
        self.game_init()
        x = 0
        while self._running:
            self.event_handler()

            self.on_loop(x)
            x += 1

            self.on_render()

        self.cleanup()

    @staticmethod
    def main() -> None:
        """do something"""
        game : Game = Game()
        game.run_game()


if __name__ == "__main__":
    Game.main()
