import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
FPS = 60
CONFIRMATION_TIMEOUT = 10  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)  # New color for moving objects

# Global variables for screen dimensions
WINDOW_WIDTH = DEFAULT_WIDTH
WINDOW_HEIGHT = DEFAULT_HEIGHT

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

def get_scaled_font(size):
    """Get a font scaled based on screen size"""
    base_size = 36
    scale_factor = min(WINDOW_WIDTH / DEFAULT_WIDTH, WINDOW_HEIGHT / DEFAULT_HEIGHT)
    return pygame.font.Font(None, int(size * scale_factor))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = get_scaled_font(36)
        self.is_hovered = False
        # Ensure button is wide enough for text
        text_surface = self.font.render(text, True, BLACK)
        min_width = text_surface.get_width() + 40  # Add padding
        self.rect.width = max(width, min_width)

    def draw(self, surface):
        color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

    def update_position(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = get_scaled_font(36)  # Update font size
        # Ensure button is still wide enough for text
        text_surface = self.font.render(self.text, True, BLACK)
        min_width = text_surface.get_width() + 40  # Add padding
        self.rect.width = max(width, min_width)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.font = get_scaled_font(36)
        self.is_dragging = False
        self.handle_rect = pygame.Rect(x + (initial_val - min_val) * width / (max_val - min_val) - 10,
                                     y - 5, 20, height + 10)

    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Draw handle
        pygame.draw.rect(surface, BLUE, self.handle_rect)
        pygame.draw.rect(surface, BLACK, self.handle_rect, 2)
        
        # Draw text
        new_height = int(self.value * (DEFAULT_HEIGHT / DEFAULT_WIDTH))
        text_surface = self.font.render(f"{self.text}: {int(self.value)}x{new_height}", True, BLACK)
        surface.blit(text_surface, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # Update handle position
            new_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.handle_rect.centerx = new_x
            # Update value
            self.value = self.min_val + (new_x - self.rect.left) * (self.max_val - self.min_val) / self.rect.width

    def update_position(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Update handle position based on current value
        self.handle_rect = pygame.Rect(x + (self.value - self.min_val) * width / (self.max_val - self.min_val) - 10,
                                     y - 5, 20, height + 10)
        self.font = get_scaled_font(36)  # Update font size

class Dialog:
    def __init__(self, x, y, width, height, title, message, confirm_text="Confirm", cancel_text="Cancel"):
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.font = get_scaled_font(36)
        self.small_font = get_scaled_font(24)
        self.start_time = time.time()
        
        # Calculate minimum width based on text
        title_width = self.font.render(title, True, BLACK).get_width()
        message_width = self.font.render(message, True, BLACK).get_width()
        
        # Create temporary buttons to measure their width
        temp_button = Button(0, 0, 100, height // 6, confirm_text, GREEN)
        button_width = temp_button.rect.width
        
        # Calculate total width needed for buttons
        total_buttons_width = button_width * 2 + 20  # 20 pixels spacing between buttons
        min_width = max(title_width, message_width, total_buttons_width) + 80  # Add padding
        
        # Ensure dialog is wide enough
        self.rect = pygame.Rect(x, y, max(width, min_width), height)
        
        # Calculate vertical spacing
        button_height = height // 6
        button_y = y + height - button_height - 20
        
        # Create confirm button
        confirm_button = Button(0, button_y, button_width, button_height, confirm_text, GREEN)
        
        # Create cancel button with same width
        cancel_button = Button(0, button_y, button_width, button_height, cancel_text, RED)
        
        # Center the buttons
        start_x = x + (self.rect.width - total_buttons_width) // 2
        
        confirm_button.rect.x = start_x
        cancel_button.rect.x = start_x + button_width + 20
        
        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
        
        # Calculate vertical positions for text elements with minimum spacing
        self.title_y = y + 20
        self.message_y = y + height // 4
        # Ensure timer is at least 40 pixels above the buttons
        min_timer_y = button_y - 40
        self.timer_y = min(y + 3 * height // 4, min_timer_y)

    def draw(self, surface):
        # Draw dialog background
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Draw title
        title_surface = self.font.render(self.title, True, BLACK)
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.title_y)
        surface.blit(title_surface, title_rect)
        
        # Draw message
        message_surface = self.font.render(self.message, True, BLACK)
        message_rect = message_surface.get_rect(centerx=self.rect.centerx, y=self.message_y)
        surface.blit(message_surface, message_rect)
        
        # Draw time remaining
        time_remaining = max(0, CONFIRMATION_TIMEOUT - (time.time() - self.start_time))
        time_text = f"Reverting in {int(time_remaining)} seconds..."
        time_surface = self.small_font.render(time_text, True, RED)
        time_rect = time_surface.get_rect(centerx=self.rect.centerx, y=self.timer_y)
        surface.blit(time_surface, time_rect)
        
        # Draw buttons
        self.confirm_button.draw(surface)
        self.cancel_button.draw(surface)

    def handle_event(self, event):
        if self.confirm_button.handle_event(event):
            return "confirm"
        elif self.cancel_button.handle_event(event):
            return "cancel"
        return None

    def should_revert(self):
        return time.time() - self.start_time >= CONFIRMATION_TIMEOUT

def create_menu_buttons():
    button_width = int(WINDOW_WIDTH * 0.25)  # 25% of screen width
    button_height = int(WINDOW_HEIGHT * 0.08)  # 8% of screen height
    spacing = int(WINDOW_HEIGHT * 0.03)  # 3% of screen height
    start_y = WINDOW_HEIGHT//2 - (button_height * 3 + spacing * 2)//2
    
    start_button = Button(WINDOW_WIDTH//2 - button_width//2, start_y, 
                         button_width, button_height, "Start Game", GREEN)
    settings_button = Button(WINDOW_WIDTH//2 - button_width//2, start_y + button_height + spacing,
                           button_width, button_height, "Settings", BLUE)
    quit_button = Button(WINDOW_WIDTH//2 - button_width//2, start_y + (button_height + spacing) * 2,
                        button_width, button_height, "Quit", RED)
    
    return start_button, settings_button, quit_button

def create_settings_buttons():
    button_width = int(WINDOW_WIDTH * 0.15)  # 15% of screen width
    button_height = int(WINDOW_HEIGHT * 0.08)  # 8% of screen height
    spacing = int(WINDOW_WIDTH * 0.02)  # 2% of screen width
    bottom_y = WINDOW_HEIGHT - button_height - int(WINDOW_HEIGHT * 0.03)  # 3% from bottom
    
    back_button = Button(WINDOW_WIDTH//2 - button_width - spacing//2, bottom_y,
                        button_width, button_height, "Back", BLUE)
    apply_button = Button(WINDOW_WIDTH//2 + spacing//2, bottom_y,
                         button_width, button_height, "Apply", GREEN)
    
    return back_button, apply_button

def update_ui_for_resolution(resolution_slider):
    global screen, WINDOW_WIDTH, WINDOW_HEIGHT
    
    # Update screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Update menu buttons
    menu_start, menu_settings, menu_quit = create_menu_buttons()
    
    # Update settings buttons
    back_button, apply_button = create_settings_buttons()
    
    # Update resolution slider
    slider_width = int(WINDOW_WIDTH * 0.4)  # 40% of screen width
    slider_height = int(WINDOW_HEIGHT * 0.03)  # 3% of screen height
    resolution_slider.update_position(
        WINDOW_WIDTH//2 - slider_width//2,
        WINDOW_HEIGHT//2 - 50,
        slider_width,
        slider_height
    )
    
    return menu_start, menu_settings, menu_quit, back_button, apply_button, resolution_slider

def create_back_button():
    button_width = int(WINDOW_WIDTH * 0.1)  # 10% of screen width
    button_height = int(WINDOW_HEIGHT * 0.05)  # 5% of screen height
    return Button(20, 20, button_width, button_height, "Back", BLUE)

def draw_road(surface):
    # Road dimensions
    road_height = int(WINDOW_HEIGHT * 0.15)  # 15% of screen height
    road_y = WINDOW_HEIGHT // 2 - road_height // 2
    
    # Draw road
    road_rect = pygame.Rect(0, road_y, WINDOW_WIDTH, road_height)
    pygame.draw.rect(surface, GRAY, road_rect)
    
    # Draw road lines
    line_width = 10
    line_length = 50
    line_spacing = 100
    line_y = road_y + road_height // 2 - line_width // 2
    
    for x in range(0, WINDOW_WIDTH, line_spacing):
        line_rect = pygame.Rect(x, line_y, line_length, line_width)
        pygame.draw.rect(surface, WHITE, line_rect)

class MovingObject:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = PURPLE

    def update(self):
        self.rect.x += self.speed
        # If object goes off screen, reset to start
        if self.rect.right < 0:
            self.rect.left = WINDOW_WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

def create_moving_objects():
    road_height = int(WINDOW_HEIGHT * 0.15)
    road_y = WINDOW_HEIGHT // 2 - road_height // 2
    
    # Create objects with different speeds
    objects = []
    for i in range(3):  # Create 3 objects
        width = int(WINDOW_WIDTH * 0.02)  # 2% of screen width
        height = int(road_height * 0.6)  # 60% of road height
        x = WINDOW_WIDTH + (i * 200)  # Stagger their starting positions
        y = road_y + (road_height - height) // 2
        speed = -2 - (i * 0.5)  # Different speeds for each object
        objects.append(MovingObject(x, y, width, height, speed))
    
    return objects

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    
    # Game states
    START_SCREEN = 0
    MENU_SCREEN = 1
    SETTINGS_SCREEN = 2
    CONFIRMATION_SCREEN = 3
    GAME_SCREEN = 4
    current_state = START_SCREEN
    
    # Create initial buttons
    start_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50, "Start", BLUE)
    
    # Create resolution slider
    slider_width = int(WINDOW_WIDTH * 0.4)
    slider_height = int(WINDOW_HEIGHT * 0.03)
    resolution_slider = Slider(
        WINDOW_WIDTH//2 - slider_width//2,
        WINDOW_HEIGHT//2 - 50,
        slider_width,
        slider_height,
        600, 1920, WINDOW_WIDTH, "Resolution"
    )
    
    # Create other UI elements
    menu_start, menu_settings, menu_quit, back_button, apply_button, resolution_slider = update_ui_for_resolution(resolution_slider)
    
    # Create back button for game screen
    game_back_button = create_back_button()
    
    # Create moving objects
    moving_objects = create_moving_objects()
    
    # Variables for resolution change
    old_width = WINDOW_WIDTH
    old_height = WINDOW_HEIGHT
    confirmation_dialog = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state == START_SCREEN:
                if start_button.handle_event(event):
                    current_state = MENU_SCREEN
            elif current_state == MENU_SCREEN:
                if menu_start.handle_event(event):
                    current_state = GAME_SCREEN
                elif menu_settings.handle_event(event):
                    current_state = SETTINGS_SCREEN
                elif menu_quit.handle_event(event):
                    running = False
            elif current_state == SETTINGS_SCREEN:
                resolution_slider.handle_event(event)
                if back_button.handle_event(event):
                    current_state = MENU_SCREEN
                elif apply_button.handle_event(event):
                    # Store old resolution
                    old_width = WINDOW_WIDTH
                    old_height = WINDOW_HEIGHT
                    
                    # Apply resolution changes
                    new_width = int(resolution_slider.value)
                    new_height = int(new_width * (DEFAULT_HEIGHT / DEFAULT_WIDTH))
                    WINDOW_WIDTH = new_width
                    WINDOW_HEIGHT = new_height
                    
                    # Update all UI elements for new resolution
                    menu_start, menu_settings, menu_quit, back_button, apply_button, resolution_slider = update_ui_for_resolution(resolution_slider)
                    game_back_button = create_back_button()  # Update game back button
                    moving_objects = create_moving_objects()  # Update moving objects
                    
                    # Create confirmation dialog with minimum width
                    dialog_height = int(WINDOW_HEIGHT * 0.3)
                    new_height = int(WINDOW_WIDTH * (DEFAULT_HEIGHT / DEFAULT_WIDTH))
                    confirmation_dialog = Dialog(
                        WINDOW_WIDTH//2 - 250,  # Start with a wider initial width
                        WINDOW_HEIGHT//2 - dialog_height//2,
                        500,  # Initial width, will be adjusted if needed
                        dialog_height,
                        "Confirm Resolution Change",
                        f"Change resolution to {WINDOW_WIDTH}x{new_height}?",
                        "Keep Changes",
                        "Revert"
                    )
                    current_state = CONFIRMATION_SCREEN
            elif current_state == CONFIRMATION_SCREEN:
                result = confirmation_dialog.handle_event(event)
                if result == "confirm":
                    current_state = SETTINGS_SCREEN
                elif result == "cancel":
                    # Revert resolution
                    WINDOW_WIDTH = old_width
                    WINDOW_HEIGHT = old_height
                    menu_start, menu_settings, menu_quit, back_button, apply_button, resolution_slider = update_ui_for_resolution(resolution_slider)
                    game_back_button = create_back_button()  # Update game back button
                    moving_objects = create_moving_objects()  # Update moving objects
                    current_state = SETTINGS_SCREEN
                elif confirmation_dialog.should_revert():
                    # Revert resolution after timeout
                    WINDOW_WIDTH = old_width
                    WINDOW_HEIGHT = old_height
                    menu_start, menu_settings, menu_quit, back_button, apply_button, resolution_slider = update_ui_for_resolution(resolution_slider)
                    game_back_button = create_back_button()  # Update game back button
                    moving_objects = create_moving_objects()  # Update moving objects
                    current_state = SETTINGS_SCREEN
            elif current_state == GAME_SCREEN:
                if game_back_button.handle_event(event):
                    current_state = MENU_SCREEN

        # Draw
        screen.fill(WHITE)
        
        if current_state == START_SCREEN:
            start_button.draw(screen)
        elif current_state == MENU_SCREEN:
            menu_start.draw(screen)
            menu_settings.draw(screen)
            menu_quit.draw(screen)
        elif current_state == SETTINGS_SCREEN:
            resolution_slider.draw(screen)
            back_button.draw(screen)
            apply_button.draw(screen)
        elif current_state == CONFIRMATION_SCREEN:
            confirmation_dialog.draw(screen)
        elif current_state == GAME_SCREEN:
            draw_road(screen)
            # Update and draw moving objects
            for obj in moving_objects:
                obj.update()
                obj.draw(screen)
            game_back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 