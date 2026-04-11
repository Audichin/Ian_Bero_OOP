"""
Entity class module.

All objects within the game that require hitpoints, movement, and interactions
should inherit entity.

Good examples:
    Player - requires health, movement, environment interaction
    Enemies - same as Player
    Bubble - Bounces around the screen checking interactions,
            and is popped (hence the need for hitpoints)

Objects that inherit entity should override entity methods and call super()
at the end of each overridden method.
"""
from typing import Any, Callable

import pygame
from pygame import Vector2, sprite, Surface, Rect

# from pygame import locals


class Entity(sprite.Sprite):
    """
    Base class for all entity types.
    """

    _SCALE: int = 5

    __slots__: list[str] = ["_world"  # Any (World this entity belongs to)
                            "_assets",  # dict[str, int]
                            "_position",  # Vector2
                            "_prev_position",  # Vector2
                            "_velocity",  # Vector2
                            "_speed",  # float
                            "_clamp_speed",  # float
                            "_friction",  # float
                            "_sounds",  # dict[str, int]
                            "_HP",  # int
                            "_invincibility",  # float
                            "_rect",  # Rect
                            "_image",  # Surface
                            "_orientation",  # bool
                            "_curr_orient",  # bool
                            "_anim_timer_top",  # float
                            "_anim_timer"]  # float

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 100.0,
                 clamp_speed: float = 300,
                 friction: float = 25,
                 HP: int | None = None,
                 assets: dict[str, Surface] | None = None,
                 image: Surface | None = None,
                 anim_timer: float = 100.0) -> None:
        """
        Entities are game objects with some "living" attributes.
        Entities collide, can die and disappear, and can perform actions.

        Args:
            world (Any): World containing this entity
            position (Vector2, optional): World position. Defaults to Vector2(0, 0).
            speed (float, optional): entity speed. Defaults to 5.0.
            clamp_speed (float, optional): clamp speed. Defaults to 5.0.
            friction (float, optional): rate of slowdown. Defaults to .75.
            HP (int | None, optional): Hit points. Defaults to None.
            img (Surface | None, optional): base Surface. Defaults to None.
        """
        super().__init__()
        from world import World
        self._world: World = world

        self._position: Vector2 = position
        self._prev_position: Vector2 = Vector2(position.x, position.y)

        self.speed = speed
        self._clamp_speed: float = clamp_speed
        self.HP = HP if HP else 100
        self._invincibility: float = 0

        self._velocity: Vector2 = Vector2()
        self._friction: float = friction
        self._sounds: dict[str, int] = dict[str, int]()

        self._assets: dict[str, Surface] = dict[str, Surface]()
        if assets:
            self._assets = assets

        self._orientation: bool = True
        self._curr_orient: bool = True
        self._anim_timer_top: float = anim_timer
        self._anim_timer: float = self._anim_timer_top
        self.__image_init(image)

    def __image_init(self, img_in: Surface | None) -> None:
        """FIXME"""
        temp_img: Surface = Surface((16 * self._SCALE, 16 * self._SCALE))
        temp_img.fill((255, 255, 255))
        if img_in:
            temp_img = img_in.convert_alpha()

        self.image: Surface = temp_img
        self.rect: Rect = self.image.get_rect()

    def _sound_init(self) -> None:
        """
        The base of this does nothing, it just serves as
        a blueprint for other entity classes that add sounds
        """

# ----- properties -----

    def set_rect(self) -> None:
        """Set rect value to position"""
        self.rect.center = (int(self._position.x), int(self._position.y))

    @property
    def position(self) -> Vector2:
        """Entity position"""
        return self._position

    @property
    def HP(self) -> int:
        """Entity hit points"""
        return self._HP

    @HP.setter
    def HP(self, other: int) -> None:
        self._HP: int = other

    @property
    def speed(self) -> float:
        """the speed to increment velocity"""
        return self._speed

    @speed.setter
    def speed(self, other: float) -> None:
        self._speed: float = other

    @property
    def move_speed(self) -> float:
        """Speed entity is moving at. Measured pixles/second"""
        return self._velocity.magnitude()

# ----- base methods -----

    def loop(self, delta: float,
             move: Vector2 | None = None) -> None:
        """
        Entity loop. Run once every frame per entity.

        The base method will call move() and collide() for updating position.
        """
        self._prev_position = Vector2(self._position.x, self._position.y)
        if move:
            self.move(delta, move)
        else:
            self.move(delta)

        self.static_collide()

        if self._invincibility > 0:
            self._invincibility -= delta

    def render(self, time: float) -> tuple[Surface, Rect]:
        """
        Returns the current image and rect of an entity.
        """
        self.animate(time)
        try:
            if self.image and isinstance(self.rect, Rect):
                self.image.set_colorkey((0, 0, 0))
            else:
                raise AttributeError()
        except AttributeError:
            raise
        return (self.image, self.rect)

# ----- entity methods -----

    def move(self, delta: float, dir: Vector2 | None = None) -> None:
        """
        Movement for an Entity object.

        Entities move in accordance to direction

        Args:
            dir (Vector2 | None, optional): Direction of acceleration.
        """
        # add direction
        if not dir:
            dir = Vector2()

        self._velocity += Vector2(dir.x * self.speed, dir.y * self.speed)

        # handle x
        try:
            self._velocity.x += -(self._velocity.x / abs(self._velocity.x)) * self._friction
            if abs(self._velocity.x) <= self._friction / 2:
                self._velocity.x = 0
        except ZeroDivisionError:
            pass

        try:
            self._velocity.y += -(self._velocity.y / abs(self._velocity.y)) * self._friction
            if abs(self._velocity.y) <= self._friction / 2:
                self._velocity.y = 0
        except ZeroDivisionError:
            pass

        # velocity clamping (check x and y of velocity)
        try:
            norm = self._velocity.normalize()
            xclamp = abs(norm.x) * self._clamp_speed if norm.x else self._clamp_speed
            yclamp = abs(norm.y) * self._clamp_speed if norm.y else self._clamp_speed
            self._velocity.x = pygame.math.clamp(self._velocity.x, -xclamp, xclamp)
            self._velocity.y = pygame.math.clamp(self._velocity.y, -yclamp, yclamp)
        except ValueError:
            pass

        self._position += (self._velocity * delta)
        # print(self._position)
        self.set_rect()

    def move_to(self, new_pos: Vector2) -> None:
        """FIXME"""
        self._position = new_pos
        self.set_rect()

    def static_collide(self) -> None:
        """FIXME"""
        data: list[Rect] = self._world.entity_action(self, "s_col")

        if len(data) > 0:
            # check every rect
            for rect in data:
                # above rect
                self.static_rect_collide(rect)

    def static_rect_collide(self, rect: Rect) -> None:
        """FIXME"""

        if not isinstance(self.rect, Rect):
            raise AttributeError("rect must be of type Rect")
        # above rect
        relative_x: int = 0
        relative_y: int = 0

        diff_x: float = self._prev_position.x // 1 - (rect.left + (0.5 * rect.width))
        if diff_x >= (rect.width / 2) + (self.rect.width / 2):
            relative_x = 1
        elif diff_x <= (-rect.width / 2) + (-self.rect.width / 2):
            relative_x = -1

        diff_y: float = self._prev_position.y // 1 - (rect.top + (0.5 * rect.height))
        if diff_y >= (rect.height / 2) + (self.rect.height / 2):
            relative_y = 1
        elif diff_y <= (-rect.height / 2) + (-self.rect.height / 2):
            relative_y = -1

        if abs(relative_x) == 1:
            self._velocity.x = 0
            if relative_x < 0:
                self._position.x = rect.left - (self.rect.width / 2)
            else:
                self._position.x = rect.left + rect.width + (self.rect.width / 2)
        if abs(relative_y) == 1:
            self._velocity.y = 0
            if relative_y < 0:
                self._position.y = rect.top - (self.rect.height / 2)
            else:
                self._position.y = rect.top + rect.height + (self.rect.height / 2)

    def damage(self, dmg: int) -> None:
        """Take damage"""
        if self._invincibility <= 0:
            self.HP -= dmg
            self._invincibility = 1

    def play_sound(self, sound_key: str) -> None:
        """FIXME"""
        self._world.queue_sound(self._sounds[sound_key])

# ---- Asset Creation ----

    def _all_frames_from_sheet(self, sheet: Surface,
                               dimension: tuple[int, int],
                               group_size: int,
                               pattern: str,
                               type: str,
                               func: Callable[..., Any] | None = None,
                               *args: list[Any]) -> None:
        """
        Create assets from a sprite sheet.

        Each individual sprite is as wide as width, and as long as height.

        Requires that _assets been created first.
        """

        def standard() -> None:
            """standard sprite sheet append"""
            pos: list[int] = [0, 0]

            # create and append individual images to _assets
            # each asset uses the naming pattern given
            for p_indx in range(len(pattern)):  # Char in pattern
                for i in range(group_size):  # size of a group
                    name: str = f"{pattern[p_indx]}{type}{i}"
                    self._assets[name] = self._single_surface_from_sheet(sheet, pos, dimension)

                    pos[0] += dimension[0]
                    if pos[0] >= sheet.get_width():
                        pos[0] = 0
                        pos[1] += dimension[1]

        if func:
            try:
                func(*args)
            except AttributeError:
                raise AttributeError("func fail")
        else:
            try:
                standard()
            except AttributeError:
                raise AttributeError("standard failure")

    @staticmethod
    def _single_surface_from_sheet(sheet: Surface,
                                   pos: tuple[int, int] | list[int],
                                   dimension: tuple[int, int]) -> Surface:
        """FIXME"""
        single: Surface = Surface(dimension).convert_alpha()
        single.blit(sheet, (0, 0), (pos[0], pos[1], dimension[0], dimension[1]))
        single = pygame.transform.scale(single, (dimension[0] * Entity._SCALE,
                                                 dimension[1] * Entity._SCALE))
        return single

# ---- Animation and Sound ----

    def animate(self, time: float) -> None:
        """
        Animations rely on _assets and changing the current image.

        > Every inherited entity should implement their own animate.
        """

# ---- overloads ----

    def __str__(self) -> str:
        return "Entity"
