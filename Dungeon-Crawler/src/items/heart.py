"""
heart item module.
"""
from pathlib import Path
from typing import Any

from pygame import Vector2, sprite, Surface, Rect

try:
    from .item import Item
except ImportError:
    from items.item import Item


class Heart(Item):
    """
    Heart item class.

    A heart is a healing item. When the player touches a heart,
    their HP goes up.
    """

    def __init__(self, world: Any,
                 position: Vector2) -> None:
        """
        Heart class item.

        Heals the player when touched.

        Args:
            world (Any): World this item belongs to.
            position (Vector2): Position of this item.
        """
        super().__init__(world, position)

    def _sound_init(self) -> None:
        """Heart sounds."""
        self._sounds['heal'] = 5

# ==== heart methods ====

    def check_player_touched(self) -> None:
        if self._world.item_action(self, "grabbed"):
            self._world.item_action(self, "heal_1")
            self.play_sound('heal')
            self._world.item_action(self, "use")
