"""
Player Module.

Contains the player controller and player class. The player is a child of the entity class,
complete with all entity attributes. With the player controller, the user is able to move the
player instance and utilize its actions.

"""
from pathlib import Path
from typing import Any
from math import sin
from typing_extensions import Self


import pygame
from pygame import Vector2, Surface, Rect, key
from pygame.joystick import Joystick, JoystickType

from entities.entity_mod import Entity


class Player(Entity):
    """
    Player class. Inherits Entity.

    A player is an entity that is controlled by the game user.
    """

    __slots__: list[str] = ["_controller",   # PlayerController
                            "_action_a_cooldown",  # float // measured in seconds
                            "_action_b_cooldown",  # float // measured in seconds
                            "_curr_group",  # str
                            "_curr_step"]  # str

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(),
                 HP: int = 100) -> None:
        """
        Player Fish controlled by the user.

        Args:
            world (Any): World parent.
            position (Vector2, optional): position. Defaults to 0, 0.
            HP (int | None, optional): Hitpoints.
        """
        # set player controller
        self._controller: PlayerController = PlayerController()
        self._action_a_cooldown: float = 0.0
        self._action_b_cooldown: float = 0.0

        # get player sprite sheet
        self._assets: dict[str, Surface] = dict[str, Surface]()
        player_sprite_sheet = Path(__file__).parent / \
            "../../assets/visual/sprites/player/Fish-Sheet.png"
        sheet: Surface = pygame.image.load(player_sprite_sheet)
        self._all_frames_from_sheet(sheet, (16, 16), 3, "ESNW", "move")

        self._curr_group: str = 'E'
        self._curr_step: str = '0'

        super().__init__(world, position, HP=HP, assets=self._assets, anim_timer=50.0,
                         image=self._assets[f"{self._curr_group}move0"])

    def quit_controller(self) -> None:
        """FIXME"""
        self._controller.quit()

# ---- base methods ----

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        self._controller.handle_inputs()

        if self._controller.action_a and self._action_a_cooldown <= 0.0:
            self.player_action_a()

        if self._controller.action_b and self._action_b_cooldown <= 0.0:
            self.player_action_b()

        if self._action_a_cooldown > 0.0:
            self._action_a_cooldown -= delta

        if self._action_b_cooldown > 0.0:
            self._action_b_cooldown -= delta

        super().loop(delta, self.player_movement())

    def render(self, time: float) -> tuple[Surface, Rect]:
        if self._invincibility > 0:
            self.image.set_alpha(int(abs(sin(time * 10) * 255)))
        else:
            self.image.set_alpha(255)
        return super().render(time)

# ---- player methods ----

    def player_movement(self) -> Vector2:
        """
        Player movement module.

        Takes in user input through pygame key wrappers.

        Returns:
            Vector2: resulting movement vector.
        """
        # don't move during action:
        if self._action_a_cooldown > 0.0:
            return Vector2()
        # take in inputs
        dir: Vector2 = Vector2()
        if self._controller.right_movement:
            dir.x += 1
            self._orientation = True
            self._curr_group = "E"
        if self._controller.left_movement:
            dir.x -= 1
            self._orientation = False
            self._curr_group = "W"
        if self._controller.up_movement:
            dir.y -= 1
            self._curr_group = "N"
        if self._controller.down_movement:
            dir.y += 1
            self._curr_group = "S"

        return dir

    def player_action_a(self) -> None:
        """FIXME"""
        self._action_a_cooldown = .3
        self._world.player_action("action_a")

    def player_action_b(self) -> None:
        """FIXME"""
        self._action_b_cooldown = .3
        self._world.player_action("action_b")

# ---- player animation ----

    def animate(self, time: float) -> None:
        """
        Player movement animation.

        Using player positional vectors and previous positional vectors,
        The player knows what direction to face, and what animations to use.

        Args:
            time (float): Time elapsed.
        """
        diff_x: float = self._position.x - self._prev_position.x
        diff_y: float = self._position.y - self._prev_position.y

        if not self._curr_orient == self._orientation and self._curr_group == "E":
            self._curr_orient = not self._curr_orient
            self.image = pygame.transform.flip(self.image, True, False)

        self._anim_timer -= abs(diff_x) + abs(diff_y)

        if self._anim_timer < 0:
            self._anim_timer = self._anim_timer_top

            if self._curr_step == "0":
                self._curr_step = "1"
            else:
                self._curr_step = "0"

        if self._action_a_cooldown > 0.0:
            self._curr_step = "2"
        elif self._curr_step == "2":
            self._curr_step = "1"

        self.image = self._assets[f"{self._curr_group}move{self._curr_step}"]


class PlayerController:
    """
    FIXME
    """
    _instance = None

    LEFT_KEYS: list[int] = [pygame.K_a, pygame.K_LEFT]
    RIGHT_KEYS: list[int] = [pygame.K_d, pygame.K_RIGHT]
    UP_KEYS: list[int] = [pygame.K_w, pygame.K_UP]
    DOWN_KEYS: list[int] = [pygame.K_s, pygame.K_DOWN]

    ACTION_A_KEY: list[int] = [pygame.K_z, pygame.K_SPACE]
    ACTION_B_KEY: list[int] = [pygame.K_x, pygame.K_e]

    AXIS_T: float = 0.5  # Joystick Axis Tolerance

    __slots__ = ["_joystick",  # Joystick
                 "_up_movement",  # negative y direction
                 "_down_movement",  # positive y direction
                 "_left_movement",  # negative x direction
                 "_right_movement",  # positive x direction
                 "_action_a",  # first action
                 "_action_b"]  # second action

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Simple singleton implementation"""
        if not cls._instance:
            cls._instance = super().__new__(cls)  # *args assumed added.
        else:
            raise Exception("Cannot instantiate new singleton.")
        return cls._instance

    def __init__(self) -> None:
        """FIXME"""

        # check for a controller
        self.__controller_init()

        # init return values
        self._up_movement: bool = False
        self._down_movement: bool = False
        self._left_movement: bool = False
        self._right_movement: bool = False
        self._action_a: bool = False
        self._action_b: bool = False

    def __controller_init(self) -> None:
        """FIXME"""
        self._joystick: JoystickType | None = None
        if self.controller_status():
            self._joystick = Joystick(0)

    def quit(self) -> None:
        """FIXME"""
        if self._joystick:
            self._joystick.quit()

# ---- getters ----

    @property
    def up_movement(self) -> bool:
        """UP-wards player movement."""
        return self._up_movement

    @property
    def down_movement(self) -> bool:
        """DOWN-wards player movement."""
        return self._down_movement

    @property
    def left_movement(self) -> bool:
        """LEFT-wards player movement."""
        return self._left_movement

    @property
    def right_movement(self) -> bool:
        """RIGHT-wards player movement."""
        return self._right_movement

    @property
    def action_a(self) -> bool:
        """Action A player pressed."""
        return self._action_a

    @property
    def action_b(self) -> bool:
        """Action B player pressed."""
        return self._action_b

# ---- get inputs ----

    def handle_inputs(self) -> None:
        """
        Take in all key and controller inputs (if there is one)

        For movement, check all valid inputs.
        """
        # reset all values
        self.reset_values()
        # controller input gathering
        self._handle_joystick_inputs()
        # keyboard input gathering
        self._handle_keyboard_inputs()

    def _handle_joystick_inputs(self) -> None:
        """
        Take in controller inputs.
        """
        if not self._joystick:
            return

        try:
            jaxis_0: float = self._joystick.get_axis(0)  # left -> right
            jaxis_1: float = self._joystick.get_axis(1)  # up -> down
            dpad_up: int = self._joystick.get_button(11)
            dpad_down: int = self._joystick.get_button(12)
            dpad_left: int = self._joystick.get_button(13)
            dpad_right: int = self._joystick.get_button(14)
            self._action_a = self._joystick.get_button(0)
            self._action_b = self._joystick.get_button(1)
        except pygame.error:
            raise pygame.error("Failed to get controller.")

        if jaxis_0 > self.AXIS_T or dpad_right:
            self._right_movement = True
        elif jaxis_0 < -self.AXIS_T or dpad_left:
            self._left_movement = True
        if jaxis_1 < -self.AXIS_T or dpad_up:
            self._up_movement = True
        elif jaxis_1 > self.AXIS_T or dpad_down:
            self._down_movement = True

    def _handle_keyboard_inputs(self) -> None:
        """
        Take in keyboard inputs.
        """
        keys: key.ScancodeWrapper = key.get_pressed()
        if self.__check_key(keys, self.LEFT_KEYS):
            self._left_movement = True
        if self.__check_key(keys, self.RIGHT_KEYS):
            self._right_movement = True
        if self.__check_key(keys, self.UP_KEYS):
            self._up_movement = True
        if self.__check_key(keys, self.DOWN_KEYS):
            self._down_movement = True

        if self.__check_key(keys, self.ACTION_A_KEY):
            self._action_a = True
        if self.__check_key(keys, self.ACTION_B_KEY):
            self._action_b = True

    def reset_values(self) -> None:
        self._up_movement = False
        self._down_movement = False
        self._left_movement = False
        self._right_movement = False
        self._up_movement = False
        self._down_movement = False
        self._action_a = False
        self._action_b = False

    def __check_key(self, keys: key.ScancodeWrapper,
                    key_codes: list[int]) -> bool:
        for code in key_codes:
            if keys[code]:
                return True
        return False

    @staticmethod
    def controller_status() -> bool:
        """
        Check a controller's connection status.
        """
        return True if pygame.joystick.get_count() > 0 else False
