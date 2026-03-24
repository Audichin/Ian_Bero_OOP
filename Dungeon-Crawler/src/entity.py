"""
Entity class module.

All objects within the game that require hitpoints, movement, and interactions
should inherit entity.

Good examples:
    Player - requires health, movement, environment interaction
    Enemies - same as Player
    Bubble - Bounces around the screen checking interactions,
            and is popped (hence the need for hitpoints)

Objects that inherit entity should override entity methods and call super()
at the end of each overridden method.
"""
from typing import Any
import pygame
from pygame import Vector2, sprite, Surface, Rect

# from pygame import locals


class Entity(sprite.Sprite):
    """
    Base class for all entity types.
    """
    __slots__: list[str] = ["_world"  # Any (World this entity belongs to)
                            "_assets",  # dict[Surface]
                            "_position",  # Vector2
                            "_velocity",  # Vector2
                            "_speed",  # float
                            "_max_speed",  # float
                            "_friction",  # float
                            "_sounds",  # list[int]
                            "_HP",  # int
                            "_rect",  # Rect
                            "_image"]  # Surface

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 5.0,
                 max_speed: float = 5.0,
                 friction: float = .75,
                 HP: int | None = None,
                 img: Surface | None = None) -> None:
        """FIXME"""
        super().__init__()
        self._world = world

        self._position: Vector2 = position

        self.speed = speed
        self._max_speed: float = max_speed
        self.HP = HP if HP else 100

        self._velocity: Vector2 = Vector2()
        self._friction: float = friction
        self._sounds: list[int] = list[int]()

        self._assets: dict[str, Surface] = dict[str, Surface]()

        self.image = img if img else Surface([0, 0])
        self._rect: Rect = self.image.get_rect()
        self.set_rect()

    def assets_init(self, width: int, height: int, sheet: Surface) -> None:
        """FIXME"""
        pass

# ----- properties -----

    @property
    def image(self) -> Surface:
        """FIXME"""
        return self._image

    @image.setter
    def image(self, other: Surface) -> None:
        self._image: Surface = other

    @property
    def rect(self) -> Rect:
        """FIXME"""
        return self._rect

    def set_rect(self) -> None:
        """FIXME"""
        self._rect.center = (int(self._position.x), int(self._position.y))

    @property
    def HP(self) -> int:
        """FIXME"""
        return self._HP

    @HP.setter
    def HP(self, other: int) -> None:
        self._HP: int = other

    @property
    def speed(self) -> float:
        """FIXME"""
        return self._speed

    @speed.setter
    def speed(self, other: float) -> None:
        self._speed: float = other

    @property
    def move_speed(self) -> float:
        return self._velocity.magnitude()

# ----- base methods -----

    def update(self) -> None:  # type: ignore
        """FIXME"""
        self.loop()

    def loop(self) -> None:
        """FIXME"""
        self.move()
        self.collide()

    def render(self) -> tuple[Surface, Rect]:
        """FIXME"""
        return (self.image, self.rect)

# ----- entity methods -----

    def move(self, dir: Vector2 | None = None) -> None:
        """
        Movement for an Entity object.

        Entities move in accordance to direction

        Args:
            dir (Vector2 | None, optional): Direction of acceleration. Defaults to None.
        """
        # add direction
        if not dir:
            dir = Vector2()

        self._velocity += Vector2(dir.x * self.speed, dir.y * self.speed)

        # handle x
        try:
            self._velocity.x += -(self._velocity.x / abs(self._velocity.x)) * self._friction
            if abs(self._velocity.x) < self._friction:
                self._velocity.x = 0
        except ZeroDivisionError:
            pass

        try:
            self._velocity.y += -(self._velocity.y / abs(self._velocity.y)) * self._friction
            if abs(self._velocity.y) < self._friction:
                self._velocity.y = 0
        except ZeroDivisionError:
            pass

        # velocity clamping (check x and y of velocity)
        try:
            norm = self._velocity.normalize()
            xclamp = abs(norm.x) * self._max_speed if norm.x else self._max_speed
            yclamp = abs(norm.y) * self._max_speed if norm.y else self._max_speed
            self._velocity.x = pygame.math.clamp(self._velocity.x, -xclamp, xclamp)
            self._velocity.y = pygame.math.clamp(self._velocity.y, -yclamp, yclamp)
        except ValueError:
            pass

        self._position += self._velocity
        self.rect.center = (int(self._position.x), int(self._position.y))

    def collide(self) -> None:
        """FIXME"""
        self._world.entity_action(self, "collision")

    def play_sound(self, indx: int) -> None:
        """FIXME"""
        pass
