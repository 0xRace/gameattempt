import pygame
import os
from config import GameConfig

class ResourceManager:
    def __init__(self):
        self.config = GameConfig()
        self.fonts = {}
        self.colors = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'YELLOW': (255, 255, 0),
            'GRAY': (128, 128, 128),
            'DARK_GRAY': (64, 64, 64),
            'LIGHT_GRAY': (192, 192, 192),
            'DARK_RED': (128, 0, 0),
            'GOLD': (255, 215, 0),
            'YELLOW_GREEN': (154, 205, 50)
        }

    def get_font(self, size):
        """Get a font of the specified size, creating it if it doesn't exist."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

    def get_scaled_font(self, base_size, scale_factor=1.0):
        """Get a font scaled based on screen size."""
        size = int(base_size * scale_factor)
        return self.get_font(size)

    def get_color(self, name):
        """Get a color by name."""
        return self.colors.get(name, self.colors['WHITE'])

    def create_button(self, x, y, width, height, text, color_name='BLUE'):
        """Create a button with the specified properties."""
        from ui import Button
        return Button(x, y, width, height, text, self.get_color(color_name), self)

    def create_slider(self, x, y, width, height, min_value, max_value, current_value, label):
        """Create a slider with the specified properties."""
        from ui import Slider
        return Slider(x, y, width, height, min_value, max_value, current_value, label, self)

    def create_dialog(self, x, y, width, height, title, message, confirm_text, cancel_text):
        """Create a dialog with the specified properties."""
        from ui import Dialog
        return Dialog(x, y, width, height, title, message, confirm_text, cancel_text, self)

    def get_road_dimensions(self, screen_width, screen_height):
        """Get the road dimensions based on screen size."""
        road_height = int(screen_height * 0.15)
        road_y = screen_height // 2 - road_height // 2  # Center vertically
        return road_y, road_height

    def get_shop_dimensions(self, screen_width, screen_height):
        """Get the shop dimensions based on screen size."""
        shop_height = int(screen_height * 0.15)
        shop_y = screen_height - shop_height  # Position at bottom
        return shop_y, shop_height

    def get_tower_size(self, screen_width, screen_height):
        """Get the tower size based on screen size."""
        return int(min(screen_width, screen_height) * 0.05)

    def get_health_bar_dimensions(self, screen_width, screen_height):
        """Get the health bar dimensions based on screen size."""
        width = int(screen_width * self.config.health_bar_width_percentage)
        height = int(screen_height * self.config.health_bar_height_percentage)
        x = (screen_width - width) // 2
        y = 20
        return x, y, width, height 