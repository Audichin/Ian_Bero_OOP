"""FIXME"""
from pathlib import Path
from typing import Any
from math import sin

import pygame
from pygame import Vector2, Surface, Rect

from entities.entity_mod import Entity
from items.projectile import Projectile


class Coral(Entity):
    """
    Coral enemy:
    * Sits in one spot while shooting at the player.
    * If projectile hits player, player takes damage.
    """

    _SHOOT_INTERVAL: float = 2.0

    __slots__: list[str] = ["_shot_timer",  # float
                            "_shots"]  # list[CoralShot]

# ==== inits ====

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 speed: float = 0,
                 clamp_speed: float = 0,
                 HP: int = 2) -> None:
        """Corals are enemies that stay in place and shoot projectiles at the player."""
        # variable inits
        self._shot_timer: float = self._SHOOT_INTERVAL
        self._shots: list[CoralShot] = list[CoralShot]()
        # Get coral assets
        self._assets: dict[str, Surface] = dict[str, Surface]()
        coral_sprite_path: Path = Path(__file__).parent / \
            "../../assets/visual/sprites/coral/coral-Sheet.png"
        sheet: Surface = pygame.image.load(coral_sprite_path)
        self._all_frames_from_sheet(sheet, (16, 16), 3, "C", "")

        super().__init__(world, position, speed, clamp_speed, HP=HP,
                         image=self._assets["C0"], assets=self._assets)

    def _sound_init(self) -> None:
        self._sounds['hurt'] = 6
        self._sounds['shoot'] = 2
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
        self.coral_attack(delta)
        for indx, shot in enumerate(self._shots):
            shot.loop(delta)
            if shot.move_speed == 0:
                self._shots.pop(indx)
            elif self._world.entity_action(self, "player_col", shot):
                self._world.entity_action(self, "player_dmg_1")
                self._shots.pop(indx)
        return super().loop(delta, move)

    def render(self, time: float) -> list[tuple[Surface, Rect]]:
        if self._invincibility > 0:
            self.image.set_alpha(int(abs(sin(time * 10) * 255)))
        else:
            self.image.set_alpha(255)
        to_render: list[tuple[Surface, Rect]] = []
        for shot in self._shots:
            to_render.append(shot.render())
        for entity in super().render(time):
            to_render.append(entity)
        return to_render

    def animate(self, time: float) -> None:
        anim_step: int = int(time * 9 % 3)
        self.image = self._assets[f'C{anim_step}']

# ==== coral methods ====

    def coral_attack(self, delta: float) -> None:
        """Shoot at the player."""
        self._shot_timer -= delta

        if self._shot_timer < 0:
            self.play_sound('shoot')
            # get player position and difference
            player: Vector2 = self._world.entity_action(self, "player_pos")
            diff: Vector2 = Vector2(player.x - self._position.x, player.y - self._position.y)
            distance: float = diff.magnitude()
            if distance == 0:
                distance = 0.00001
            direction: Vector2 = diff / distance

            # create shot
            new_shot: CoralShot = CoralShot(self.position)
            new_shot.push(direction)
            self._shots.append(new_shot)

            self._shot_timer = self._SHOOT_INTERVAL


class CoralShot(Projectile):
    """Coral Projectile"""

    def __init__(self, position: Vector2,
                 speed: float = 200,
                 friction: float = .5) -> None:
        shot_path: Path = Path(__file__).parent / \
            "../../assets/visual/sprites/coral/coral_shot.png"
        shot_sheet: Surface = pygame.image.load(shot_path)
        super().__init__(position, speed, friction,
                         image=self._single_from_sheet(shot_sheet, (8, 8)))
