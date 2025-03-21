import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        self.is_hovered = False

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

def main():
    # Create start button
    start_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50, "Start Game", BLUE)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if start_button.handle_event(event):
                print("Start button clicked!")  # Placeholder for game start logic
                # TODO: Add game start logic here

        # Draw
        screen.fill(WHITE)
        start_button.draw(screen)
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 