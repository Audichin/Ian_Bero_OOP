
import typing_extensions
import pygame
from pygame import Vector2
from pygame import locals


class Entity:
    """
    Base class for all entity types.
    """
    __slots__ = ["_position"
                 , "_velocity"
                 , "_speed"
                 , "_max_speed"
                 , "_hitpoints"]

    def __init__(self, position : Vector2 = Vector2(0, 0)
                 , velocity : Vector2 = Vector2(0, 0)
                 , speed : float = 5.0
                 , max_speed : float = 10.0
                 , hitpoints : int = 100) -> None:
        """Entity Init.

        Args:
            position (tuple[float, float], optional): Entity Position
            velocity (tuple[float, float], optional): Entity Velocity
            speed (float, optional): Entity speed.
            max_speed (float, optional): Maximum possible speed.
            hitpoints (int, optional): Entity health.
        """
        self._position : Vector2 = position  # x, y
        self._velocity : Vector2 = velocity  # x, y
        self._speed : float = speed
        self._max_speed : float = max_speed
        self._hitpoints : int = hitpoints

    def loop(self) -> None:
        self.move()
        print(f"pos: {self._position}\nvel: {self._velocity}")

    def move(self, x_dir : int = 0, y_dir : int = 0) -> None:
        """Check if there is a direction. If so, increase velocity in that position. Otherwise,
        bring it to zero.

        Args:
            direction (tuple[int, int] | None, optional): Direction of movement. Defaults to None.
        """

        if x_dir != 0:
            self._velocity.x += (self._speed * x_dir)
        elif self._velocity.x != 0.0:
            self._velocity.x += ((-(self._velocity.x)/abs(self._velocity.x)) * self._speed)

            self._velocity.x = 0.0 if abs(self._velocity.x) < 0.5 else self._velocity.x

        if y_dir != 0:
            self._velocity.y += (self._speed * y_dir)
        elif self._velocity.y != 0.0:
            self._velocity.y += ((-(self._velocity.y)/abs(self._velocity.y)) * self._speed)

            self._velocity.y = 0.0 if abs(self._velocity.y) < 0.5 else self._velocity.y

        self._position.x += self._velocity.x
        self._position.y += self._velocity.y
