import random
from collections import deque

import pygame
from pygame import locals


class Room:
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
    def __init__(self, seed, total_rooms=12, min_puzzle_rooms=4):
        self._seed = seed
        self.total_rooms = total_rooms
        self.min_puzzle_rooms = min_puzzle_rooms
        self.rooms = {}  # {(x, y): Room}
        self.rng = random.Random(self._seed)  # Independent RNG
        self.generate()

    @property
    def seed(self):
        return self._seed
    
    @seed.setter
    def seed(self, new_seed):
        self._seed = new_seed
        self.rng = random.Random(self._seed)

    def get_roomdata(self, x, y):
        return self.rooms.get((x, y), None)
    
    def get_roomtype(self, x, y):
        room = self.get_roomdata(x, y)
        return room.room_type if room else None

    def generate(self):  # Call this function to generate dungeon
        self._generate_layout()
        self._assign_room_types()

    def _generate_layout(self):
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

    def wall_hitbox(self, room: Room, orientation: str) -> list[list[int, int, int, int, int]]:
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
            List[list[
                    int(X-cord)
                    int (Y-cord)
                    int (Width)
                    int (Height)
                    int(rotation)]]
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

        # Fixed-anchor hitboxes for single-resolution testing.
        # Room bounds: left=80, top=5, right=1200, bottom=725.
        # Door opening center band: x=[592..688], y=[405..485].
        if orientation == "N":
            if hasdoor and isopen:
                return [
                    [80, 5, 512, 80, 0],   # left segment
                    [592, 5, 96, 80, 0],   # door band
                    [688, 5, 512, 80, 0],  # right segment
                ]
            return [[80, 5, 1120, 80, 0]]

        if orientation == "S":
            if hasdoor and isopen:
                return [
                    [80, 725, 512, 80, 0],   # left segment
                    [592, 725, 96, 80, 0],   # narrow door band
                    [688, 725, 512, 80, 0],  # right segment
                ]
            return [[80, 725, 1120, 80, 0]]

        if orientation == "E":
            if hasdoor and isopen:
                return [
                    [1200, 5, 80, 400, 0],    # top segment
                    [1200, 405, 80, 80, 0],   # door band
                    [1200, 485, 80, 320, 0],  # bottom segment
                ]
            return [[1200, 5, 80, 800, 0]]

        if orientation == "W":
            if hasdoor and isopen:
                return [
                    [80, 5, 80, 400, 0],    # top segment
                    [80, 405, 80, 80, 0],   # door band
                    [80, 485, 80, 320, 0],  # bottom segment
                ]
            return [[80, 5, 80, 800, 0]]

        raise ValueError(f"Invalid orientation for wall hitbox: {orientation}")
