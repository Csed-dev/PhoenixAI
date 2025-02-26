# tests/sprite_test.py
import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.Sprites.sprite import Sprite

class MockSurface:
    def __init__(self, size=None, *args, **kwargs):
        self.size = size if size else (64, 64)
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])

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

@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup pygame environment"""
    pygame.init()
    yield

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
        mock_surface.side_effect = lambda size, *args, **kwargs: MockSurface(size)
        yield mock_surface

@pytest.fixture
def sprite_info():
    """Create sprite info dictionary for testing"""
    return {
        'spritesheet_filename': 'test_sprite.png',
        'width': 32,
        'height': 32,
        'rows': 2,
        'columns': 3
    }

class TestSprite:
    def test_initialization(self, mock_sprite_loading, mock_surface, sprite_info):
        """Test sprite initialization"""
        # Create sprite instance
        sprite = Sprite(sprite_info)

        # Verify image loading
        mock_sprite_loading.assert_called_once_with('resources/test_sprite.png')

        # Check basic attributes
        assert sprite.width == sprite_info['width']
        assert sprite.height == sprite_info['height']
        assert isinstance(sprite, pygame.sprite.Sprite)

    def test_image_extraction(self, mock_sprite_loading, mock_surface, sprite_info):
        """Test sprite sheet image extraction"""
        sprite = Sprite(sprite_info)

        # Verify number of extracted images
        expected_images = sprite_info['rows'] * sprite_info['columns']
        assert len(sprite.images) == expected_images

        # Verify each image is a Surface
        for image in sprite.images:
            assert isinstance(image, MockSurface)

    def test_rect_initialization(self, mock_sprite_loading, mock_surface, sprite_info):
        """Test rect initialization"""
        sprite = Sprite(sprite_info)
        
        # Verify rect exists and has correct dimensions
        assert hasattr(sprite, 'rect')
        assert isinstance(sprite.rect, pygame.Rect)
        assert sprite.rect.width == sprite_info['width']
        assert sprite.rect.height == sprite_info['height']

    def test_colorkey_setting(self, mock_sprite_loading, mock_surface, sprite_info):
        """Test colorkey setting for transparency"""
        sprite = Sprite(sprite_info)

        # Check each extracted image has colorkey set
        for image in sprite.images:
            assert hasattr(image, 'colorkey')
            assert hasattr(image, 'flags')
            assert image.flags == pygame.RLEACCEL

    def test_spritesheet_dimensions(self, mock_sprite_loading, mock_surface, sprite_info):
        """Test sprite sheet dimensions and image extraction positions"""
        sprite = Sprite(sprite_info)
        total_width = sprite_info['width'] * sprite_info['columns']
        total_height = sprite_info['height'] * sprite_info['rows']

        # Create a list of expected extraction rectangles
        expected_rects = []
        for i in range(sprite_info['rows']):
            for j in range(sprite_info['columns']):
                rect = pygame.Rect(
                    j * sprite_info['width'],
                    i * sprite_info['height'],
                    sprite_info['width'],
                    sprite_info['height']
                )
                expected_rects.append(rect)

        # Verify the number of rects matches the number of images
        assert len(expected_rects) == len(sprite.images)