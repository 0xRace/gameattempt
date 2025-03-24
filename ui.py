import pygame
from abc import ABC, abstractmethod
from config import GameConfig
from resources import ResourceManager

class UIElement(ABC):
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.config = GameConfig()
        self.resources = ResourceManager()
        self.is_hovered = False

    @abstractmethod
    def draw(self, surface):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        return False

class Button(UIElement):
    def __init__(self, x, y, width, height, text, color, resource_manager):
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.resource_manager = resource_manager
        self.font = resource_manager.get_scaled_font(36)
        self.ensure_min_width()

    def ensure_min_width(self):
        text_width = self.font.size(self.text)[0]
        if self.rect.width < text_width + 40:
            self.rect.width = text_width + 40

    def draw(self, surface):
        color = self.resource_manager.get_color('LIGHT_GRAY') if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.resource_manager.get_color('BLACK'), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.resource_manager.get_color('BLACK'))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False

class Slider(UIElement):
    def __init__(self, x, y, width, height, min_value, max_value, current_value, label, resource_manager):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = current_value
        self.label = label
        self.resource_manager = resource_manager
        self.font = resource_manager.get_scaled_font(24)
        self.handle_rect = pygame.Rect(0, 0, 20, height)
        self.update_handle_position()
        self.is_dragging = False

    def update_handle_position(self):
        value_range = self.max_value - self.min_value
        value_position = (self.value - self.min_value) / value_range
        handle_x = self.rect.x + int(self.rect.width * value_position) - 10
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y

    def draw(self, surface):
        # Draw track
        pygame.draw.rect(surface, self.resource_manager.get_color('GRAY'), self.rect)
        pygame.draw.rect(surface, self.resource_manager.get_color('BLACK'), self.rect, 2)
        
        # Draw handle
        pygame.draw.rect(surface, self.resource_manager.get_color('BLUE'), self.handle_rect)
        pygame.draw.rect(surface, self.resource_manager.get_color('BLACK'), self.handle_rect, 2)
        
        # Draw label and value
        label_surface = self.font.render(f"{self.label}: {int(self.value)}", True, self.resource_manager.get_color('BLACK'))
        surface.blit(label_surface, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.is_dragging = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            return False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # Update value based on handle position
            handle_x = max(self.rect.x, min(event.pos[0], self.rect.right))
            value_range = self.max_value - self.min_value
            position_ratio = (handle_x - self.rect.x) / self.rect.width
            self.value = self.min_value + (value_range * position_ratio)
            self.update_handle_position()
            return True
        
        return False

class Dialog(UIElement):
    def __init__(self, x, y, width, height, title, message, confirm_text, cancel_text, resource_manager):
        super().__init__(x, y, width, height)
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.resource_manager = resource_manager
        self.title_font = resource_manager.get_scaled_font(32)
        self.message_font = resource_manager.get_scaled_font(24)
        self.button_font = resource_manager.get_scaled_font(24)
        
        # Create buttons
        button_width = 120
        button_height = 40
        button_y = y + height - button_height - 20
        
        self.confirm_button = Button(
            x + width//2 - button_width - 10,
            button_y,
            button_width,
            button_height,
            confirm_text,
            'GREEN',
            resource_manager
        )
        
        self.cancel_button = Button(
            x + width//2 + 10,
            button_y,
            button_width,
            button_height,
            cancel_text,
            'RED',
            resource_manager
        )
        
        self.start_time = pygame.time.get_ticks()
        self.revert_time = 5000  # 5 seconds

    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, self.resource_manager.get_color('WHITE'), self.rect)
        pygame.draw.rect(surface, self.resource_manager.get_color('BLACK'), self.rect, 2)
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, self.resource_manager.get_color('BLACK'))
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 20)
        surface.blit(title_surface, title_rect)
        
        # Draw message
        message_surface = self.message_font.render(self.message, True, self.resource_manager.get_color('BLACK'))
        message_rect = message_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 80)
        surface.blit(message_surface, message_rect)
        
        # Draw buttons
        self.confirm_button.draw(surface)
        self.cancel_button.draw(surface)

    def handle_event(self, event):
        if self.confirm_button.handle_event(event):
            return "confirm"
        if self.cancel_button.handle_event(event):
            return "cancel"
        return None

    def should_revert(self):
        return pygame.time.get_ticks() - self.start_time > self.revert_time

class HealthBar(UIElement):
    def __init__(self, x, y, width, height, resource_manager):
        super().__init__(x, y, width, height)
        self.resource_manager = resource_manager
        self.font = resource_manager.get_scaled_font(24)
        self.health = 100

    def set_health(self, health):
        self.health = max(0, min(100, health))

    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, self.resource_manager.get_color('DARK_RED'), self.rect)
        
        # Draw health
        health_width = int(self.rect.width * (self.health / 100))
        health_rect = pygame.Rect(self.rect.x, self.rect.y, health_width, self.rect.height)
        pygame.draw.rect(surface, self.resource_manager.get_color('RED'), health_rect)
        
        # Draw border
        pygame.draw.rect(surface, self.resource_manager.get_color('BLACK'), self.rect, 2)
        
        # Draw text
        text = f"Health: {self.health}"
        text_surface = self.font.render(text, True, self.resource_manager.get_color('WHITE'))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect) 