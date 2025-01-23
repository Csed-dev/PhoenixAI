# tests/map_test.py
import pytest
from unittest.mock import Mock, patch
import pygame
import random
from constants import Constants
from src.exceptions import LevelFinished
from src.map import Map
from src.Sprites.horde import Horde


class MockSurface:
    def __init__(self):
        self._width = 800
        self._height = 600

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height


@pytest.fixture
def mock_display():
    """Mock pygame display"""
    mock_surface = MockSurface()
    with patch('pygame.display.get_surface', return_value=mock_surface):
        yield mock_surface


@pytest.fixture
def mock_horde():
    """Create a mock Horde class"""
    # Changed the patch path to target the import in map.py
    with patch('src.map.Horde') as mock_horde_class:
        # Create unique mock instances for each call
        mock_horde_class.side_effect = [Mock(spec=Horde) for _ in range(20)]
        yield mock_horde_class


@pytest.fixture
def mock_random_choice():
    """Mock random.choice to return predictable values"""
    with patch('random.choice') as mock_choice:
        mock_choice.return_value = list(Constants.FORMATIONS.keys())[0]
        yield mock_choice


@pytest.fixture
def test_map(mock_horde, mock_random_choice, mock_display):
    """Create a Map instance for testing"""
    renderables = Mock()
    return Map(renderables)


class TestMap:
    def test_initialization(self, test_map, mock_horde):
        """Test map initialization"""
        # Check initial state
        assert test_map.active == False
        assert len(test_map.horde_list) == 20

        # Verify Horde creation
        assert mock_horde.call_count == 20

    def test_map_control(self, test_map):
        """Test map start and pause functionality"""
        # Test start
        test_map.start()
        assert test_map.active == True

        # Test pause
        test_map.pause()
        assert test_map.active == False

    def test_horde_generation(self, mock_random_choice, mock_display):
        """Test that hordes are generated with random formations"""
        renderables = Mock()
        map_instance = Map(renderables)

        # Verify random.choice was called with formations
        mock_random_choice.assert_called_with(list(Constants.FORMATIONS.keys()))
        assert mock_random_choice.call_count == 20

    def test_next_horde_iteration(self, test_map):
        """Test next_horde method and iteration behavior"""
        # Get all hordes and store them
        hordes = []
        for _ in range(20):
            horde = test_map.next_horde()
            assert horde is not None
            hordes.append(horde)

        # Verify LevelFinished is raised when all hordes are exhausted
        with pytest.raises(LevelFinished):
            test_map.next_horde()

    def test_horde_uniqueness(self, test_map, mock_horde):
        """Test that each horde in the list is unique"""
        hordes = []

        # Get all hordes
        try:
            while True:
                horde = test_map.next_horde()
                hordes.append(horde)
        except LevelFinished:
            pass

        # Verify we got exactly 20 hordes
        assert len(hordes) == 20

        # Verify all hordes are unique
        assert len(set(id(horde) for horde in hordes)) == 20

    def test_formation_assignment(self, mock_random_choice, mock_horde, mock_display):
        """Test that formations are properly assigned to hordes"""
        renderables = Mock()
        map_instance = Map(renderables)

        expected_formation = list(Constants.FORMATIONS.keys())[0]
        mock_random_choice.assert_called_with(list(Constants.FORMATIONS.keys()))

        # Verify the formation was passed to Horde constructor
        for call in mock_horde.call_args_list:
            assert call[0][1] == expected_formation
