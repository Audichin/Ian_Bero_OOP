"""
item module.

Items in our dungeon crawler game are objects that can be picked up
and used by the player. Items can have various uses and functionalities,
and can even serve as weapons for player use.

This base module doesn't have any base functionality for items, it is
a stepping stone for other items to be created.
"""
from typing import Any

# import pygame
from pygame import Vector2, sprite, Surface, Rect


class Item(sprite.Sprite):
    """
    Item class.
    """

    _SCALE: int = 5

# ---- State Values ----
    GROUNDED: int = 0
    COLLECTED: int = 1
    USED: int = 2

# ---- Type Values ----
    SINGLEUSE = 0
    MULTIUSE = 1

# ---- attributes ----
    __slots__: list[str] = ["_world",  # Any (World this belongs to)
                            "_assets",  # dict[str, Surface]
                            "_position",  # Vector2
                            "_sounds",  # dict[str, int]
                            "_state",  # int
                            "_type"]  # int

# ---- inits ----
    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 state: int = GROUNDED,
                 type: int = SINGLEUSE,
                 assets: dict[str, Surface] | None = None,
                 image: Surface | None = None) -> None:
        """FIXME"""
        super().__init__()
        from world import World
        self._world: World = world

        self._position: Vector2 = position

        self._state: int = state
        self._type: int = type

        self._assets = assets
        self.__image_init(image)

    def __image_init(self, img_in: Surface | None) -> None:
        """FIXME"""
        temp_img: Surface = Surface((16 * self._SCALE, 16 * self._SCALE))
        temp_img.fill((255, 255, 255))
        if img_in:
            temp_img = img_in.convert_alpha()

        self.image: Surface = temp_img
        self.rect: Rect = self.image.get_rect()
        self.set_rect()

# ---- properties -----

    def set_rect(self) -> None:
        """Set rect value to position"""
        self.rect.center = (int(self._position.x), int(self._position.y))

    @property
    def position(self) -> Vector2:
        """item position"""
        return self._position

    @property
    def state(self) -> int:
        """item state"""
        return self._state

    @state.setter
    def state(self, new_state: int) -> None:
        self.set_state(new_state)

    def set_state(self, new_state: int) -> None:
        """
        Check that state is valid
        """
        if new_state not in [self.GROUNDED, self.COLLECTED, self.USED]:
            raise TypeError("Item state not valid.")

        self._state = new_state

    @property
    def type(self) -> int:
        """item type"""
        return self._type

    @type.setter
    def type(self, new_type: int) -> None:
        self.set_type(new_type)

    def set_type(self, new_type: int) -> None:
        """
        check that type is valid
        """
        if new_type not in [self.SINGLEUSE, self.MULTIUSE]:
            raise TypeError("Item type not valid.")

        self._type = new_type

# ---- base methods ----

    def loop(self, delta: float) -> None:
        """FIXME"""
        if self.state == self.GROUNDED:
            self.check_player_touched()

    def render(self) -> tuple[Surface, Rect]:
        """FIXME"""
        return (self.image, self.rect)

# ---- item methods ----

    def check_player_touched(self) -> None:
        """FIXME"""
        if self._world.item_action(self, "grabbed"):
            self.set_state(self.COLLECTED)
            self._position = Vector2(-999, -999)
