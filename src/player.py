import pygame
import config 
from src.pet import Pet 
from src.inventory_manager import InventoryManager # Import InventoryManager
from src.items import Item # Import Item for creating item instances
# Placeholder constants previously here have been removed.

# Player class and related logic.
# This class will be updated in subsequent steps to use 'config.CONSTANT_NAME'
# Placeholder constants previously here have been removed.

# Player class and related logic.
# This class will be updated in subsequent steps to use 'config.CONSTANT_NAME'
# for all constants currently hardcoded or previously accessed as globals.

class Player:
    def __init__(self, x, y, width, height, color, sound_manager=None): # Added sound_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        # Stats and properties from config
        self.speed = config.PLAYER_SPEED
        self.velocity_y = 0
        self.is_jumping = False
        self.max_health = config.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.attack_range = config.PLAYER_ATTACK_RANGE
        self.attack_damage = config.PLAYER_ATTACK_DAMAGE
        self.attack_cooldown = config.PLAYER_ATTACK_COOLDOWN
        self.last_attack_time = 0 # Tracks time since last successful attack

        # XP and Leveling attributes
        self.level = 1
        self.experience_points = 0
        self.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.level
        
        self.inventory = InventoryManager(capacity=config.PLAYER_INVENTORY_CAPACITY)
        
        self.original_color = self.color
        self.is_hit = False
        self.hit_flash_duration = config.PLAYER_HIT_FLASH_DURATION
        self.hit_flash_timer = 0

        self.is_attacking = False # To show attack visual
        self.attack_visual_duration = config.PLAYER_ATTACK_VISUAL_DURATION
        self.attack_visual_timer = 0
        self.direction = 1 # 1 for right, -1 for left

        self.sound_manager = sound_manager

        # Pet instantiation using config values
        pet_x_offset = config.PET_FOLLOW_DISTANCE + 10 # Initial offset from player
        self.pet = Pet(
            self.rect.x - pet_x_offset, 
            self.rect.y, 
            config.PET_WIDTH, 
            config.PET_HEIGHT, 
            config.PET_COLOR, 
            self, 
            self.sound_manager
        )


    def draw(self, screen):
        current_player_color = self.original_color
        if self.is_hit and self.hit_flash_timer > 0:
            # This will become config.HIT_COLOR in the next step
            current_player_color = config.HIT_COLOR 
            self.hit_flash_timer -= 1
        elif self.is_hit and self.hit_flash_timer <= 0:
            self.is_hit = False
        
        pygame.draw.rect(screen, current_player_color, self.rect)


        if self.is_attacking:
            attack_rect_width = 30
            attack_rect_height = self.rect.height * 0.8
            attack_rect_y = self.rect.centery - attack_rect_height / 2
            if self.direction == 1: 
                attack_rect_x = self.rect.right
            else: 
                attack_rect_x = self.rect.left - attack_rect_width
            attack_visual_rect = pygame.Rect(attack_rect_x, attack_rect_y, attack_rect_width, attack_rect_height)
            # This will become config.ATTACK_VISUAL_COLOR in the next step
            pygame.draw.rect(screen, config.ATTACK_VISUAL_COLOR, attack_visual_rect) 


    def move(self, dx, dy, platforms):
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1

        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0: 
                    self.rect.right = platform.rect.left
                elif dx < 0: 
                    self.rect.left = platform.rect.right
        
        old_rect_bottom = self.rect.bottom 
        old_rect_top = self.rect.top       
        self.rect.y += dy                  
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dy > 0:  
                    if old_rect_bottom <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                elif dy < 0:  
                    if old_rect_top >= platform.rect.bottom:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0 

        if self.rect.left < 0:
            self.rect.left = 0
        # These will become config.SCREEN_WIDTH in the next step
        if self.rect.right > config.SCREEN_WIDTH: 
            self.rect.right = config.SCREEN_WIDTH 
        
        if self.rect.top < 0:
            self.rect.top = 0
            if dy < 0: 
                 self.velocity_y = 0


    def update(self, platforms, monsters): 
        # This will become config.GRAVITY in the next step
        self.velocity_y += config.GRAVITY 
        if self.velocity_y > 15: 
            self.velocity_y = 15
        
        self.move(0, self.velocity_y, platforms)

        # This will become config.SCREEN_HEIGHT in the next step
        if self.rect.bottom >= config.SCREEN_HEIGHT: 
            self.rect.bottom = config.SCREEN_HEIGHT 
            self.velocity_y = 0
            self.is_jumping = False

        self.velocity_y += config.GRAVITY
        if self.velocity_y > 15: # Max fall speed
            self.velocity_y = 15
        
        self.move(0, self.velocity_y, platforms)

        if self.rect.bottom >= config.SCREEN_HEIGHT:
            self.rect.bottom = config.SCREEN_HEIGHT
            self.velocity_y = 0
            self.is_jumping = False

        # Attack cooldown logic - increments regardless of attacking
        if self.last_attack_time < self.attack_cooldown:
            self.last_attack_time += 1

        # Attack visual timer
        if self.is_attacking:
            self.attack_visual_timer -= 1
            if self.attack_visual_timer <= 0:
                self.is_attacking = False
                
    # This method is intended to be called when an attack input is received (e.g., space bar)
    # The actual call will be managed by GameplayScreen based on input events.
    def attempt_attack(self, monsters):
        if self.last_attack_time >= self.attack_cooldown:
            attack_occurred_this_attempt = False
            # Determine attack hitbox based on direction
            attack_hitbox_width = self.attack_range 
            attack_hitbox_height = self.rect.height 
            
            if self.direction == 1: # Facing right
                attack_hitbox_x = self.rect.right
            else: # Facing left
                attack_hitbox_x = self.rect.left - attack_hitbox_width
            
            attack_hitbox_y = self.rect.y
            
            # This is a simplified hitbox; for more accuracy, it could be centered better
            # or be a shape other than a rectangle (e.g., arc).
            # For now, a rect extending from the player's facing side.
            attack_rect = pygame.Rect(attack_hitbox_x, attack_hitbox_y, attack_hitbox_width, attack_hitbox_height)

            for monster in monsters:
                if monster.rect.colliderect(attack_rect):
                    monster.take_damage(self.attack_damage) # Monster handles its own hit flash
                    if self.sound_manager:
                        self.sound_manager.play_sound(config.SOUND_MONSTER_HIT) # Use config for sound key
                    print(f"Player attacked monster (ID: {id(monster)}). Monster health: {monster.health}")
                    
                    if monster.health <= 0:
                        # GameplayScreen will handle monster death (XP, drops)
                        pass # Monster death is detected and handled in GameplayScreen.update_monsters
                        
                    attack_occurred_this_attempt = True
                    # Typically, an attack might hit multiple monsters if they overlap the hitbox.
                    # For simplicity, let's assume one attack action hits all valid targets in range
                    # rather than breaking after the first. If only one monster should be hit, use break.
            
            if attack_occurred_this_attempt:
                if self.sound_manager:
                    self.sound_manager.play_sound(config.SOUND_PLAYER_ATTACK) # Use config for sound key
                self.is_attacking = True # Trigger visual
                self.attack_visual_timer = self.attack_visual_duration
                self.last_attack_time = 0 # Reset cooldown
                return True # Attack was performed
        return False # Attack on cooldown or no targets hit (though cooldown is main check)


    def gain_xp(self, amount):
        self.experience_points += amount
        print(f"Player gained {amount} XP. Total XP: {self.experience_points}/{self.xp_to_next_level}")
        self.check_for_level_up()

    def check_for_level_up(self):
        while self.experience_points >= self.xp_to_next_level:
            self.level += 1
            # Carry over excess XP: subtract the cost of the level just completed
            self.experience_points -= self.xp_to_next_level 
            
            # Update xp_to_next_level for the NEW level
            self.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.level 
            
            # Apply level-up benefits
            self.max_health += config.HEALTH_GAIN_PER_LEVEL
            self.health = self.max_health # Heal to new max health
            
            if self.sound_manager:
                self.sound_manager.play_sound(config.SOUND_LEVEL_UP) # Use config for sound key
            print(f"Player reached Level {self.level}! Max health increased to {self.max_health}. XP for next level: {self.xp_to_next_level}.")
            # If experience_points is still >= new xp_to_next_level, the loop continues
            
    def calculate_xp_for_next_level(self):
        """Calculates XP needed for the current level to advance to the next."""
        return config.XP_PER_LEVEL_BASE * self.level

    def take_damage(self, amount):
        self.health -= amount
        self.is_hit = True
        self.hit_flash_timer = self.hit_flash_duration # Use PLAYER_HIT_FLASH_DURATION from config
        if self.sound_manager:
            self.sound_manager.play_sound(config.SOUND_PLAYER_HIT) # Use config for sound key
        
        if self.health <= 0:
            self.health = 0
            print("Player has been defeated.")
            # Game over logic will be handled by GameplayScreen or Game class
        else:
            print(f"Player took {amount} damage. Health: {self.health}/{self.max_health}")
