"""
bubble module.

A bubble is a simple base weapon used by the player in the game.
When the player starts the game, they will only have the bubble.

The weapon produces bubbles. The projectile is the bubble itself.
"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2, Surface, Rect

try:
    from .item import Item
    from .projectile import Projectile
except ImportError:
    from items.item import Item
    from items.projectile import Projectile


class BubbleWeapon(Item):
    """
    Bubble Weapon class.

    When used, produces a moving bubble in front of the player. The bubble checks
    for any collisions with entities and if it collides, pops and deals damage.

    If there are no collisions with entities, slows down and pops on its own.
    """

    ICON: Path = Path(__file__).parent / \
        "../../assets/visual/items/bubble_weapon/icon.png"

    __slots__ = ["_bubbles"]  # list(Bubble)

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(-999, -999),
                 state: int = Item.COLLECTED,
                 type: int = Item.MULTIUSE) -> None:
        """
        Bubble weapon object initialization.

        Since this weapon initializes into the player inventory as soon as the game
        runs, the followings variables are set:
        * state = COLLECTED: Already collected into the player inventory.
        * type = MULTIUSE: Can be used multiple times.
        """
        self._bubbles: list[Bubble] = list[Bubble]()
        super().__init__(world, position, state, type)

    @property
    def name(self) -> str:
        return "bubble_weapon"

    def loop(self, delta: float) -> None:
        """Loop over all bubble projectiles"""
        for indx, bubble in enumerate(self._bubbles):
            bubble.loop(delta)
            if bubble.move_speed == 0:
                self.kill_bubble(indx)
            else:
                if self._world.item_action(self, "attack", bubble):
                    self.kill_bubble(indx)

    def render_projectiles(self) -> list[tuple[Surface, Rect]]:
        """
        Item Projectile render.
        """
        to_render: list[tuple[Surface, Rect]] = list[tuple[Surface, Rect]]()
        for bubble in self._bubbles:
            to_render.append(bubble.render())
        return to_render

    def kill_bubble(self, index: int) -> None:
        """FIXME"""
        self._bubbles.pop(index)

    def item_action_a(self, player_pos: Vector2, player_look: tuple[int, int]) -> None:
        """Called when used by the player."""
        new_bubble: Bubble = Bubble(player_pos)
        new_bubble.push(Vector2(player_look[0], player_look[1]))
        self._bubbles.append(new_bubble)


class Bubble(Projectile):
    """
    Bubble projectile class.

    When produced, moves forwards in the world, damages entities, and pops.
    """

    def __init__(self, position: Vector2) -> None:
        """Bubble init"""
        bubble_path = Path(__file__).parent / \
            "../../assets/visual/items/bubble_weapon/Bubble_projectile.png"
        bubble_sheet = pygame.image.load(bubble_path)
        super().__init__(position, speed=600.0, friction=15.0, damage=1,
                         image=self._single_from_sheet(bubble_sheet, (15, 15)))
