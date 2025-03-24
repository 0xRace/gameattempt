import pygame
import random
from config import GameConfig
from resources import ResourceManager
from entities import MovingObject, Tower, Projectile
from ui import HealthBar

class GameWorld:
    def __init__(self):
        self.config = GameConfig()
        self.resources = ResourceManager()
        
        # Initialize game state
        self.health = self.config.starting_health
        self.balance = self.config.starting_balance
        self.towers = []
        self.moving_objects = []
        self.selected_tower = None
        self.is_dragging = False
        self.last_spawn_time = pygame.time.get_ticks()
        
        # Initialize UI elements
        self.initialize_ui()
        
        # Create initial moving objects
        self.create_moving_objects()

    def initialize_ui(self):
        # Create health bar
        x, y, width, height = self.resources.get_health_bar_dimensions(
            self.config.window_width,
            self.config.window_height
        )
        self.health_bar = HealthBar(x, y, width, height, self.resources)

    def create_moving_objects(self):
        # Create moving objects with varying speeds
        for _ in range(5):
            speed = random.uniform(
                self.config.object_speed * 0.8,
                self.config.object_speed * 1.2
            )
            self.moving_objects.append(MovingObject(speed, self.resources))

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Spawn new moving objects
        if current_time - self.last_spawn_time >= self.config.object_spawn_rate:
            self.create_moving_objects()
            self.last_spawn_time = current_time
        
        # Update moving objects
        for obj in self.moving_objects[:]:
            if obj.update():
                self.health -= 1
                self.health_bar.set_health(self.health)
                if self.health <= 0:
                    return True  # Game over
            if obj.position >= self.config.window_width:
                self.moving_objects.remove(obj)
        
        # Update towers and their projectiles
        for tower in self.towers:
            tower.update(self.moving_objects)
        
        return False  # Game not over

    def draw(self, surface):
        # Draw road first (background)
        self.draw_road(surface)
        
        # Draw moving objects
        for obj in self.moving_objects:
            obj.draw(surface)
        
        # Draw towers and their projectiles
        for tower in self.towers:
            tower.draw(surface)
        
        # Draw selected tower preview if dragging
        if self.selected_tower:
            self.selected_tower.draw(surface)
        
        # Draw shop last (foreground)
        self.draw_shop(surface)
        
        # Draw balance
        self.draw_balance(surface)
        
        # Draw health bar
        self.health_bar.draw(surface)

    def draw_road(self, surface):
        road_y, road_height = self.resources.get_road_dimensions(
            self.config.window_width,
            self.config.window_height
        )
        
        # Draw road background
        road_rect = pygame.Rect(0, road_y, self.config.window_width, road_height)
        pygame.draw.rect(surface, self.resources.get_color('DARK_GRAY'), road_rect)
        
        # Draw road lines
        line_spacing = 50
        line_width = 10
        line_height = road_height // 2
        
        for x in range(0, self.config.window_width, line_spacing):
            line_rect = pygame.Rect(x, road_y + (road_height - line_height) // 2,
                                  line_width, line_height)
            pygame.draw.rect(surface, self.resources.get_color('WHITE'), line_rect)

    def draw_shop(self, surface):
        shop_y, shop_height = self.resources.get_shop_dimensions(
            self.config.window_width,
            self.config.window_height
        )
        
        # Draw shop background
        shop_rect = pygame.Rect(0, shop_y, self.config.window_width, shop_height)
        pygame.draw.rect(surface, self.resources.get_color('GRAY'), shop_rect)
        
        # Draw tower preview
        tower_size = self.resources.get_tower_size(
            self.config.window_width,
            self.config.window_height
        )
        preview_rect = pygame.Rect(20, shop_y + (shop_height - tower_size) // 2,
                                 tower_size, tower_size)
        pygame.draw.rect(surface, self.resources.get_color('BLUE'), preview_rect)
        pygame.draw.rect(surface, self.resources.get_color('BLACK'), preview_rect, 2)
        
        # Draw tower cost
        cost_text = f"Cost: ${self.config.tower_cost}"
        font = self.resources.get_scaled_font(24)
        text_surface = font.render(cost_text, True, self.resources.get_color('BLACK'))
        text_rect = text_surface.get_rect(midleft=(preview_rect.right + 20, preview_rect.centery))
        surface.blit(text_surface, text_rect)

    def draw_balance(self, surface):
        font = self.resources.get_scaled_font(24)
        text = f"Balance: {self.balance}"
        text_surface = font.render(text, True, self.resources.get_color('BLACK'))
        surface.blit(text_surface, (self.config.window_width - 150, 20))

    def handle_mouse_down(self, event):
        if event.button == 1:  # Left click
            # Check if clicking in shop area
            shop_y, shop_height = self.resources.get_shop_dimensions(
                self.config.window_width,
                self.config.window_height
            )
            if shop_y <= event.pos[1] <= shop_y + shop_height:
                # Check if clicking on tower preview
                tower_size = self.resources.get_tower_size(
                    self.config.window_width,
                    self.config.window_height
                )
                preview_rect = pygame.Rect(20, shop_y + (shop_height - tower_size) // 2,
                                         tower_size, tower_size)
                if preview_rect.collidepoint(event.pos):
                    if self.balance >= self.config.tower_cost:
                        # Create tower at current mouse position
                        self.selected_tower = Tower(event.pos[0], event.pos[1], self.resources)
                        self.is_dragging = True
                        return
            
            # Check if clicking on existing towers
            for tower in self.towers:
                if tower.rect.collidepoint(event.pos):
                    tower.selected = not tower.selected
                    return

    def is_valid_tower_placement(self, pos):
        """Check if a tower can be placed at the given position."""
        road_y, road_height = self.resources.get_road_dimensions(
            self.config.window_width,
            self.config.window_height
        )
        
        # Check if position is NOT on the road
        if road_y <= pos[1] <= road_y + road_height:
            return False
            
        # Check if position is within screen bounds
        tower_size = self.resources.get_tower_size(
            self.config.window_width,
            self.config.window_height
        )
        if not (tower_size//2 <= pos[0] <= self.config.window_width - tower_size//2):
            return False
            
        # Check for overlap with existing towers
        for tower in self.towers:
            if abs(tower.rect.centerx - pos[0]) < tower_size and \
               abs(tower.rect.centery - pos[1]) < tower_size:
                return False
                
        return True

    def handle_mouse_up(self, event):
        if event.button == 1 and self.is_dragging and self.selected_tower:
            # Check if tower placement is valid
            if self.is_valid_tower_placement(event.pos):
                # Place tower
                self.selected_tower.rect.center = event.pos
                self.towers.append(self.selected_tower)
                # Deduct the cost from balance
                self.balance -= self.config.tower_cost
            else:
                # Invalid placement, don't place the tower
                self.selected_tower = None
            
            self.is_dragging = False

    def handle_mouse_motion(self, event):
        if self.is_dragging and self.selected_tower:
            # Update tower position
            self.selected_tower.rect.center = event.pos
            
            # Change color based on valid placement
            if self.is_valid_tower_placement(event.pos):
                self.selected_tower.color = self.resources.get_color('BLUE')
            else:
                self.selected_tower.color = self.resources.get_color('RED')

    def is_game_over(self):
        return self.health <= 0 