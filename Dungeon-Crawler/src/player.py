"""FIXME"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2, Surface

from entity import Entity


class Player(Entity):
    """FIXME"""

    __slots__: list[str] = ["_curr_group",
                            "_curr_step"]

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 HP: int = 100) -> None:
        """
        Player Fish controlled by the user.

        Args:
            world (Any): World parent.
            position (Vector2, optional): position. Defaults to 0, 0.
            HP (int | None, optional): Hitpoints.
        """
        # get player sprite sheet
        self._assets: dict[str, Surface] = dict[str, Surface]()
        player_sprite_sheet = Path(__file__).parent / \
            "../assets/visual/sprites/player/Fish-Sheet.png"
        sheet: Surface = pygame.image.load(player_sprite_sheet)
        self._all_frames_from_sheet(sheet, (16, 16), 3, "ESNW", "move")

        self._curr_group: str = 'E'
        self._curr_step: str = '0'

        super().__init__(world, position, HP=HP, assets=self._assets, anim_timer=50.0,
                         image=self._assets[f"{self._curr_group}move0"])

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        super().loop(delta, self.player_movement(keys))

    def player_movement(self, keys: pygame.key.ScancodeWrapper) -> Vector2:
        """FIXME"""
        # take in inputs
        dir: Vector2 = Vector2()
        if keys[pygame.K_d]:
            dir.x += 1
            self._orientation = True
            self._curr_group = "E"
        if keys[pygame.K_a]:
            dir.x -= 1
            self._orientation = False
            self._curr_group = "W"
        if keys[pygame.K_w]:
            dir.y -= 1
            self._curr_group = "N"
        if keys[pygame.K_s]:
            dir.y += 1
            self._curr_group = "S"

        return dir

# ---- player animation ----

    def animate(self) -> None:
        """
        player animation
        """
        diff_x: float = self._position.x - self._prev_position.x
        diff_y: float = self._position.y - self._prev_position.y

        if not self._curr_orient == self._orientation and self._curr_group == "E":
            self._curr_orient = not self._curr_orient
            self.image = pygame.transform.flip(self.image, True, False)

        self._anim_timer -= abs(diff_x) + abs(diff_y)

        if self._anim_timer < 0:
            self._anim_timer = self._anim_timer_top

            if self._curr_step == "0":
                self._curr_step = "1"
            else:
                self._curr_step = "0"
        self.image = self._assets[f"{self._curr_group}move{self._curr_step}"]
