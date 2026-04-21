import sys
import os
from unittest import case
import pygame
from pygame import locals

class SoundManager:
    def __init__(self):
        self._music: str = ""
        self._sounds: list[pygame.mixer.Sound] = []
        pygame.mixer.set_num_channels(16)
        self.load_music()
        self.load_sound_effect()


    @property
    def music(self) -> str:
        """
        Gets the current music.

        Returns:
            str: _description_
        """
        return self._music

    @property
    def sounds(self) -> list[pygame.mixer.Sound]:
        return self._sounds

    @music.setter
    def music(self, new_music: str) -> None:
        self._music = new_music

    @sounds.setter
    def sounds(self, new_sounds: list[pygame.mixer.Sound]) -> None:
        self._sounds = new_sounds
    
    def pause_audio(self) -> None:
        """
        Pauses the music.
        """
        pygame.mixer.music.pause()

    def stop_audio(self, sound_index: int) -> None:
        """
        Fades out the wanted sound effect. Should be called in the sound handler.
        
        Args:
            sound_index (int): The index of the sound to stop. Should be between 0 and 12, inclusive.
        """
        fadeout: int = 1000  # Fade out duration in milliseconds
        match sound_index:
            # Sound effect cases
            case 0:
                pygame.mixer.Channel(0).stop()  # Chest_pick
            case 1:
                pygame.mixer.Channel(1).stop()  # Death
            case 2:
                pygame.mixer.Channel(2).stop()  # Explosion
            case 3:
                pygame.mixer.Channel(3).stop()  # Flame
            case 4:
                pygame.mixer.Channel(4).stop()  # Fuze
            case 5:
                pygame.mixer.Channel(5).stop()  # Healing
            case 6:
                pygame.mixer.Channel(6).stop()  # NPChurt
            case 7:
                pygame.mixer.Channel(7).stop()  # PChurt
            case 8:
                pygame.mixer.Channel(8).stop()  # Swordmiss
            # Music cases
            case 9:
                pygame.mixer.Channel(9).fadeout(fadeout)  # Main_theme
            case 10:
                pygame.mixer.Channel(10).fadeout(fadeout)  # Boss_theme
            # case 11:
            #     pygame.mixer.Channel(11).fadeout(fadeout)  # Puzzle_theme
            case 12:
                pygame.mixer.Channel(12).fadeout(fadeout)  # Enemy_theme
            case _:
                print(f"Error: Sound index {sound_index} is out of range.")

    def play_audio(self, sound_index: int) -> None:
        """
        Plays the wanted sound effect. Should be called in the sound handler.

        Args:
            sound_index (int): The index of the sound to play. Should be between 0 and 12, inclusive.
        """
        fade_in: int = 1000  # Fade in duration in milliseconds
        match sound_index:
            # Sound effect cases
            case 0:
                pygame.mixer.Channel(0).play(self._sounds[0])  # Chest_pick
            case 1:
                pygame.mixer.Channel(1).play(self._sounds[1])  # Death
            case 2:
                pygame.mixer.Channel(2).play(self._sounds[2])  # Explosion
            case 3:
                pygame.mixer.Channel(3).play(self._sounds[3])  # Flame
            case 4:
                pygame.mixer.Channel(4).play(self._sounds[4])  # Fuze
            case 5:
                pygame.mixer.Channel(5).play(self._sounds[5])  # Healing
            case 6:
                pygame.mixer.Channel(6).play(self._sounds[6])  # NPChurt
            case 7:
                pygame.mixer.Channel(7).play(self._sounds[7])  # PChurt
            case 8:
                pygame.mixer.Channel(8).play(self._sounds[8])  # Swordmiss
            # Music cases
            case 9:
                pygame.mixer.Channel(9).play(self._sounds[9], fade_ms = fade_in)  # Main_theme
            case 10:
                pygame.mixer.Channel(10).play(self._sounds[10], fade_ms = fade_in)  # Boss_theme
            # case 11:
            #     pygame.mixer.Channel(11).play(self._sounds[11], fade_ms = fade_in)  # Puzzle_theme
            case 12:
                pygame.mixer.Channel(12).play(self._sounds[12], fade_ms = fade_in)  # Enemy_theme
            case _:
                print(f"Error: Sound index {sound_index} is out of range.")

    def load_music(self) -> None:
        """
        Adds music to the list of sounds. Performed duricng initialization.

        Args:
            new_sounds (list[pygame.mixer.Sound]): List of new sounds that got added
        """

        # Next few lines are for music
        Main_theme_sound = self.load_audio("assets/audio/music/Main_Theme.mp3")
        # Next themes to add:
        Boss_theme_sound = self.load_audio("assets/audio/music/Boss_Theme.mp3")
        # Puzzle_theme_sound = self.load_audio("assets/audio/music/Puzzle_Theme.mp3")
        Enemy_theme_sound = self.load_audio("assets/audio/music/Enemy_Theme.mp3")

        Main_theme_channel = pygame.mixer.Channel(9)
        # Future channels needed:
        Boss_theme_channel = pygame.mixer.Channel(10)
        # Puzzle_theme_channel = pygame.mixer.Channel(11)
        Enemy_theme_channel = pygame.mixer.Channel(12)

        for sound in [Main_theme_sound, Boss_theme_sound, Enemy_theme_sound]:
            self._sounds.append(sound)
    
    def load_sound_effect(self) -> None:
        """
        Adds a new sound effect to the list of sounds. Performed during initialization.

        Args:
            new_sound (pygame.mixer.Sound): The new sound effect to add.
        """

        Chest_pick_sound = self.load_audio("assets/audio/sound/Chest_pick.wav")
        Death_sound = self.load_audio("assets/audio/sound/Death.wav")
        Explosion_sound = self.load_audio("assets/audio/sound/Explosion.wav")
        Flame_sound = self.load_audio("assets/audio/sound/Flame.wav")
        Fuze_sound = self.load_audio("assets/audio/sound/Fuze.wav")
        Healing_sound = self.load_audio("assets/audio/sound/Healing.wav")
        NPChurt_sound = self.load_audio("assets/audio/sound/NPChurt.wav")
        PChurt_sound = self.load_audio("assets/audio/sound/PChurt.wav")
        Swordmiss_sound = self.load_audio("assets/audio/sound/Swordmiss.wav")
        
        Chest_pick_channel = pygame.mixer.Channel(0)
        Death_channel = pygame.mixer.Channel(1)
        Explosion_channel = pygame.mixer.Channel(2)
        Flame_channel = pygame.mixer.Channel(3)
        Fuze_channel = pygame.mixer.Channel(4)
        Healing_channel = pygame.mixer.Channel(5)
        NPChurt_channel = pygame.mixer.Channel(6)
        PChurt_channel = pygame.mixer.Channel(7)
        Swordmiss_channel = pygame.mixer.Channel(8)
    
        for sound in [Chest_pick_sound, Death_sound, Explosion_sound, Flame_sound, Fuze_sound, Healing_sound, NPChurt_sound, PChurt_sound, Swordmiss_sound]:
            self._sounds.append(sound)

    def load_audio(self, file_path: str) -> pygame.mixer.Sound:
        """
        Loads audio and will either return back the mixer variable with the music location or throw an error

        Args:
            file_path (str): the filepath to the audio

        Returns:
            pygame.mixer.Sound: the created mixer audio 
        """
        if not os.path.isfile(file_path):
            print(f"Error: Sound file '{file_path}' not found.")
            sys.exit(1)
        try:
            return pygame.mixer.Sound(file_path)
        except pygame.error as e:
            print(f"Error loading sound '{file_path}': {e}")
            sys.exit(1)