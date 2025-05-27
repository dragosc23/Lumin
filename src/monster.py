import pygame
import math
import config # Import the config file

class BaseMonster:
    def __init__(self, x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, sound_manager=None, possible_drops=None, gravity_val=0, screen_height_val=0): # Added sound_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.health = health
        self.sound_manager = sound_manager # Store sound_manager
        self.attack_damage = attack_damage
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.speed = speed
        self.last_attack_time = 0
        self.original_color = color # Store original color
        
        # For hit flash effect
        self.is_hit = False
        self.hit_flash_duration = config.MONSTER_HIT_FLASH_DURATION  # Use from config
        self.hit_flash_timer = 0
        
        # Item drops
        self.possible_drops = possible_drops if possible_drops is not None else []

        # Attributes to be initialized by subclasses if they use specific movement patterns
        self.gravity = gravity_val
        self.screen_height = screen_height_val
        # self.velocity_y, self.start_x, self.direction, self.patrol_range_x will be set by Grunt

    def draw(self, screen): # Removed HIT_COLOR from parameters
        color_to_draw = self.original_color
        if self.is_hit and self.hit_flash_timer > 0:
            color_to_draw = config.HIT_COLOR # Use config.HIT_COLOR directly
            self.hit_flash_timer -= 1
        elif self.is_hit and self.hit_flash_timer <= 0: # Check if is_hit was true and timer just ran out
            self.is_hit = False
            # self.color = self.original_color # Reset to original color - not needed due to color_to_draw logic
        
        pygame.draw.rect(screen, color_to_draw, self.rect)

    def take_damage(self, amount):
        """Reduces monster's health and triggers hit flash."""
        self.health -= amount
        self.is_hit = True
        self.hit_flash_timer = self.hit_flash_duration # Uses MONSTER_HIT_FLASH_DURATION from config
        
        if self.sound_manager:
            self.sound_manager.play_sound(config.SOUND_MONSTER_HIT)

        print(f"Monster (ID: {id(self)}, Type: {self.__class__.__name__}) took {amount} damage. Health: {self.health}")
        if self.health <= 0:
            self.health = 0
            print(f"Monster (ID: {id(self)}, Type: {self.__class__.__name__}) defeated.")
            # Death handling (XP, drops) will be managed by GameplayScreen

    def attack(self, player):
        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
            if effective_attack_rect.colliderect(player.rect):
                # Player's take_damage method handles its own hit flash and sound.
                # So, no need to play player_hit sound here.
                player.take_damage(self.attack_damage) 
                
                # Potentially play a monster-specific attack sound here if desired in the future
                # if self.sound_manager:
                #     self.sound_manager.play_sound(config.SOUND_MONSTER_ATTACK_SOUND_KEY) # Needs new const
                
                print(f"Monster (ID: {id(self)}, Type: {self.__class__.__name__}) attacked player. Player health: {player.health}")
                self.last_attack_time = 0

    def update(self, platforms, player):
        # Common update logic (like attack call) can remain here, or be called by subclasses.
        # For now, specific movement patterns are in subclasses.
        # self.attack(player) # Moved to subclass updates to allow specific attack conditions/timing
        pass # BaseMonster update can be expanded if there's more shared logic beyond drawing/taking damage.


class Grunt(BaseMonster):
    def __init__(self, x, y, width, height, color, 
                 health, attack_damage, attack_range, attack_cooldown, speed, 
                 patrol_range_x, gravity_val, screen_height_val, sound_manager=None, possible_drops=None): # Added sound_manager
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, sound_manager, possible_drops, gravity_val, screen_height_val) # Pass sound_manager
        self.patrol_range_x = patrol_range_x
        self.start_x = x 
        self.direction = 1 # 1 for right, -1 for left
        self.velocity_y = 0
    
    def update(self, platforms, player): # Added player argument back
        # Gravity and vertical collision
        self.velocity_y += self.gravity
        old_rect_for_v_collision = self.rect.copy()
        self.rect.y += self.velocity_y

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0 and old_rect_for_v_collision.bottom <= platform.rect.top: # Landing on top
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                elif self.velocity_y < 0 and old_rect_for_v_collision.top >= platform.rect.bottom: # Hitting bottom of platform
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0 # Stop upward movement

        if self.rect.bottom >= self.screen_height: # Ground collision
            self.rect.bottom = self.screen_height
            self.velocity_y = 0

        # Horizontal movement and patrol logic
        old_rect_for_h_collision = self.rect.copy()
        self.rect.x += self.speed * self.direction

        # Patrol boundaries
        if self.direction == 1 and self.rect.right > self.start_x + self.patrol_range_x:
            self.direction = -1
            self.rect.right = self.start_x + self.patrol_range_x
        elif self.direction == -1 and self.rect.left < self.start_x - self.patrol_range_x:
            self.direction = 1
            self.rect.left = self.start_x - self.patrol_range_x
            
        # Horizontal collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Check if it's a side collision (and not just landing/hitting head)
                if not (old_rect_for_h_collision.bottom <= platform.rect.top or \
                        old_rect_for_h_collision.top >= platform.rect.bottom):
                    if self.direction == 1: # Moving right, hit left side of platform
                        self.rect.right = platform.rect.left
                        self.direction = -1 # Turn around
                    elif self.direction == -1: # Moving left, hit right side of platform
                        self.rect.left = platform.rect.right
                        self.direction = 1 # Turn around
        
        super().attack(player) # Call BaseMonster's attack logic


class Flyer(BaseMonster):
    def __init__(self, x, y, width, height, color, 
                 health, attack_damage, attack_range, attack_cooldown, speed, 
                 vertical_amplitude, vertical_speed_factor, patrol_range_x, y_offset, sound_manager=None, possible_drops=None): # Added sound_manager, y_offset
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, sound_manager, possible_drops) # Pass sound_manager
        # y_offset is used by GameplayScreen to place the flyer initially.
        # The Flyer's own initial_y for its sine wave movement should be its starting y.
        self.initial_y = y 
        self.vertical_amplitude = vertical_amplitude
        self.vertical_speed_factor = vertical_speed_factor 
        self.direction = 1 # 1 for right, -1 for left
        self.start_x = x   
        self.patrol_range_x = patrol_range_x 

    def update(self, platforms, player, monsters_list=None): # monsters_list not used by Flyer
        # Horizontal patrol
        self.rect.x += self.speed * self.direction
        if self.direction == 1 and self.rect.right >= self.start_x + self.patrol_range_x:
            self.direction = -1
            self.rect.right = self.start_x + self.patrol_range_x # Snap to boundary
        elif self.direction == -1 and self.rect.left <= self.start_x - self.patrol_range_x:
            self.direction = 1
            self.rect.left = self.start_x - self.patrol_range_x # Snap to boundary
        
        # Vertical sine wave movement
        time_ticks = pygame.time.get_ticks() # Get current time in milliseconds
        # Ensure vertical_speed_factor is scaled appropriately if it's small,
        # or adjust the divisor (1000.0) if the factor is already scaled.
        # For example, if vertical_speed_factor is 0.005, then time_ticks * 0.005 / 1000.0 might be too slow.
        # Let's assume vertical_speed_factor is something like 1 or 2 for reasonable speed.
        # If it's meant to be a small multiplier, the division by 1000.0 might be too much.
        # Re-evaluating: config.DEFAULT_FLYER_STATS sets "vertical_speed_factor": 0.01.
        # This value likely needs to be used without further division by 1000 if it's pre-scaled for sin function.
        # Or, if it's a frequency, it needs to be multiplied by time.
        # Typical use: math.sin(frequency * time_ticks * 0.001) to convert ms to s for frequency in Hz.
        # If vertical_speed_factor is the frequency:
        self.rect.y = self.initial_y + math.sin(self.vertical_speed_factor * time_ticks * 0.001) * self.vertical_amplitude
        # If vertical_speed_factor is just a time multiplier for the existing formula:
        # self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor / 1000.0) * self.vertical_amplitude
        # Given the value 0.01, it might be a direct multiplier for time_ticks for a slow oscillation.
        # Let's try this: self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor) * self.vertical_amplitude
        # This makes more sense if vertical_speed_factor = 0.01 is intended to make a slow wave.
        # Original: self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor / 1000.0) * self.vertical_amplitude
        # This implies vertical_speed_factor is a small adjustment to a per-second cycle.
        # Let's stick to the original interpretation from the code for now.
        self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor) * self.vertical_amplitude


        super().attack(player) # Call BaseMonster's attack logic
