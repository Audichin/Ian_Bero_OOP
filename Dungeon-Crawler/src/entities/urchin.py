"""FIXME"""
from pathlib import Path
from typing import Any
from math import sin

import pygame
from pygame import Vector2, Surface, Rect

from entities.entity_mod import Entity


class Urchin(Entity):
    """
    Urchin enemy:
    * From position, determine if player is closer in the X axis or Y axis
    * Choose the shorter axis and move in that axis until aligned with player.
    """

    _MOVE_INTERVAL: float = 1

    __slots__: list[str] = []

# ==== inits ====

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 speed: float = 100,
                 clamp_speed: float = 300,
                 friction: float = 25,
                 HP: int = 5) -> None:
        """Urchins are enemies that move in a single direction at a time."""
        super().__init__(world, position, speed, clamp_speed, friction, HP)
