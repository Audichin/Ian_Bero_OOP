"""FIXME"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2, Surface

from entities.entity_mod import Entity


class Jelly(Entity):
    """
    Simple enemy:
    * detect the distance to the player
    * if player is within distance, move towards them
    * else, don't move, just stay in place
    """
    _DIST_DETECT: float = 350.0
    _MOVE_INTERVAL: float = 2  # measured in seconds

    __slots__: list[str] = ["_move_timer"]  # float

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 300,
                 clamp_speed: float = 300,
                 friction: float = 5,
                 HP: int | None = None,
                 assets: dict[str, Surface] | None = None,
                 image: Surface | None = None,
                 anim_timer: float = 100) -> None:

        self._move_timer: float = self._MOVE_INTERVAL

        self._assets: dict[str, Surface] = dict[str, Surface]()
        jelly_sprite_sheet = Path(__file__).parent / \
            "../../assets/visual/sprites/player/Jelly-Sheet.png"
        sheet: Surface = pygame.image.load(jelly_sprite_sheet)
        self._all_frames_from_sheet(sheet, (16, 16), 2, "M", "")

        super().__init__(world, speed=speed, clamp_speed=clamp_speed, friction=friction,
                         position=position, assets=self._assets, image=self._assets["M1"])

# ---- base ----

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        self.jelly_attack()
        return super().loop(delta, self.jelly_move(delta))

    def animate(self, time: float) -> None:
        anim_step: int = int(time % 2)
        if anim_step:
            self.image = self._assets["M0"]
        else:
            self.image = self._assets["M1"]

# ---- jelly methods ----

    def jelly_move(self, delta: float) -> Vector2:
        """
        1. Search for player position
            * if found, move to player
            * else, stay in place

        2. touching player?
            * deal damage
        """
        player: Vector2 = self._world.entity_action(self, "player_pos")
        diff: Vector2 = Vector2(player.x - self._position.x, player.y - self._position.y)

        # use the magnitude of the difference to get the distance.
        # check using distance detect constant
        distance: float = diff.magnitude()
        if distance == 0:
            distance = 0.00001
        direction: Vector2 = diff / distance

        vector_ret: Vector2 = Vector2(0, 0)
        if distance <= self._DIST_DETECT:
            # Move towards the player once timer
            # reached zero.
            self._move_timer -= delta
            if self._move_timer <= 0.0:
                self._move_timer = self._MOVE_INTERVAL
                vector_ret = Vector2(direction.x, direction.y)

        return vector_ret

    def jelly_attack(self) -> None:
        if self._world.entity_action(self, "player_col"):
            self._world.entity_action(self, "player_dmg_10")
