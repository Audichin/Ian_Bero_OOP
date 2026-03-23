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
import pygame
from pygame import Vector2, sprite, Surface, Rect

from world import World
# from pygame import locals


class Entity(sprite.Sprite):
    """
    Base class for all entity types.
    """
    __slots__: list[str] = ["_world"  # World
                            "_assets",  # dict[Surface]
                            "_position",  # Vector2
                            "_velocity",  # Vector2
                            "_speed",  # float
                            "_max_speed",  # float
                            "_sounds",  # list[int]
                            "_HP",  # int
                            "_rect",  # Rect
                            "_image"]  # Surface

    def __init__(self, world: World,
                 position: Vector2 = Vector2(0, 0),
                 speed: float | None = None,
                 max_speed: float | None = None,
                 HP: int | None = None,
                 img: Surface | None = None,
                 rct: Rect | None = None) -> None:
        """
        Initialize Entity
        """
        super().__init__()
        self._world = world

        self._position: Vector2 = position

        self.speed = speed if speed else 0.0
        self._max_speed: float = max_speed if max_speed else 0.0
        self.HP = HP if HP else 100

        self._velocity: Vector2 = Vector2()
        self._sounds: list[int] = list[int]()

        self._assets: dict[str, Surface] = dict[str, Surface]()

        self.image = img if img else Surface([0, 0])
        self.rect = rct if rct else Rect(0.0, 0.0, 0.0, 0.0)

# ----- properties -----

    @property
    def image(self) -> Surface:
        """FIXME"""
        return self._image

    @image.setter
    def image(self, other: Surface) -> None:
        """FIXME"""
        self._image: Surface = other

    @property
    def rect(self) -> Rect:
        """FIXME"""
        return self._rect

    @rect.setter
    def rect(self, other: Rect) -> None:
        """FIXME"""
        self._rect: Rect = other

    @property
    def HP(self) -> int:
        """FIXME"""
        return self._HP

    @HP.setter
    def HP(self, other: int) -> None:
        """FIXME"""
        self._HP: int = other

    @property
    def speed(self) -> float:
        """FIXME"""
        return self._speed

    @speed.setter
    def speed(self, other: float) -> None:
        """FIXME"""
        self._speed: float = other

# ----- base methods -----

    def update(self) -> None:  # type: ignore
        """FIXME"""
        self.loop()

    def loop(self) -> None:
        """FIXME"""
        pass

    def render(self) -> None:
        """FIXME"""
        pass

# ----- entity methods -----

    def move(self, dir: Vector2) -> None:
        """FIXME"""
        pass

    def collide(self) -> None:
        """FIXME"""
        pass

    def play_sound(self, indx: int) -> None:
        """FIXME"""
        pass
