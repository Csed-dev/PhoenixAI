# tests/explosion_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.Sprites.explosion import Explosion

class MockSurface:
    def __init__(self, *args, **kwargs):
        self.rect = pygame.Rect(0, 0, 32, 32)

    def convert_alpha(self):
        return self

    def convert(self):
        return self

    def get_rect(self):
        return self.rect

    def set_colorkey(self, color, flags=0):
        self.colorkey = color
        self.flags = flags

    def get_at(self, pos):
        return (0, 0, 0, 255)

    def blit(self, source, dest, area=None):
        pass

class MockSprite:
    def __init__(self, *args, **kwargs):
        self.images = [MockSurface(), MockSurface(), MockSurface()]
        self.rect = self.images[0].get_rect()
        self.called_with_args = args

@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup pygame environment"""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def mock_sprite():
    """Mock our Sprite class"""
    with patch('src.Sprites.explosion.Sprite', MockSprite):
        yield MockSprite

@pytest.fixture
def mock_sprite_loading():
    """Mock sprite loading"""
    with patch('pygame.image.load') as mock_load:
        mock_surface = MockSurface()
        mock_load.return_value = mock_surface
        yield mock_load

@pytest.fixture
def mock_surface():
    """Mock pygame.Surface"""
    with patch('pygame.Surface') as mock_surface:
        mock_surface.side_effect = lambda *args, **kwargs: MockSurface()
        yield mock_surface

@pytest.fixture
def explosion_info():
    """Create explosion info dictionary for testing"""
    return {
        'spritesheet_filename': 'explosion.png',
        'width': 32,
        'height': 32,
        'rows': 1,
        'columns': 3
    }

class TestExplosion:
    def test_initialization(self, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test explosion initialization"""
        delay = 5
        explosion = Explosion(explosion_info, delay)
        
        # Check basic attributes
        assert explosion.image_index == 0
        assert explosion.timer == 0
        assert explosion.animation_delay == delay
        assert hasattr(explosion, 'image')
        assert hasattr(explosion, 'images')

    def test_update_before_delay(self, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test update when timer hasn't reached delay"""
        delay = 5
        explosion = Explosion(explosion_info, delay)
        
        initial_image_index = explosion.image_index
        
        # Update but don't exceed delay
        for _ in range(delay):
            explosion.update()
            assert explosion.image_index == initial_image_index

    def test_update_animation_sequence(self, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test complete animation sequence"""
        delay = 2
        explosion = Explosion(explosion_info, delay)
        
        # First frame
        assert explosion.image_index == 0
        
        # Update to second frame
        for _ in range(delay + 1):
            explosion.update()
        assert explosion.image_index == 1
        
        # Update to third frame
        for _ in range(delay + 1):
            explosion.update()
        assert explosion.image_index == 2

    def test_timer_reset(self, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test timer reset after reaching delay"""
        delay = 3
        explosion = Explosion(explosion_info, delay)
        
        # Update until timer should reset
        for _ in range(delay + 1):
            explosion.update()
        assert explosion.timer == 0
        assert explosion.image_index == 1

    @patch('pygame.sprite.Sprite.kill')
    def test_kill_at_animation_end(self, mock_kill, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test that explosion is killed after last frame"""
        delay = 1
        explosion = Explosion(explosion_info, delay)
        
        # Run through all frames
        for _ in range((delay + 1) * len(explosion.images) + 1):
            explosion.update()
        
        # Verify kill was called
        mock_kill.assert_called_once()

    def test_variable_delays(self, mock_sprite, mock_sprite_loading, mock_surface, explosion_info):
        """Test explosion with different delay values"""
        test_delays = [1, 3, 5]
        
        for delay in test_delays:
            explosion = Explosion(explosion_info, delay)
            
            # Update just before delay
            for _ in range(delay):
                explosion.update()
                assert explosion.image_index == 0
            
            # Update after delay
            explosion.update()
            assert explosion.image_index == 1