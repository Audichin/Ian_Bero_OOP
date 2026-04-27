import random
from collections import deque
from typing import Any, Self

import pygame

try:
    from .generation import Generation
except ImportError:
    from generation import Generation

try:
    from .entities.entity_mod import Entity
    from .entities.jelly import Jelly
    from .entities.urchin import Urchin
    from .entities.coral import Coral
except ImportError:
    from entities.entity_mod import Entity
    from entities.jelly import Jelly
    from entities.urchin import Urchin
    from entities.coral import Coral


class Room:
    """
    Room class for handling cords, used by Dungeon class
    """
    __slots__ = ["_world",
                 "_x",
                 "_y",
                 "_rng",
                 "_room_type",
                 "_connections",
                 "_enemies"]

    def __init__(self, world: Any,
                 x: int, y: int,
                 rng: random.Random,
                 room_type: str = "empty") -> None:
        self._world: Any = world
        self._x: int = x
        self._y: int = y
        self._rng: random.Random = rng
        self._room_type: str = room_type
        self._connections: list[Self] = []
        self._enemies: list[Entity] = []

    def init_enemies(self) -> None:
        """
        Initialize enemies in this room.

        This is a list representation of all the enemies
        belonging to this room.
        """
        enemy_types: list[str] = [
            "Jelly", "Jelly", "Urchin", "Coral", "Coral"]
        room_bounds: dict[str, tuple[int, int]] = {
            'X': (284, 1160),
            'Y': (205, 685)
        }

        enemy_count = self._rng.randint(1, 5)

        for i in range(enemy_count):
            # get randomized values
            enemy = self._rng.choice(enemy_types)
            position: pygame.Vector2 = pygame.Vector2(
                self._rng.randint(room_bounds['X'][0], room_bounds['X'][1]),
                self._rng.randint(room_bounds['Y'][0], room_bounds['Y'][1])
            )
            # store enemy
            if enemy == "Jelly":
                self._enemies.append(Jelly(self._world, position))
            elif enemy == "Urchin":
                position.x = pygame.math.clamp(position.x, 325, 1119)
                position.y = pygame.math.clamp(position.y, 246, 644)
                self._enemies.append(Urchin(self._world, room_bounds, position))
            else:
                self._enemies.append(Coral(self._world, position))

# ==== properties ====

    @property
    def x(self) -> int:
        """room x position"""
        return self._x

    @property
    def y(self) -> int:
        """room y position"""
        return self._y

    @property
    def room_type(self) -> str:
        """room type"""
        return self._room_type

    @room_type.setter
    def room_type(self, other: str) -> None:
        self._room_type = other

    @property
    def connections(self) -> list[Self]:
        """room connections"""
        return self._connections

    @property
    def enemies(self) -> list[Entity]:
        """enemies in this room"""
        return self._enemies

# ==== Room methods ====

    def connect(self, other_room: Self) -> None:
        """Creates a bidirectional connection."""
        if other_room not in self.connections:
            self.connections.append(other_room)
        if self not in other_room.connections:
            other_room.connections.append(self)

# ==== overloads ====

    def __repr__(self) -> str:
        return f"Room({self.x}, {self.y}, {self.room_type})"


class Dungeon:
    """
    Dungeon class to create a dungeon, requires Room class
    """

    _SCALE: int = 5
    _RESOLUTION: tuple[int, int] = (1440, 810)

    __slots__ = ["_world",  # Any
                 "_seed",  # Any
                 "_total_rooms",  # int
                 "_min_puzzle_rooms",  # int
                 "_native_size",  # tuple[int, int]
                 "_rooms",  # dict[tuple[int, int], Room]
                 "_rng",  # random.Random
                 "_generation"]  # Generation

    def __init__(self, world: Any,
                 seed: Any,
                 total_rooms: int = 12,
                 min_puzzle_rooms: int = 4) -> None:
        self._world: Any = world
        self._seed: Any = seed
        self._total_rooms: int = total_rooms
        self._min_puzzle_rooms: int = min_puzzle_rooms
        self._native_size: tuple[int, int] = (256, 160)
        self._rooms: dict[tuple[int, int], Room] = {}  # {(x, y): Room}
        self._rng: random.Random = random.Random(seed)  # Independent RNG

        # generate structure?
        self.generate()
        self._generation: Generation = Generation(self)
        self._generation.Apply_textures()

# ==== properties ====

    @property
    def rooms(self) -> dict[tuple[int, int], Room]:
        """The rooms held within dungeon."""
        return self._rooms

    def generate(self) -> None:  # Call this function to generate dungeon
        """
        Creates a dungeon
        """
        self._generate_layout()
        self._assign_room_types()

    def _generate_layout(self) -> None:
        """
        Generates the layout for dungeon
        """
        start = Room(self._world, 0, 0, self._rng, "start")
        self.rooms[(0, 0)] = start
        active_rooms = [start]

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while len(self.rooms) < self._total_rooms:
            current = self._rng.choice(active_rooms)
            dx, dy = self._rng.choice(directions)

            new_x = current.x + dx
            new_y = current.y + dy

            if (new_x, new_y) not in self.rooms:
                new_room = Room(self._world, new_x, new_y, self._rng)
                self.rooms[(new_x, new_y)] = new_room
                current.connect(new_room)
                active_rooms.append(new_room)

    def _find_farthest_room(self, start: Room) -> Room:

        """
        Finding the farthest room for setting the dungeon room to the farthest room away.

        Args:
            start (Room): The starting room (usually the one at (0, 0)).
        Returns:
            Room: The farthest room from the starting room.
        """
        visited: set[Room] = set()  # no duplicate items
        queue: deque[tuple[Room, int]] = deque([(start, 0)])
        farthest: tuple[Room, int] = (start, 0)

        while queue:
            room, dist = queue.popleft()
            visited.add(room)

            if dist > farthest[1]:
                farthest = (room, dist)

            for neighbor in room.connections:
                if neighbor not in visited:
                    queue.append((neighbor, dist + 1))

        return farthest[0]

    def _assign_room_types(self) -> None:
        """
        Assigns room types to the active rooms list, required to be called after _generate_layout()
        """
        all_rooms = list(self.rooms.values())

        start_room = self.rooms[(0, 0)]

        # Find farthest room for boss
        boss_room = self._find_farthest_room(start_room)
        boss_room.room_type = "boss"

        remaining = [
            r for r in all_rooms
            if r != start_room and r != boss_room
        ]

        # Assign puzzle rooms
        puzzle_rooms = self._rng.sample(
            remaining,
            min(self._min_puzzle_rooms, len(remaining))
        )

        for room in puzzle_rooms:
            room.room_type = "puzzle"

        # Assign enemy rooms to remaining empty rooms
        for room in remaining:
            if room.room_type == "empty":
                room.room_type = "enemy"
                room.init_enemies()

    def wall_hitbox(self, room: Room, orientation: str) -> list[pygame.Rect]:
        """
        Checks if the wall selected (depending on orientation)
        has a door and is open, returning two types of hitboxes for
        that wall for 3 different scenarios:
        1) Door = true, state = closed -> fully blocked wall
        2) Door = false -> fully blocked wall
        3) Door = true, state = open -> two walls on either side with a
                                        collider in the middle
                                        to allow player into next room

        args:
            room (Room): the room we are checking
            orientation (str): the wall orientation we are checking (W, N, E, S)
        returns:
            list[pygame.Rect]
        """
        wall_data = self._generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            # Refresh once in case generation data is stale.
            self._generation.Apply_textures()
            wall_data = self._generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            raise ValueError(
                f"No wall data for room ({room.x}, {room.y}) orientation {orientation}")

        hasdoor = wall_data["hasdoor"]
        isopen = wall_data["isopen"]

        if orientation == "N":
            return self.get_wall_N_rects(hasdoor, isopen)
        elif orientation == "S":
            return self.get_wall_S_rects(hasdoor, isopen)
        elif orientation == "E":
            return self.get_wall_E_rects(hasdoor, isopen)
        elif orientation == "W":
            return self.get_wall_W_rects(hasdoor, isopen)

        raise ValueError(f"Invalid orientation for wall hitbox: {orientation}")

    def set_all_doors_in_room(self, room: Room, state: bool) -> None:
        """
        Sets all the doors in a room to the state.

        Args:
            room (Room): Room to set the walls of
            state (bool): The state to switch the wall to.
                A true = open, a false = closed.
        """
        orientations: list[str] = ['N', 'E', 'S', 'W']

        for cardinal in orientations:
            self.set_wall_door(room, cardinal, state)

    def switch_all_doors_in_room(self, room: Room) -> None:
        """
        Switches the state of all the walls in a room.

        Args:
            room (Room): room to switch walls.
        """
        orientations: list[str] = ['N', 'E', 'S', 'W']

        for cardinal in orientations:
            self.switch_wall_door_state(room, cardinal)

    def set_wall_door(self, room: Room, orientation: str, state: bool) -> None:
        """
        Set the wall corresponding to the room and orientation.

        Args:
            room (Room): Room the wall belongs to.
            orientation (str): The wall to set the state to.
            state (bool): The state to switch the wall to.
                A true = open, a false = closed.
        """
        wall_data = self._generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            raise ValueError()
        # get wall attributes.
        hasdoor = wall_data['hasdoor']
        isopen = wall_data['isopen']

        # early return
        if not hasdoor:
            return

        # open door if the door is closed.
        if state and not isopen:
            self.switch_wall_door_state(room, orientation)
        elif not state and isopen:
            self.switch_wall_door_state(room, orientation)

    def switch_wall_door_state(self, room: Room, orientation: str) -> None:
        """
        Switches the state of the corresponding room wall.

        Args:
            room (Room): room the wall belongs to
            orientation (str): wall.
        """
        wall_data = self._generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            raise ValueError()

        # wall attribute get
        hasdoor = wall_data['hasdoor']
        isopen = wall_data['isopen']
        walltype = wall_data['wall_type']

        if not hasdoor:
            return  # No changes

        wall_data['isopen'] = not isopen  # flip state

        # set image path
        image_path = f"{self._generation.PROJECT_DIR_NAME}/assets/visual/textures/walls"
        if walltype.__str__() == "Boss":
            image_path += "/boss/"
        else:
            image_path += "/door/"

        # set the rest of the path corresponding to the wall.
        image_path += orientation + "_"
        if wall_data['isopen']:
            image_path += "o"
        else:
            image_path += "x"
        if orientation == "S" and walltype.__str__() == 'Boss':
            image_path += "_" + walltype.__str__()
        elif orientation != "S":
            image_path += "_" + walltype.__str__()
        image_path += ".png"

        # set asset
        wall_data['sel_img'] = self._generation.whole_filepath(image_path)

    def get_wall_N_rects(self, hasdoor: object, isopen: object) -> list[pygame.Rect]:
        """return North wall rects"""
        if hasdoor and isopen:
            return [
                pygame.Rect(80, 5, 585, 160),   # left segment
                pygame.Rect(665, 5, 115, 60),   # door band
                pygame.Rect(780, 5, 590, 160),  # right segment
            ]
        return [pygame.Rect(80, 5, 1290, 160)]

    def get_wall_S_rects(self, hasdoor: object, isopen: object) -> list[pygame.Rect]:
        """return South wall rects"""
        if hasdoor and isopen:
            return [
                pygame.Rect(80, 725, 555, 80),   # left segment
                pygame.Rect(633, 800, 173, 80),   # narrow door band
                pygame.Rect(804, 725, 570, 80),  # right segment
            ]
        return [pygame.Rect(80, 725, 1290, 80)]

    def get_wall_E_rects(self, hasdoor: object, isopen: object) -> list[pygame.Rect]:
        """return East wall rects"""
        if hasdoor and isopen:
            return [
                pygame.Rect(1200, 5, 170, 370),    # top segment
                pygame.Rect(1300, 375, 170, 110),   # door band
                pygame.Rect(1200, 485, 170, 320),  # bottom segment
            ]
        return [pygame.Rect(1200, 5, 170, 800)]

    def get_wall_W_rects(self, hasdoor: object, isopen: object) -> list[pygame.Rect]:
        """return West wall rects"""
        if hasdoor and isopen:
            return [
                pygame.Rect(80, 5, 164, 375),    # top segment
                pygame.Rect(80, 380, 65, 110),   # door band
                pygame.Rect(80, 490, 164, 315),  # bottom segment
            ]
        return [pygame.Rect(80, 5, 164, 800)]
