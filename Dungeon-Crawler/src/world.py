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
import pygame
# from pygame import locals

# from sound import SoundManager
from entities.entity_mod import Entity
from entities.jelly import Jelly
from entities.player import Player
from items.item import Item
from items.projectile import Projectile
from items.bubble import BubbleWeapon
from ui import UI
# from structures import Dungeon, Room


class World:
    """
    World class.
    > Manages all in-world objects and their interactions with eachother.

    This Module is specific to the Dungeon Crawler project, and is not meant
    to be utilized as an API or game engine.
    """

    __slots__ = ["_sound_manager"  # : SoundManager
                 , "_time"  # : float
                 , "_sounds"  # : list[int] // int representation of sound
                 , "_entities"  # : list[Entity]
                 , "_player"  # : Player
                 , "_items"  # Item // items in the room
                 , "_item_slot"  # : Item // item to be used with player action
                 , "_inventory"  # : list[Item]
                 , "_ui"  # : UI
                 , "_dungeon"  # : Dungeon
                 , "_dungeon_seed"  # : Any
                 , "_curr_room"]  # : Room

# --- initializers ---

    def __init__(self, seed: Any) -> None:
        """
        World Object.

        Args:
            seed (Any): Dungeon seed.
        """
        # initialize sounds
        # self._sound_manager : SoundManager = SoundManager()
        self._sounds: list[int] = list[int]()

        # initialize entities
        self._entity_init()

        # initialize items
        self._item_init()

        # initialize UI
        self._ui_init()

        # initialize dungeon
        self._dungeon_init(seed)

        self._time: float = float()

    def _dungeon_init(self, seed: Any) -> None:
        """
        Dungeon structure initializer.
        > Initialize dungeon and hold it in memory.

        Args:
            seed (Any): Dungeon seed
        """
        self._dungeon_seed: Any = seed
        # self._dungeon: Dungeon = Dungeon(self._dungeon_seed)
        # self._curr_room: Room = Room(0, 0)

    def _entity_init(self) -> None:
        """
        Entity initializer.
        > The entity list is initialized here, along with the player.

        > The player when initialized should be placed appropriately according to

        > the starting room. All regular values should be set.
        """
        self._entities: list[Entity] = list[Entity]()
        self._entities.append(Jelly(self, position=pygame.Vector2(600, 255)))
        self._entities.append(Jelly(self, position=pygame.Vector2(300, 755)))
        self._player: Player = Player(self, position=pygame.Vector2(400, 255))

    def _ui_init(self) -> None:  # FIXME
        """
        UI initializer.
        > World UI should be initialized here.

        > All of the UI should be updated, set, and rendered according to the game

        > display.
        """
        self._ui : UI = UI()
        self._ui.update_item_slot(self._item_slot.name)

    def _item_init(self) -> None:
        """
        Item initializer.
        > Item slot should contain the bubble weapon.

        > Inventory and grounded items should be empty.
        """
        self._items: list[Item] = list[Item]()
        self._items = [
            Item(self, position=pygame.Vector2(800, 0)),
            Item(self, position=pygame.Vector2(304, 564))
            ]
        self._item_slot : Item = BubbleWeapon(self)
        self._inventory : list[Item] = list[Item]()

# --- loop method ---

    def loop(self, delta: float) -> None:
        """
        World Loop method.
        > Once per frame, loop() should be called. In a game loop, all logic is processed.

        Processed logic:
        - Room changes / updates
        - player loop
        - entity loop
        - UI changes / updates
        - etc
        """
        self._time += delta
        self._player.loop(delta)

        for indx, _entity in enumerate(self._entities):
            self._entities[indx].loop(delta)
            if _entity.HP <= 0:
                self._entities.pop(indx)

        if len(self._items):
            for indx, _item in enumerate(self._items):
                self._items[indx].loop(delta)

        self._item_slot.loop(delta)

        # print(self._inventory)

        self.update_room()
        self.update_ui()
        # print("world-loop")

# --- render method ---

    def render(self) -> list[tuple[pygame.surface.Surface, pygame.rect.Rect]]:  # FIXME
        """
        World Render method.
        > Called once at the end of each frame by game, **AFTER** loop.

        > When called, all render functions of every object should be called.

        > Sounds should be played and music should be updated.

        To render:
        - sounds
        - Room
        - entities
        - items
        - UI
        - etc.
        """
        # for indx, entity in enumerate(self._entities):
        #     self._entities[indx].render()

        # while self._sounds:
        #     self._sound_manager.play_audio(self._sounds.pop())
        # self.set_world_music()

        # self._ui.render()
        # self._curr_room.render()

        temp = []
        temp.append(self._player.render(self._time))
        for indx, _entity in enumerate(self._entities):
            temp.append(self._entities[indx].render(self._time))

        if len(self._items):
            for indx, _item in enumerate(self._items):
                temp.append(self._items[indx].render())

        for proj in self._item_slot.render_projectiles():
            temp.append(proj)

        # final one on display stack
        for elem in self._ui.render():
            temp.append(elem)

        return temp

# --- sound methods ---

    def set_world_music(self) -> None:  # FIXME
        """
        Sets the world music according to the room type.
        > This method should change the music once the room type changes

        > Example: Enemy -> Puzzle
        """
        pass

    def queue_sound(self, sound: int) -> None:
        """
        Add a sound to the queue.
        > Should be called by objects when they play a sound.
        > Rather than storing sound objects, sound ID's are to be passed.

        Args:
            sound (int): Sound ID to append
        """
        self._sounds.append(sound)

# --- dungeon methods ---

    def update_room(self) -> None:  # FIXME
        """
        Updates the room according to changes.

        > Called each frame, updates the room according to puzzle completion,

        > door unlocks, etc.
        """
        pass

# --- UI methods ---

    def update_ui(self) -> None:  # FIXME
        """
        Updates the UI according to changes.

        > Called each frame, updates the UI according to item selections, player HP,

        > key and bomb count, etc.
        """
        self._ui.update_hearts(self._player.HP)

# --- entity methods ---

    def player_action(self, action: str) -> None:
        """
        Get player actions and change the world accordingly.
        > When the player makes an action (such as swinging a sword or using an item),

        > this function is called by the player.

        requests:
        * action_a // use currently equipped item
        * action_b

        Args:
            action (str): Action ID passed by player.
        """
        if action == "action_a":
            self._item_slot.item_action_a(
                self._player.position, self._player.look_dir)

    def quit_controller(self) -> None:
        """FIXME"""
        self._player.quit_controller()

    def entity_action(self, entity: Entity, action: str) -> Any:
        """
        Get entity actons and change the world accordingly.
        > Whenever an entity makes an action (such as attacking)

        > this function is to be called by that entity.

        requests:
        * s_col: Static collision
        * get_player: get player position

        Args:
            entity (Entity): Entity calling the function.

            action (str): Action ID passed by the entity.
        """
        # this collision return is temporary.
        # s_col returns all static objects (walls, pits, etc)
        if action == "s_col":
            collides: list[pygame.Rect] = list[pygame.Rect]()
            # Check collisions with all walls in a room.
            """
            FIXME
            """
            return collides
        elif action == "player_pos":
            return self._player.position
        elif action == "player_col":
            if pygame.sprite.collide_rect(entity, self._player):
                return self._player.rect
        elif action == "player_dmg_1":
            self._player.damage(1)

        return 0

# ---- item methods ----

    def item_action(self, item: Item, action: str,
                    projectile: Projectile | None = None) -> Any:
        """FIXME"""
        if action == "grabbed":
            if pygame.sprite.collide_rect(item, self._player):
                self._inventory.append(item)
                self._items.remove(item)
                return True
        if action == "attack":
            for entity in self._entities:
                if projectile and pygame.sprite.collide_rect(projectile, entity):
                    entity.damage(projectile.damage_points)
                    return True
        return 0

# --- properties ---

    @property
    def music(self) -> str:
        """Music currently playing. Handled by sound manager."""
        # return self._sound_manager.Getmusic
        return ""  # FIXME

    @property
    def data(self) -> dict[str, Any]:
        """World dictionary data."""
        data: dict[str, Any] = dict[str, Any]()

        # Store player data
        data['player'] = {
            'position': self._player.position,
            'hp': self._player.HP,
            'speed': self._player.speed
        }

        # store all present entity data
        entity_data: list[dict[str, Any]] = list[dict[str, Any]]()
        for entity in self._entities:
            entity_data.append(
                {
                    'name': entity.__str__(),
                    'position': entity.position,
                    'hp': entity.HP,
                    'speed': entity.speed
                }
            )
        data['entities'] = entity_data

        # pass item data

        data['items'] = {}

        grounded_items: list[dict[str, Any]] = list[dict[str, Any]]()
        for item in self._items:
            grounded_items.append(
                {
                    'name': item.__str__(),
                    'position': item.position
                }
            )
        data['items']['grounded'] = grounded_items

        inventory_items: list[dict[str, Any]] = list[dict[str, Any]]()
        for item in self._inventory:
            inventory_items.append(
                {
                    'name': item.__str__()
                }
            )
        data['items']['inventory'] = inventory_items

        data['items']['slot'] = {
            'name': self._item_slot.__str__()
        }

        return data
