import pygame

import random
from collections import deque
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "Dungeon-Crawler" / "src"))
from generation import Generation # type: ignore
from entity import Entity # type: ignore

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
        self.room_native_size = (256, 256)
        self.floor_native_size = (256, 160)
        self.wall_thickness_EW = 32
        self.wall_thickness_NS = 32
        self.door_size = 32
        self.render_scale = Entity._SCALE
        self.rooms = {}  # {(x, y): Room}
        self.rng = random.Random(seed)  # Independent RNG
        self.generate()
        self.generation = Generation(self)
        self.generation.Apply_textures()

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

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 1000000)
    dungeon: Dungeon = Dungeon(seed=seed)
    generation = dungeon.generation
    floor_texture = (
        Path(__file__).resolve().parents[1]
        / "Dungeon-Crawler"
        / "assets"
        / "visual"
        / "textures"
        / "rooms"
        / "enemy"
        / "1.png"
    )
    room_floors: dict[tuple[int, int], Path] = {
        (room.x, room.y): floor_texture for room in dungeon.rooms.values()
    }

    print(f"Seed: {seed}")
    print(f"Rooms generated: {len(dungeon.rooms)}")
    print(f"Wall records generated: {len(generation.room_walls)}")
    print(f"Floor texture used for testing: {floor_texture}")

    for (x, y), room in sorted(dungeon.rooms.items()):
        print(
            f"Room ({x}, {y}): type={room.room_type}, "
            f"connections={[f'({r.x}, {r.y})' for r in room.connections]}, "
            f"floor={room_floors[(x, y)]}"
        )
    directions = {"W": (-1, 0),"N": (0, 1),"E": (1, 0),"S": (0, -1),}

    errors = []

    for (x, y), room in sorted(dungeon.rooms.items()):
        print(f"\nRoom ({x}, {y}) type={room.room_type}")
        for orientation in ["W", "N", "E", "S"]:
            key = (x, y, orientation)
            wall_data = generation.room_walls.get(key)
            if wall_data is None:
                errors.append(f"Missing wall data for {key}")
                continue

            dx, dy = directions[orientation]
            neighbor_exists = (x + dx, y + dy) in dungeon.rooms

            # Match generation.py behavior exactly:
            # boss south side is always forced to closed boss door texture.
            expected_hasdoor = neighbor_exists
            if room.room_type == "boss" and orientation == "S":
                expected_hasdoor = True

            if wall_data["hasdoor"] != expected_hasdoor:
                errors.append(
                    f"{key}: hasdoor={wall_data['hasdoor']} expected={expected_hasdoor}"
                )

            expected_open = expected_hasdoor and room.room_type != "boss"
            if wall_data["isopen"] != expected_open:
                errors.append(
                    f"{key}: isopen={wall_data['isopen']} expected={expected_open}"
                )

            wall_path = wall_data["sel_img"]
            if not isinstance(wall_path, Path):
                errors.append(f"{key}: sel_img is not a pathlib.Path ({type(wall_path)})")

            print(
                f"{orientation}: hasdoor={wall_data['hasdoor']}, "
                f"isopen={wall_data['isopen']}, path={wall_path}"
            )

    print("\nVerification Summary")
    if errors:
        print(f"FAIL ({len(errors)} issues)")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("PASS (all wall records match expected room-surroundings logic)")

def test_image_displayment():
# --- Variables ---
    pygame.init()
    window_size = (1920, 1080)
    D: Dungeon = Dungeon(seed=random.randint(0, 1000000))
    screen = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()
    debug_font = pygame.font.SysFont("consolas", 18)
    show_debug = True
    show_hitboxes = True
    directions = ["W", "N", "E", "S"]
    wall_hitboxes = []

    G: Generation = D.generation

    room_center = (window_size[0] // 2, window_size[1] // 2)
    floor_native_size = D.floor_native_size
    floor_image_raw: pygame.Surface = pygame.Surface(floor_native_size, pygame.SRCALPHA)
    floor_path = (Path(__file__).resolve().parents[1] / "Dungeon-Crawler" / "assets" / "visual" / "textures" / "rooms" / "enemy" / "floor.png")

# --- Loading floor ---
    try:
        floor_image_raw = pygame.image.load(floor_path).convert_alpha()
        print(f"Loaded floor image from {floor_path}")
    except Exception as e:
        print(f"Failed to load floor image from {floor_path}: {e}")
        floor_image_raw.fill((50, 50, 50))  # Fallback: fill with gray
    floor = floor_image_raw
    floor_rect = floor.get_rect(center=room_center)
    wall_surfaces: dict[str, pygame.Surface] = {}
    
# --- Select random room for testing (excluding boss rooms) ---
    random_room = random.choice([room for room in D.rooms.values() if room.room_type != "boss"])
    print(f"Testing {random_room.room_type} room at ({random_room.x}, {random_room.y})")

# --- Load walls ---
    for orientation in directions:
        key = (random_room.x, random_room.y, orientation)
        wall_data = G.room_walls.get(key)

        if wall_data is None:
            print(f"Missing wall data for {key}")
            continue

        wall_path = wall_data["sel_img"]
        if not isinstance(wall_path, Path):
            print(f"{key}: sel_img is not a pathlib.Path ({type(wall_path)})")
            continue

        try:
            test_image = pygame.image.load(wall_path).convert_alpha()
            wall_surfaces[orientation] = test_image
            print(f"Loaded image for {key} from {wall_path}")
        except Exception as e:
            print(f"Failed to load image for {key} from {wall_path}: {e}")
            continue

# --- Adding hitbox data for walls ---
    for orientation in directions:
        wall_hitboxes.append(D.wall_hitbox(random_room, orientation))

# --- main method ---
    wall_rects: dict[str, pygame.Rect] = {}
    room_rect = pygame.Rect(0, 0, D.room_native_size[0], D.room_native_size[1])
    room_rect.center = room_center
    if wall_surfaces:
        sample_wall = next(iter(wall_surfaces.values()))
        base_wall_w, base_wall_h = sample_wall.get_size()
        scale_factor = D.render_scale

        wall_target_size = ( int(base_wall_w * scale_factor), int(base_wall_h * scale_factor))
        wall_surfaces = {
            orientation: pygame.transform.smoothscale(wall_image, wall_target_size)
            for orientation, wall_image in wall_surfaces.items()
        }

        floor_target_size = (
            int(floor_native_size[0] * scale_factor),
            int(floor_native_size[1] * scale_factor),
        )
        floor = pygame.transform.smoothscale(floor_image_raw, floor_target_size)
        floor_rect = floor.get_rect(center=room_center)

        room_rect = next(iter(wall_surfaces.values())).get_rect(center=room_center)
        for orientation, wall_image in wall_surfaces.items():
            wall_rects[orientation] = wall_image.get_rect(center=room_rect.center)
# --- Main loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    show_debug = not show_debug
                if event.key == pygame.K_h:
                    show_hitboxes = not show_hitboxes

        screen.fill((0, 0, 0))  # Clear the screen with black
        mouse_pos = pygame.mouse.get_pos()
        any_hitbox_collision = False

        # Draw floor first so it shows through transparent wall pixels.
        screen.blit(floor, floor_rect.topleft)

        # Draw walls on top of floor
        for orientation, wall_image in wall_surfaces.items(): 
            screen.blit(wall_image, wall_rects[orientation].topleft)

        # Build/draw hitboxes directly in fixed screen-space anchor coordinates.
        for wall_hitbox in wall_hitboxes:
            for segment_index, hitbox in enumerate(wall_hitbox):
                x, y, width, height, rotation = hitbox
                hitbox_rect = pygame.Rect(x, y, width, height)
                hitbox_colliding = hitbox_rect.collidepoint(mouse_pos)
                if hitbox_colliding:
                    any_hitbox_collision = True

                if show_hitboxes:
                    if hitbox_colliding:
                        color = (0, 120, 255)  # Blue when mouse collision occurs
                    elif len(wall_hitbox) == 3 and segment_index == 1:
                        color = (0, 255, 0)  # door band
                    else:
                        color = (255, 0, 0)  # wall segment
                    pygame.draw.rect(screen, color, hitbox_rect, 2)

        if show_debug:
            debug_lines = [
                f"Room: ({random_room.x}, {random_room.y}) type={random_room.room_type}",
                f"Window: {window_size[0]}x{window_size[1]}",
                f"RoomRect: x={room_rect.left}, y={room_rect.top}, w={room_rect.width}, h={room_rect.height}",
                "Hitbox Space: fixed screen anchors",
                f"Entity._SCALE: {D.render_scale}",
                f"Collision: {'True' if any_hitbox_collision else 'False'}",
                f"Toggles: [D]ebug={'ON' if show_debug else 'OFF'} [H]itboxes={'ON' if show_hitboxes else 'OFF'}",
            ]
            for i, line in enumerate(debug_lines):
                txt = debug_font.render(line, True, (220, 220, 220))
                screen.blit(txt, (20, 20 + i * 22))

        # Update the display
        pygame.display.flip()  
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
    test_image_displayment()
