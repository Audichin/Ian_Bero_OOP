"""
Boss entity module.

Contains both the actual Boss entity and the Boss projectiles.
"""
from pathlib import Path
from typing import Any
from math import sin

import pygame
from pygame import Vector2, Surface, Rect

from entities.entity_mod import Entity
from items.projectile import Projectile


class Boss(Entity):
    """
    Boss enemy

    Acts as all other entities combined into a hybrid.
    Changes between jelly and urchin movements as a pattern,
    and shoots in four directions between transitions.
    """

# ==== modes ====

    _JELLY: int = 0
    _URCHIN: int = 1

# ==== constants ====

    _JELLY_MOVE_INTERVAL: float = 1.5
    _URCHIN_MOVE_INTERVAL: float = 0.8
    _SWITCH_INTERVAL: float = 5

    _JELLY_ATTRIBUTES: dict[str, int] = {
        'speed': 500,
        'clamp': 500,
        'friction': 5
    }

    _URCHIN_ATTRIBUTES: dict[str, int] = {
        'speed': 600,
        'clamp': 600,
        'friction': 30
    }

    __slots__: list[str] = ["_bounds",  # dict[str, tuple[int, int]]
                            "_move_timer",  # float
                            "_target_pos",  # list[float]
                            "_directions",  # list[tuple(int, int)]
                            "_shots",  # list[BossShot]
                            "_mode",  # int
                            "_mode_timer"]  # float

# ==== inits ====

    def __init__(self, world: Any,
                 bounds: dict[str, tuple[int, int]],
                 position: Vector2 = Vector2(),
                 HP: int = 15) -> None:
        """
        The boss is a hybrid enemy of all the other enemies combined.
        """
        # initialize variables
        self._bounds: dict[str, tuple[int, int]] = bounds
        self._move_timer: float = self._JELLY_MOVE_INTERVAL
        self._target_pos: list[float] = []
        self._directions: list[tuple[int, int]] = []
        self._shots: list[BossShot] = []
        self._mode: int = self._JELLY
        self._mode_timer: float = self._SWITCH_INTERVAL

        # get boss assets
        self._assets: dict[str, Surface] = dict[str, Surface]()
        boss_sprite_sheet: Path = Path(__file__).parent / \
            "../../assets/visual/sprites/boss/boss-Sheet.png"
        sheet: Surface = pygame.image.load(boss_sprite_sheet)
        self._all_frames_from_sheet(sheet, (32, 32), 2, "M", "")

        super().__init__(world, position, self._JELLY_ATTRIBUTES['speed'],
                         self._JELLY_ATTRIBUTES['clamp'], self._JELLY_ATTRIBUTES['friction'],
                         HP, image=self._assets["M0"], assets=self._assets)

    def _sound_init(self) -> None:
        """Initialize boss sounds"""
        self._sounds['hurt'] = 6
        self._sounds['shoot'] = 2
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
        """
        Boss loop. Handles shots, movement, and behavior.

        Args:
            delta (float): delta time
        """
        self.switch_mode(delta)
        self.boss_attack()

        # handle shots
        for indx, shot in enumerate(self._shots):
            shot.loop(delta)
            if self._world.entity_action(self, "player_col", shot):
                self._world.entity_action(self, "player_dmg_1")
                self._shots.pop(indx)

        return super().loop(delta, self.boss_move(delta))

    def render(self, time: float) -> list[tuple[Surface, Rect]]:
        """
        Boss render. Returns itself and all its projectiles.

        Args:
            time (float): Time the program has been run for.

        Returns:
            list[tuple[Surface, Rect]]: list of rendering attributes.
        """
        if self._invincibility > 0:
            self.image.set_alpha(int(abs(sin(time * 10) * 255)))
        else:
            self.image.set_alpha(255)

        # render shots
        to_render: list[tuple[Surface, Rect]] = []
        for shot in self._shots:
            to_render.append(shot.render())
        for entity in super().render(time):
            to_render.append(entity)
        return to_render

    def animate(self, time: float) -> None:
        """
        Boss animation. Switch between two sprites.

        Args:
            time (float): Time since the start of program in seconds.
        """
        anim_step: int = int(time % 2)
        if anim_step:
            self.image = self._assets['M0']
        else:
            self.image = self._assets['M1']

# ==== boss methods ====

    def boss_move(self, delta: float) -> Vector2:
        """
        Check what mode we are in.

        Depending on the mode type, we return a different Vector2

        Args:
            delta (float): Delta time.

        Raises:
            Exception: _description_

        Returns:
            Vector2: _description_
        """
        match self._mode:
            case self._JELLY:
                return self.jelly_move(delta)
            case self._URCHIN:
                return self.urchin_move(delta)

        raise Exception("Didnt match a mode.")  # pragma nocover

    def boss_shoot(self) -> None:
        """
        Shoot in four directions
        """

        self.play_sound('shoot')
        # get player position and difference
        pattern: dict[str, list[int]]
        if self._mode == self._JELLY:
            pattern = {
                'X': [-1, 0, 1, 0],
                'Y': [0, -1, 0, 1]
            }
        else:
            pattern = {
                'X': [-1, -1, 1, 1],
                'Y': [1, -1, 1, -1]
            }

        # create shots
        for i in range(4):
            new_shot: BossShot = BossShot(self.position)
            new_shot.push(Vector2(pattern['X'][i], pattern['Y'][i]))
            self._shots.append(new_shot)

    def boss_attack(self) -> None:
        """If touching player, deal 2 damage.
        """
        if self._world.entity_action(self, "player_col"):
            self._world.entity_action(self, "player_dmg_2")

    def switch_mode(self, delta: float) -> None:
        """
        Switch to the next mode when mode timer is zero

        Args:
            delta (float): delta time
        """
        # decrement timer
        self._mode_timer -= delta

        if self._mode_timer <= 0:
            self._mode += 1
            self._mode_timer = self._SWITCH_INTERVAL
            if self._mode > self._URCHIN:
                self._mode = self._JELLY
            self.boss_shoot()

            # set attributes
            match self._mode:
                case self._JELLY:
                    self._speed = self._JELLY_ATTRIBUTES['speed']
                    self._clamp_speed = self._JELLY_ATTRIBUTES['clamp']
                    self._friction = self._JELLY_ATTRIBUTES['friction']
                case self._URCHIN:
                    self._speed = self._URCHIN_ATTRIBUTES['speed']
                    self._clamp_speed = self._URCHIN_ATTRIBUTES['clamp']
                    self._friction = self._URCHIN_ATTRIBUTES['friction']

# ==== jelly ====

    def jelly_move(self, delta: float) -> Vector2:
        """
        Jelly behavior.

        Args:
            delta (float): delta time
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

        # Move towards the player once timer
        # reached zero.
        self._move_timer -= delta
        if self._move_timer <= 0.0:
            self.play_sound('move')
            self._move_timer = self._JELLY_MOVE_INTERVAL
            vector_ret = Vector2(direction.x, direction.y)

        return vector_ret

# ==== urchin ====

    def urchin_move(self, delta: float) -> Vector2:
        """
        Urchin behavior.

        Args:
            delta (float): delta time
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
            diff.x = 0.00001 if diff.x == 0 else diff.x
            diff.y = 0.00001 if diff.y == 0 else diff.y
            abs_diff: tuple[float, float] = (abs(diff.x), abs(diff.y))

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

    def __check_all_potential(self) -> None:
        """Check all the potential directions in Urchin behavior.

        If there has been a collision or the boss has passed the target,
        pop the current direction and target, and reset the movement timer.
        """
        if len(self._directions):
            if self._world.entity_action(self, "s_col"):
                self._directions.pop(0)
                self._target_pos.pop(0)
                self._move_timer = self._URCHIN_MOVE_INTERVAL
            elif self._directions[0][0] == 0:
                # check bounds
                # check if we have passed the target in the y direction
                if self.__check_y_bounds() or self.__check_y_target():
                    self._directions.pop(0)
                    self._target_pos.pop(0)
                    self._move_timer = self._URCHIN_MOVE_INTERVAL
            elif self._directions[0][1] == 0:
                # check bounds
                # check if we have passed the target in the x direction
                if self.__check_x_bounds() or self.__check_x_target():
                    self._directions.pop(0)
                    self._target_pos.pop(0)
                    self._move_timer = self._URCHIN_MOVE_INTERVAL

    def __check_y_target(self) -> bool:
        """
        Check if boss has passed the target in the Y direction.

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
        Check if boss has passed the target in the X direction.

        Returns:
            bool: True if target pass. False if not.
        """
        if self._directions[0][0] > 0:
            return True if self.position.x > self._target_pos[0] else False
        elif self._directions[0][0] < 0:
            return True if self.position.x < self._target_pos[0] else False
        return False  # pragma nocover

    def __check_y_bounds(self) -> bool:
        """Check if the target is outside of urchin Y-axis bounds.

        Returns:
            bool: True if target out of bounds. False if not.
        """
        if self._target_pos[0] < self._bounds['Y'][0]:
            return True
        elif self._target_pos[0] > self._bounds['Y'][1]:
            return True
        return False

    def __check_x_bounds(self) -> bool:
        """Check if the target is outside of urchin X-axis bounds.

        Returns:
            bool: True if target out of bounds. False if not.
        """
        if self._target_pos[0] < self._bounds['X'][0]:
            return True
        elif self._target_pos[0] > self._bounds['X'][1]:
            return True
        return False


class BossShot(Projectile):
    """Boss projectile"""

    def __init__(self, position: Vector2,
                 speed: float = 300,
                 friction: float = .5) -> None:
        """Boss projectiles deal more damage than regular projectiles, and are
        large.
        """
        shot_path: Path = Path(__file__).parent / \
            "../../assets/visual/sprites/boss/boss_shot.png"
        shot_sheet: Surface = pygame.image.load(shot_path)
        super().__init__(position, speed, friction,
                         image=self._single_from_sheet(shot_sheet, (16, 16)))
