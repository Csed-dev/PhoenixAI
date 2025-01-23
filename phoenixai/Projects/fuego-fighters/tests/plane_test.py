# tests/plane_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from constants import Constants
from src.Sprites.plane import Plane
from src.Sprites.bullet import Bullet


class MockSurface:
    def __init__(self, *args, **kwargs):
        self.rect = pygame.Rect(0, 0, 64, 64)
        self._width = 800
        self._height = 600

    def convert_alpha(self):
        return self

    def convert(self):
        return self

    def get_rect(self):
        return self.rect

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def subsurface(self, rect):
        return self

    def set_colorkey(self, color, flags=0):
        pass

    def get_at(self, pos):
        return (0, 0, 0, 255)

    def blit(self, source, dest, area=None):
        pass

    def set_width(self, width):
        self._width = width

    def set_height(self, height):
        self._height = height


@pytest.fixture
def mock_display():
    """Mock pygame display"""
    mock_surface = MockSurface()
    with patch('pygame.display.get_surface', return_value=mock_surface):
        yield mock_surface


@pytest.fixture(autouse=True)
def setup_pygame(mock_display):
    """Setup pygame environment"""
    pygame.init()
    yield


@pytest.fixture
def mock_sprite_loading():
    """Mock sprite loading"""
    with patch('pygame.image.load') as mock_load:
        mock_surface = MockSurface()
        mock_load.return_value = mock_surface
        yield mock_surface


@pytest.fixture
def mock_surface():
    """Mock pygame.Surface"""
    with patch('pygame.Surface', MockSurface):
        yield


@pytest.fixture
def mock_mask():
    """Mock pygame.mask"""
    with patch('pygame.mask.from_surface') as mock_mask_func:
        mock_mask_func.return_value = Mock()
        yield mock_mask_func


@pytest.fixture
def test_plane(mock_sprite_loading, mock_surface, mock_mask, mock_display):
    """Create a plane instance for testing"""
    plane = Plane(Constants.SPRITE_PLAYER_PLANE, 5, 4, 100, 30, respect_borders=False)
    plane.rect.width = 64
    plane.rect.height = 64
    return plane


class TestPlane:
    def test_initialization(self, test_plane):
        """Test plane initialization"""
        assert test_plane.speed_h == 5
        assert test_plane.speed_v == 4
        assert test_plane.cooldown == 100
        assert test_plane.hit_points == 30
        assert test_plane.respect_borders == False
        assert test_plane.keyup == False
        assert test_plane.image == test_plane.image_top

    def test_fire_mechanism(self, test_plane):
        """Test firing mechanics"""
        with patch('pygame.time.get_ticks') as mock_ticks:
            # Initial time
            mock_ticks.return_value = 0
            test_plane.last_fire = -200  # Ensure cooldown has passed
            test_plane.rect.x = 50  # Set valid position
            test_plane.rect.y = 50

            bullet = test_plane.fire()
            assert isinstance(bullet, Bullet)
            assert bullet.rect.x == test_plane.rect.x + (test_plane.rect.width / 2)
            assert bullet.rect.y == test_plane.rect.y - 10

            # Try firing during cooldown
            mock_ticks.return_value = 50
            assert test_plane.fire() is None

            # Test with cooldown reset
            mock_ticks.return_value = 200  # After cooldown period
            test_plane.reset_weapon_cooldown()
            bullet = test_plane.fire()
            assert isinstance(bullet, Bullet)

    def test_damage_system(self, test_plane):
        """Test damage and health system"""
        initial_hp = test_plane.hit_points
        assert test_plane.take_damage(10) == False
        assert test_plane.hit_points == initial_hp - 10
        assert test_plane.take_damage(initial_hp) == True
        assert test_plane.hit_points <= 0

    def test_sprite_management(self, test_plane, mock_mask):
        """Test sprite changing mechanism"""
        test_plane.move_left()
        test_plane.reset_sprite()
        assert test_plane.image == test_plane.image_top

        test_plane.move_right()
        assert test_plane.image == test_plane.image_right
        test_plane.move_left()
        assert test_plane.image == test_plane.image_left
