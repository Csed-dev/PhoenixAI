# tests/mixer_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import random
from constants import Constants
from src.mixer import Mixer


class MockMixerMusic:
    def __init__(self):
        self.loaded_music = None
        self.is_playing = False
        self.end_event = None

    def load(self, music_file):
        self.loaded_music = music_file

    def play(self):
        self.is_playing = True

    def set_endevent(self, event):
        self.end_event = event


class MockPygameMixer:
    def __init__(self):
        self.music = MockMixerMusic()
        self.last_sound = None
        self.last_sound_file = None

    def Sound(self, sound_file):
        self.last_sound_file = sound_file
        mock_sound = Mock()
        self.last_sound = mock_sound
        return mock_sound


@pytest.fixture
def mock_mixer():
    """Create a mock pygame mixer"""
    return MockPygameMixer()


@pytest.fixture
def test_mixer(mock_mixer):
    """Create a Mixer instance for testing"""
    return Mixer(mock_mixer)


class TestMixer:
    def test_initialization(self, test_mixer, mock_mixer):
        """Test mixer initialization"""
        assert mock_mixer.music.loaded_music == Constants.MUSIC_BACKGROUND_INTRO
        assert mock_mixer.music.end_event == pygame.USEREVENT + 100

    def test_play_music(self, test_mixer, mock_mixer):
        """Test playing music"""
        test_mixer.play_music()
        assert mock_mixer.music.is_playing == True

    def test_stop_music(self, test_mixer, mock_mixer):
        """Test stopping music"""
        test_mixer.stop_music()
        assert mock_mixer.music.loaded_music == Constants.MUSIC_BACKGROUND

    def test_play_single_sound(self, test_mixer, mock_mixer):
        """Test playing a single sound"""
        test_sound = "test_sound"
        Constants.SOUNDS[test_sound] = "test_sound.wav"

        test_mixer.play_sound(test_sound)

        assert mock_mixer.last_sound_file == "test_sound.wav"
        assert mock_mixer.last_sound.play.called

    def test_play_random_sound(self, test_mixer, mock_mixer):
        """Test playing a sound from a list of sounds"""
        test_sound = "test_sound_list"
        sound_files = ["sound1.wav", "sound2.wav", "sound3.wav"]
        Constants.SOUNDS[test_sound] = sound_files

        # Mock random.randint to return a specific value
        with patch('random.randint', return_value=1):
            test_mixer.play_sound(test_sound)

            assert mock_mixer.last_sound_file == "sound2.wav"
            assert mock_mixer.last_sound.play.called

    def test_handle_event(self, test_mixer, mock_mixer):
        """Test event handling"""
        # Create a mock event
        event = Mock()
        event.type = pygame.USEREVENT + 100

        # Test event handling
        test_mixer.handle_event(event)

        # Verify that stop_music and play_music were called
        assert mock_mixer.music.loaded_music == Constants.MUSIC_BACKGROUND
        assert mock_mixer.music.is_playing == True

    def test_handle_other_event(self, test_mixer, mock_mixer):
        """Test handling of non-mixer events"""
        # Create a mock event with different type
        event = Mock()
        event.type = pygame.USEREVENT + 1

        # Initial state
        initial_music = mock_mixer.music.loaded_music
        initial_playing = mock_mixer.music.is_playing

        # Test event handling
        test_mixer.handle_event(event)

        # Verify that nothing changed
        assert mock_mixer.music.loaded_music == initial_music
        assert mock_mixer.music.is_playing == initial_playing
