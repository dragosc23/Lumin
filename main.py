import pygame

from pet import Pet # Import the Pet class

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize font module

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "My Pygame"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0) # For Flyers
HIT_COLOR = (255, 100, 100) # For damage flash
ATTACK_VISUAL_COLOR = (200, 200, 0) # Yellowish for player attack

# Game constants
GRAVITY = 1
JUMP_STRENGTH = -20
PLAYER_START_X = 50
PLAYER_START_Y = SCREEN_HEIGHT - 70 # Assuming player height is around 50
PLAYER_MAX_HEALTH = 200

# Import monster classes
from monster import BaseMonster, Grunt, Flyer

LEVEL_CONFIGS = [
    {
        "monsters": [{"type": "Grunt", "count": 1, "patrol_range": 50}],
        "message": "Level 1: A Grunt!"
    },
    {
        "monsters": [{"type": "Grunt", "count": 2, "patrol_range": 50}],
        "message": "Level 2: Two Grunts!"
    },
    {
        "monsters": [{"type": "Flyer", "count": 1, "vertical_amplitude": 30, "vertical_speed_factor": 0.005, "patrol_range": 70}], # Adjusted speed factor
        "message": "Level 3: A Flyer appears!"
    },
    {
        "monsters": [
            {"type": "Grunt", "count": 1, "patrol_range": 50},
            {"type": "Flyer", "count": 1, "vertical_amplitude": 30, "vertical_speed_factor": 0.005, "patrol_range": 70}
        ],
        "message": "Level 4: Mixed company!"
    }
]
current_level_index = 0

# UI Fonts
UI_FONT = pygame.font.SysFont("arial", 24)
GAME_OVER_FONT = pygame.font.SysFont("arial", 72)


# Helper function to draw text
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect # Optional: return rect for positioning or interaction

# Player class
class Player:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5
        self.velocity_y = 0
        self.is_jumping = False
        self.health = PLAYER_MAX_HEALTH # Use constant
        self.attack_range = 75
        self.attack_damage = 10
        self.attack_cooldown = 60 # Frames (1 attack per second at 60FPS)
        self.last_attack_time = 0
        self.inventory = [] # Player inventory
        
        # Damage flash attributes for Player
        self.original_color = self.color 
        self.is_hit = False
        self.hit_flash_duration = 10
        self.hit_flash_timer = 0

        # Attack visual attributes for Player
        self.is_attacking = False
        self.attack_visual_duration = 7 # frames
        self.attack_visual_timer = 0
        self.direction = 1 # 1 for right, -1 for left

        # Create the pet instance, positioning it relative to the player
        # Pet color is BLUE (0,0,255)
        self.pet = Pet(self.rect.x - 50, self.rect.y, 20, 20, (0, 0, 255), self)


    def draw(self, screen):
        # Player damage flash
        current_player_color = self.original_color
        if self.is_hit and self.hit_flash_timer > 0:
            current_player_color = HIT_COLOR
            self.hit_flash_timer -= 1
        else: # Reset if timer is done (or wasn't hit)
            self.is_hit = False 
        
        if self.hit_flash_timer <= 0: # Additional check as per subtask
            self.is_hit = False
            self.color = self.original_color # Ensure player's self.color is reset

        pygame.draw.rect(screen, current_player_color, self.rect)

        # Player attack visual
        if self.is_attacking:
            attack_rect_width = 30
            attack_rect_height = self.rect.height * 0.8
            attack_rect_y = self.rect.centery - attack_rect_height / 2
            if self.direction == 1: # Facing right
                attack_rect_x = self.rect.right
            else: # Facing left
                attack_rect_x = self.rect.left - attack_rect_width
            attack_visual_rect = pygame.Rect(attack_rect_x, attack_rect_y, attack_rect_width, attack_rect_height)
            pygame.draw.rect(screen, ATTACK_VISUAL_COLOR, attack_visual_rect)


    def move(self, dx, dy, platforms):
        # Update player direction based on horizontal movement
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1

        # Move horizontally
        self.rect.x += dx
        # Check for horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif dx < 0:  # Moving left
                    self.rect.left = platform.rect.right
        
        # Move vertically
        old_rect_bottom = self.rect.bottom # Player's bottom before this vertical move
        old_rect_top = self.rect.top       # Player's top before this vertical move
        self.rect.y += dy                  # Apply vertical movement (dy is self.velocity_y from update)
        
        # Check for vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dy > 0:  # Player is moving down (dy is positive velocity_y)
                    # Check if player was above or at the platform's top before this move
                    if old_rect_bottom <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                elif dy < 0:  # Player is moving up (dy is negative velocity_y)
                    # Check if player was below or at the platform's bottom before this move
                    if old_rect_top >= platform.rect.bottom:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0 # Stop upward movement

        # Screen boundary checks for X-axis
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Screen boundary checks for Y-axis (simple top boundary)
        # Note: Hitting underside of platform is handled above, this handles screen top
        if self.rect.top < 0:
            self.rect.top = 0
            # Only reset velocity if not already handled by platform collision
            if dy < 0: # If moving up when hitting screen top
                 self.velocity_y = 0


    def update(self, platforms, monsters): # Added monsters parameter
        # Apply gravity
        self.velocity_y += GRAVITY
        if self.velocity_y > 15: # Terminal velocity (optional)
            self.velocity_y = 15
        
        # Move the player vertically (and check for vertical platform collisions)
        self.move(0, self.velocity_y, platforms)

        # Ground collision (fallback)
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.is_jumping = False

        # Player Attack Logic
        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            # Attempt to attack
            attack_occurred = False
            for monster in monsters:
                effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
                # Adjust effective_attack_rect based on player direction for more precise visual correlation
                # This is optional, current logic uses a general circular/square range
                # For simplicity, we keep the inflated rect centered on the player for range check.

                if effective_attack_rect.colliderect(monster.rect):
                    monster.health -= self.attack_damage
                    # Trigger monster's hit flash
                    monster.is_hit = True
                    monster.hit_flash_timer = monster.hit_flash_duration
                    print(f"Player attacked monster (ID: {id(monster)}). Monster health: {monster.health}")
                    
                    if monster.health <= 0:
                        print(f"Monster (ID: {id(monster)}) defeated! It dropped a 'Monster Part'.")
                        self.inventory.append("Monster Part")
                        print(f"Player inventory: {self.inventory}")
                        
                    self.last_attack_time = 0
                    attack_occurred = True # Mark that an attack happened
                    break 
            
            if attack_occurred: # If an attack was made
                self.is_attacking = True
                self.attack_visual_timer = self.attack_visual_duration
        
        # Update attack visual timer
        if self.is_attacking:
            self.attack_visual_timer -= 1
            if self.attack_visual_timer <= 0:
                self.is_attacking = False
# Platform class (Monster class has been moved to monster.py)
class Platform: 
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Game loop
running = True
clock = pygame.time.Clock()

# Create platforms
platforms = [
    Platform(100, SCREEN_HEIGHT - 100, 200, 20, GREEN),
    Platform(400, SCREEN_HEIGHT - 200, 150, 20, GREEN),
    Platform(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 300, 100, 20, GREEN)
]

# Define monsters list globally (or pass to functions that modify it)
monsters = []

# Function to load a level
def load_level(level_idx, player_obj, monsters_list, level_configs_to_use, current_platforms):
    # global platforms # No longer needed as platforms is passed
    print(level_configs_to_use[level_idx]["message"])
    
    monsters_list.clear()
    
    player_obj.rect.topleft = (PLAYER_START_X, PLAYER_START_Y)
    player_obj.health = PLAYER_MAX_HEALTH
    player_obj.velocity_y = 0 # Reset velocity to prevent carrying over jump state
    player_obj.is_jumping = False # Reset jump state
    
    monster_spawn_offset_x = 0 # To space out different types/groups of monsters

    for monster_group_config in level_configs_to_use[level_idx]["monsters"]:
        monster_type_str = monster_group_config["type"]
        count = monster_group_config["count"]
        
        for i in range(count):
            # Base positioning logic (can be adjusted per type)
            monster_width = 40
            monster_height = 40
            
            # Attempt to place on the first platform, provide some spacing
            if current_platforms: # Use current_platforms passed as argument
                base_x_on_platform = current_platforms[0].rect.left + 70 
                monster_x = base_x_on_platform + i * (monster_width + 80) + monster_spawn_offset_x
                monster_y = current_platforms[0].rect.top - monster_height
                
                # Simple check to avoid spawning too far on a small platform
                if monster_x + monster_width > current_platforms[0].rect.right - 20:
                     monster_x = current_platforms[0].rect.left + 20 + i * 10 + monster_spawn_offset_x # Fallback minimal spacing
            else: # Fallback to ground if no platforms
                monster_x = 150 + i * 150 + monster_spawn_offset_x
                monster_y = SCREEN_HEIGHT - monster_height - 5

            new_monster = None
            if monster_type_str == "Grunt":
                patrol_range = monster_group_config.get("patrol_range", 50)
                new_monster = Grunt(x=monster_x, y=monster_y, width=monster_width, height=monster_height, color=RED,
                                    health=100, attack_damage=5, attack_range=60, attack_cooldown=90, speed=2,
                                    patrol_range_x=patrol_range, gravity_val=GRAVITY, screen_height_val=SCREEN_HEIGHT)
            elif monster_type_str == "Flyer":
                flyer_y = SCREEN_HEIGHT / 2 - 50 + i * 10 # Adjust Y for flyers, spread them a bit
                vertical_amplitude = monster_group_config.get("vertical_amplitude", 30)
                vertical_speed_factor = monster_group_config.get("vertical_speed_factor", 0.005)
                patrol_range = monster_group_config.get("patrol_range", 70)
                new_monster = Flyer(x=monster_x, y=flyer_y, width=35, height=35, color=YELLOW,
                                    health=70, attack_damage=7, attack_range=50, attack_cooldown=100, speed=2.5,
                                    vertical_amplitude=vertical_amplitude, vertical_speed_factor=vertical_speed_factor,
                                    patrol_range_x=patrol_range)
            
            if new_monster:
                # new_monster.start_x is set in their respective __init__ methods using the passed 'x'
                monsters_list.append(new_monster)
        
        monster_spawn_offset_x += count * (monster_width + 80) + 100 # Add spacing for the next group of monsters


# Create a player instance
player_width = 50
player_height = 50
# Player initial position is now set by load_level
player = Player(PLAYER_START_X, PLAYER_START_Y, player_width, player_height, WHITE)

# Initial level load
load_level(current_level_index, player, monsters, LEVEL_CONFIGS, platforms)


while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if not player.is_jumping: # Condition is correct, is_jumping becomes False on any surface
                    player.velocity_y = JUMP_STRENGTH
                    player.is_jumping = True # Mark as jumping

    # Handle continuous key presses for horizontal movement
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -player.speed
    if keys[pygame.K_RIGHT]:
        dx = player.speed
    
    if dx != 0: # Only call move if there's horizontal movement
        player.move(dx, 0, platforms)
    
    # Update player (applies gravity, vertical movement, platform/ground collisions, and attacks)
    player.update(platforms, monsters)

    # Update pet
    if player.pet: # Ensure pet exists
        player.pet.update(platforms, monsters, player) # Pass monsters and player

    # Update monsters
    for monster in monsters:
        monster.update(platforms, player) # Pass player object
    
    # Remove dead monsters
    monsters = [m for m in monsters if m.health > 0]

    # Game State Checks and Drawing
    if player.health <= 0:
        screen.fill(BLACK)
        game_over_surface = GAME_OVER_FONT.render("Game Over!", True, RED)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(game_over_surface, game_over_rect)

        sub_text_surface = UI_FONT.render("Press any key to exit.", True, WHITE)
        sub_text_rect = sub_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(sub_text_surface, sub_text_rect)
        pygame.display.flip()

        game_over_active = True
        while game_over_active:
            for event_game_over in pygame.event.get(): # Use a different event variable name
                if event_game_over.type == pygame.QUIT:
                    game_over_active = False
                    running = False
                if event_game_over.type == pygame.KEYDOWN:
                    game_over_active = False
                    running = False
            clock.tick(30) # Keep the loop from running too fast
        
    elif not monsters and player.health > 0: # Player cleared the level
        current_level_index += 1
        if current_level_index < len(LEVEL_CONFIGS):
            load_level(current_level_index, player, monsters, LEVEL_CONFIGS, platforms)
        else: # All levels completed
            screen.fill(BLACK)
            win_surface = GAME_OVER_FONT.render("You Win!", True, GREEN)
            win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(win_surface, win_rect)

            congrats_surface = UI_FONT.render("Congratulations! Press any key to exit.", True, WHITE)
            congrats_rect = congrats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(congrats_surface, congrats_rect)
            pygame.display.flip()

            win_active = True
            while win_active:
                for event_win in pygame.event.get(): # Use a different event variable name
                    if event_win.type == pygame.QUIT:
                        win_active = False
                        running = False
                    if event_win.type == pygame.KEYDOWN:
                        win_active = False
                        running = False
                clock.tick(30) # Keep the loop from running too fast
            # If running is set to False above, the main loop will terminate
    
    if running: # Only draw the main game if still running
        # Fill the screen
        screen.fill(BLACK)

        # Draw platforms
        for platform in platforms:
            platform.draw(screen)

        # Draw monsters
        for monster in monsters:
        monster.draw(screen, HIT_COLOR) # Pass HIT_COLOR to monster draw

        # Draw the player
        player.draw(screen)

        # Draw pet
        if player.pet: # Ensure pet exists
            player.pet.draw(screen)

        # --- Draw UI Elements ---
        # Display Player Health
        player_health_text = f"Health: {player.health}/{PLAYER_MAX_HEALTH}"
        draw_text(screen, player_health_text, UI_FONT, WHITE, 10, 10)

        # Display Current Level
        level_text = f"Level: {current_level_index + 1}" # Add 1 because indices are 0-based
        draw_text(screen, level_text, UI_FONT, WHITE, 10, 40) # Position below health

        # Display Monster Parts Inventory
        monster_part_count = player.inventory.count("Monster Part")
        inventory_text = f"Monster Parts: {monster_part_count}"
        draw_text(screen, inventory_text, UI_FONT, WHITE, 10, 70) # Position below level text

        # Update the display
        pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
