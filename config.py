# config.py - Centralized game configuration settings
import pygame # Added to define RED, YELLOW, BLUE if not already

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Player Default Stats & Properties
# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
HIT_COLOR = (255, 100, 100)       # For damage flash
ATTACK_VISUAL_COLOR = (200, 200, 0) # For player attack visual

# Player Default Stats & Properties
PLAYER_START_X = SCREEN_WIDTH // 2 - 20 # Assuming player width is 40
PLAYER_START_Y = SCREEN_HEIGHT - 50 - 20 # Assuming player height is 40, and 20 is offset from bottom
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_COLOR = GREEN # References the GREEN color defined above
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
ATTACK_POWER_GAIN_PER_LEVEL = 2 # How much attack_power increases per level
DEFENSE_GAIN_PER_LEVEL = 1      # How much defense increases per level
PLAYER_BASE_ATTACK_POWER = 10 # Player's base attack power
PLAYER_BASE_DEFENSE = 5       # Player's base defense


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
PET_SPAWN_OFFSET_X = 50 # Horizontal offset from player for pet spawning
PET_ASSIST_RANGE_MULTIPLIER = 1.5 # Multiplier for player's attack range to determine pet's assist range


# Monster Properties
MONSTER_HIT_FLASH_DURATION = 10 # In frames

# Game Physics & Mechanics
GRAVITY = 1
JUMP_STRENGTH = -20

# Item Defaults
DEFAULT_ITEM_MAX_STACK = 20 # Default max stack for generic items if not specified

GENERIC_ITEM_DEFAULTS = {
    "MonsterPart": {
        "name": "Monster Part", 
        "description": "A common part from a defeated monster.",
        "value": 5,
        "stackable": True,
        "max_stack": DEFAULT_ITEM_MAX_STACK 
    },
    "HealthPotion": { # Assuming HealthPotion will be an item type
        "name": "Health Potion",
        "description": "Restores a small amount of health.",
        "value": 25,
        "stackable": True,
        "max_stack": 5, # Potions might stack less
        "heal_amount": 50 # Added from HealthPotion constructor for consistency
    },
    "BasicSword": {
        "item_class_name": "Weapon", # Used by factory
        "name": "Basic Sword",
        "description": "A simple, trusty sword.",
        # "slot": "weapon", # Automatically set by Weapon class, redundant here
        "stat_modifiers": {"attack_power": 3},
        "value": 15
    },
    "LeatherArmor": {
        "item_class_name": "Armor", # Used by factory
        "name": "Leather Armor",
        "description": "Basic protection.",
        "slot": "body", # Specify which armor slot for Armor class constructor
        "stat_modifiers": {"defense": 5},
        "value": 20
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
    "vertical_speed_factor": 0.01
}

# LEVEL_CONFIGS
# Defines monsters per level, their stats (can override defaults), and drops.
LEVEL_CONFIGS = [
    {
        "monsters": [
            {
                "type": "Grunt", "count": 1, "patrol_range": 50,
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            }
        ],
        "message": "Level 1: A Grunt with potential drops!"
    },
    {
        "monsters": [
            {
                "type": "Grunt", "count": 2, "patrol_range": 50, # This implies two Grunts, each with these drops
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            }
        ],
        "message": "Level 2: Two Grunts, more chances for loot!"
    },
    {
        "monsters": [
            {
                "type": "Flyer", "count": 1, 
                "vertical_amplitude": 30, "vertical_speed_factor": 0.005, "patrol_range": 70,
                "drops": [
                    {"item_id": "MonsterPart", "chance": 0.75, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.05, "quantity": 1}
                ]
            }
        ],
        "message": "Level 3: A Flyer appears with its own loot table!"
    },
    {
        "monsters": [
            {
                "type": "Grunt", "count": 1, "patrol_range": 50,
                "drops": [
                    {"item_id": "MonsterPart", "chance": 1.0, "quantity": 1},
                    {"item_id": "HealthPotion", "chance": 0.2, "quantity": 1}
                ]
            },
            {
                "type": "Flyer", "count": 1, 
                "vertical_amplitude": 30, "vertical_speed_factor": 0.005, "patrol_range": 70,
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
UI_FONT_FAMILY = "arial"
UI_FONT_SIZE = 24
GAME_OVER_FONT_SIZE = 72
TITLE_FONT_SIZE = 50 # For MainMenuScreen title
PAUSED_FONT_SIZE = 48 # For PauseScreen title

print("config.py loaded") # For verification during development
