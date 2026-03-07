"""
World class module.

Manages all items in the game world (rooms, entities, items, etc.)


* Creates the level layout.
  > Includes saving and loading the game.

* Calls the loop of each respective entity.
* Handles requests its aggregates.

Ideally I believe there should only be one world at a time, managing levels, a single player, etc.
(makes sense, let me know)
"""
import pygame
# from pygame import locals

from entity import Entity


class World:
    """
    Object that handles the game world itself. Recieves calls and sends back data to entities.
    Singleton?
    """

    __slots__ = ["_entities"  # list[Entity]
                 , "_music"
                 , "_sounds"]

    def __init__(self) -> None:
        """Init World"""
        self._music : str = str()
        self._sounds : list[pygame.mixer.Sound] = []  # empty
        self._entities : list[Entity] = list[Entity]()

    def loop(self) -> None:
        # self._player.loop()
        pass

    def retrieve_sounds(self) -> None:
        """fixme"""
        for entity in self._entities:
            self._sounds.append(entity.curr_sound)

    @property
    def music(self) -> str:
        return self._music

    @property
    def sounds(self) -> list[pygame.mixer.Sound]:
        return self._sounds
