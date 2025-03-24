import pygame
import sys
from config import GameConfig
from resources import ResourceManager
from world import GameWorld
from ui import Button, Slider, Dialog

class Game:
    def __init__(self):
        pygame.init()
        self.config = GameConfig()
        self.resources = ResourceManager()
        
        # Set up the display
        self.screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))
        pygame.display.set_caption(self.config.window_title)
        self.clock = pygame.time.Clock()
        
        # Create game world
        self.world = GameWorld()
        
        # Create UI elements
        self.create_ui_elements()
        
        # Game state
        self.current_state = "START"
        self.running = True

    def create_ui_elements(self):
        # Create start button
        self.start_button = self.resources.create_button(
            self.config.window_width//2 - 100,
            self.config.window_height//2 - 25,
            200, 50, "Start", "BLUE"
        )
        
        # Create menu buttons
        self.menu_start = self.resources.create_button(
            self.config.window_width//2 - int(self.config.window_width * 0.125),
            self.config.window_height//2 - 100,
            int(self.config.window_width * 0.25),
            int(self.config.window_height * 0.08),
            "Start Game", "GREEN"
        )
        self.menu_settings = self.resources.create_button(
            self.config.window_width//2 - int(self.config.window_width * 0.125),
            self.config.window_height//2,
            int(self.config.window_width * 0.25),
            int(self.config.window_height * 0.08),
            "Settings", "BLUE"
        )
        self.menu_quit = self.resources.create_button(
            self.config.window_width//2 - int(self.config.window_width * 0.125),
            self.config.window_height//2 + 100,
            int(self.config.window_width * 0.25),
            int(self.config.window_height * 0.08),
            "Quit", "RED"
        )
        
        # Create settings buttons
        self.settings_back = self.resources.create_button(
            self.config.window_width//2 - int(self.config.window_width * 0.15),
            self.config.window_height - int(self.config.window_height * 0.1),
            int(self.config.window_width * 0.15),
            int(self.config.window_height * 0.08),
            "Back", "BLUE"
        )
        self.settings_apply = self.resources.create_button(
            self.config.window_width//2 + int(self.config.window_width * 0.01),
            self.config.window_height - int(self.config.window_height * 0.1),
            int(self.config.window_width * 0.15),
            int(self.config.window_height * 0.08),
            "Apply", "GREEN"
        )
        
        # Create resolution slider
        self.resolution_slider = self.resources.create_slider(
            self.config.window_width//2 - int(self.config.window_width * 0.2),
            self.config.window_height//2 - 50,
            int(self.config.window_width * 0.4),
            int(self.config.window_height * 0.03),
            600, 1920, self.config.window_width, "Resolution"
        )
        
        # Create game back button
        self.game_back = self.resources.create_button(
            20, 20,
            int(self.config.window_width * 0.1),
            int(self.config.window_height * 0.05),
            "Back", "BLUE"
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.current_state == "START":
                if self.start_button.handle_event(event):
                    self.current_state = "MENU"
            
            elif self.current_state == "MENU":
                if self.menu_start.handle_event(event):
                    self.current_state = "GAME"
                    self.world = GameWorld()  # Reset game world
                elif self.menu_settings.handle_event(event):
                    self.current_state = "SETTINGS"
                elif self.menu_quit.handle_event(event):
                    self.running = False
            
            elif self.current_state == "SETTINGS":
                self.resolution_slider.handle_event(event)
                if self.settings_back.handle_event(event):
                    self.current_state = "MENU"
                elif self.settings_apply.handle_event(event):
                    self.handle_resolution_change()
            
            elif self.current_state == "GAME":
                if self.game_back.handle_event(event):
                    self.current_state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.world.handle_mouse_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.world.handle_mouse_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.world.handle_mouse_motion(event)
            
            elif self.current_state == "CONFIRMATION":
                result = self.confirmation_dialog.handle_event(event)
                if result == "confirm":
                    self.current_state = "SETTINGS"
                elif result == "cancel" or self.confirmation_dialog.should_revert():
                    # Revert resolution
                    self.config.set('window', 'width', self.old_width)
                    self.config.set('window', 'height', self.old_height)
                    self.screen = pygame.display.set_mode((self.old_width, self.old_height))
                    self.create_ui_elements()  # Recreate UI elements with old resolution
                    self.current_state = "SETTINGS"

    def handle_resolution_change(self):
        new_width = int(self.resolution_slider.value)
        new_height = int(new_width * (self.config.window_height / self.config.window_width))
        
        # Store old resolution
        old_width = self.config.window_width
        old_height = self.config.window_height
        
        # Update config
        self.config.set('window', 'width', new_width)
        self.config.set('window', 'height', new_height)
        
        # Update display
        self.screen = pygame.display.set_mode((new_width, new_height))
        
        # Create confirmation dialog
        dialog_height = int(new_height * 0.3)
        self.confirmation_dialog = self.resources.create_dialog(
            new_width//2 - 250,
            new_height//2 - dialog_height//2,
            500,
            dialog_height,
            "Confirm Resolution Change",
            f"Change resolution to {new_width}x{new_height}?",
            "Keep Changes",
            "Revert"
        )
        
        self.current_state = "CONFIRMATION"
        
        # Store old resolution for potential revert
        self.old_width = old_width
        self.old_height = old_height

    def update(self):
        if self.current_state == "GAME":
            if self.world.update():
                self.current_state = "MENU"

    def draw(self):
        self.screen.fill(self.resources.get_color('WHITE'))
        
        if self.current_state == "START":
            self.start_button.draw(self.screen)
        
        elif self.current_state == "MENU":
            self.menu_start.draw(self.screen)
            self.menu_settings.draw(self.screen)
            self.menu_quit.draw(self.screen)
        
        elif self.current_state == "SETTINGS":
            self.resolution_slider.draw(self.screen)
            self.settings_back.draw(self.screen)
            self.settings_apply.draw(self.screen)
        
        elif self.current_state == "GAME":
            self.world.draw(self.screen)
            self.game_back.draw(self.screen)
        
        elif self.current_state == "CONFIRMATION":
            self.confirmation_dialog.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.fps)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 