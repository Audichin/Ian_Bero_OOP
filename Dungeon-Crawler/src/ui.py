"""
UI Module

> Displays game data in an inuitive format for the player.
"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Surface, Rect


class UI:
    """
    UI class.

    Contains Surfaces to display with their rects.
    This class doesn't have access to world. Instead,
    world will pass updates and values to update.
    """

    _RESOLUTION: tuple[int, int] = (1440, 810)
    _SCALE: int = 5
    __slots__ = ["_assets",  # dict[str, Surface]
                 "_hearts",  # list[list[Any]]
                 "_player_hp"]  # int (player health)
# ==== inits ====

    def __init__(self) -> None:
        """UI Init."""
        self._assets: dict[str, Surface] = {}
        self._player_hp: int = 10
        self.__init_item_slot()
        self.__init_hearts()
        self.__init_gameover()

    def __init_item_slot(self) -> None:
        """Initializes the item slot for rendering."""
        path: Path = Path(__file__).parent / \
            "../assets/visual/ui/item_slot.png"
        self._store_ui_element('item_slot', pygame.image.load(path), (0, 0), (32, 32))

    def __init_hearts(self) -> None:
        """Initializes the hearts for rendering."""
        path: Path = Path(__file__).parent / \
            "../assets/visual/ui/Hearts-Sheet.png"
        heart_sheet: Surface = pygame.image.load(path)
        # Retrive three stages of hearts
        self._store_ui_element('hearts_2', heart_sheet, (0, 0), (16, 16))
        self._store_ui_element('hearts_1', heart_sheet, (16, 0), (16, 16))
        self._store_ui_element('hearts_0', heart_sheet, (32, 0), (16, 16))

        # Set hearts for display
        self._hearts: list[list[Any]] = []
        for i in range(5):
            heart_rect: Rect = self._assets['hearts_2'].get_rect()
            heart_rect.topleft = (0, (i*16*self._SCALE))
            self._hearts.append([self._assets['hearts_2'], heart_rect])

    def __init_gameover(self) -> None:
        """Initialize asset for game over"""
        path: Path = Path(__file__).parent / \
            "../assets/visual/ui/gameover.png"
        gameover_sheet: Surface = pygame.image.load(path)
        # Retrieve and store game over image
        self._store_ui_element('gameover', gameover_sheet, (0, 0), (160, 64))

# ==== base ====

    def render(self) -> list[tuple[Surface, Rect]]:
        """Return all displays"""
        temp: list[tuple[Surface, Rect]] = []

        # append hearts to the display
        for heart in self._hearts:
            temp.append((heart[0], heart[1]))

        # append the item slot to the display
        item_slot_rect: Rect = self._assets['item_slot'].get_rect()
        item_slot_rect.topleft = (0, self._RESOLUTION[1] - 32*self._SCALE)
        temp.append((self._assets['item_slot'], item_slot_rect))

        # append item on top of the display
        item_rect: Rect = self._assets['item'].get_rect()
        item_rect.topleft = (0, self._RESOLUTION[1] - 32*self._SCALE)
        temp.append((self._assets['item'], item_rect))

        if self._player_hp <= 0:
            gameover_rect: Rect = self._assets['gameover'].get_rect()
            gameover_rect.topleft = (64 * self._SCALE, 32 * self._SCALE)
            temp.append((self._assets['gameover'], gameover_rect))

        return temp

# ==== UI methods ====

    def update_hearts(self, hp: int) -> None:
        """Update heart UI according to player health."""
        self._player_hp = hp
        for indx, heart in enumerate(self._hearts):
            rel_hp: int = hp - (indx*2)
            if rel_hp > 2:
                continue
            elif rel_hp < 0:
                heart[0] = self._assets['hearts_0']
                continue
            heart[0] = self._assets[f'hearts_{rel_hp}']

    def update_item_slot(self, item_name: str) -> None:
        """Update the item in the item slot."""
        item_path: Path = Path(__file__).parent / \
            f"../assets/visual/items/{item_name}/icon.png"
        self._store_ui_element('item', pygame.image.load(item_path), (0, 0), (32, 32))

# ==== get image from file ====

    def _store_ui_element(self, name: str,
                          image: Surface,
                          position: tuple[int, int],
                          dimension: tuple[int, int]) -> None:
        """FIXME"""
        single: Surface = Surface(dimension).convert_alpha()
        single.blit(image, (0, 0), (position[0], position[1], dimension[0], dimension[1]))
        single = pygame.transform.scale(single, (dimension[0] * self._SCALE,
                                                 dimension[1] * self._SCALE))
        single.set_colorkey((0, 0, 0))
        # store into dictionaries
        self._assets[name] = single
