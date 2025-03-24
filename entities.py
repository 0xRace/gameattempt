import pygame
import math
from abc import ABC, abstractmethod
from config import GameConfig
from resources import ResourceManager

class Entity(ABC):
    def __init__(self, resource_manager):
        self.config = GameConfig()
        self.resources = resource_manager

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass

class MovingObject(Entity):
    def __init__(self, speed, resource_manager):
        super().__init__(resource_manager)
        self.speed = speed
        self.position = 0
        self.has_passed = False
        self.size = int(self.config.window_height * 0.02)
        self.color = self.resources.get_color('RED')

    def update(self):
        self.position += self.speed
        
        # Check if object has passed
        if not self.has_passed and self.position >= self.config.window_width:
            self.has_passed = True
            return True
        
        return False

    def draw(self, surface):
        road_y, road_height = self.resources.get_road_dimensions(
            self.config.window_width,
            self.config.window_height
        )
        
        # Draw object
        x = int(self.position)
        y = road_y + (road_height - self.size) // 2
        rect = pygame.Rect(x, y, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)

class Projectile(Entity):
    def __init__(self, x, y, target_x, target_y, resource_manager, speed=10):
        super().__init__(resource_manager)
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.size = 5
        self.color = self.resources.get_color('YELLOW_GREEN')
        self.update_trajectory()

    def update_trajectory(self):
        # Calculate direction vector
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize and scale by speed
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = 0

    def update(self):
        # Update position with exact trajectory
        self.x += self.dx
        self.y += self.dy
        
        # Check if projectile has reached or passed target
        if (self.dx > 0 and self.x >= self.target_x) or \
           (self.dx < 0 and self.x <= self.target_x):
            return True
            
        # Check if projectile is off screen
        if (self.x < 0 or self.x > self.config.window_width or
            self.y < 0 or self.y > self.config.window_height):
            return True
            
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

    def check_hit(self, target):
        # Calculate distance between projectile center and target center
        distance = math.sqrt(
            (self.x - target.position) ** 2 +
            (self.y - (self.config.window_height // 2)) ** 2
        )
        
        # Consider both projectile and target size for hit detection
        # Projectile is considered to hit if at least half of it touches the target
        hit_threshold = (self.size + target.size) / 2
        return distance < hit_threshold

class Tower(Entity):
    def __init__(self, x, y, resource_manager):
        super().__init__(resource_manager)
        self.size = self.resources.get_tower_size(
            self.config.window_width,
            self.config.window_height
        )
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.color = self.resources.get_color('BLUE')
        self.selected = False
        self.projectiles = []
        self.last_shot_time = 0
        self.shoot_cooldown = 1000  # 1 second
        self.range = 300  # Shooting range

    def update(self, moving_objects):
        current_time = pygame.time.get_ticks()
        
        # Find nearest target within range
        nearest_target = None
        min_distance = float('inf')
        
        for obj in moving_objects:
            # Calculate distance to target
            dx = obj.position - self.rect.centerx
            dy = self.config.window_height // 2 - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.range and distance < min_distance:
                min_distance = distance
                nearest_target = obj
        
        # Shoot at target if cooldown is over
        if nearest_target and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.shoot(nearest_target)
            self.last_shot_time = current_time
        
        # Update projectiles and check for hits
        for projectile in self.projectiles[:]:
            if projectile.update():
                self.projectiles.remove(projectile)
            elif nearest_target and projectile.check_hit(nearest_target):
                moving_objects.remove(nearest_target)
                self.projectiles.remove(projectile)

    def shoot(self, target):
        # Calculate exact target position
        target_x = target.position
        target_y = self.config.window_height // 2  # Road center
        
        # Create projectile with exact target position
        projectile = Projectile(
            self.rect.centerx,
            self.rect.centery,
            target_x,
            target_y,
            self.resources,
            speed=10  # Increased speed for better accuracy
        )
        self.projectiles.append(projectile)

    def draw(self, surface):
        # Draw tower
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.resources.get_color('BLACK'), self.rect, 2)
        
        # Draw selection highlight if selected
        if self.selected:
            highlight_rect = self.rect.inflate(4, 4)
            pygame.draw.rect(surface, self.resources.get_color('GOLD'), highlight_rect, 2)
            
            # Draw range circle
            pygame.draw.circle(surface, self.resources.get_color('BLUE'), 
                             self.rect.center, self.range, 1)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

    def start_drag(self, mouse_pos):
        self.is_dragging = True
        self.drag_offset = (self.rect.x - mouse_pos[0], self.rect.y - mouse_pos[1])

    def stop_drag(self):
        self.is_dragging = False

    def update_drag(self, mouse_pos):
        if self.is_dragging:
            self.rect.x = mouse_pos[0] + self.drag_offset[0]
            self.rect.y = mouse_pos[1] + self.drag_offset[1] 