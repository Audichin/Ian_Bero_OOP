
import typing_extensions
import pygame
from pygame import locals

from entity import Entity


class Bubble(Entity):
    """
    A bouncing bubble
    """

    def __init__(self) -> None:
        super().__init__()
        print("boing")
