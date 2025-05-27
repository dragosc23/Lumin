# config.py - Centralized game configuration settings
import pygame # Added to define RED, YELLOW, BLUE if not already

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Player Default Stats & Properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_COLOR = GREEN # Defined below
PLAYER_START_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20 # 20px offset from bottom
PLAYER_MAX_HEALTH = 200
PLAYER_SPEED = 5
PLAYER_ATTACK_DAMAGE = 20
PLAYER_ATTACK_RANGE = 75
PLAYER_ATTACK_COOLDOWN = 60 # In frames
PLAYER_HIT_FLASH_DURATION = 10 # In frames
PLAYER_ATTACK_VISUAL_DURATION = 7 # In frames
PLAYER_INVENTORY_CAPACITY = 16 # Max number of item STACKS
XP_PER_LEVEL_BASE = 100      # Base XP needed for each level (e.g., level 1 needs 100, level 2 needs 200)
XP_PER_MONSTER_DEFEAT = 25   # XP awarded for defeating a common monster
HEALTH_GAIN_PER_LEVEL = 20   # How much max_health increases per level

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_GREY = (40, 40, 40)
UI_BUTTON_COLOR = (100, 100, 100)
UI_BUTTON_HOVER_COLOR = (150, 150, 150)
UI_BUTTON_TEXT_COLOR = WHITE
MAIN_MENU_BG_COLOR = (30, 30, 50) # Dark blueish
PAUSE_OVERLAY_COLOR = (0, 0, 0, 180) # Black with alpha for transparency
GAME_OVER_BG_COLOR = (50, 20, 20) # Dark reddish
GAME_WON_BG_COLOR = (20, 50, 20) # Dark greenish
HIT_COLOR = (255, 100, 100)       # For damage flash
ATTACK_VISUAL_COLOR = (200, 200, 0) # For player attack visual


# Pet Default Stats
# PET_WIDTH, PET_HEIGHT, PET_COLOR are already defined
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

# Item Defaults
DEFAULT_ITEM_MAX_STACK = 20 # Default max stack for generic items if not specified

GENERIC_ITEM_DEFAULTS = {
    "MonsterPart": {
        "item_class_name": "Item", # Added for robust item creation
        "name": "Monster Part", 
        "description": "A common part from a defeated monster.",
        "value": 5,
        "stackable": True,
        "max_stack": DEFAULT_ITEM_MAX_STACK 
    },
    "HealthPotion": { # Assuming HealthPotion will be an item type
        "item_class_name": "HealthPotion", # Added for robust item creation
        "name": "Health Potion",
        "description": "Restores a small amount of health.",
        "value": 25,
        "stackable": True,
        "max_stack": 5, # Potions might stack less
        "heal_amount": 50 # Added here for HealthPotion specific data
    }
}

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
    "vertical_speed_factor": 0.01,
    "y_offset": 50 # Default y offset for flyers from the top or a reference point
}

# LEVEL_CONFIGS
# Defines platforms, monsters per level, their stats (can override defaults), and drops.
# Platform format: [x, y, width, height, (optional) color]
LEVEL_CONFIGS = [
    {
        "platforms": [
            [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, GREY], # Ground
            [200, SCREEN_HEIGHT - 200, 150, 20, GREY],
            [SCREEN_WIDTH - 350, SCREEN_HEIGHT - 350, 150, 20, GREY]
        ],
        "monsters": [
            {
                "type": "Grunt", "count": 1, "x": 300, "y": SCREEN_HEIGHT - 40 - DEFAULT_GRUNT_HEIGHT, # on ground
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            }
        ],
        "message": "Level 1: A Grunt with potential drops!"
    },
    {
        "platforms": [
            [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, GREY], # Ground
            [100, SCREEN_HEIGHT - 150, 100, 20, GREY],
            [300, SCREEN_HEIGHT - 250, 100, 20, GREY],
            [500, SCREEN_HEIGHT - 150, 100, 20, GREY]
        ],
        "monsters": [
            {
                "type": "Grunt", "count": 2, "x": [200, 400], "y": SCREEN_HEIGHT - 40 - DEFAULT_GRUNT_HEIGHT,
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            }
        ],
        "message": "Level 2: Two Grunts, more chances for loot!"
    },
    {
        "platforms": [
            [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, GREY], # Ground
            [150, SCREEN_HEIGHT - 200, 200, 20, GREY],
            [SCREEN_WIDTH - 350, SCREEN_HEIGHT - 300, 200, 20, GREY]
        ],
        "monsters": [
            {
                "type": "Flyer", "count": 1, "x": SCREEN_WIDTH // 2, "y": DEFAULT_FLYER_STATS["y_offset"],
                "drops": [
                    {"item_id": "MonsterPart", "chance": 0.75, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.05, "quantity": 1}
                ]
            }
        ],
        "message": "Level 3: A Flyer appears with its own loot table!"
    },
    {
        "platforms": [
            [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, GREY], # Ground
            [50, SCREEN_HEIGHT - 150, 100, 20, DARK_GREY],
            [200, SCREEN_HEIGHT - 250, 100, 20, DARK_GREY],
            [350, SCREEN_HEIGHT - 350, 100, 20, DARK_GREY],
            [SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, 100, 20, DARK_GREY]
        ],
        "monsters": [
            {
                "type": "Grunt", "count": 1, "x": 100, "y": SCREEN_HEIGHT - 40 - DEFAULT_GRUNT_HEIGHT,
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            },
            {
                "type": "Flyer", "count": 1, "x": SCREEN_WIDTH - 200, "y": DEFAULT_FLYER_STATS["y_offset"] + 50, # Slightly lower
                "drops": [
                    {"item_id": "MonsterPart", "chance": 0.75, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.05, "quantity": 1}
                ]
            }
        ],
        "message": "Level 4: Mixed company, mixed loot!"
    }
]


# UI settings
UI_FONT_FAMILY = None # Use Pygame's default font
UI_FONT_SIZE = 24
UI_TITLE_FONT_SIZE = 50 # For MainMenuScreen title
UI_SUBTITLE_FONT_SIZE = 30
UI_GAME_OVER_FONT_SIZE = 72
UI_PAUSED_FONT_SIZE = 48
UI_BUTTON_HEIGHT = 50
UI_BUTTON_PADDING = 10

# Sound Keys (used with SoundManager)
SOUND_UI_CLICK = "ui_click"
SOUND_PLAYER_JUMP = "player_jump"
SOUND_PLAYER_ATTACK = "player_attack"
SOUND_PLAYER_HIT = "player_hit"
SOUND_MONSTER_HIT = "monster_hit"
SOUND_MONSTER_DEATH = "monster_death"
SOUND_ITEM_PICKUP = "item_pickup"
SOUND_LEVEL_UP = "level_up"
SOUND_GAME_OVER = "game_over"
SOUND_GAME_WON = "game_won"
SOUND_PET_ATTACK = "pet_attack" # Added

# Music Keys
MUSIC_MAIN_MENU = "music_main_menu"
MUSIC_GAMEPLAY = "music_gameplay"

# File paths
SAVE_GAME_FILENAME = "savegame.json"

# Sound File Paths (Placeholders)
ASSETS_SOUNDS_DIR = "assets/sounds/"
ASSETS_MUSIC_DIR = "assets/music/"

SOUND_PATH_UI_CLICK = ASSETS_SOUNDS_DIR + "ui_click.wav"
SOUND_PATH_PLAYER_JUMP = ASSETS_SOUNDS_DIR + "player_jump.wav"
SOUND_PATH_PLAYER_ATTACK = ASSETS_SOUNDS_DIR + "player_attack.wav"
SOUND_PATH_PLAYER_HIT = ASSETS_SOUNDS_DIR + "player_hit.wav"
SOUND_PATH_MONSTER_HIT = ASSETS_SOUNDS_DIR + "monster_hit.wav"
SOUND_PATH_MONSTER_DEATH = ASSETS_SOUNDS_DIR + "monster_death.wav"
SOUND_PATH_PET_ATTACK = ASSETS_SOUNDS_DIR + "pet_attack.wav"
SOUND_PATH_ITEM_PICKUP = ASSETS_SOUNDS_DIR + "item_pickup.wav"
SOUND_PATH_LEVEL_UP = ASSETS_SOUNDS_DIR + "level_up.wav"
SOUND_PATH_GAME_OVER = ASSETS_SOUNDS_DIR + "game_over.wav"
SOUND_PATH_GAME_WON = ASSETS_SOUNDS_DIR + "game_won.wav"

# Music File Paths (Placeholders)
MUSIC_PATH_MAIN_MENU = ASSETS_MUSIC_DIR + "main_menu.ogg"
MUSIC_PATH_GAMEPLAY = ASSETS_MUSIC_DIR + "gameplay.ogg"

# Example SOUND_FILES dictionary (optional, if SoundManager uses it directly)
# SOUND_FILES = {
#     SOUND_UI_CLICK: SOUND_PATH_UI_CLICK,
#     SOUND_PLAYER_JUMP: SOUND_PATH_PLAYER_JUMP,
#     SOUND_PLAYER_ATTACK: SOUND_PATH_PLAYER_ATTACK,
#     SOUND_PLAYER_HIT: SOUND_PATH_PLAYER_HIT,
#     SOUND_MONSTER_HIT: SOUND_PATH_MONSTER_HIT,
#     SOUND_MONSTER_DEATH: SOUND_PATH_MONSTER_DEATH,
#     SOUND_PET_ATTACK: SOUND_PATH_PET_ATTACK,
#     SOUND_ITEM_PICKUP: SOUND_PATH_ITEM_PICKUP,
#     SOUND_LEVEL_UP: SOUND_PATH_LEVEL_UP,
#     SOUND_GAME_OVER: SOUND_PATH_GAME_OVER,
#     SOUND_GAME_WON: SOUND_PATH_GAME_WON,
#     # Music files could be handled separately or added here if SoundManager supports it
#     MUSIC_MAIN_MENU: MUSIC_PATH_MAIN_MENU,
#     MUSIC_GAMEPLAY: MUSIC_PATH_GAMEPLAY,
# }

print("config.py loaded") # For verification during development
