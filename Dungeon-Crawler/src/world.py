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

from sound import SoundManager
from entities.entity_mod import Entity
from entities.player import Player
from items.item import Item
from structures import Dungeon, Room
from items.projectile import Projectile
from items.bubble import BubbleWeapon
from ui import UI


class World:
    """
    World class.
    > Manages all in-world objects and their interactions with eachother.

    This Module is specific to the Dungeon Crawler project, and is not meant
    to be utilized as an API or game engine.
    """

    SCREEN_CENTER: tuple[int, int] = (720, 405)

    __slots__ = ["_sound_manager"  # : SoundManager
                 , "_time"  # : float
                 , "_sounds"  # : list[int] // int representation of sound
                 , "_prev_music"  # : list[int] // int representation of music
                 , "_Music_IDs"  # : dict[str, int] // string representation of music
                 , "_prev_room_type"
                 , "_player"  # : Player
                 , "_items"  # Item // items in the room
                 , "_item_slot"  # : Item // item to be used with player action
                 , "_inventory"  # : list[Item]
                 , "_ui"  # : UI
                 , "_dungeon"  # : Dungeon
                 , "_dungeon_seed"  # : Any
                 , "_curr_room"  # : Room
                 , "_prev_room"  # : Room
                 , "_room_transition"  # : float // transition timer
                 , "_transition_state"]  # : int // 1 = up, -1 = down, 0 = none

# --- initializers ---

    def __init__(self, seed: Any) -> None:
        """
        World Object.

        Args:
            seed (Any): Dungeon seed.
        """
        # initialize time
        self._time: float = float()

        # initialize entities
        self._entity_init()

        # initialize items
        self._item_init()

        # initialize UI
        self._ui_init()

        # initialize dungeon
        self._dungeon_init(seed)
        self._room_transition: float = 0
        self._transition_state: int = 0

        # inialize sounds
        self._sounds: list[int] = list[int]()
        self._sound_manager: SoundManager = SoundManager()
        self._prev_music: list[int] = [9]

        self._Music_IDs = {
            "start": 9,
            "boss": 10,
            "enemy": 11,
            "puzzle": 12
        }

    def _dungeon_init(self, seed: Any) -> None:
        """
        Dungeon structure initializer.
        > Initialize dungeon and hold it in memory.

        Args:
            seed (Any): Dungeon seed
        """
        self._dungeon_seed: Any = seed
        self._dungeon: Dungeon = Dungeon(self, self._dungeon_seed)
        self._curr_room: Room = self._dungeon.rooms[(0, 0)]
        self._prev_room: Room = self._dungeon.rooms[(0, 0)]
        self._prev_room_type: str = "none"

    def _entity_init(self) -> None:
        """
        Entity initializer.
        > The entity list is initialized here, along with the player.

        > The player when initialized should be placed appropriately according to

        > the starting room. All regular values should be set.
        """
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
            # Item(self, position=pygame.Vector2(800, 0)),
            # Item(self, position=pygame.Vector2(304, 564))
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

        # Stop game if player health is zero
        if self._player.HP <= 0:
            self._player.position = pygame.Vector2(-999, -999)
            return

        self._time += delta
        self._player.loop(delta)

        for indx, entity in enumerate(self._curr_room.enemies):
            entity.loop(delta)
            if entity.HP <= 0:
                self._curr_room.enemies.pop(indx)

        if len(self._items):
            for indx, _item in enumerate(self._items):
                self._items[indx].loop(delta)

        self._item_slot.loop(delta)

        self.update_room(delta)
        self.update_ui()

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
        temp: list[tuple[pygame.Surface, pygame.Rect]] = []

        for to_render in self.render_room():
            temp.append(to_render)

        temp.append(self._player.render(self._time)[0])
        for entity in self._curr_room.enemies:
            for entity_item in entity.render(self._time):
                temp.append(entity_item)

        if len(self._items):
            for indx, _item in enumerate(self._items):
                temp.append(self._items[indx].render())

        for proj in self._item_slot.render_projectiles():
            temp.append(proj)

        # black box for transition
        if self._transition_state:
            # create a black box
            black_box: pygame.Surface = pygame.Surface((1440, 810))
            black_box.fill((0, 0, 0))
            black_box.set_alpha(int(self._room_transition * 255))
            temp.append((black_box, black_box.get_rect()))

        # final one on display stack
        for elem in self._ui.render():
            temp.append(elem)

        self.play_world_music()
        self.play_sound_effects()
        return temp

# --- sound methods ---

    def play_sound_effects(self) -> None:
        """
        Plays all sound effects in the queue.
        > Should be called in the render method, after all objects
        have had a chance to queue sounds.

        > After playing, the sound queue should be cleared.
        """
        while self._sounds:
            self._sound_manager.play_audio(self._sounds.pop())

    def play_world_music(self) -> None:  # FIXME
        """
        Sets the world music according to the room type.
        > This method should change the music once the room type changes

        > Example: Enemy -> Puzzle
        """
        # print(f"Music curr_room: {self._curr_room.room_type}, \
        #       Music prev_room: {self._prev_room_type}")
        if self._curr_room.room_type != self._prev_room_type:
            prev_song = self._prev_music.pop()
            print(f"Music prev_song: {prev_song}")
            # print(f"Music curr_song: {self._Music_IDs[self._curr_room.room_type]}")
            self._sound_manager.stop_audio(prev_song)  # stop previous music
            # play new music
            self._sound_manager.play_audio(self._Music_IDs[self._curr_room.room_type])
            # update prev_music
            self._prev_music.append(self._Music_IDs[self._curr_room.room_type])
            self._prev_room_type = self._curr_room.room_type
        else:
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

    def update_room(self, delta: float) -> None:  # FIXME
        """
        Updates the room according to changes.

        > Called each frame, updates the room according to puzzle completion,

        > door unlocks, etc.
        """

        # handle transition
        if self._transition_state:
            self._room_transition += (delta * self._transition_state) * 10

        if self._room_transition > 1 and self._transition_state == 1:
            self._transition_state = -1
        elif self._room_transition <= 0 and self._transition_state == -1:
            self._transition_state = 0
            self._room_transition = 0

    def render_room(self) -> list[tuple[pygame.Surface, pygame.Rect]]:
        """
        Render the room
        """
        temp: list[tuple[pygame.Surface, pygame.Rect]] = []

        floor_img: pygame.Surface = pygame.image.load(
            self._dungeon._generation.FLOOR_TEXTURE_ROOT.__str__()).convert_alpha()
        floor_img = pygame.transform.scale(
            floor_img, (256 * Dungeon._SCALE, 160 * Dungeon._SCALE))
        temp.append((floor_img, pygame.Rect(80, 5, 256, 160)))

        x, y = self._curr_room.x, self._curr_room.y
        directions = ["W", "N", "E", "S"]
        for d in directions:
            img_directory = self._dungeon._generation.room_walls.get((x, y, d))
            if img_directory:
                wall_img: pygame.Surface = pygame.image.load(
                    img_directory['sel_img'].__str__()).convert_alpha()
                wall_img = pygame.transform.scale(
                    wall_img, (256 * Dungeon._SCALE, 160 * Dungeon._SCALE))
                temp.append((wall_img, pygame.Rect(80, 5, 256, 160)))

        return temp

    def get_room_hitboxes(self) -> dict[str, list[pygame.Rect]]:
        """
        Get all hitboxes in the current room.

        hitboxes are ordered as:

        'N': list[pygame.Rect],
        'E': list[pygame.Rect],
        'S': list[pygame.Rect],
        'W': list[pygame.Rect]
        """
        all_hitboxes: dict[str, list[pygame.Rect]] = {}
        orientations: list[str] = ['N', 'E', 'S', 'W']
        for cardinal in orientations:
            all_hitboxes[cardinal] = self._dungeon.wall_hitbox(self._curr_room, cardinal)
        return all_hitboxes

    def switch_room(self, cardinal: str) -> None:
        """
        Go to the next room with respects to the cardinal of the door
        the player interacted with.
        """
        # set transition state to 1
        if not self._transition_state:
            self._transition_state = 1

        if self._room_transition < 1:
            return

        position_tp: dict[str, tuple[float, float]] = {
            'N': (720, 725),  # position to tp player if they go through N door
            'E': (240, 445),  # position to tp player if they go through E door
            'S': (720, 150),  # position to tp player if they go through S door
            'W': (1200, 445)  # position to tp player if they go through W door
        }

        next_room: tuple[int, int] = (0, 0)
        if cardinal == 'S':  # going through south door
            next_room = (self._curr_room.x, self._curr_room.y - 1)
        elif cardinal == 'N':  # going through north door
            next_room = (self._curr_room.x, self._curr_room.y + 1)
        elif cardinal == 'E':  # going through east door
            next_room = (self._curr_room.x + 1, self._curr_room.y)
        elif cardinal == 'W':  # going through west door
            next_room = (self._curr_room.x - 1, self._curr_room.y)

        try:
            self._curr_room = self._dungeon.rooms[next_room]
        except KeyError:
            raise KeyError("room doesnt exist")

        # teleport player to appropriate position
        self._player.position = pygame.Vector2(
            position_tp[cardinal][0],
            position_tp[cardinal][1])

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
        self._player.quit_controller()

    def entity_action(self, entity: Entity, action: str,
                      projectile: Projectile | None = None) -> Any:
        """
        Get entity actons and change the world accordingly.
        > Whenever an entity makes an action (such as attacking)

        > this function is to be called by that entity.

        requests:
        * s_col: Static collision
        * player_pos: get player position
        * player_col: check this for collision with player
        * player_dmg_1: damage the player by one point
        * player_dmg_2: damage the player by two points

        Args:
            entity (Entity): Entity calling the function.

            action (str): Action ID passed by the entity.
        """
        # this collision return is temporary.
        # s_col returns all static objects (walls, pits, etc)
        if action == "s_col":
            if projectile:
                return self._static_collision(projectile)
            return self._static_collision(entity)
        elif action == "player_pos":
            return self._player.position
        elif action == "player_col":
            if projectile:
                if pygame.sprite.collide_rect(projectile, self._player):
                    return self._player.rect
            if pygame.sprite.collide_rect(entity, self._player):
                return self._player.rect
        elif action == "player_dmg_1":
            self._player.damage(1)
        elif action == "player_dmg_2":
            self._player.damage(2)

        return 0

    def _static_collision(self, obj: Entity | Projectile) -> list[pygame.Rect]:
        """Check entity collides with nearest wall"""
        collides: list[pygame.Rect] = list[pygame.Rect]()
        checks: list[str] = []

        # Check position relative to Y direction
        if obj.position.y < self.SCREEN_CENTER[1]:
            checks.append('N')
        elif obj.position.y > self.SCREEN_CENTER[1]:
            checks.append('S')
        # Check position relative to X direction
        if obj.position.x > self.SCREEN_CENTER[0]:
            checks.append('E')
        elif obj.position.x < self.SCREEN_CENTER[0]:
            checks.append('W')

        dungeon_walls: dict[str, list[pygame.Rect]] = self.get_room_hitboxes()
        for cardinal in checks:
            for segment, rec in enumerate(dungeon_walls[cardinal]):
                if obj.rect.colliderect(rec):
                    if segment == 1 and obj is self._player:
                        self.switch_room(cardinal)
                        return []
                    collides.append(rec)

        return collides

# ---- item methods ----

    def item_action(self, item: Item, action: str,
                    projectile: Projectile | None = None) -> Any:
        """
        Get item action and projectiles.

        Args:
            item (Item): Item requesting action.
            action (str): Action code.
            projectile (Projectile | None, optional): Projectile passed. Defaults to None.

        Returns:
            Any: _description_
        """
        if action == "grabbed":
            if pygame.sprite.collide_rect(item, self._player):
                self._inventory.append(item)
                self._items.remove(item)
                return True
        if action == "attack":
            for entity in self._curr_room.enemies:
                if projectile and pygame.sprite.collide_rect(projectile, entity):
                    entity.damage(projectile.damage_points)
                    return True
        if action == "s_col":
            if projectile:
                return self._static_collision(projectile)
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
        for entity in self._curr_room.enemies:
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

        data['room'] = {
            'current': self._curr_room,
            'music': self._Music_IDs[self._curr_room.room_type]
        }

        return data
