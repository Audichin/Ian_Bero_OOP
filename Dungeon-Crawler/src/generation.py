import sys
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    try:
        from .structures import Dungeon
    except ImportError:
        from structures import Dungeon


class Generation:
    """
    Generation class for creating textures based off dungeon layout,
    requires structures.py to be called.

    All wall data is appended into room_walls:

    X -> (int) x cord in map

    Y -> (int) y cord in map

    has_door -> (bool) if the wall needs a door

    is_open -> (bool) if door, is it open (default true except boss door, then false)

    sel_img -> (str) our path to get to the right texture (boss textures are still being made)
    """
    def __init__(self, dungeon: Any = None):
        self.dungeon: Dungeon = dungeon
        seed_value = self.dungeon._seed if self.dungeon is not None else None
        self.rng = random.Random(seed_value)
        self.directions = [("N", (0, 1)), ("E", (1, 0)), ("W", (-1, 0)), ("S", (0, -1))]
        self.PROJECT_ROOT = Path(__file__).resolve().parents[1]
        self.SRC_ROOT = self.PROJECT_ROOT / "src"
        self.WALL_TEXTURE_ROOT = self.PROJECT_ROOT / \
            "assets" / "visual" / "textures" / "walls"
        self.FLOOR_TEXTURE_ROOT = self.PROJECT_ROOT / \
            "assets" / "visual" / "textures" / "rooms" / "enemy" / "1.png"
        self.PROJECT_DIR_NAME = self.PROJECT_ROOT.name
        if str(self.SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(self.SRC_ROOT))
        # First is checking Left (W), Second is checking Up (N),
        # Thrird is checking Right (E), Fourth is Down (S)
        self.sel_img: str = f"{self.PROJECT_DIR_NAME}/assets/visual/textures/walls"
        self.room_walls: dict[tuple[int, int, str], dict[str, object]] = {}
        # room_walls information:
        # x: X cordinate on map
        # y: y cordinate on map
        # ori: orientation (West, North, East, or South) to know which rectangle to apply
        # the texture to, may not need this!
        # hasdoor: know if we have a wall or door
        # isopen, if hasdoor is true, then isopen will state if our texture should use
        # the open or closed state
        # sel_img, our path to get to the right texture (no need to specify boss texture or not,
        # should be fine either way)

    def Apply_textures(self) -> None:
        """
        Creates textures based off dungeon layout, structures.py must be called before
        this function is called.
        All wall data is appended into room_walls:
        X -> (int) x cord in map
        Y -> (int) y cord in map
        has_door -> (bool) if the wall needs a door
        is_open -> (bool) if door, is it open (default true except boss door, then false)
        """

        self.room_walls.clear()

        for cur_room in self.dungeon.rooms.values():
            for direction_check, (x, y) in self.directions:
                if direction_check == "S":
                    if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                        if self.dungeon.rooms[(cur_room.x + x, cur_room.y + y)].room_type == "boss":
                            self.sel_img += "/boss/S_x_Boss.png"
                            self._store_wall(
                                cur_room.x, cur_room.y, direction_check,
                                True, False, "Boss", self.sel_img)
                            self._reset_sel_img()
                            # South wall of boss room will always be closed,
                            # so we can break out of the loop after storing the wall
                            break
                        elif cur_room.room_type == "boss":
                            self.sel_img += "/boss/"
                            self.Sel_ori(direction_check)
                            self.sel_img += "o_Boss.png"
                            self._store_wall(
                                cur_room.x, cur_room.y, direction_check,
                                True, False, "Boss", self.sel_img)
                            self._reset_sel_img()
                            continue
                        self.sel_img += "/door/S_o.png"
                        self._store_wall(
                            cur_room.x, cur_room.y, direction_check,
                            True, True, "", self.sel_img)
                        self._reset_sel_img()
                        # South wall of non-boss room will always be open,
                        # so we can break out of the loop after storing the wall
                        break
                    else:
                        self.sel_img += "/empty/S_1.png"
                        self._store_wall(
                            cur_room.x, cur_room.y, direction_check,
                            False, False, "1", self.sel_img)
                    self._reset_sel_img()
                    continue

                if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                    if self.dungeon.rooms[(cur_room.x + x, cur_room.y + y)].room_type == "boss":
                        self.sel_img += "/boss/"
                        self.Sel_ori(direction_check)
                        self.sel_img += "x_Boss.png"
                        self._store_wall(
                            cur_room.x, cur_room.y, direction_check,
                            True, False, "Boss", self.sel_img)
                        self._reset_sel_img()
                        continue
                    elif cur_room.room_type == "boss":
                        self.sel_img += "/boss/"
                        self.Sel_ori(direction_check)
                        self.sel_img += "o_Boss.png"
                        self._store_wall(
                            cur_room.x, cur_room.y, direction_check,
                            True, False, "Boss", self.sel_img)
                        self._reset_sel_img()
                        continue
                    self.sel_img += "/door/"
                    self.Sel_ori(direction_check)
                    self.sel_img += "o_"
                    wall_type = self.Ran_wall()
                    self._store_wall(
                        cur_room.x, cur_room.y, direction_check,
                        True, True, wall_type, self.sel_img)
                    self._reset_sel_img()
                else:
                    self.sel_img += "/empty/"
                    self.Sel_ori(direction_check)
                    wall_type = self.Ran_wall()
                    self._store_wall(
                        cur_room.x, cur_room.y, direction_check,
                        False, False, wall_type, self.sel_img)
                self._reset_sel_img()

    def Sel_ori(self, wall_ori: str) -> None:
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

    def Ran_wall(self) -> str:
        """
        Selects a random wall based on our random seed to allow for simular walls with like seed
        """
        wall_type = self.rng.randint(1, 4)
        if wall_type == 1:
            self.sel_img += "1.png"
            return "1"
        if wall_type == 2:
            self.sel_img += "2.png"
            return "2"
        if wall_type == 3:
            self.sel_img += "3.png"
            return "3"
        if wall_type == 4:
            self.sel_img += "4.png"
            return "4"
        return "0"

    def whole_filepath(self, rel_path: str) -> Path:
        """
        Creates full used file path to locate all texture data

        Args:
            rel_path (str): created bit based off Apply_textures()

        Returns:
            Path: Full path to the texture file.
        """
        rel_path_obj = Path(rel_path)
        if rel_path_obj.parts and rel_path_obj.parts[0] == self.PROJECT_ROOT.name:
            rel_path_obj = Path(*rel_path_obj.parts[1:])
        return self.PROJECT_ROOT / rel_path_obj

    def _reset_sel_img(self) -> None:
        """Reset sel_img for next wall"""
        self.sel_img = f"{self.PROJECT_DIR_NAME}/assets/visual/textures/walls"

    def _store_wall(self, x: int, y: int,
                    orientation: str,
                    hasdoor: bool,
                    isopen: bool,
                    walltype: str,
                    rel_path: str | Path) -> None:
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
            "wall_type": walltype,
            "sel_img": sel_img_path,
            }
