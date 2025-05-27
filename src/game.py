import pygame
import time # Added import

import config
from src.world_elements import Platform # Import Platform class
from src.save_manager import SaveManager # Import SaveManager
from src.player import Player # Import Player for type hinting and potential instantiation
from src.items import ITEM_CLASS_MAP, create_item_from_dict # For loading inventory if player is created here

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()  # If not in SoundManager

        # Screen setup
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None  # Will be set to a screen object e.g., MainMenuScreen()
        self.current_level_index = 0 # Start at the first level
        self.player = None # Will be initialized by GameplayScreen or explicitly in load_game_state
        self.platforms = [] # Will be managed by GameplayScreen or load_level
        self.monsters = [] # Will be managed by GameplayScreen or load_level
        
        self.save_manager = SaveManager() # Instantiate SaveManager

        # Placeholder for current_screen, actual screen instances will be created later
        # from src.screens import MainMenuScreen, GameplayScreen # Example
        # self.current_screen = MainMenuScreen(self.screen, self) # Pass screen and game instance
        
        # Sound manager (assuming it's initialized elsewhere or passed to Game)
        # For now, if Player requires it, it must be handled here or in create_player_from_config
        self.sound_manager = None # Placeholder, actual SoundManager instance should be set up
        # Example: if SoundManager is a class
        # from src.sound_manager import SoundManager
        # self.sound_manager = SoundManager()


    def create_player_from_config(self):
        """Creates a new Player instance using default settings from config.py."""
        # sound_manager_instance = getattr(self, 'sound_manager', None) # Get self.sound_manager if it exists
        # For this refactor, assuming sound_manager might not be fully integrated into Game yet
        # If Player class requires a non-None sound_manager, this needs to be ensured.
        # The Player class in the provided context has sound_manager=None as a default.
        new_player = Player(
            x=config.PLAYER_START_X,
            y=config.PLAYER_START_Y,
            width=config.PLAYER_WIDTH,
            height=config.PLAYER_HEIGHT,
            color=config.PLAYER_COLOR,
            sound_manager=self.sound_manager # Pass the game's sound_manager instance
        )
        print(f"DEBUG: New player created from config at ({new_player.rect.x}, {new_player.rect.y})")
        return new_player

    def save_game_state(self, filename=None): # Default to None
        if filename is None:
            filename = config.SAVE_FILENAME # Use from config if None

        if self.player is None:
            print("DEBUG: Player object does not exist, cannot save game state.")
            return False # Or handle more gracefully, maybe save non-player data

        player_data = {
            "health": self.player.health,
            "max_health": self.player.max_health,
            "level": self.player.level,
            "xp": self.player.experience_points,
            "xp_to_next_level": self.player.xp_to_next_level,
            "attack_power": self.player.attack_power, # New
            "defense": self.player.defense,           # New
            "gold": self.player.gold, # Added gold
            "inventory": self.player.inventory.get_serializable_data(),
            "position": [self.player.rect.x, self.player.rect.y],
            # Note: Player's width, height, color are usually part of its definition,
            # not dynamic state, unless they can change and need saving.
        }
        
        # Save equipped items
        equipped_items_data = {}
        if hasattr(self.player, 'equipment'): # Ensure player object has equipment attribute
            for slot_name, item_instance in self.player.equipment.items():
                if item_instance:
                    equipped_items_data[slot_name] = item_instance.to_dict()
                else:
                    equipped_items_data[slot_name] = None
        player_data["equipped_items"] = equipped_items_data
        
        game_state_data = {
            "current_level_index": self.current_level_index,
            "player_data": player_data,
            # Add other game-wide states here if necessary (e.g., game time, overall progress flags)
        }
        
        # Add timestamp before saving
        current_timestamp = time.time()
        game_state_data["last_seen_timestamp"] = current_timestamp
        
        # Use the SaveManager's configured filename if the passed 'filename' is the default config one
        # Or, if SaveManager should always use its own internal filename, this logic changes.
        # For now, assume filename passed to save_game_state overrides SaveManager's default.
        # However, the SaveManager itself is initialized with config.SAVE_FILENAME.
        # So, passing filename here seems redundant if it's always config.SAVE_FILENAME.
        # Let's simplify: SaveManager uses its configured name. This method just triggers.
        if self.save_manager.save_data(game_state_data): 
            print(f"Game state saved successfully to {self.save_manager.save_filename}.")
            return True
        else:
            print("Failed to save game state.")
            return False

    def load_game_state(self, filename=None): # Default to None
        if filename is None:
            filename = config.SAVE_FILENAME # Use from config if None
        
        # Similar to save, SaveManager uses its own configured filename.
        # The 'filename' parameter here could be used to tell SaveManager to load a *different* file
        # but current SaveManager.load_data() doesn't take a filename.
        # For consistency with the refactor, let's assume SaveManager's methods will be updated
        # or this method implies "load the default save file".
        loaded_data = self.save_manager.load_data() 
        
        # Initialize offline seconds attribute
        self.offline_seconds_for_reward_calculation = 0

        if loaded_data is None:
            print("DEBUG: No save data found or error loading.")
            # Optionally, start a new game or return to main menu
            # self.start_new_game() # Example method call
            return False
        
        # Calculate offline time
        last_seen_timestamp = loaded_data.get("last_seen_timestamp")
        if last_seen_timestamp is not None:
            current_time = time.time()
            offline_seconds = current_time - last_seen_timestamp
            self.offline_seconds_for_reward_calculation = offline_seconds
            print(f"DEBUG: Player was offline for {offline_seconds:.0f} seconds.")
        else:
            print("DEBUG: No last_seen_timestamp found. Skipping offline progress calculation for this session.")

        self.current_level_index = loaded_data.get("current_level_index", 0)
        
        loaded_player_data = loaded_data.get("player_data")
        if loaded_player_data:
            # If player doesn't exist (e.g. loading from main menu directly into game)
            # it needs to be created. This assumes Player constructor can handle it.
            # For a robust system, GameplayScreen might handle player creation.
            # For now, let's assume player is typically created by a screen transition
            # and we are just updating its state. If not, player creation logic is needed here.
            if self.player is None:
                print("DEBUG: Player object is None during load_game_state. Creating new Player instance using config.")
                self.player = self.create_player_from_config()
                # The rest of the loading logic will then populate this new player instance's state.
                # Position will be set specifically from save data if available, overriding config start X/Y.

            self.player.level = loaded_player_data.get("level", 1)
            self.player.experience_points = loaded_player_data.get("xp", 0)
            self.player.max_health = loaded_player_data.get("max_health", config.PLAYER_MAX_HEALTH)
            # Recalculate xp_to_next_level based on loaded level, or load it if saved precisely
            self.player.xp_to_next_level = loaded_player_data.get("xp_to_next_level", config.XP_PER_LEVEL_BASE * self.player.level)
            self.player.health = loaded_player_data.get("health", self.player.max_health)
            
            # Load attack_power and defense, defaulting to base values from config if not in save file
            self.player.attack_power = loaded_player_data.get("attack_power", config.PLAYER_BASE_ATTACK_POWER)
            self.player.defense = loaded_player_data.get("defense", config.PLAYER_BASE_DEFENSE)
            self.player.gold = loaded_player_data.get("gold", config.PLAYER_STARTING_GOLD) # Added gold loading

            # Position
            player_pos = loaded_player_data.get("position")
            if player_pos and len(player_pos) == 2:
                self.player.rect.x = player_pos[0]
                self.player.rect.y = player_pos[1]
            
            # Inventory
            inventory_data = loaded_player_data.get("inventory")
            if inventory_data is not None and hasattr(self.player, 'inventory'):
                self.player.inventory.load_from_serializable_data(inventory_data)
            
            # Equipped Items
            loaded_equipped_items_data = loaded_player_data.get("equipped_items", {})
            if hasattr(self.player, 'equipment'): # Ensure player object is ready with equipment dict
                for slot_name, item_dict_data in loaded_equipped_items_data.items():
                    if item_dict_data:
                        item_instance = create_item_from_dict(item_dict_data)
                        if item_instance and slot_name in self.player.equipment:
                            self.player.equipment[slot_name] = item_instance
                        elif item_instance:
                            print(f"Warning: Player equipment slot '{slot_name}' not found during load for item {item_instance.name}.")
                        elif not item_instance:
                            print(f"Warning: Could not create item instance from saved equipped data for slot '{slot_name}'. Data: {item_dict_data}")
                    else:
                        if slot_name in self.player.equipment:
                            self.player.equipment[slot_name] = None
            
            # Adjust health after all stats and equipment are loaded
            current_total_max_health = self.player.get_total_max_health()
            if self.player.health > current_total_max_health:
                self.player.health = current_total_max_health
            self.player.health = max(1, self.player.health) # Ensure health is at least 1

            print("Player data loaded and applied, including equipment and health adjustment.")
        else:
            print("Warning: No player data found in save file.")
            # Decide how to handle this: new player, error, etc.

        # After loading, you might want to load the level entities, switch screens, etc.
        # For example, directly loading into gameplay:
        # self.load_level(self.current_level_index) # This would populate platforms/monsters
        # from src.screens import GameplayScreen # Careful with import cycles
        # self.current_screen = GameplayScreen(self.screen, self, self.player) # Assuming GameplayScreen takes player
        
        # Initialize and potentially calculate offline rewards
        self.offline_rewards_to_display = None
        if self.offline_seconds_for_reward_calculation >= config.OFFLINE_MIN_SECONDS_FOR_REWARDS:
            if self.player: 
                rewards_summary = self.calculate_and_apply_offline_rewards()
                if rewards_summary.get("gold_earned", 0) > 0 or rewards_summary.get("xp_earned", 0) > 0:
                    self.offline_rewards_to_display = rewards_summary
                    print(f"DEBUG: Offline rewards to display: {self.offline_rewards_to_display}")
                else:
                    print("DEBUG: Offline rewards were zero, nothing to display.")
            else:
                print("DEBUG: Player object not available, cannot calculate offline rewards during load_game_state.")
        else:
            print(f"DEBUG: Offline time {self.offline_seconds_for_reward_calculation:.0f}s is less than minimum {config.OFFLINE_MIN_SECONDS_FOR_REWARDS}s. No rewards to display.")

        print(f"Game state loaded. Current level index: {self.current_level_index}")
        return True

    @staticmethod
    def draw_text(surface, text, size, x, y, color=config.WHITE, font_name=None):
        # If a specific font name is provided, try to load it. Otherwise, use default system font.
        # Updated to use config.UI_FONT_FAMILY as default font name
        actual_font_name = font_name if font_name is not None else config.UI_FONT_FAMILY
        try:
            font = pygame.font.Font(actual_font_name, size)
        except pygame.error: # Fallback if specific font (even default from config) is not found
            print(f"Warning: Font '{actual_font_name}' not found. Falling back to Pygame default.")
            font = pygame.font.Font(None, size) # Pygame's default font
            
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y) # Or other positioning as needed, e.g. topleft
        surface.blit(text_surface, text_rect)

    def load_level(self, level_index):
        """
        Loads platform data for the specified level index and sets current_level_index.
        Monster and player setup for the level are handled by GameplayScreen.
        """
        if 0 <= level_index < len(config.LEVEL_CONFIGS):
            self.current_level_index = level_index
            level_data = config.LEVEL_CONFIGS[level_index]
            
            # Reset/initialize game elements for the new level managed by Game class
            self.platforms.clear() # Clear existing platforms
            self.monsters.clear()  # Clear existing monsters (GameplayScreen will repopulate)
            
            # Load platform data
            for p_data in level_data.get("platforms", []):
                # Ensure p_data from config matches Platform constructor (x, y, width, height, [color])
                if len(p_data) == 4: # x, y, width, height
                    self.platforms.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3]))
                elif len(p_data) == 5: # x, y, width, height, color
                    self.platforms.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3], p_data[4]))
            
            print(f"Game.load_level: Loaded level {level_index + 1}. Platforms loaded: {len(self.platforms)}")
            # Note: Player state for the level (position, health reset) and monster instantiation
            # are handled by GameplayScreen._load_level_logic or similar screen-specific methods.
            
            # Potentially switch to GameplayScreen here if not already on it
            # from src.screens import GameplayScreen # Example, careful with circular imports
            # self.current_screen = GameplayScreen(self.screen, self)
        else:
            print(f"Error: Level index {level_index} out of bounds.")
            # Optionally, go to a game over screen or main menu
            # from src.screens import MainMenuScreen # Example
            # self.current_screen = MainMenuScreen(self.screen, self)

    def calculate_and_apply_offline_rewards(self):
        rewards_summary = {"gold_earned": 0, "xp_earned": 0}

        if not self.player:
            print("DEBUG: No player object found, cannot calculate offline rewards.")
            return rewards_summary

        if self.offline_seconds_for_reward_calculation < config.OFFLINE_MIN_SECONDS_FOR_REWARDS:
            print(f"DEBUG: Offline time ({self.offline_seconds_for_reward_calculation:.0f}s) below minimum threshold ({config.OFFLINE_MIN_SECONDS_FOR_REWARDS}s), no rewards.")
            return rewards_summary

        offline_hours = self.offline_seconds_for_reward_calculation / 3600.0
        
        if config.OFFLINE_MAX_HOURS_FOR_REWARDS > 0:
            effective_offline_hours = min(offline_hours, config.OFFLINE_MAX_HOURS_FOR_REWARDS)
            if offline_hours > config.OFFLINE_MAX_HOURS_FOR_REWARDS:
                print(f"DEBUG: Offline time ({offline_hours:.2f}h) capped at max ({config.OFFLINE_MAX_HOURS_FOR_REWARDS}h) for reward calculation.")
        else:
            effective_offline_hours = offline_hours

        player_level = self.player.level

        # Gold Calculation
        base_gold_rate = config.OFFLINE_GOLD_PER_HOUR_BASE
        scaling_factor = config.OFFLINE_REWARD_SCALING_FACTOR_PER_PLAYER_LEVEL
        effective_gold_per_hour = base_gold_rate * (1 + player_level * scaling_factor)
        gold_earned = int(effective_gold_per_hour * effective_offline_hours)

        # XP Calculation
        base_xp_rate = config.OFFLINE_XP_PER_HOUR_BASE
        effective_xp_per_hour = base_xp_rate * (1 + player_level * scaling_factor)
        xp_earned = int(effective_xp_per_hour * effective_offline_hours)

        # Apply Rewards
        # Gold
        current_gold = getattr(self.player, 'gold', 0)
        # Ensure player has a gold attribute before setting.
        # This might be better handled by initializing player.gold = 0 in Player.__init__
        if not hasattr(self.player, 'gold'):
            self.player.gold = 0 
        self.player.gold = current_gold + gold_earned
        
        # XP
        if xp_earned > 0: # Only call gain_xp if there's XP to gain, to avoid unnecessary log messages from gain_xp
            self.player.gain_xp(xp_earned)

        rewards_summary["gold_earned"] = gold_earned
        rewards_summary["xp_earned"] = xp_earned

        print(f"DEBUG: Offline rewards calculated: {gold_earned} gold, {xp_earned} XP for {effective_offline_hours:.2f} effective hours (Total offline: {offline_hours:.2f}h).")
        
        return rewards_summary

    def run(self):
        # self.load_level(self.current_level_index) # Initial level load, might be done by MainMenuScreen starting game

        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Pass event to the current screen if it exists
                if self.current_screen:
                    self.current_screen.handle_event(event)

            # Update current screen if it exists
            if self.current_screen:
                self.current_screen.update(dt)

            # Draw current screen if it exists
            self.screen.fill(config.BLACK) # Default background
            if self.current_screen:
                self.current_screen.draw()
            
            pygame.display.flip()

        pygame.quit()

# The if __name__ == '__main__': block is not needed here anymore,
# as main.py will be responsible for creating and running the game.
#
# if __name__ == '__main__':
# game = Game()
# game.run()
