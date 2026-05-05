"""
Key item module.
"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2

try:
    from .item import Item
except ImportError:
    from items.item import Item


class Key(Item):
    """
    Key item class.

    A key is used to open the boss door in the dungeon.
    """

    def __init__(self, world: Any) -> None:
        """
        Key class item

        When four fragments are collected, is stored in inventory.

        Args:
            world (Any): world this item belongs to.
        """
        key_path = Path(__file__).parent / \
            "../../assets/visual/items/key/key.png"
        key_sheet = pygame.image.load(key_path)
        super().__init__(world, state=Item.COLLECTED,
                         image=self._single_from_sheet(key_sheet, (16, 16)))


class KeyFragment(Item):
    """
    Key Fragment item class.

    A key fragment are the individual pieces needed to make a full key.
    """

    def __init__(self, world: Any,
                 position: Vector2) -> None:
        """
        Key fragment class item.

        Stored in inventory when touched.

        Args:
            world (Any): World this item belongs to.
            position (Vector2): Position of this item.
        """
        key_fragment_path = Path(__file__).parent / \
            "../../assets/visual/items/key/key_fragment.png"
        key_fragment_sheet = pygame.image.load(key_fragment_path)
        super().__init__(world, position,
                         image=self._single_from_sheet(key_fragment_sheet, (16, 16)))

    def _sound_init(self) -> None:
        """Key Fragment Sounds."""
        self._sounds['collect'] = 0

    def check_player_touched(self) -> None:
        if self._world.item_action(self, "grabbed"):
            self.play_sound('collect')
        return super().check_player_touched()
