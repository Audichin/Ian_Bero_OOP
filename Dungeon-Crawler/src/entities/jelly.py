"""Jelly Entity Module."""
from pathlib import Path
from typing import Any
from math import sin

import pygame
from pygame import Vector2, Surface, Rect

from entities.entity_mod import Entity


class Jelly(Entity):
    """
    Simple enemy

    Stays in place until the player is within range.

    When player is in range, inch towards them on an interval
    """
    _DIST_DETECT: float = 350.0
    _MOVE_INTERVAL: float = 2  # measured in seconds

    __slots__: list[str] = ["_move_timer"]  # float

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 300,
                 clamp_speed: float = 300,
                 friction: float = 5,
                 HP: int = 3) -> None:
        """Jellies are simple enemies that attack the player when they're close"""
        self._move_timer: float = self._MOVE_INTERVAL

        self._assets: dict[str, Surface] = dict[str, Surface]()
        jelly_sprite_sheet = Path(__file__).parent / \
            "../../assets/visual/sprites/jelly/Jelly-Sheet.png"
        sheet: Surface = pygame.image.load(jelly_sprite_sheet)
        self._all_frames_from_sheet(sheet, (16, 16), 2, "M", "")

        super().__init__(world, speed=speed, clamp_speed=clamp_speed, friction=friction,
                         position=position, assets=self._assets, image=self._assets["M1"],
                         HP=HP)

    def _sound_init(self) -> None:
        """Jellyfish sound initialization
        """
        self._sounds['hurt'] = 6
        self._sounds['move'] = 6
        self._sounds['death'] = 1

# ==== properties ====

    def damage(self, dmg: int) -> None:
        if self._invincibility <= 0:
            self.play_sound('hurt')
        super().damage(dmg)
        if self.HP <= 0:
            self.play_sound('death')

# ==== base methods ====

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        """Jellyfish loop method. Attacks and moves.

        Args:
            delta (float): delta time.
        """
        self.jelly_attack()
        return super().loop(delta, self.jelly_move(delta))

    def render(self, time: float) -> list[tuple[Surface, Rect]]:
        """Jellyfish render method.

        Args:
            time (float): delta time.

        Returns:
            list[tuple[Surface, Rect]]: Entity render data.
        """
        if self._invincibility > 0:
            self.image.set_alpha(int(abs(sin(time * 10) * 255)))
        else:
            self.image.set_alpha(255)
        return super().render(time)

    def animate(self, time: float) -> None:
        anim_step: int = int(time % 2)
        if anim_step:
            self.image = self._assets["M0"]
        else:
            self.image = self._assets["M1"]

# ---- jelly methods ----

    def jelly_move(self, delta: float) -> Vector2:
        """Jelly movement logic.

        Jelly detects if the player is close enough, and then accelerates in
        that direction.

        Args:
            delta (float): delta time.

        Returns:
            Vector2: movement direction vector.
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
                self.play_sound('move')
                self._move_timer = self._MOVE_INTERVAL
                vector_ret = Vector2(direction.x, direction.y)

        return vector_ret

    def jelly_attack(self) -> None:
        """Deal one point of damage if touching player.
        """
        if self._world.entity_action(self, "player_col"):
            self._world.entity_action(self, "player_dmg_1")
