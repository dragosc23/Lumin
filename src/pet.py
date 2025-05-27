import pygame
import config # Import the config file

class Pet:
    def __init__(self, x, y, width, height, color, owner, sound_manager=None): # Added sound_manager
        self.rect = pygame.Rect(x, y, width, height) # Width and height from Player for now
        self.owner = owner
        self.sound_manager = sound_manager # Store the sound manager

        # Stats from config
        self.speed = config.PET_SPEED
        self.health = config.PET_HEALTH
        self.attack_damage = config.PET_ATTACK_DAMAGE
        self.attack_range = config.PET_ATTACK_RANGE
        self.attack_cooldown = config.PET_ATTACK_COOLDOWN
        self.follow_distance = config.PET_FOLLOW_DISTANCE

        self.last_attack_time = 0
        
        # For hit flash effect
        self.original_color = color # Color passed from Player (ideally config.PET_COLOR)
        self.color = color # Current color
        self.is_hit = False
        self.hit_flash_duration = config.PET_HIT_FLASH_DURATION
        self.hit_flash_timer = 0

    def draw(self, surface): # Renamed screen to surface for consistency
        current_color = self.original_color 
        if self.is_hit and self.hit_flash_timer > 0:
            current_color = config.HIT_COLOR 
            self.hit_flash_timer -= 1
        elif self.is_hit and self.hit_flash_timer <= 0: # Check if is_hit was true and timer just ran out
            self.is_hit = False # Reset is_hit state
            # self.color = self.original_color # No longer needed as current_color handles it

        pygame.draw.rect(surface, current_color, self.rect)

    def update(self, platforms, monsters, player): 
        # --- Follow Logic ---
        # Using self.follow_distance now
        dx_to_owner = self.owner.rect.centerx - self.rect.centerx
        dy_to_owner = self.owner.rect.centery - self.rect.centery
        dist_to_owner = (dx_to_owner**2 + dy_to_owner**2)**0.5
        if dist_to_owner == 0: # Avoid division by zero if pet is exactly on owner
            dist_to_owner = 0.0001 

        if dist_to_owner > self.follow_distance:
            norm_dx = dx_to_owner / dist_to_owner
            norm_dy = dy_to_owner / dist_to_owner
            old_rect = self.rect.copy()
            self.rect.x += norm_dx * self.speed
            self.rect.y += norm_dy * self.speed
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.rect = old_rect
                    break
        
        # --- Attack Logic ---
        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown and monsters: # Check if monsters list is not empty
            closest_monster = None
            min_dist_sq = float('inf')

            for monster in monsters:
                dist_sq = (self.rect.centerx - monster.rect.centerx)**2 + \
                          (self.rect.centery - monster.rect.centery)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_monster = monster
            
            if closest_monster and min_dist_sq < self.attack_range**2:
                # Check if the monster is also close to the player
                dist_to_player_sq = (closest_monster.rect.centerx - player.rect.centerx)**2 + \
                                    (closest_monster.rect.centery - player.rect.centery)**2
                player_engagement_range = player.attack_range * 1.5 
                
                if dist_to_player_sq < player_engagement_range**2:
                    closest_monster.health -= self.attack_damage
                    # Trigger monster's hit flash
                    closest_monster.is_hit = True # Monster's take_damage will handle this and its own hit sound
                    closest_monster.hit_flash_timer = closest_monster.hit_flash_duration # Monster handles its own flash
                    # Call monster's take_damage method, which also plays SOUND_MONSTER_HIT
                    closest_monster.take_damage(self.attack_damage) 
                    
                    if self.sound_manager:
                        self.sound_manager.play_sound(config.SOUND_PET_ATTACK)
                    
                    print(f"Pet attacked monster (ID: {id(closest_monster)}). Monster health: {closest_monster.health}")
                    self.last_attack_time = 0
                    # Monster death sound (SOUND_MONSTER_DEATH) is handled by GameplayScreen

        # (No specific platform collision for attack logic, pet attacks from its current position)
