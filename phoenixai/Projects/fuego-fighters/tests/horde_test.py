import pytest
import pygame
import random
from unittest.mock import MagicMock, patch
import os
import sys

# Import the necessary classes and exceptions
from src.Sprites.horde import Horde
from constants import Constants
from src.exceptions import FormationEnd
from src.Sprites.enemy import Enemy
from constants import Layer

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture(autouse=True)
def mock_pygame():
    """Fixture to mock pygame setup and display"""
    with patch('pygame.init'), \
         patch('pygame.display.init'), \
         patch('pygame.display.set_mode'), \
         patch('pygame.display.get_surface') as mock_get_surface, \
         patch('pygame.image.load') as mock_image_load, \
         patch('pygame.Surface') as mock_surface, \
         patch('pygame.mask.from_surface') as mock_mask, \
         patch('pygame.time.get_ticks', return_value=0), \
         patch('pygame.time.set_timer'), \
         patch('random.randint', return_value=2000):
        
        # Create a mock surface with a predictable width
        mock_surface_instance = MagicMock()
        mock_surface_instance.get_width.return_value = 800
        mock_get_surface.return_value = mock_surface_instance
        
        # Prepare mock image and surface
        mock_image = MagicMock()
        mock_image.get_width.return_value = 800
        mock_image_load.return_value = mock_image
        
        # Prepare mock mask
        mock_mask_instance = MagicMock()
        mock_mask.return_value = mock_mask_instance
        
        yield {
            'surface': mock_surface_instance,
            'image_load': mock_image_load,
            'mask': mock_mask
        }

@pytest.fixture
def mock_renderables():
    """Fixture to create a mock renderables group"""
    return MagicMock()

@pytest.fixture
def horde(mock_renderables):
    """Fixture to create a Horde instance with test formation"""
    Constants.FORMATIONS = {
        'test_formation': [
            [1, 1, 0, 1],
            [0, 1, 1, 0],
            [1, 0, 1, 1]
        ]
    }
    return Horde(mock_renderables, 'test_formation')

def test_initialization(horde):
    """Test Horde initialization"""
    assert horde.formation == 'test_formation'
    assert horde.columns == 4
    assert horde.rows == 3
    assert horde.column_size == 200.0  # 800 / 4
    assert horde.active is None
    assert horde.current_line is None

def test_activate(horde):
    """Test activation of horde"""
    horde.activate()
    assert horde.active is True
    assert horde.current_line == 2  # rows - 1

def test_deactivate(horde):
    """Test deactivation of horde"""
    horde.activate()
    horde.deactivate()
    assert horde.active is False
    assert horde.current_line == 2  # rows - 1

def test_render_line(horde, mock_renderables):
    """Test rendering a line of the formation"""
    # Create a custom Enemy mock that tracks creations
    class EnemyMock:
        _creation_count = 0

        def __new__(cls, *args, **kwargs):
            cls._creation_count += 1
            mock_enemy = MagicMock()
            mock_enemy.rect = MagicMock()
            mock_enemy.rect.width = 50
            mock_enemy.rect.x = 0
            mock_enemy.rect.y = 0
            return mock_enemy

        @classmethod
        def get_creation_count(cls):
            return cls._creation_count

        @classmethod
        def reset_creation_count(cls):
            cls._creation_count = 0

    # Reset the creation count
    EnemyMock.reset_creation_count()

    # Patch Enemy with our mock class
    with patch('src.Sprites.horde.Enemy', EnemyMock), \
         patch('src.Sprites.enemy.Enemy', EnemyMock), \
         patch('pygame.time.set_timer'), \
         patch.object(mock_renderables, 'add') as mock_add:
        
        # Activate the horde first
        horde.activate()

        # Reset the mock to track only this call
        mock_add.reset_mock()

        # Call render_line
        horde.render_line()

        # Verify enemies were created and added
        assert EnemyMock.get_creation_count() == 3
        assert mock_add.call_count == 3

        # Check current line was decremented
        assert horde.current_line == 1

# def test_render_line_formation_end(horde):
#     """Test that FormationEnd is raised when all lines are rendered"""
#     # Patch Enemy with a mock to prevent actual instantiation
#     with patch('src.Sprites.horde.Enemy') as mock_enemy, \
#          patch('src.Sprites.enemy.Enemy', mock_enemy), \
#          patch('pygame.time.set_timer'):
        
#         # Activate the horde and render all lines
#         horde.activate()
    
#         # Render first line
#         horde.render_line()
#         # Render second line
#         horde.render_line()
#         # Render third (last) line
#         horde.render_line()

#         # Try to render beyond the last line should raise FormationEnd
#         with pytest.raises(FormationEnd) as excinfo:
#             horde.render_line()
        
#         # Optional: Add additional assertions about the exception if needed
#         assert str(excinfo.value) == ""  # If you want to check specific error message

def test_interval_default(mock_renderables):
    """Test default interval"""
    horde = Horde(mock_renderables, 'test_formation')
    assert horde.interval == 450

def test_interval_custom(mock_renderables):
    """Test custom interval"""
    horde = Horde(mock_renderables, 'test_formation', interval=600)
    assert horde.interval == 600