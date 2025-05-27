import pygame
import math
import config # Import the config file

class BaseMonster:
    def __init__(self, x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, possible_drops=None, gravity_val=0, screen_height_val=0):
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
        self.hit_flash_duration = config.MONSTER_HIT_FLASH_DURATION  # Use from config
        self.hit_flash_timer = 0
        
        # Item drops
        self.possible_drops = possible_drops if possible_drops is not None else []

        # Attributes to be initialized by subclasses if they use specific movement patterns
        self.gravity = gravity_val
        self.screen_height = screen_height_val
        # self.velocity_y, self.start_x, self.direction, self.patrol_range_x will be set by Grunt

    def draw(self, screen, HIT_COLOR): 
        if self.is_hit and self.hit_flash_timer > 0:
            color_to_draw = HIT_COLOR
            self.hit_flash_timer -= 1
        else:
            color_to_draw = self.original_color
        
        pygame.draw.rect(screen, color_to_draw, self.rect)

        if self.hit_flash_timer <= 0: # Ensure reset after flash
            self.is_hit = False
            # self.color = self.original_color # Not strictly needed if color_to_draw is used

    def attack(self, player):
        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
            if effective_attack_rect.colliderect(player.rect):
                base_damage_dealt = self.attack_damage
                
                # Calculate effective damage after player's total defense
                player_total_defense = player.get_total_defense() # Use total defense
                effective_damage = base_damage_dealt - player_total_defense
                effective_damage = max(1, effective_damage) # Ensure at least 1 damage if attack hits
                
                player.health -= effective_damage
                
                if hasattr(player, 'is_hit'): 
                    player.is_hit = True
                    # Use player's own flash duration from config
                    player.hit_flash_timer = config.PLAYER_HIT_FLASH_DURATION 
                
                # Play sound via player's sound_manager if available
                if hasattr(player, 'sound_manager') and player.sound_manager:
                    player.sound_manager.play_sound("player_hit")
                
                print(f"Monster (ID: {id(self)}, Type: {self.__class__.__name__}) attacked player for {effective_damage} damage (Player total defense: {player_total_defense}). Player health: {player.health}")
                self.last_attack_time = 0

    def update(self, platforms, player):
        if hasattr(self, 'velocity_y') and hasattr(self, 'gravity') and hasattr(self, 'screen_height'):
            self.velocity_y += self.gravity 
            old_rect_for_v_collision = self.rect.copy() 
            self.rect.y += self.velocity_y

            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity_y > 0 and old_rect_for_v_collision.bottom <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
            
            if self.rect.bottom >= self.screen_height: 
                self.rect.bottom = self.screen_height
                self.velocity_y = 0
        else:
            old_rect_for_v_collision = self.rect.copy()

        if hasattr(self, 'direction') and hasattr(self, 'start_x') and hasattr(self, 'patrol_range_x'):
            self.rect.x += self.speed * self.direction

            if self.direction == 1 and self.rect.right >= self.start_x + self.patrol_range_x:
                self.direction = -1
                self.rect.right = self.start_x + self.patrol_range_x 
            elif self.direction == -1 and self.rect.left <= self.start_x - self.patrol_range_x:
                self.direction = 1
                self.rect.left = self.start_x - self.patrol_range_x
                
            for platform in platforms:
                if self.rect.colliderect(platform.rect): 
                    if not (old_rect_for_v_collision.bottom <= platform.rect.top or \
                            old_rect_for_v_collision.top >= platform.rect.bottom):
                        if self.direction == 1: 
                            self.rect.right = platform.rect.left
                            self.direction = -1 
                        elif self.direction == -1: 
                            self.rect.left = platform.rect.right
                            self.direction = 1 
        
        self.attack(player)


class Grunt(BaseMonster):
    def __init__(self, x, y, width=config.DEFAULT_GRUNT_STATS["width"], height=config.DEFAULT_GRUNT_STATS["height"], 
                 color=config.DEFAULT_GRUNT_STATS["color"], 
                 health=config.DEFAULT_GRUNT_STATS["health"], 
                 attack_damage=config.DEFAULT_GRUNT_STATS["attack_damage"], 
                 attack_range=config.DEFAULT_GRUNT_STATS["attack_range"], 
                 attack_cooldown=config.DEFAULT_GRUNT_STATS["attack_cooldown"], 
                 speed=config.DEFAULT_GRUNT_STATS["speed"], 
                 patrol_range_x=config.DEFAULT_GRUNT_STATS["patrol_range_x"], 
                 gravity_val=0, screen_height_val=0, possible_drops=None): 
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, possible_drops, gravity_val, screen_height_val)
        self.patrol_range_x = patrol_range_x
        self.start_x = x 
        self.direction = 1
        self.velocity_y = 0
    

class Flyer(BaseMonster):
    def __init__(self, x, y, width=config.DEFAULT_FLYER_STATS["width"], height=config.DEFAULT_FLYER_STATS["height"], 
                 color=config.DEFAULT_FLYER_STATS["color"], 
                 health=config.DEFAULT_FLYER_STATS["health"], 
                 attack_damage=config.DEFAULT_FLYER_STATS["attack_damage"], 
                 attack_range=config.DEFAULT_FLYER_STATS["attack_range"], 
                 attack_cooldown=config.DEFAULT_FLYER_STATS["attack_cooldown"], 
                 speed=config.DEFAULT_FLYER_STATS["speed"], 
                 vertical_amplitude=config.DEFAULT_FLYER_STATS["vertical_amplitude"], 
                 vertical_speed_factor=config.DEFAULT_FLYER_STATS["vertical_speed_factor"], 
                 patrol_range_x=config.DEFAULT_FLYER_STATS["patrol_range_x"], 
                 possible_drops=None):
        super().__init__(x, y, width, height, color, health, attack_damage, attack_range, attack_cooldown, speed, possible_drops)
        self.initial_y = y
        self.vertical_amplitude = vertical_amplitude
        self.vertical_speed_factor = vertical_speed_factor 
        self.direction = 1 
        self.start_x = x   
        self.patrol_range_x = patrol_range_x 

    def update(self, platforms, player, monsters_list=None): # monsters_list is not used here, consider removing if not planned
        self.rect.x += self.speed * self.direction
        if self.direction == 1 and self.rect.right >= self.start_x + self.patrol_range_x:
            self.direction = -1
            self.rect.right = self.start_x + self.patrol_range_x
        elif self.direction == -1 and self.rect.left <= self.start_x - self.patrol_range_x:
            self.direction = 1
            self.rect.left = self.start_x - self.patrol_range_x
        
        time_ticks = pygame.time.get_ticks()
        self.rect.y = self.initial_y + math.sin(time_ticks * self.vertical_speed_factor / 1000.0) * self.vertical_amplitude

        self.attack(player)
