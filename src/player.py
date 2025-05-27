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
        # Stats and properties from config (or defaults if config not used yet)
        self.speed = 5 # To be config.PLAYER_SPEED
        self.velocity_y = 0
        self.is_jumping = False
        # This will become config.PLAYER_MAX_HEALTH in the next step
        self.health = config.PLAYER_MAX_HEALTH # Updated to use config for now, assuming it's available
        self.attack_range = 75 # To be config.PLAYER_ATTACK_RANGE
        self.attack_damage = 10 # To be config.PLAYER_ATTACK_DAMAGE
        self.attack_cooldown = 60 # To be config.PLAYER_ATTACK_COOLDOWN
        self.last_attack_time = 0
        
        self.inventory = InventoryManager(capacity=config.PLAYER_INVENTORY_CAPACITY)
        
        self.original_color = self.color 
        self.is_hit = False
        self.hit_flash_duration = 10 # To be config.PLAYER_HIT_FLASH_DURATION
        self.hit_flash_timer = 0

        self.is_attacking = False
        self.attack_visual_duration = 7 # To be config.PLAYER_ATTACK_VISUAL_DURATION
        self.attack_visual_timer = 0
        self.direction = 1 

        self.sound_manager = sound_manager

        # Pet instantiation will also use config values for its dimensions/color
        # The color (0,0,255) and dimensions (20,20) are placeholders.
        # Player.__init__ is already passing sound_manager to Pet in main.py's version.
        # When config is fully integrated into this class, these will be config.PET_WIDTH etc.
        self.pet = Pet(self.rect.x - 50, self.rect.y, 20, 20, (0,0,255) , self, self.sound_manager)


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

        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            attack_occurred = False
            for monster in monsters:
                effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
                if effective_attack_rect.colliderect(monster.rect):
                    monster.health -= self.attack_damage
                    monster.is_hit = True
                    
                    if hasattr(monster, 'hit_flash_duration'): 
                         monster.hit_flash_timer = monster.hit_flash_duration
                    else: 
                         monster.hit_flash_timer = 10 # Fallback


                    if self.sound_manager:
                        self.sound_manager.play_sound("monster_hit")
                    print(f"Player attacked monster (ID: {id(monster)}). Monster health: {monster.health}")
                    
                    if monster.health <= 0:
                        if self.sound_manager:
                            self.sound_manager.play_sound("monster_die")
                        # Item creation and adding logic is now moved to GameplayScreen.update
                        print(f"Monster (ID: {id(monster)}) defeated by player.") 
                        
                    self.last_attack_time = 0
                    attack_occurred = True 
                    break 
            
            if attack_occurred: 
                if self.sound_manager:
                    self.sound_manager.play_sound("player_attack")
                self.is_attacking = True
                self.attack_visual_timer = self.attack_visual_duration
        
        if self.is_attacking:
            self.attack_visual_timer -= 1
            if self.attack_visual_timer <= 0:
                self.is_attacking = False
