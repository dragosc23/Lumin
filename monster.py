import pygame
import math

class BaseMonster:
    def __init__(self, x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, gravity_val=0, screen_height_val=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.health = health
        self.attack_damage = attack_damage
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.speed = speed
        self.last_attack_time = 0
        self.original_color = color # Store original color
        
        # For hit flash effect
        self.is_hit = False
        self.hit_flash_duration = 10  # frames
        self.hit_flash_timer = 0
        
        # Attributes to be initialized by subclasses if they use specific movement patterns
        self.gravity = gravity_val
        self.screen_height = screen_height_val
        # self.velocity_y, self.start_x, self.direction, self.patrol_range_x will be set by Grunt

    def draw(self, screen, HIT_COLOR): # Pass HIT_COLOR as argument as planned
        if self.is_hit and self.hit_flash_timer > 0:
            # self.color is temporarily changed for the flash
            # This means original_color must be reliably stored and self.color reset
            # The __init__ already sets self.original_color = color, so self.color is the one to modify
            color_to_draw = HIT_COLOR
            self.hit_flash_timer -= 1
        else:
            color_to_draw = self.original_color
        
        pygame.draw.rect(screen, color_to_draw, self.rect)

        if self.hit_flash_timer <= 0:
            self.is_hit = False
            self.color = self.original_color # Ensure self.color is reset to its original state
                                         # This is important if the flash logic changed self.color directly,
                                         # which it doesn't with color_to_draw.
                                         # However, to match subtask "self.color = self.original_color"
                                         # this line ensures it, even if redundant with current color_to_draw.
                                         # If the above `color_to_draw = HIT_COLOR` was `self.color = HIT_COLOR`, this is crucial.
                                         # Let's follow the subtask's direct implication for self.color reset.
                                         # The subtask's draw logic is:
                                         # If hit: current_color = HIT_COLOR
                                         # Else: current_color = self.original_color
                                         # Draw(current_color)
                                         # If timer <=0: self.is_hit = False; self.color = self.original_color
                                         # This implies current_color is local to draw, and self.color should be reset.
                                         # My `color_to_draw` local variable aligns with this.
                                         # The final `self.color = self.original_color` is a safeguard.

    def attack(self, player):
        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
            if effective_attack_rect.colliderect(player.rect):
                player.health -= self.attack_damage
                # Trigger player's hit flash
                if hasattr(player, 'is_hit'): # Check if player has these attributes
                    player.is_hit = True
                    player.hit_flash_timer = player.hit_flash_duration
                print(f"Monster (ID: {id(self)}, Type: {self.__class__.__name__}) attacked player. Player health: {player.health}")
                self.last_attack_time = 0

    def update(self, platforms, player):
        # This update method is intended for ground-based monsters like Grunt
        # It assumes self.velocity_y, self.gravity, self.screen_height, 
        # self.start_x, self.direction, self.patrol_range_x are initialized by the subclass.

        # --- Vertical Movement and Collision (Gravity) ---
        if hasattr(self, 'velocity_y') and hasattr(self, 'gravity') and hasattr(self, 'screen_height'):
            self.velocity_y += self.gravity 
            old_rect_for_v_collision = self.rect.copy() # Use a distinct name for clarity
            self.rect.y += self.velocity_y

            # Vertical Collision with Platforms
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity_y > 0 and old_rect_for_v_collision.bottom <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
            
            # Ground Collision (fallback)
            if self.rect.bottom >= self.screen_height: 
                self.rect.bottom = self.screen_height
                self.velocity_y = 0
        else:
            # This monster type might not use gravity (e.g., a basic Flyer without vertical platform interaction)
            old_rect_for_v_collision = self.rect.copy() # Still needed for horizontal collision check

        # --- Horizontal Movement and Collision (Patrolling) ---
        if hasattr(self, 'direction') and hasattr(self, 'start_x') and hasattr(self, 'patrol_range_x'):
            self.rect.x += self.speed * self.direction

            # Patrol Boundary Check
            if self.direction == 1 and self.rect.right >= self.start_x + self.patrol_range_x:
                self.direction = -1
                self.rect.right = self.start_x + self.patrol_range_x 
            elif self.direction == -1 and self.rect.left <= self.start_x - self.patrol_range_x:
                self.direction = 1
                self.rect.left = self.start_x - self.patrol_range_x
                
            # Horizontal Collision with Platforms
            for platform in platforms:
                if self.rect.colliderect(platform.rect): 
                    # Check if it's a true horizontal collision, not a step-up/down.
                    # This requires comparing with the state *before* any y-movement in this frame.
                    # old_rect_for_v_collision helps here if no y-movement has occurred for this monster type.
                    # A more robust way would be to separate X and Y movement and collision checks.
                    # For now, this simplified check attempts to avoid false positives.
                    if not (old_rect_for_v_collision.bottom <= platform.rect.top or \
                            old_rect_for_v_collision.top >= platform.rect.bottom):
                        if self.direction == 1: 
                            self.rect.right = platform.rect.left
                            self.direction = -1 
                        elif self.direction == -1: 
                            self.rect.left = platform.rect.right
                            self.direction = 1 
        
        # --- Monster Attack ---
        self.attack(player)


class Grunt(BaseMonster):
    def __init__(self, x, y, width, height, color, 
                 health=120, attack_damage=8, attack_range=60, attack_cooldown=90, speed=2, 
                 patrol_range_x=50, gravity_val=0, screen_height_val=0): # Added defaults and patrol_range_x default
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, gravity_val, screen_height_val)
        self.patrol_range_x = patrol_range_x
        self.start_x = x # Initial left edge for patrol calculations
        self.direction = 1
        self.velocity_y = 0
    
    # Grunt uses the BaseMonster's update method which handles gravity, patrolling, and platform collision.


class Flyer(BaseMonster):
    def __init__(self, x, y, width, height, color, 
                 health=60, attack_damage=6, attack_range=50, attack_cooldown=100, speed=2.5, 
                 vertical_amplitude=30, vertical_speed_factor=0.005, patrol_range_x=50): # Added defaults
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed)
        # Flyer does not use gravity or screen_height from BaseMonster by default
        self.initial_y = y
        self.vertical_amplitude = vertical_amplitude
        self.vertical_speed_factor = vertical_speed_factor # e.g., 0.01
        self.direction = 1 # For horizontal patrol
        self.start_x = x   # Initial left edge for patrol
        self.patrol_range_x = patrol_range_x # Patrol range for flyer

    def update(self, platforms, player, monsters_list=None): # monsters_list for API consistency
        # --- Horizontal Patrol ---
        self.rect.x += self.speed * self.direction
        if self.direction == 1 and self.rect.right >= self.start_x + self.patrol_range_x:
            self.direction = -1
            self.rect.right = self.start_x + self.patrol_range_x
        elif self.direction == -1 and self.rect.left <= self.start_x - self.patrol_range_x:
            self.direction = 1
            self.rect.left = self.start_x - self.patrol_range_x
        
        # --- Vertical Bobbing ---
        # pygame.time.get_ticks() returns milliseconds, factor might need adjustment
        time_ticks = pygame.time.get_ticks()
        self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor / 1000.0) * self.vertical_amplitude # Adjusted factor for smoother bobbing

        # --- Attack ---
        self.attack(player)

        # Note: Basic Flyer does not interact with platforms in this example.
        # If platform collision is needed for Flyer, it would require more complex logic here.
