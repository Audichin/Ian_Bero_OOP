
import typing_extensions
import pygame
from pygame import locals

from rat import Rat
from bubble import Bubble


class World:
    """
    Object that handles the game world itself. Recieves calls and sends back data to entities.
    Singleton?
    """
    __slots__ = ["_player", "_bubbles"]

    def __init__(self) -> None:
        self._player : Rat = Rat()
        self._bubbles : list[Bubble] = list[Bubble]()

    def loop(self) -> None:
        self._player.loop()
        for bubble in self._bubbles:
            bubble.loop()
