from hypothesis import given
import hypothesis.strategies as some
from unittest.mock import patch
import unittest

from src.sound import Sound

class TestSound(unittest.TestCase):
    @given(some.text())
    def test_play_sound(self, sound_name):
        with patch('src.sound.print') as mock_print:
            Sound.play_sound(sound_name)
            mock_print.assert_called_with(f"Playing sound: {sound_name}")
        
    def test_play_sound_with_empty_name(self):
        with patch('src.sound.print') as mock_print:
            Sound.play_sound("")
            mock_print.assert_called_with("Playing sound: ")
            

if __name__ == '__main__':
    unittest.main()