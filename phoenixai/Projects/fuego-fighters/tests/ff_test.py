import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Initialize pygame for testing without display
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

# Now we can import our project modules
from constants import Constants, Layer
from src.Sprites.plane import Plane
from src.Sprites.health_bar import HealthBar
from src.Sprites.bullet import Bullet
import ff

class MockSurface:
    def __init__(self, *args, **kwargs):
        self.rect = pygame.Rect(0, 0, 64, 64)
    def convert_alpha(self):
        return self
    def convert(self):
        return self
    def get_rect(self):
        return self.rect
    def subsurface(self, rect):
        return self
    def get_width(self):
        return self.rect.width
    def get_height(self):
        return self.rect.height
    def set_colorkey(self, color, flags=0):
        pass
    def get_at(self, pos):
        return (0, 0, 0, 255)
    def blit(self, source, dest, area=None):
        pass

@pytest.fixture(autouse=True)
def setup_pygame():
    with patch('pygame.display.set_mode') as mock_set_mode, \
         patch('pygame.display.get_surface') as mock_get_surface:
        mock_surface = MockSurface()
        mock_set_mode.return_value = mock_surface
        mock_get_surface.return_value = mock_surface
        pygame.display.set_mode(Constants.WINDOW_SIZE)
        yield

@pytest.fixture
def mock_sprite_loading():
    with patch('pygame.image.load') as mock_load:
        mock_surface = MockSurface()
        mock_load.return_value = mock_surface
        yield mock_surface

@pytest.fixture
def mock_surface():
    with patch('pygame.Surface', MockSurface):
        yield

@pytest.fixture
def mock_mask():
    with patch('pygame.mask.from_surface') as mock_mask_func:
        mock_mask_func.return_value = Mock()
        yield mock_mask_func

@pytest.fixture
def mock_player(mock_sprite_loading, mock_surface, mock_mask, setup_pygame):
    """Create a player plane for testing"""
    player = Plane(Constants.SPRITE_PLAYER_PLANE, 5, 4, 100, 30, respect_borders=False)
    # Explicitly set the speed and verify it's set
    player.speed_h = 5
    player.speed_v = 5
    # Set initial position
    player.rect.x = 50
    player.rect.y = 50
    # Verify the properties are set correctly
    assert player.speed_h == 5, "Horizontal speed not set correctly"
    assert player.speed_v == 5, "Vertical speed not set correctly"
    assert not player.respect_borders, "respect_borders should be False"
    return player

class TestGame:
    def test_create_player_plane(self, mock_sprite_loading, mock_surface, mock_mask):
        renderables = pygame.sprite.LayeredUpdates()
        with patch('pygame.display.get_surface') as mock_get_surface:
            mock_display_surface = MockSurface()
            mock_get_surface.return_value = mock_display_surface
            player_plane = ff.create_player_plane(renderables)
            assert isinstance(player_plane, Plane)
            assert player_plane.rect.y == pygame.display.get_surface().get_height() - 100
            assert len(renderables.sprites()) > 0
            health_bars = [sprite for sprite in renderables.sprites() if isinstance(sprite, HealthBar)]
            assert len(health_bars) == 1

    def test_draw_text(self):
        mock_screen = Mock()
        test_text = "game_over,restart"
        with patch.object(Constants, 'get_available_text') as mock_get_text:
            mock_get_text.return_value = {
                'game_over': {'text': Mock(), 'pos': (0, 0)},
                'restart': {'text': Mock(), 'pos': (0, 0)}
            }
            ff.draw_text(mock_screen, test_text)
            assert mock_screen.blit.call_count == 2

    def test_player_movement(self, mock_player):
        # Mock the display surface for boundary checks
        screen_height = 600  # Example screen height
        screen_width = 800  # Example screen width

        with patch('pygame.display.get_surface') as mock_get_surface:
            mock_surface = Mock()
            mock_surface.get_width.return_value = screen_width
            mock_surface.get_height.return_value = screen_height
            mock_get_surface.return_value = mock_surface

            # Test each movement method individually
            # Right movement
            mock_player.rect.x = 50
            mock_player.rect.y = 50
            mock_player.move_right()
            assert mock_player.rect.x == 55, "Right movement failed"
            assert mock_player.rect.y == 50, "Y should not change for right movement"

            # Left movement
            mock_player.rect.x = 50
            mock_player.rect.y = 50
            mock_player.move_left()
            assert mock_player.rect.x == 45, "Left movement failed"
            assert mock_player.rect.y == 50, "Y should not change for left movement"

            # Up movement
            mock_player.rect.x = 50
            mock_player.rect.y = 50
            mock_player.move_up()
            assert mock_player.rect.x == 50, "X should not change for up movement"
            assert mock_player.rect.y == 45, "Up movement failed"

            # Down movement
            mock_player.rect.x = 50
            mock_player.rect.y = 50
            print(f"\nBefore move_down: ({mock_player.rect.x}, {mock_player.rect.y})")
            print(f"Speed_v: {mock_player.speed_v}")
            print(f"Screen height: {screen_height}")
            print(f"respect_borders: {mock_player.respect_borders}")
            mock_player.move_down()
            print(f"After move_down: ({mock_player.rect.x}, {mock_player.rect.y})")
            assert mock_player.rect.x == 50, "X should not change for down movement"
            assert mock_player.rect.y == 55, "Down movement failed"

    def test_player_movement_without_borders(self, mock_player):
        screen_height = 600
        screen_width = 800

        with patch('pygame.display.get_surface') as mock_get_surface:
            mock_surface = Mock()
            mock_surface.get_width.return_value = screen_width
            mock_surface.get_height.return_value = screen_height
            mock_get_surface.return_value = mock_surface

            # Test all movements from center position
            movements = [
                ('move_right', (50, 50), (55, 50)),
                ('move_left', (50, 50), (45, 50)),
                ('move_up', (50, 50), (50, 45)),
                ('move_down', (50, 50), (50, 55))
            ]

            for method_name, start_pos, expected_pos in movements:
                # Reset position
                mock_player.rect.x, mock_player.rect.y = start_pos
                # Call movement method
                method = getattr(mock_player, method_name)
                method()
                # Assert new position
                actual_pos = (mock_player.rect.x, mock_player.rect.y)
                assert actual_pos == expected_pos, (
                    f"{method_name} failed. "
                    f"Expected {expected_pos}, got {actual_pos}"
                )

    def test_player_movement_with_borders(self, mock_player):
        # Set respect_borders to True for this test
        mock_player.respect_borders = True
        screen_height = 100  # Small screen to test boundaries
        screen_width = 100

        with patch('pygame.display.get_surface') as mock_get_surface:
            mock_surface = Mock()
            mock_surface.get_width.return_value = screen_width
            mock_surface.get_height.return_value = screen_height
            mock_get_surface.return_value = mock_surface

            # Test boundary behaviors
            tests = [
                ('move_right', (95, 50), (100 - mock_player.rect.width, 50)),
                ('move_left', (2, 50), (0, 50)),
                ('move_up', (50, 2), (50, 0)),
                ('move_down', (50, 95), (50, 100 - mock_player.rect.height))
            ]

            for method_name, start_pos, expected_pos in tests:
                # Reset position
                mock_player.rect.x, mock_player.rect.y = start_pos
                # Call movement method
                method = getattr(mock_player, method_name)
                method()
                # Assert new position
                actual_pos = (mock_player.rect.x, mock_player.rect.y)
                assert actual_pos == expected_pos, (
                    f"{method_name} boundary check failed. "
                    f"Expected {expected_pos}, got {actual_pos}"
                )
