import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
WALL_TEXTURE_ROOT = PROJECT_ROOT / "assets" / "visual" / "textures" / "walls"
PROJECT_DIR_NAME = PROJECT_ROOT.name
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import random

if TYPE_CHECKING:
    try:
        from .structures import Dungeon
    except ImportError:
        from structures import Dungeon


class Generation:
    """
    Generation class for creating textures based off dungeon layout, requires structures.py to be called.

    All wall data is appended into room_walls:

    X -> (int) x cord in map

    Y -> (int) y cord in map
    has_door -> (bool) if the wall needs a door

    is_open -> (bool) if door, is it open (default true except boss door, then false)
    
    sel_img -> (str) our path to get to the right texture (boss textures are still being made)
    """
    def __init__(self, dungeon: Optional["Dungeon"] = None):
        self.dungeon = dungeon
        seed_value = self.dungeon.seed if self.dungeon is not None else None
        self.rng = random.Random(seed_value)
        self.sel_img: str = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls"
        self.room_walls: dict[tuple[int, int, str], dict[str, object]] = {}
        # room_walls information:
        # x: X cordinate on map
        # y: y cordinate on map
        # ori: orientation (West, North, East, or South) to know which rectangle to apply the texture to, may not need this!
        # hasdoor: know if we have a wall or door
        # isopen, if hasdoor is true, then isopen will state if our texture should use the open or closed state
        # sel_img, our path to get to the right texture (no need to specify boss texture or not, should be fine either way)

    def Apply_textures(self):
        """
        Creates textures based off dungeon layout, structures.py must be called before this function is called.
        All wall data is appended into room_walls:
        X -> (int) x cord in map
        Y -> (int) y cord in map
        has_door -> (bool) if the wall needs a door
        is_open -> (bool) if door, is it open (default true except boss door, then false)
        """
        directions = [("W", (-1, 0)),("N", (0, 1)),("E", (1, 0)),("S", (0, -1)),] # First is checking Left (W), Second is checking Up (N), Thrird is checking Right (E), Fourth is Down (S)
        self.room_walls.clear()

        for cur_room in self.dungeon.rooms.values():
            if cur_room.room_type == "enemy" or cur_room.room_type == "puzzle" or cur_room.room_type == "start":
                for direction_check, (x, y) in directions:
                    if direction_check == "S":
                        if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                            if self.dungeon.rooms[(cur_room.x + x, cur_room.y + y)].room_type == "boss":
                                self.sel_img += "/boss/S_x_Boss.png"
                                self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)    
                                self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next wall
                                break # South wall of boss room will always be closed, so we can break out of the loop after storing the wall
                            self.sel_img += "/door/S_o.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, True, True, self.sel_img)
                            self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next wall
                            break # South wall of non-boss room will always be open, so we can break out of the loop after storing the wall
                        else:
                            self.sel_img += "/empty/S_1.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                        self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next wall
                        continue

                    if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                        if self.dungeon.rooms[(cur_room.x + x, cur_room.y + y)].room_type == "boss":
                            self.sel_img += "/boss/"
                            self.Sel_ori(direction_check)
                            self.sel_img += "x_Boss.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)
                            self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next room
                            continue
                        self.sel_img += "/door/"
                        self.Sel_ori(direction_check)
                        self.sel_img += "o_"
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, True, True, self.sel_img)
                        self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next room
                    else:
                        self.sel_img += "/empty/"
                        self.Sel_ori(direction_check)
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                    self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next wall
            if cur_room.room_type == "boss":
                for direction_check, (x, y) in directions:
                    if direction_check == "S":
                        if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                            # Boss south door exists but remains closed by default.
                            self.sel_img += "/boss/N_x_Boss.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)
                        else:
                            # No south door: use empty south wall variant.
                            self.sel_img += "/empty/S_1.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                        self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls"
                        continue

                    if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                        self.sel_img += "/door/"
                        self.Sel_ori(direction_check)
                        self.sel_img += "o_"
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)
                    else:
                        self.sel_img += "/boss/N_x_Boss.png" # By defualt, the boss room will remain closed till changed later
                        self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                    self.sel_img = f"{PROJECT_DIR_NAME}/assets/visual/textures/walls" # reset sel_img for next wall

    def Sel_ori(self, wall_ori: int):
            """Sets the orientation for the wall image.

            Args:
                wall_ori (str): The orientation of the wall ('W', 'N', 'E', 'S').
            """
            if wall_ori == 'W':
                self.sel_img += "/W_"
            if wall_ori == 'N':
                self.sel_img += "/N_"
            if wall_ori == 'E':
                self.sel_img += "/E_"
            if wall_ori == 'S':
                self.sel_img += "/S_"

    def Ran_wall(self):
        """
        Selects a random wall based on our random seed to allow for simular walls with like seed
        """
        wall_type = self.rng.randint(1, 4)
        if wall_type == 1:
            self.sel_img += "1.png"
        if wall_type == 2:
            self.sel_img += "2.png"
        if wall_type == 3:
            self.sel_img += "3.png"
        if wall_type == 4:
            self.sel_img += "4.png"
    
    def whole_filepath(self, rel_path: str) -> Path:
        """
        Creates full used file path to locate all texture data

        Args:
            rel_path (str): created bit based off Apply_textures()

        Returns:
            Path: Full path to the texture file.
        """
        rel_path_obj = Path(rel_path)
        if rel_path_obj.parts and rel_path_obj.parts[0] == PROJECT_ROOT.name:
            rel_path_obj = Path(*rel_path_obj.parts[1:])
        return PROJECT_ROOT / rel_path_obj

    def _store_wall(self, x: int, y: int, orientation: str, hasdoor: bool, isopen: bool, rel_path: str | Path):
        """
        Stores wall data in the room_walls dictionary.

        Args:
            x (int): The x-coordinate of the room.
            y (int): The y-coordinate of the room.
            orientation (str): The orientation of the wall ('W', 'N', 'E', 'S').
            hasdoor (bool): Whether the wall has a door.
            isopen (bool): Whether the door is open (if hasdoor is True).
            rel_path (str | Path): The relative path to the wall texture.
        """
        sel_img_path = rel_path if isinstance(rel_path, Path) else self.whole_filepath(rel_path)
        self.room_walls[(x, y, orientation)] = {
            "x": x,
            "y": y,
            "ori": orientation,
            "hasdoor": hasdoor,
            "isopen": isopen,
            "sel_img": sel_img_path,
            }
