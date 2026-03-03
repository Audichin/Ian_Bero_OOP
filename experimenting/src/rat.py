
import typing_extensions
import pygame
from pygame import locals
from pygame import Vector2

# inherited class
from entity import Entity


class Rat(Entity):
    """the player
    """

    def __init__(self) -> None:
        super().__init__(velocity=Vector2(20, -20), speed=2.0)
        print("RRRAAAAGHHH")
