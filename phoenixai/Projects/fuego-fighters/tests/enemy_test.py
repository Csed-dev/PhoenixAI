# tests/enemy_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from constants import Constants
from src.Sprites.enemy import Enemy
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
def test_enemy(mock_sprite_loading, mock_surface, mock_mask, mock_display):
    """Create an enemy instance for testing"""
    enemy = Enemy(5, 4, 100, 30, x=100, y=100)
    enemy.rect.width = 64
    enemy.rect.height = 64
    return enemy


class TestEnemy:
    def test_initialization(self, test_enemy):
        """Test enemy initialization"""
        assert test_enemy.speed_h == 5
        assert test_enemy.speed_v == 4
        assert test_enemy.cooldown == 100
        assert test_enemy.hit_points == 30
        assert test_enemy.rect.x == 100
        assert test_enemy.rect.y == 100
        assert test_enemy.direction == Constants.DIR_L
        assert callable(test_enemy.towards[Constants.DIR_L])
        assert callable(test_enemy.towards[Constants.DIR_R])

    def test_direction_change(self, test_enemy):
        """Test direction change mechanism"""
        initial_direction = test_enemy.direction
        test_enemy.change_direction()
        assert test_enemy.direction == initial_direction * -1
        test_enemy.change_direction()
        assert test_enemy.direction == initial_direction

    def test_update_with_bounds(self, test_enemy):
        """Test update method when hitting bounds"""
        # Mock the move methods to simulate hitting bounds
        test_enemy.move_left = Mock(return_value=Constants.ENEMY_TOUCH_INSIDE)
        test_enemy.disappear = Mock()

        # Test update when hitting bounds
        test_enemy.update()
        assert test_enemy.disappear.called

    def test_update_with_down_movement(self, test_enemy):
        """Test update method with downward movement"""
        # Mock move_down to return False (hit bottom)
        test_enemy.move_down = Mock(return_value=False)
        test_enemy.disappear = Mock()

        # Test update when hitting bottom
        test_enemy.update()
        assert test_enemy.disappear.called

    def test_fire_mechanism(self, test_enemy):
        """Test firing mechanics"""
        bullet = test_enemy.fire()

        # Test bullet properties
        assert isinstance(bullet, Bullet)
        assert bullet.rect.x == test_enemy.rect.x + (test_enemy.rect.width / 2)
        assert bullet.rect.y == test_enemy.rect.y - 10
        assert bullet.speed == 6
        assert bullet.direction == 1

    def test_movement_towards(self, test_enemy):
        """Test movement using towards dictionary"""
        initial_x = test_enemy.rect.x

        # Test left movement
        test_enemy.towards[Constants.DIR_L]()
        assert test_enemy.rect.x == initial_x - test_enemy.speed_h

        # Reset position and test right movement
        test_enemy.rect.x = initial_x
        test_enemy.towards[Constants.DIR_R]()
        assert test_enemy.rect.x == initial_x + test_enemy.speed_h

    def test_inheritance(self, test_enemy):
        """Test inheritance from Plane class"""
        # Test inheritance
        assert isinstance(test_enemy, Enemy)

        # Test damage system from parent class
        initial_hp = test_enemy.hit_points
        assert test_enemy.take_damage(10) == False
        assert test_enemy.hit_points == initial_hp - 10

        # Test basic Plane attributes are present
        assert hasattr(test_enemy, 'speed_h')
        assert hasattr(test_enemy, 'speed_v')
        assert hasattr(test_enemy, 'cooldown')
        assert hasattr(test_enemy, 'hit_points')
        assert hasattr(test_enemy, 'rect')

        # Test movement methods exist and are callable
        assert callable(test_enemy.move_up)
        assert callable(test_enemy.move_down)
        assert callable(test_enemy.move_left)
        assert callable(test_enemy.move_right)
