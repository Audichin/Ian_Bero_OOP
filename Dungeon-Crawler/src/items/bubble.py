"""
bubble module.

A bubble is a simple base weapon used by the player in the game.
When the player starts the game, they will only have the bubble.

The weapon produces bubbles. The projectile is the bubble itself.
"""
from typing import Any

from pygame import Vector2, Surface, Rect

try:
    from .item import Item
except ImportError:
    from items.item import Item


class BubbleWeapon(Item):
    """
    Bubble Weapon class.

    When used, produces a moving bubble in front of the player. The bubble checks
    for any collisions with entities and if it collides, pops and deals damage.

    If there are no collisions with entities, slows down and pops on its own.
    """

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(-999, -999),
                 state: int = Item.COLLECTED,
                 type: int = Item.MULTIUSE,
                 assets: dict[str, Surface] | None = None,
                 image: Surface | None = None) -> None:
        """
        Bubble weapon object initialization.

        Since this weapon initializes into the player inventory as soon as the game
        runs, the followings variables are set:
        * state = COLLECTED: Already collected into the player inventory.
        * type = MULTIUSE: Can be used multiple times.
        """
        super().__init__(world, position, state, type, assets, image)
