# tests/health_bar_test.py
import pytest
import pygame
from unittest.mock import Mock, patch, call
from pygame import Rect
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from constants import Constants
from src.Sprites.health_bar import HealthBar

class MockParent:
    def __init__(self, hit_points=100, width=64, height=64, x=100, y=100):
        self.hit_points = hit_points
        self.width = width
        self.height = height
        self.rect = Rect(x, y, width, height)

class MockSurface:
    def __init__(self, size):
        self.size = size
        self.fills = []
        self.rect = Rect(0, 0, *size)

    def fill(self, color):
        self.fills.append(color)


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup pygame environment"""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def parent():
    """Create a mock parent sprite"""
    return MockParent()

class TestHealthBar:
    def test_initialization(self, parent):
        """Test health bar initialization"""
        health_bar = HealthBar(parent)
        
        assert health_bar.parent == parent
        assert health_bar.max == parent.hit_points
        assert health_bar.hit_points == parent.hit_points

    def test_health_decrease_animation(self, parent):
        """Test smooth health decrease animation"""
        health_bar = HealthBar(parent)
        initial_health = parent.hit_points
        
        # Simulate parent taking damage
        parent.hit_points -= 20
        
        # Health bar should decrease smoothly
        assert health_bar.hit_points == initial_health
        health_bar.update()
        assert health_bar.hit_points == initial_health - 0.5
        
        # After multiple updates
        for _ in range(39):  # 20 damage / 0.5 decrease per update = 40 updates needed
            health_bar.update()
        assert abs(health_bar.hit_points - parent.hit_points) < 0.5

    def test_death_handling(self, parent):
        """Test health bar behavior on death"""
        health_bar = HealthBar(parent)
        
        # Mock kill method
        health_bar.kill = Mock()
        
        # Simulate death
        parent.hit_points = 0
        
        # Update until health reaches 0
        while health_bar.hit_points > 0:
            health_bar.update()
        
        # Verify kill was called
        health_bar.kill.assert_called_once()

    def test_image_creation(self, parent):
        """Test health bar image creation"""
        with patch('src.Sprites.health_bar.Surface') as mock_surface, \
             patch('src.Sprites.health_bar.draw_rect') as mock_draw:
            
            # Setup mock surface
            mock_surface_instance = Mock()
            mock_surface_instance.fill = Mock()
            mock_surface.return_value = mock_surface_instance
            
            health_bar = HealthBar(parent)
            
            # Get image to trigger creation
            image = health_bar.image
            
            # Verify Surface creation
            mock_surface.assert_called_with((parent.rect.width, Constants.HP_BAR_HEIGHT))
            
            # Verify background fill
            mock_surface_instance.fill.assert_called_with(Constants.INERT)
            
            # Verify health bar drawing
            expected_calls = [
                # Damage bar
                call(mock_surface_instance, Constants.DAMAGE, 
                     Rect(0, 0, int(health_bar.hit_points / health_bar.max * parent.rect.width), 
                          Constants.HP_BAR_HEIGHT)),
                # Health bar
                call(mock_surface_instance, Constants.HP, 
                     Rect(0, 0, int(parent.hit_points / health_bar.max * parent.rect.width), 
                          Constants.HP_BAR_HEIGHT))
            ]
            assert mock_draw.call_args_list == expected_calls

    def test_rect_positioning(self, parent):
        """Test health bar positioning relative to parent"""
        health_bar = HealthBar(parent)
        
        bar_rect = health_bar.rect
        
        # Check dimensions
        assert bar_rect.width == parent.width
        assert bar_rect.height == Constants.HP_BAR_HEIGHT
        
        # Check position (should be centered above parent)
        assert bar_rect.midtop == parent.rect.midbottom
        
        # Test position update when parent moves
        parent.rect.x += 50
        parent.rect.y += 30
        new_rect = health_bar.rect
        assert new_rect.midtop == parent.rect.midbottom

    def test_multiple_damage_instances(self, parent):
        """Test health bar behavior with multiple damage instances"""
        health_bar = HealthBar(parent)
        initial_health = parent.hit_points
        
        # First damage instance
        parent.hit_points -= 20
        for _ in range(40):  # Enough updates to catch up
            health_bar.update()
        
        # Second damage instance before animation completes
        parent.hit_points -= 30
        for _ in range(60):  # Enough updates to catch up
            health_bar.update()
            
        assert abs(health_bar.hit_points - parent.hit_points) < 0.5

    def test_no_health_increase(self, parent):
        """Test that health bar doesn't increase when parent health increases"""
        health_bar = HealthBar(parent)
        initial_health = parent.hit_points
        
        # Decrease health first
        parent.hit_points -= 20
        for _ in range(40):
            health_bar.update()
            
        health_bar_after_damage = health_bar.hit_points
        
        # Try to increase parent health
        parent.hit_points += 10
        health_bar.update()
        
        # Health bar should remain at lower value
        assert health_bar.hit_points == health_bar_after_damage