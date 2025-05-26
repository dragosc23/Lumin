# config.py - Centralized game configuration settings
import pygame # Added to define RED, YELLOW, BLUE if not already

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Player Default Stats & Properties
PLAYER_START_X = SCREEN_WIDTH // 2 - 20 # Assuming player width is 40
PLAYER_START_Y = SCREEN_HEIGHT - 50 - 20 # Assuming player height is 40, and 20 is offset from bottom
PLAYER_MAX_HEALTH = 200
PLAYER_SPEED = 5
PLAYER_ATTACK_DAMAGE = 20
PLAYER_ATTACK_RANGE = 75
PLAYER_ATTACK_COOLDOWN = 60 # In frames
PLAYER_HIT_FLASH_DURATION = 10 # In frames
PLAYER_ATTACK_VISUAL_DURATION = 7 # In frames

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
HIT_COLOR = (255, 100, 100)       # For damage flash
ATTACK_VISUAL_COLOR = (200, 200, 0) # For player attack visual


# Pet Default Stats
PET_SPEED = 3
PET_HEALTH = 50
PET_ATTACK_DAMAGE = 2
PET_ATTACK_RANGE = 40
PET_ATTACK_COOLDOWN = 120 # In frames
PET_FOLLOW_DISTANCE = 50
PET_HIT_FLASH_DURATION = 10 # In frames 
PET_WIDTH = 20
PET_HEIGHT = 20
PET_COLOR = BLUE # Uses color defined above


# Monster Properties
MONSTER_HIT_FLASH_DURATION = 10 # In frames

# Game Physics & Mechanics
GRAVITY = 1
JUMP_STRENGTH = -20


# Default Monster Stats (base values, can be overridden by LEVEL_CONFIGS)
DEFAULT_GRUNT_WIDTH = 40
DEFAULT_GRUNT_HEIGHT = 40
DEFAULT_GRUNT_STATS = {
    "health": 120,
    "attack_damage": 8,
    "attack_range": 50,
    "attack_cooldown": 70, # frames
    "speed": 2,
    "color": RED, 
    "width": DEFAULT_GRUNT_WIDTH,
    "height": DEFAULT_GRUNT_HEIGHT,
    "patrol_range_x": 50 
}

DEFAULT_FLYER_WIDTH = 35
DEFAULT_FLYER_HEIGHT = 35
DEFAULT_FLYER_STATS = {
    "health": 60,
    "attack_damage": 6,
    "attack_range": 60,
    "attack_cooldown": 100, # frames
    "speed": 3,
    "color": YELLOW, 
    "width": DEFAULT_FLYER_WIDTH,
    "height": DEFAULT_FLYER_HEIGHT,
    "patrol_range_x": 50, 
    "vertical_amplitude": 30,
    "vertical_speed_factor": 0.01
}

# UI settings
UI_FONT_FAMILY = "arial"
UI_FONT_SIZE = 24
GAME_OVER_FONT_SIZE = 72
TITLE_FONT_SIZE = 50 # For MainMenuScreen title
PAUSED_FONT_SIZE = 48 # For PauseScreen title

print("config.py loaded") # For verification during development
