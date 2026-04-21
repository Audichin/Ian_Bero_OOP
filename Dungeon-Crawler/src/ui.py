"""
UI Module

> Displays game data in an inuitive format for the player.
"""
from pathlib import Path

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
                 "_hearts"]  # list[tuple[Surface, Rect]]

# ==== inits ====

    def __init__(self) -> None:
        """UI Init."""
        self._assets: dict[str, Surface] = {}
        self.__init_item_slot()
        self.__init_hearts()

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
        self._hearts: list[tuple[Surface, Rect]] = []
        for i in range(5):
            heart_rect: Rect = self._assets['hearts_2'].get_rect()
            heart_rect.topleft = (0, (i*16*self._SCALE))
            self._hearts.append((self._assets['hearts_2'], heart_rect))

# ==== base ====

    def render(self) -> list[tuple[Surface, Rect]]:
        """Return all displays"""
        temp: list[tuple[Surface, Rect]] = []
        # append the item slot to the display
        item_slot_rect: Rect = self._assets['item_slot'].get_rect()
        item_slot_rect.topleft = (0, self._RESOLUTION[1] - 32*self._SCALE)
        temp.append((self._assets['item_slot'], item_slot_rect))

        # append hearts to the display
        for heart in self._hearts:
            temp.append(heart)

        return temp

# ==== UI methods ====

# ==== get image from file ====

    def _store_ui_element(self, name: str,
                          image: Surface,
                          position: tuple[int, int],
                          dimension: tuple[int, int]) -> None:
        """FIXME"""
        single: Surface = Surface(dimension).convert_alpha()
        single.blit(image, (position[0], position[1]), (0, 0, dimension[0], dimension[1]))
        single = pygame.transform.scale(single, (dimension[0] * self._SCALE,
                                                 dimension[1] * self._SCALE))
        single.set_colorkey((0, 0, 0))
        # store into dictionaries
        self._assets[name] = single
