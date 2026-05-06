"""
Projectile Module.
"""

import pygame
from pygame import sprite, Vector2, Surface, Rect


class Projectile(sprite.Sprite):
    """
    Base class for all projectiles.

    A projectile is a game object that has movement data, sound data,
    and damage data. They do not possess hitpoints, instead opting
    to be deleted once they expire.

    Projectiles are typically used by items or entities to create
    obstacles that damage other entities.
    """

    _SCALE: int = 5

    __slots__: list[str] = ["_dmg",  # int
                            "_position",  # Vector2
                            "_velocity",  # Vector2
                            "_speed",  # float
                            "_friction",  # float
                            "_sounds"]  # dict[str, int]

    def __init__(self, position: Vector2 = Vector2(),
                 speed: float = 100.0,
                 friction: float = 10.0,
                 damage: int = 1,
                 image: Surface | None = None) -> None:
        """Projectile object. Utilized for damaging other entities.

        Args:
            position (Vector2, optional): World position. Defaults to Vector2().
            speed (float, optional): Projectile speed increase per frame. Defaults to 100.0.
            friction (float, optional): Projectile fricition. Defaults to 10.0.
            damage (int, optional): Damage a projectile can deal. Defaults to 1.
            image (Surface | None, optional): Image this projectile possesses. Defaults to None.
        """
        super().__init__()

        self._dmg: int = damage

        # Vector inits
        self._position: Vector2 = position
        self._velocity: Vector2 = Vector2()

        # speed inits
        self._speed: float = speed
        self._friction: float = friction

        # sound init
        self._sounds: dict[str, int] = dict[str, int]()
        self._sound_init()

        self.__image_init(image)

    def __image_init(self, img_in: Surface | None) -> None:
        """Image and rect initialization.

        Args:
            img_in (Surface | None): Input image. Important for Rect creation.
        """
        temp_img: Surface = Surface((8 * self._SCALE, 8 * self._SCALE))
        temp_img.fill((222, 133, 255))
        if img_in:
            temp_img = img_in.convert_alpha()

        self.image: Surface = temp_img
        self.rect: Rect = self.image.get_rect()
        self.set_rect()

    def _sound_init(self) -> None:
        """
        The base of this doesn't do anything.
        """

# ==== properties ====

    def set_rect(self) -> None:
        """Set rect to the center of position."""
        self.rect.center = (int(self._position.x), int(self._position.y))

    @property
    def position(self) -> Vector2:
        """Projectile position."""
        return self._position

    @property
    def speed(self) -> float:
        """Speed to increment projectile velocity."""
        return self._speed

    @property
    def move_speed(self) -> float:
        """Speed projectile is moving at. Measured pixles/second"""
        return self._velocity.magnitude()

    @property
    def damage_points(self) -> int:
        """Amount of damage a projectile deals."""
        return self._dmg

    @damage_points.setter
    def damage_points(self, other: int) -> None:
        self._dmg = other

# ==== base methods ====

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        """
        Projectile loop. Run once every frame per projectile.

        Args:
            delta (float): milliseconds since last frame
            move (Vector2 | None, optional): movement. Defaults to None.
        """
        if move:
            self.move(delta, move)
        else:
            self.move(delta)

    def render(self) -> tuple[Surface, Rect]:
        """Returns the current image and rect of a projectile.

        Raises:
            AttributeError: Image doesn't exist.

        Returns:
            tuple[Surface, Rect]: Projectile render data.
        """
        try:
            self.image.set_colorkey((0, 0, 0))
        except AttributeError:
            raise AttributeError(f"{self.__str__}: Image Error.")
        return (self.image, self.rect)

# ==== projectile methods ====

    def move(self, delta: float, dir: Vector2 = Vector2()) -> None:
        """
        Movement for projectile object.

        Args:
            delta (float): milliseconds since last frame.
            dir (Vector2 | None, optional): direction of acceleration. Defaults to (0, 0)
        """
        self.push(dir)
        # handle x
        try:
            self._velocity.x += -(self._velocity.x / abs(self._velocity.x)) * self._friction
            if abs(self._velocity.x) <= self._friction / 2:
                self._velocity.x = 0
        except ZeroDivisionError:
            pass

        # handle y
        try:
            self._velocity.y += -(self._velocity.y / abs(self._velocity.y)) * self._friction
            if abs(self._velocity.y) <= self._friction / 2:
                self._velocity.y = 0
        except ZeroDivisionError:
            pass

        self.move_to(self.position + (self._velocity * delta))

    def move_to(self, new_pos: Vector2) -> None:
        """Move position to the passed position and update rect.

        Args:
            new_pos (Vector2): New position.
        """
        self._position = new_pos
        self.set_rect()

    def push(self, dir: Vector2) -> None:
        """Add passed direction to velocity.

        Args:
            dir (Vector2): Passed direction vector.
        """
        self._velocity += Vector2(dir.x * self.speed, dir.y * self.speed)

# ==== get image from file ====

    def _single_from_sheet(self, image: Surface,
                           dimension: tuple[int, int]) -> Surface:
        """
        Obtain a single frame from a sprite sheet.

        Args:
            image (Surface): Image to cut frame from.
            dimension (tuple[int, int]): size of frame. (width, height)

        Returns:
            Surface: Single frame cut from sheet.
        """
        single: Surface = Surface(dimension).convert_alpha()
        single.blit(image, (0, 0), (0, 0, dimension[0], dimension[1]))
        single = pygame.transform.scale(single, (dimension[0] * self._SCALE,
                                                 dimension[1] * self._SCALE))
        return single
