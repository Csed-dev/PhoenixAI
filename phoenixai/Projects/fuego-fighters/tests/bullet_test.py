# tests/bullet_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.Sprites.bullet import Bullet

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
        self.images = [MockSurface()]
        self.rect = self.images[0].get_rect()

@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup pygame environment"""
    pygame.init()
    yield

@pytest.fixture
def mock_sprite_class():
    """Mock Sprite class"""
    with patch('src.Sprites.bullet.Sprite', MockSprite):
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
def bullet_info():
    """Create bullet info dictionary for testing"""
    return {
        'spritesheet_filename': 'bullet.png',
        'width': 10,
        'height': 20,
        'rows': 1,
        'columns': 1
    }

class TestBullet:
    def test_initialization(self, mock_sprite_class, mock_sprite_loading, mock_surface, bullet_info):
        """Test bullet initialization"""
        bullet = Bullet(bullet_info, speed=5, direction=1)
        
        # Check basic attributes
        assert bullet.width == bullet_info['width']
        assert bullet.height == bullet_info['height']
        assert bullet.speed == 5
        assert bullet.direction == 1
        assert hasattr(bullet, 'image')
        assert hasattr(bullet, 'images')
        assert bullet.image == bullet.images[0]

    def test_update_movement(self, mock_sprite_class, mock_sprite_loading, mock_surface, bullet_info):
        """Test bullet movement in both directions"""
        # Test downward movement
        bullet = Bullet(bullet_info, speed=5, direction=1)
        bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
        initial_y = bullet.rect.y
        bullet.update()
        assert bullet.rect.y == initial_y + (bullet.speed * bullet.direction)

        # Test upward movement
        bullet = Bullet(bullet_info, speed=5, direction=-1)
        bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
        initial_y = bullet.rect.y
        bullet.update()
        assert bullet.rect.y == initial_y + (bullet.speed * bullet.direction)

    def test_movement_with_different_speeds(self, mock_sprite_class, mock_sprite_loading, mock_surface, bullet_info):
        """Test bullet movement with various speeds"""
        test_speeds = [1, 3, 5, 10]
        
        for speed in test_speeds:
            # Test upward movement
            bullet = Bullet(bullet_info, speed=speed, direction=-1)
            bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
            initial_y = bullet.rect.y
            bullet.update()
            assert bullet.rect.y == initial_y - speed

            # Test downward movement
            bullet = Bullet(bullet_info, speed=speed, direction=1)
            bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
            initial_y = bullet.rect.y
            bullet.update()
            assert bullet.rect.y == initial_y + speed

    def test_boundary_values(self, mock_sprite_class, mock_sprite_loading, mock_surface, bullet_info):
        """Test bullet with boundary values"""
        # Test with zero speed
        bullet = Bullet(bullet_info, speed=0, direction=1)
        bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
        initial_y = bullet.rect.y
        bullet.update()
        assert bullet.rect.y == initial_y

        # Test with zero direction
        bullet = Bullet(bullet_info, speed=5, direction=0)
        bullet.rect = pygame.Rect(100, 100, bullet_info['width'], bullet_info['height'])
        initial_y = bullet.rect.y
        bullet.update()
        assert bullet.rect.y == initial_y