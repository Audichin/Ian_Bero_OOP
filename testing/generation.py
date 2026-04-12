from structures import Dungeon  # type: ignore
from pathlib import Path
import random


class Generation:
    def __init__(self, dungeon: Dungeon | None = None):
        self.dungeon = dungeon
        seed_value = self.dungeon.seed if self.dungeon is not None else None
        self.rng = random.Random(seed_value)
        self.sel_img: str = "../assets/visual/textures/walls"
        self.room_walls: dict[tuple[int, int, str], dict[str, object]] = {}
        # room_walls information:
        # x: X cordinate on map
        # y: y cordinate on map
        # ori: orientation (West, North, East, or South) to know which rectangle to apply
        # the texture to, may not need this!
        # hasdoor: know if we have a wall or door
        # isopen, if hasdoor is true, then isopen will state if our texture should use
        # the open or closed state
        # sel_img, our path to get to the right texture (no need to specify boss texture
        # or not, should be fine either way)

    def Apply_textures(self):
        # First is checking Left (W), Second is checking Up (N),
        # Thrird is checking Right (E), Fourth is Down (S)
        directions = [("W", (-1, 0)), ("N", (0, 1)), ("E", (1, 0)), ("S", (0, -1)),]
        self.room_walls.clear()

        for cur_room in self.dungeon.rooms.values():
            if cur_room.room_type == "enemy" or cur_room.room_type == "puzzle" or cur_room.room_type == "start":
                for direction_check, (x, y) in directions:
                    if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                        self.sel_img += "/door/"
                        self.Sel_ori(direction_check)
                        if direction_check == "S":
                            self.sel_img += "o.png"
                            self._store_wall(cur_room.x, cur_room.y, direction_check, True, True, self.sel_img)
                            self.sel_img = "../assets/visual/textures/walls" # reset sel_img for next room
                            continue
                        self.sel_img += "o_"
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, True, True, self.sel_img)
                        self.sel_img = "../assets/visual/textures/walls" # reset sel_img for next room
                    else:
                        self.sel_img += "/empty/"
                        self.Sel_ori(direction_check)
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                    self.sel_img = "../assets/visual/textures/walls" # reset sel_img for next wall
            if cur_room.room_type == "boss":
                for direction_check, (x, y) in directions:
                    if direction_check == "S":
                        self.sel_img += "/boss/N_x_boss.png" # By default, boss south wall is closed
                        self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)
                        self.sel_img = "../assets/visual/textures/walls"
                        continue

                    if (cur_room.x + x, cur_room.y + y) in self.dungeon.rooms:
                        self.sel_img += "/door/"
                        self.Sel_ori(direction_check)
                        self.sel_img += "o_"
                        self.Ran_wall()
                        self._store_wall(cur_room.x, cur_room.y, direction_check, True, False, self.sel_img)
                    else:
                        self.sel_img += "/boss/N_x_boss.png" # By defualt, the boss room will remain closed till changed later
                        self._store_wall(cur_room.x, cur_room.y, direction_check, False, False, self.sel_img)
                    self.sel_img = "../assets/visual/textures/walls" # reset sel_img for next wall
                    


    def Sel_ori(self, wall_ori: int):
            print(f"Selecting orientation {wall_ori} for wall texture.")
            if wall_ori == 'W':
                print("Selected West orientation.")
                self.sel_img += "/W_"
            if wall_ori == 'N':
                print("Selected North orientation.")
                self.sel_img += "/N_"
            if wall_ori == 'E':
                print("Selected East orientation.")
                self.sel_img += "/E_"
            if wall_ori == 'S':
                print("Selected South orientation.")
                self.sel_img += "/S_"

    def Ran_wall(self):
        wall_type = self.rng.randint(1, 4)
        if wall_type == 1:
            self.sel_img += "1.png"
        if wall_type == 2:
            self.sel_img += "2.png"
        if wall_type == 3:
            self.sel_img += "3.png"
        if wall_type == 4:
            self.sel_img += "4.png"
    
    def whole_filepath(self, rel_path: str):
        file_path = Path(__file__).parent / rel_path
        print(f"Generated file path: {file_path} \n")
        return file_path

    def _store_wall(self, x: int, y: int, orientation: str, hasdoor: bool, isopen: bool, rel_path: str | Path):
        sel_img_path = rel_path if isinstance(rel_path, Path) else self.whole_filepath(rel_path)
        self.room_walls[(x, y, orientation)] = {
            "x": x,
            "y": y,
            "ori": orientation,
            "hasdoor": hasdoor,
            "isopen": isopen,
            "sel_img": sel_img_path,
            }
