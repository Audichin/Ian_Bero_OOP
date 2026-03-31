"""FIXME"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2

from entity import Entity


class Player(Entity):
    """FIXME"""

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 HP: int | None = None) -> None:
        player = Path(__file__).parent / "../assets/visual/sprites/test.png"
        super().__init__(world, position, HP=HP, image_path=player)

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        super().loop(delta, self.player_movement(keys))

    def player_movement(self, keys: pygame.key.ScancodeWrapper) -> Vector2:
        """FIXME"""
        # take in inputs
        dir: Vector2 = Vector2()
        if keys[pygame.K_d]:
            dir.x += 1
        if keys[pygame.K_a]:
            dir.x -= 1
        if keys[pygame.K_w]:
            dir.y -= 1
        if keys[pygame.K_s]:
            dir.y += 1

        return dir
