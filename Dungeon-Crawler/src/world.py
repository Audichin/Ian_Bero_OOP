"""
World class module.

Manages all games within the game world.

Inccludes management for but is not limited to:
- Sound
- UI
- Dungeon
- Entities
- items

All in-world objects should be handled within this module.
Interactions between in-world objects should be handled within this module.

NOTE: MUUUCHH of the functionality is commented to allow the program to remain
functional. Please be sure to un-comment lines of code you are able to use.
"""
from typing import Any
# import pygame
# from pygame import locals

# from sound import SoundManager
from entity import Entity
# from player import Player
# from item import Item
# from ui import UI
# from structures import Dungeon, Room


class World:
    """
    World class.
    > Manages all in-world objects and their interactions with eachother.

    This Module is specific to the Dungeon Crawler project, and is not meant
    to be utilized as an API or game engine.
    """

    __slots__ = ["_sound_manager"  # : SoundManager
                 , "_sounds"  # : list[int] // int representation of sound
                 , "_entities"  # : list[Entity]
                 , "_player"  # : Player
                 , "_item_slot"  # : Item // item to be used with player action
                 , "_inventory"  # : list[Item]
                 , "_ui"  # : UI
                 , "_dungeon"  # : Dungeon
                 , "_dungeon_seed"  # : Any
                 , "_curr_room"]  # : Room

# --- initializers ---

    def __init__(self, seed : Any) -> None:
        """Init World"""
        # initialize sounds
        # self._sound_manager : SoundManager = SoundManager()
        self._sounds : list[int] = list[int]()

        # initialize entities
        self._entity_init()

        # initialize items
        # self._item_slot : Item = Item()
        # self._inventory : list[Item] = list[Item]()

        # initialize UI
        self._ui_init()

        # initialize dungeon
        self._dungeon_init(seed)

    def _dungeon_init(self, seed : Any) -> None:
        """FIXME"""
        self._dungeon_seed : Any = seed
        # self._dungeon: Dungeon = Dungeon(self._dungeon_seed)
        # self._curr_room: Room = Room(0, 0)

    def _entity_init(self) -> None:
        """FIXME"""
        self._entities : list[Entity] = list[Entity]()
        # self._player : Player = Player()

    def _ui_init(self) -> None:
        """FIXME"""
        # self._ui : UI = UI()

# --- loop method ---

    def loop(self) -> None:
        """FIXME"""
        # self._player.loop()

        for indx, entity in enumerate(self._entities):
            self._entities[indx].loop()

        self.update_room
        self.update_ui
        print("world-loop")

# --- render method ---

    def render(self) -> None:
        """FIXME"""
        # self._player.render()
        # for indx, entity in enumerate(self._entities):
        #     self._entities[indx].render()

        # while self._sounds:
        #     self._sound_manager.play_audio(self._sounds.pop())
        # self.set_world_music()

        # self._ui.render()
        # self._curr_room.render()
        print("world-render")

# --- sound methods ---

    def set_world_music(self) -> None:
        """FIXME"""
        pass

    def queue_sound(self, sound: int) -> None:
        """FIXME"""
        self._sounds.append(sound)

# --- dungeon methods ---

    def update_room(self) -> None:
        """FIXME"""
        pass

# --- UI methods ---

    def update_ui(self) -> None:
        """FIXME"""
        pass

# --- entity methods ---

    # def get_collide(self, entity: Entity) -> bool:
    #     """FIXME"""
    #     return bool()

    def player_action(self, action: str) -> None:
        """FIXME"""
        pass

    def entity_action(self, action: str) -> None:
        """FIXME"""
        pass

# --- properties ---

    @property
    def music(self) -> str:
        """Music currently playing. Handled by sound manager."""
        # return self._sound_manager.Getmusic
        return ""  # FIXME
