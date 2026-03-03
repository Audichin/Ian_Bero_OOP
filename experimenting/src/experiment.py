"""
Wrapper module for my simple pygame experiment

This project is intended to help us learn more about pygame, how to work
in with its modules and make developer-friendly, modular, OOD friendly code.
"""
import sys
from typing_extensions import Self

import random
from collections import deque

import pygame
import pygame.locals as locals


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
        self.seed = seed
        self.total_rooms = total_rooms
        self.min_puzzle_rooms = min_puzzle_rooms
        self.rooms = {}  # {(x, y): Room}
        self.rng = random.Random(seed)  # Independent RNG
        self.generate()


    def generate(self):
        self._generate_layout()
        self._assign_room_types()

    def _generate_layout(self):
        start = Room(0, 0, "start")
        self.rooms[(0, 0)] = start
        active_rooms = [start]

        directions = [(0,1), (0,-1), (1,0), (-1,0)]

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
class Game:
    """singleton obj"""
    _instance = None

    __slots__ = ["_resolution", "_screen", "_running"]

    def __new__(cls) -> Self:
        """simple singleton implementation"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, resolution : tuple[int, int] | None = None) -> None:
        """init fix me"""

        self._resolution : tuple[int, int] = tuple[int, int]()
        if resolution is None:
            self._resolution = (1280, 720)
        else:
            self._resolution = resolution
        self._running : bool = False

    def game_init(self) -> None:
        """fixme"""
        pygame.init()
        self._screen : pygame.Surface = pygame.display.set_mode(self._resolution)
        self._running = True

    def event_handler(self) -> None:
        """fixme"""
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self._running = False
            # sys.exit()
    

    def gui_render(self) -> None:
        """fixme"""
        self._screen.fill("black")
        pygame.display.flip()

    def run_game(self) -> None:
        """fixme"""
        # run the game

        while self._running:
            self.event_handler()

            self.gui_render()

        pygame.quit()

    @staticmethod
    def main() -> None:
        """do something"""
        game : Game = Game()
        game.game_init()
        game.run_game()

    def dog(self) -> None:
        dog = 20
        print(dog)


if __name__ == "__main__":
    Game.main()
