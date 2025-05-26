import pygame

class Pet:
    def __init__(self, x, y, width, height, color, owner):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.owner = owner  # This will be the player instance
        self.speed = 3
        self.health = 50
        self.attack_damage = 2
        self.attack_range = 40
        self.attack_cooldown = 120  # e.g., 2 seconds at 60FPS
        self.last_attack_time = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def update(self, platforms, monsters, player): # Added monsters and player parameters
        # --- Follow Logic (from previous subtask) ---
        follow_distance = 50  # How far the pet tries to stay from the player
        dx_to_owner = self.owner.rect.centerx - self.rect.centerx
        dy_to_owner = self.owner.rect.centery - self.rect.centery
        dist_to_owner = (dx_to_owner**2 + dy_to_owner**2)**0.5
        if dist_to_owner == 0:
            dist_to_owner = 0.0001

        if dist_to_owner > follow_distance:
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
                    closest_monster.is_hit = True
                    closest_monster.hit_flash_timer = closest_monster.hit_flash_duration
                    print(f"Pet attacked monster (ID: {id(closest_monster)}). Monster health: {closest_monster.health}")
                    self.last_attack_time = 0

        # (No specific platform collision for attack logic, pet attacks from its current position)
