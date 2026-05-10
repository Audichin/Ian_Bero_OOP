"""Urchin entity module."""
from pathlib import Path
from typing import Any
from math import sin

import pygame
from pygame import Vector2, Surface, Rect

from entities.entity_mod import Entity


class Urchin(Entity):
    """
    Urchin enemy

    Moves towards the player in a single axis at a time.
    """

    _MOVE_INTERVAL: float = 1

    __slots__: list[str] = ["_bounds",  # dict[str, tuple[int, int]]
                            "_move_timer",  # float
                            "_target_pos",  # list[float]
                            "_directions"]  # list[tuple(int, int)]

# ==== inits ====

    def __init__(self, world: Any,
                 bounds: dict[str, tuple[int, int]],
                 position: Vector2 = Vector2(),
                 speed: float = 50,
                 clamp_speed: float = 400,
                 friction: float = 25,
                 HP: int = 3) -> None:
        """Urchins are enemies that move in a single direction at a time."""
        # intialize variables
        self._bounds: dict[str, tuple[int, int]] = bounds
        self._move_timer: float = self._MOVE_INTERVAL
        self._target_pos: list[float] = []
        self._directions: list[tuple[int, int]] = []

        # Get urchin asset
        self._assets: dict[str, Surface] = dict[str, Surface]()
        urchin_sprite_sheet: Path = Path(__file__).parent / \
            "../../assets/visual/sprites/urchin/urchin-sheet.png"
        sheet: Surface = pygame.image.load(urchin_sprite_sheet)
        self._all_frames_from_sheet(sheet, (32, 32), 4, "M", "")

        super().__init__(world, position, speed, clamp_speed, friction,
                         HP, image=self._assets["M0"], assets=self._assets)

    def _sound_init(self) -> None:
        """Urchin sound initialization.
        """
        self._sounds['hurt'] = 6
        self._sounds['move'] = 3
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
        """Urchin loop method.

        Executes movement and attack logic.

        Args:
            delta (float): delta time.
            move (Vector2 | None, optional): Movement direction vector. Defaults to None.
        """
        self.urchin_attack()
        return super().loop(delta, self.urchin_move(delta))

    def render(self, time: float) -> list[tuple[Surface, Rect]]:
        """Urchin render method.

        Args:
            time (float): time elapsed since game start.

        Returns:
            list[tuple[Surface, Rect]]: urchin render data.
        """
        if self._invincibility > 0:
            self.image.set_alpha(int(abs(sin(time * 10) * 255)))
        else:
            self.image.set_alpha(255)
        return super().render(time)

    def animate(self, time: float) -> None:
        """Urchin animation. loops between four frames.

        Args:
            time (float): time elapsed since game start.
        """
        anim_step: int = int((time * self.move_speed / 100) % 4)
        self.image = self._assets[f'M{anim_step}']

# ==== urchin methods ====

    def urchin_move(self, delta: float) -> Vector2:
        """
        Urchin movement logic.

        Detect where the player is, set directions and target positions.

        Once moving, move in a single prioritized axis until the target has been passed.

        Args:
            delta (float): delta time.

        Returns:
            Vector2: Movement direction vector.
        """
        # check if we are moving
        self.__check_all_potential()

        if len(self._directions) and self._move_timer <= 0:
            if self.move_speed == 0:
                self.play_sound('move')
            return Vector2(self._directions[0][0], self._directions[0][1])

        # Not moving:
        # decrement timer
        self._move_timer -= delta

        # When the timer runs out, set direction and target
        if self._move_timer <= 0 and not len(self._directions):
            player: Vector2 = self._world.entity_action(self, "player_pos")
            diff: Vector2 = Vector2(player.x - self._position.x, player.y - self._position.y)
            abs_diff: tuple[float, float] = (abs(diff.x), abs(diff.y))

            if diff.x == 0:
                diff.x = 0.0001
            if diff.y == 0:
                diff.y = 0.0001

            # Set diff and targets
            if abs_diff[0] > abs_diff[1]:
                self._directions.append((int(diff.x / abs(diff.x)), 0))
                self._directions.append((0, int(diff.y / abs(diff.y))))
                self._target_pos.append(player.x)
                self._target_pos.append(player.y)
            else:
                self._directions.append((0, int(diff.y / abs(diff.y))))
                self._directions.append((int(diff.x / abs(diff.x)), 0))
                self._target_pos.append(player.y)
                self._target_pos.append(player.x)

        return Vector2()

    def urchin_attack(self) -> None:
        """If touching player, deal 2 damage to player.
        """
        if self._world.entity_action(self, "player_col"):
            self._world.entity_action(self, "player_dmg_2")

    def __check_all_potential(self) -> None:
        """Check all the potential directions.

        If there has been a collision or the urchin has passed the target,
        pop the current direction and target, and reset the movement timer.
        """
        if len(self._directions):
            if self._world.entity_action(self, "s_col"):
                self._directions.pop(0)
                self._target_pos.pop(0)
                self._move_timer = self._MOVE_INTERVAL
            elif self._directions[0][0] == 0:
                # check bounds
                # check if we have passed the target in the y direction
                if self.__check_y_bounds() or self.__check_y_target():
                    self._directions.pop(0)
                    self._target_pos.pop(0)
                    self._move_timer = self._MOVE_INTERVAL
            elif self._directions[0][1] == 0:
                # check bounds
                # check if we have passed the target in the x direction
                if self.__check_x_bounds() or self.__check_x_target():
                    self._directions.pop(0)
                    self._target_pos.pop(0)
                    self._move_timer = self._MOVE_INTERVAL

    def __check_y_target(self) -> bool:
        """
        Check if Urchin has passed the target in the Y direction.

        Returns:
            bool: True if target pass. False if not.
        """
        if self._directions[0][1] > 0:
            return True if self.position.y > self._target_pos[0] else False
        elif self._directions[0][1] < 0:
            return True if self.position.y < self._target_pos[0] else False
        return False  # pragma nocover

    def __check_x_target(self) -> bool:
        """
        Check if Urchin has passed the target in the X direction.

        Returns:
            bool: True if target pass. False if not.
        """
        if self._directions[0][0] > 0:
            return True if self.position.x > self._target_pos[0] else False
        elif self._directions[0][0] < 0:
            return True if self.position.x < self._target_pos[0] else False
        return False  # pragma nocover

    def __check_y_bounds(self) -> bool:
        """Check if the target is outside of Urchin Y-axis bounds.

        Returns:
            bool: True if target out of bounds. False if not.
        """
        if self._target_pos[0] < self._bounds['Y'][0]:
            return True
        elif self._target_pos[0] > self._bounds['Y'][1]:
            return True
        return False

    def __check_x_bounds(self) -> bool:
        """Check if the target is outside of Urchin X-axis bounds.

        Returns:
            bool: True if target out of bounds. False if not.
        """
        if self._target_pos[0] < self._bounds['X'][0]:
            return True
        elif self._target_pos[0] > self._bounds['X'][1]:
            return True
        return False
