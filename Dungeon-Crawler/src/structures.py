import random
from collections import deque

import pygame
from pygame import locals

try:
    from .entities.entity_mod import Entity
except ImportError:
    from entities.entity_mod import Entity

try:
    from .generation import Generation
except ImportError:
    from generation import Generation

class Room:
    """
    Room class for handling cords, used by Dungeon class
    """
    def __init__(self, x, y, room_type="empty"):
        self.x = x
        self.y = y
        self.room_type = room_type
        self.connections = []

    def connect(self, other_room):
        """Creates a bidirectional connection."""
        if other_room not in self.connections:
            self.connections.append(other_room)
        if self not in other_room.connections:
            other_room.connections.append(self)

    def __repr__(self):
        return f"Room({self.x}, {self.y}, {self.room_type})"


class Dungeon:
    """
    Dungeon class to create a dungeon, requires Room class
    """
    def __init__(self, seed, total_rooms=12, min_puzzle_rooms=4):
        self.seed = seed
        self.total_rooms = total_rooms
        self.min_puzzle_rooms = min_puzzle_rooms
        self.native_size = (256, 160)
        self.render_scale = Entity._SCALE
        self.rooms = {}  # {(x, y): Room}
        self.rng = random.Random(seed)  # Independent RNG
        
        self.generate()
        self.generation = Generation(self)
        self.generation.Apply_textures()
        self.base_resolution: tuple[int, int] = (1440, 810)
        self.res: tuple[int, int] = self.base_resolution

    def generate(self):  # Call this function to generate dungeon
        """
        Creates a dungeon
        """
        self._generate_layout()
        self._assign_room_types()

    def _generate_layout(self):
        """
        Generates the layout for dungeon 
        """
        start = Room(0, 0, "start")
        self.rooms[(0, 0)] = start
        active_rooms = [start]

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while len(self.rooms) < self.total_rooms:
            current = self.rng.choice(active_rooms)
            dx, dy = self.rng.choice(directions)

            new_x = current.x + dx
            new_y = current.y + dy

            if (new_x, new_y) not in self.rooms:
                new_room = Room(new_x, new_y)
                self.rooms[(new_x, new_y)] = new_room
                current.connect(new_room)
                active_rooms.append(new_room)

    def _find_farthest_room(self, start):

        """
        Finding the farthest room for setting the dungeon room to the farthest room away.

        Args:
            start (Room): The starting room (usually the one at (0, 0)).
        Returns:
            Room: The farthest room from the starting room.
        """
        visited = set()
        queue = deque([(start, 0)])
        farthest = (start, 0)

        while queue:
            room, dist = queue.popleft()
            visited.add(room)

            if dist > farthest[1]:
                farthest = (room, dist)

            for neighbor in room.connections:
                if neighbor not in visited:
                    queue.append((neighbor, dist + 1))

        return farthest[0]

    def _assign_room_types(self):
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
        puzzle_rooms = self.rng.sample(
            remaining,
            min(self.min_puzzle_rooms, len(remaining))
        )

        for room in puzzle_rooms:
            room.room_type = "puzzle"

        # Assign enemy rooms to remaining empty rooms
        for room in remaining:
            if room.room_type == "empty":
                room.room_type = "enemy"
    
    def wall_hitbox(self, room: Room, orientation: str) -> list[pygame.Rect]:
        """
        Checks if the wall selected (depending on orientation) 
        has a door and is open, returning two types of hitboxes for that wall for 3 different scenarios:
        1) Door = true, state = closed -> fully blocked wall
        2) Door = false -> fully blocked wall
        3) Door = true, state = open -> two walls on either side with a collider in the middle 
                                        to allow player into next room

        args:
            room (Room): the room we are checking
            orientation (str): the wall orientation we are checking (W, N, E, S)
        returns:
            list[pygame.Rect]
        """
        wall_data = self.generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            # Refresh once in case generation data is stale.
            self.generation.Apply_textures()
            wall_data = self.generation.room_walls.get((room.x, room.y, orientation))
        if wall_data is None:
            raise ValueError(f"No wall data for room ({room.x}, {room.y}) orientation {orientation}")

        hasdoor = wall_data["hasdoor"]
        isopen = wall_data["isopen"]

        if orientation == "N":
            if hasdoor and isopen:
                return [
                    pygame.Rect(80, 5, 585, 160),   # left segment
                    pygame.Rect(665, 5, 115, 160),   # door band
                    pygame.Rect(780, 5, 590, 160),  # right segment
                ]
            return [pygame.Rect(80, 5, 1290, 160)]

        if orientation == "S":
            if hasdoor and isopen:
                return [
                    pygame.Rect(80, 725, 555, 80),   # left segment
                    pygame.Rect(633, 725, 173, 80),   # narrow door band
                    pygame.Rect(804, 725, 570, 80),  # right segment
                ]
            return [pygame.Rect(80, 725, 1290, 80)]

        if orientation == "E":
            if hasdoor and isopen:
                return [
                    pygame.Rect(1200, 5, 170, 370),    # top segment
                    pygame.Rect(1200, 375, 170, 110),   # door band
                    pygame.Rect(1200, 485, 170, 320),  # bottom segment
                ]
            return [pygame.Rect(1200, 5, 170, 800)]

        if orientation == "W":
            if hasdoor and isopen:
                return [
                    pygame.Rect(80, 5, 164, 375),    # top segment
                    pygame.Rect(80, 380, 165, 110),   # door band
                    pygame.Rect(80, 490, 164, 315),  # bottom segment
                ]
            return [pygame.Rect(80, 5, 164, 800)]

        raise ValueError(f"Invalid orientation for wall hitbox: {orientation}")
