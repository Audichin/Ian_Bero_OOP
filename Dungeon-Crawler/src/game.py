"""
Game Module

> Contains the Game singleton manager for everything within the game.

As per the tutorial online, a game loop should look like this:

>>> while True:
>>>     event()
>>>     loop()
>>>     render()
>>>     sound()

We handle events first, then run the next game loop (next frame)
and then render the game to the screen last.

RULES:
    Screen is 1440 by 810
    All images should be scaled up by a factor of 5
"""
import sys
from typing import Self, Any

import pygame
import pygame.mixer_music as music
from pygame import locals

from world import World


class Game:
    """singleton obj"""
    _instance = None

    # --- constants ---
    _FPS: int = 60
    _VOLUME: float = 0.5
    _RESOLUTION: tuple[int, int] = (1440, 810)

    __slots__ = ["_debug_mode"   # bool
                 , "_debug_font"  # pygame.font.SysFont
                 , "_resolution"  # tuple[int, int]: manage screen resolution
                 , "_screen"  # Screen: Manage display
                 , "_framerate"  # Clock: Manage framerate
                 , "_running"  # boolean: game status
                 , "_curr_music"  # str: playing currently
                 , "_world"  # World: Object
                 , "_seed"]  # seed: any

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Simple singleton implementation"""
        if not cls._instance:
            cls._instance = super().__new__(cls)  # *args assumed added.
        else:
            raise Exception("Cannot instantiate new singleton.")
        return cls._instance

    def __init__(self, seed: Any, resolution: tuple[int, int] | None = None) -> None:
        """
        Class Game Initializer.
        > Initializes variables belonging to Game.

        > Sets mixer values before initialization

        Args:
            resolution (tuple[int, int] | None, optional): Game resolution.
            Defaults to (1440, 810)

        _running = false.
        """
        # debug mode set to disabled (False)
        self._debug_mode: bool = False
        pygame.font.init()
        self._debug_font: pygame.font.Font = pygame.font.SysFont("consolas", 18)

        # initialize game seed
        self._seed: Any = seed

        # initialize game resolution
        self._resolution: tuple[int, int] = (0, 0)
        if resolution is None:
            self._resolution = self._RESOLUTION
        else:
            self._resolution = resolution

        # Initialize game running state
        self._running: bool = False

        # clock for handling framerate
        self._framerate: pygame.time.Clock = pygame.time.Clock()

        pygame.mixer.pre_init()  # No changes

    # --- game initialization ---

    def _game_init(self) -> None:
        """
        Game initializer
        > Initializes the game objects when they are wanted.

        > Opposed to __init__, this method should be called to initialize pygame objects.

        > Should also initialize world.

        Things to be initialized:
        * pygame
        * screen
        * world
        * game state
        """
        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(
            self._resolution, pygame.NOFRAME)
        pygame.mixer.init()
        self._running = True
        self._world: World = World(self._seed)
        self._curr_music: str = str()

    # --- event handler ---

    def event_handler(self) -> None:
        """
        Event Handler
        > Handles all PyGame events.

        Main events to handle:
        * Quit
            * Should close out of the game.
        * etc. (May need other events)
        """
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                print("Quitting...")
                self._running = False
            elif event.type == locals.KEYDOWN:
                if event.dict['key'] == locals.K_ESCAPE:
                    print("Quitting...")
                    self._running = False
                if event.dict['key'] == locals.K_F1:
                    self.switch_debug()

    # --- debug methods ---

    def switch_debug(self) -> None:
        """
        Switch debug states.
        """
        self._debug_mode = not self._debug_mode
        if self._debug_mode:
            print("Debug enabled.")
        else:
            print("Debug disabled.")

    def display_debug(self) -> None:
        """
        Display debug to the screen.
        """
        debug_data: dict[str, Any] = self._world.data

        debug_log: list[str] = [
            "Player:",
            f"  position: {debug_data['player']['position']}",
            f"  HP: {debug_data['player']['hp']}"
        ]
        debug_log.append("Entities:")
        for entity in debug_data['entities']:
            debug_log.append(f" {entity['name']}:")
            debug_log.append(f"     position: {entity['position']}")
            debug_log.append(f"     HP: {entity['hp']}")

        debug_log.append("Grounded items:")
        for item in debug_data['items']['grounded']:
            debug_log.append(f" {item['name']}:")
            debug_log.append(f"     position: {item['position']}")

        debug_log.append("Inventory Items:")
        for item in debug_data['items']['inventory']:
            debug_log.append(f" {item['name']}:")

        debug_log.append("Item Slot:")
        debug_log.append(f" {debug_data['items']['slot']['name']}")

        debug_log.append("Room:")
        debug_log.append(f" Data: {debug_data['room']['current']}")
        debug_log.append(f" Music: {debug_data['room']['music']}")
        debug_log.append(f"FRAMERATE: {self._framerate.get_fps()}")

        # Display to screen
        for i, line in enumerate(debug_log):
            text = self._debug_font.render(line, False, (255, 255, 0))
            self._screen.blit(text, (120, 60 + i * 20))

    # --- render method ---

    def on_render(self) -> None:
        """
        Rendering method
        > Draws all objects to the screen by calling all draw() methods.

        > Should probably only need to call _world.draw()

        Objects to be drawn:
        * World
            * Entity
                * Player
                * Enemy
                * etc.
            * Item
            * etc.
        * etc.

        Also calls sound handler.
        """
        self._screen.fill("black")
        items = self._world.render()
        for i, _n in enumerate(items):
            self._screen.blit(items[i][0], items[i][1])

        # check to display debug
        if self._debug_mode:
            self.display_debug()

        pygame.display.flip()

        self.sound_handler()

    # --- sound module ---

    def sound_handler(self) -> None:
        """
        Sound Handler method.

        May not be needed, but if it is:
        > Handles all object sounds in a queue

        Sound includes:
        * Music
        * Sound effects

        STEPS:
            1. Retrieve sound data from WORLD
                * includes both sounds and music
            2. Play music.
                * If the music changed from the last, fade them.

        All of the above should be done at the _VOLUME constant.
        """
        # set volumes
        music.set_volume(self._VOLUME)

        world_music: str = self._world.music

        if world_music != self._curr_music:  # Fade out music.
            music.queue(world_music, loops=1)
            if pygame.mixer.music.get_busy():
                music.fadeout(100)

    # --- cleanup module ---

    def cleanup(self) -> None:
        """
        Cleanup method.

        > Utilize this method every time the game closes down.

        Things that should be cleaned up upon a game close:
        * Audio handler
        * Visual screen
        * Anything else that needs to be safely shut down.
        """
        pygame.display.quit()
        self._world.quit_controller()
        pygame.joystick.quit()
        pygame.quit()
        sys.exit()

    # --- loop module ---

    def on_loop(self) -> None:
        """
        Loop method.
        > Calls the loop method of all in game objects with a loop method.

        Those with loop methods should include:
        * World
            * Entity
                * Player
                * Enemy
                * etc.
            * Items
            * etc.
        * etc.
        """
        delta: float = self._framerate.tick(self._FPS) / 1000.0  # Game runs at 60fps
        self._world.loop(delta)
        # print(self._framerate.get_fps())

    # --- run game module ---

    def run_game(self) -> None:
        """
        Run Game method.
        > Starts and continues to run the game in a while loop.

        > Everything that the game does should be within the while-loop.

        Game actions during run-time includes:
        * Handling events
        * Main game loop
            * Player actions and movement
            * Enemy actions and movement
            * Dungeon room logic
            * Puzzle logic
            * Inventory handling
            * etc.
        * Render handler
            * Dungeon rendering
            * Player rendering
            * Enemy rendering
            * etc.
            * also handles sounds!
        """
        self._game_init()
        while self._running:
            self.event_handler()
            self.on_loop()
            self.on_render()
        self.cleanup()

    # --- static methods ---

    @staticmethod
    def main() -> None:
        """
        Build the game here!
        """
        seed: Any = 2983
        game: Game = Game(seed=seed)
        game.run_game()


if __name__ == "__main__":
    Game.main()
