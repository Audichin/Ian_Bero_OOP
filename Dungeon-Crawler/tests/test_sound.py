from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import MagicMock, patch
import unittest

from src.sound import SoundManager


class TestSound(unittest.TestCase):
    @given(song_number=some.integers(min_value=0, max_value=12))
    def test_play_sound(self, song_number):
        """
        tests sounds to ensure al sounds can be played

        Args:
            song_number (_type_): a bunch of song numbers to test

        Returns:
            _type_: none
        """
        channels = {}

        def get_channel(channel_number):
            """
            gets channel

            Args:
                channel_number (_type_): the channel number (between 1-12)

            Returns:
                dict: channels
            """
            if channel_number not in channels:
                channels[channel_number] = MagicMock()
            return channels[channel_number]

        with patch('src.sound.pygame.mixer') as mock_mixer:
            mock_mixer.Sound.side_effect = lambda file_path: MagicMock(name=file_path)
            mock_mixer.Channel.side_effect = get_channel
            mock_mixer.get_busy.return_value = True

            SM = SoundManager()
            SM.play_audio(song_number)

            if song_number <= 8:
                channels[song_number].play.assert_called_with(SM.sounds[song_number])
            else:
                channels[song_number].play.assert_called_with(
                    SM.sounds[song_number], -1, fade_ms=1000
                )
            self.assertEqual(SM.is_busy(), True)
