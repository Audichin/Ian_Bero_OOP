"""
item module.

Items in our dungeon crawler game are objects that can be picked up
and used by the player. Items can have various uses and functionalities,
and can even serve as weapons for player use.

This base module doesn't have any base functionality for items, it is
a stepping stone for other items to be created.
"""
from pathlib import Path
from typing import Any

# import pygame
from pygame import Vector2, sprite, Surface, Rect


class Item(sprite.Sprite):
    """
    Item class.

    An item is an in-game object that can be interacted with through player collision.
    When an item collides with the player character, the item disappears from the render
    and is stored in the player inventory.

    Special items can have special behaviors that aren't initialized here. Some
    Examples can include:
    * A sword that can be swung by the player.
    * A key that unlocks a door.
    * A bomb that deals area of effect damage.

    The base class of Item doesn't do much other than exist in the game world to be picked up,
    and when it is stays in the inventory.
    """

    _SCALE: int = 5
    ICON: Path = Path()  # placeholder for item slot items

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
        """
        Item class object.

        Args:
            world (Any): The world inheriting this Item.
            position (Vector2, optional): The position of this Item. Defaults to Vector2().
            state (int, optional): Item state to start. Defaults to GROUNDED.
            type (int, optional): Item type. Helps define behavior. Defaults to SINGLEUSE.
            assets (dict[str, Surface] | None, optional): Image assets. Defaults to None.
            image (Surface | None, optional): Current image to display. Defaults to None.
        """
        super().__init__()
        from world import World
        self._world: World = world

        self._position: Vector2 = position

        self._state: int = state
        self._type: int = type

        self._assets = assets
        self.__image_init(image)

    def __image_init(self, img_in: Surface | None = None) -> None:
        """
        Item Image initialization.

        Args:
            img_in (Surface | None): Image to display. Defaults to None.
        """
        temp_img: Surface = Surface((16 * self._SCALE, 16 * self._SCALE))
        temp_img.fill((255, 255, 255))
        if img_in:
            #  Set the image
            temp_img = img_in.convert_alpha()

        self.image: Surface = temp_img
        self.rect: Rect = self.image.get_rect()
        self.set_rect()

# ---- properties -----

    def set_rect(self) -> None:
        """Set rect value to position"""
        self.rect.center = (int(self._position.x), int(self._position.y))

    @property
    def name(self) -> str:
        """Name of this item"""
        return ""

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
        Set Item state.

        Args:
            new_state (int): State to switch to.

        Raises:
            TypeError: Raised if state passed is invalid.
        """
        if new_state not in [self.GROUNDED, self.COLLECTED, self.USED]:
            raise TypeError("Item state not valid.")

        self._state = new_state

    @property
    def type(self) -> int:
        """Item type (for defining behavior)"""
        return self._type

    @type.setter
    def type(self, new_type: int) -> None:
        self.set_type(new_type)

    def set_type(self, new_type: int) -> None:
        """
        Switch Item type.

        Args:
            new_type (int): Type to set Item to.

        Raises:
            TypeError: Raised if type passed is invalid.
        """
        if new_type not in [self.SINGLEUSE, self.MULTIUSE]:
            raise TypeError("Item type not valid.")

        self._type = new_type

# ---- base methods ----

    def loop(self, delta: float) -> None:
        """
        Item game loop.

        > If the state of the item is GROUNDED, check for player collisions.

        Args:
            delta (float): Delta time.
        """
        if self.state == self.GROUNDED:
            # Detect when the item is collected by the player.
            self.check_player_touched()

    def render(self) -> tuple[Surface, Rect]:
        """
        Item game render.

        Returns:
            tuple[Surface, Rect]: Render parameters.
        """
        self.image.set_colorkey((0, 0, 0))
        return (self.image, self.rect)

    def render_projectiles(self) -> list[tuple[Surface, Rect]]:
        """
        Item Projectile render.
        """
        return list[tuple[Surface, Rect]]()

# ---- item methods ----

    def check_player_touched(self) -> None:
        """Check if the player collects this item by colliding with it."""
        if self._world.item_action(self, "grabbed"):
            #  Change state, move it very far off screen.
            self.set_state(self.COLLECTED)
            self._position = Vector2(-999, -999)

    def item_action_a(self, player_pos: Vector2, player_look: tuple[int, int]) -> None:
        """Base method for items with actions. Does nothing."""
