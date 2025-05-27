import pygame

import config
from src.world_elements import Platform
from src.save_manager import SaveManager
from src.player import Player
from src.items import ITEM_CLASS_MAP, create_item_from_dict
# Import screens here to avoid circular dependencies if screens also import Game
from src.screens import MainMenuScreen, GameplayScreen, PauseScreen, GameOverScreen, GameWonScreen
from src.sound_manager import SoundManager # Assuming SoundManager is ready

# Game State Constants
STATE_MAIN_MENU = "main_menu"
STATE_GAMEPLAY = "gameplay"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_GAME_WON = "game_won"

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        # Core Components
        self.save_manager = SaveManager(save_filename=config.SAVE_GAME_FILENAME) # Use config for filename
        self.sound_manager = SoundManager() # Initialize SoundManager
        
        # Load all game sounds
        self.sound_manager.load_sound(config.SOUND_UI_CLICK, config.SOUND_PATH_UI_CLICK)
        self.sound_manager.load_sound(config.SOUND_PLAYER_JUMP, config.SOUND_PATH_PLAYER_JUMP)
        self.sound_manager.load_sound(config.SOUND_PLAYER_ATTACK, config.SOUND_PATH_PLAYER_ATTACK)
        self.sound_manager.load_sound(config.SOUND_PLAYER_HIT, config.SOUND_PATH_PLAYER_HIT)
        self.sound_manager.load_sound(config.SOUND_MONSTER_HIT, config.SOUND_PATH_MONSTER_HIT)
        self.sound_manager.load_sound(config.SOUND_MONSTER_DEATH, config.SOUND_PATH_MONSTER_DEATH)
        self.sound_manager.load_sound(config.SOUND_PET_ATTACK, config.SOUND_PATH_PET_ATTACK)
        self.sound_manager.load_sound(config.SOUND_ITEM_PICKUP, config.SOUND_PATH_ITEM_PICKUP)
        self.sound_manager.load_sound(config.SOUND_LEVEL_UP, config.SOUND_PATH_LEVEL_UP)
        self.sound_manager.load_sound(config.SOUND_GAME_OVER, config.SOUND_PATH_GAME_OVER)
        self.sound_manager.load_sound(config.SOUND_GAME_WON, config.SOUND_PATH_GAME_WON)
        
        # Fonts
        try:
            # Use UI_FONT_FAMILY (None for default) and UI_FONT_SIZE for standard UI text
            self.ui_font = pygame.font.Font(config.UI_FONT_FAMILY, config.UI_FONT_SIZE)
            # Use UI_FONT_FAMILY (None for default) and UI_TITLE_FONT_SIZE for larger titles
            self.title_font = pygame.font.Font(config.UI_FONT_FAMILY, config.UI_TITLE_FONT_SIZE)
        except pygame.error as e:
            print(f"Error loading font: {e}. Using default pygame font.")
            # Fallback to pygame's default font with sizes from config
            self.ui_font = pygame.font.Font(None, config.UI_FONT_SIZE)
            self.title_font = pygame.font.Font(None, config.UI_TITLE_FONT_SIZE)


        # Colors
        self.colors = {
            "WHITE": config.WHITE,
            "BLACK": config.BLACK,
            "RED": config.RED,
            "GREEN": config.GREEN,
            "BLUE": config.BLUE,
            # Add more colors as needed
        }

        # Game State and Screen Management
        self.current_game_state = None
        self.current_screen = None

        # Player and Level Assets
        self.player = None
        self.platforms_list = []
        self.monsters_list = []
        self.current_level_index = 0

        # Initial state and screen
        self.set_game_state(STATE_MAIN_MENU)

    def set_game_state(self, new_state):
        if self.current_game_state == new_state:
            return # No change

        self.current_game_state = new_state
        print(f"DEBUG: Setting game state to {new_state}")

        if new_state == STATE_MAIN_MENU:
            self.current_screen = MainMenuScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAMEPLAY:
            # Player should be created/loaded before this screen is set
            if not self.player:
                 # This case should ideally be handled by start_new_game or load_saved_game
                print("DEBUG: Player not initialized before transitioning to GameplayScreen. Creating a new one.")
                # Use PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR from config
                self.player = Player(config.PLAYER_START_X, config.PLAYER_START_Y, 
                                     config.PLAYER_WIDTH, config.PLAYER_HEIGHT, 
                                     config.PLAYER_COLOR, self.sound_manager)
            self.current_screen = GameplayScreen(self.screen, self, self.player, self.platforms_list, self.monsters_list, self.ui_font)
            # GameplayScreen's __init__ or a separate method should handle level loading if needed
            # self.current_screen.start_level(self.current_level_index) # Or similar
        elif new_state == STATE_PAUSED:
            self.current_screen = PauseScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAME_OVER:
            self.current_screen = GameOverScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAME_WON:
            self.current_screen = GameWonScreen(self.screen, self, self.ui_font)
        else:
            print(f"Warning: Unknown game state {new_state}")
            self.current_screen = MainMenuScreen(self.screen, self, self.ui_font) # Fallback to main menu

    def start_new_game(self):
        print("DEBUG: Starting new game...")
        # Use config constants for player creation
        self.player = Player(
            x=config.PLAYER_START_X, 
            y=config.PLAYER_START_Y, 
            width=config.PLAYER_WIDTH, 
            height=config.PLAYER_HEIGHT, 
            color=config.PLAYER_COLOR, # Direct from config
            sound_manager=self.sound_manager
        )
        self.current_level_index = 0
        self.load_level_assets(self.current_level_index) # This populates platforms_list and monsters_list
        self.set_game_state(STATE_GAMEPLAY) # This will create GameplayScreen with the new player and lists
        # If GameplayScreen needs to re-initialize with new player/level data:
        if isinstance(self.current_screen, GameplayScreen):
            self.current_screen.player = self.player
            self.current_screen.platforms = self.platforms_list
            self.current_screen.monsters = self.monsters_list
            # self.current_screen.start_level(self.current_level_index) # If level setup is in GameplayScreen

    def load_saved_game(self):
        print("DEBUG: Attempting to load saved game...")
        if self.load_game_state(): # load_game_state handles player creation/update and current_level_index
            self.load_level_assets(self.current_level_index) # Load assets for the loaded level
            self.set_game_state(STATE_GAMEPLAY)
            # Ensure GameplayScreen uses the loaded player and assets
            if isinstance(self.current_screen, GameplayScreen):
                self.current_screen.player = self.player
                self.current_screen.platforms = self.platforms_list
                self.current_screen.monsters = self.monsters_list
                # self.current_screen.start_level(self.current_level_index)
            print("DEBUG: Game loaded successfully.")
        else:
            print("DEBUG: Failed to load game. Returning to main menu.")
            self.set_game_state(STATE_MAIN_MENU) # Or show an error message on current screen

    def pause_game(self):
        if self.current_game_state == STATE_GAMEPLAY:
            print("DEBUG: Pausing game...")
            self.set_game_state(STATE_PAUSED)

    def resume_game(self):
        if self.current_game_state == STATE_PAUSED:
            print("DEBUG: Resuming game...")
            self.set_game_state(STATE_GAMEPLAY)
            # Ensure GameplayScreen is correctly configured if it was re-instantiated
            # or if its state needs refreshing.
            if isinstance(self.current_screen, GameplayScreen):
                self.current_screen.player = self.player # Ensure it has the correct player instance
                self.current_screen.platforms = self.platforms_list
                self.current_screen.monsters = self.monsters_list


    def go_to_main_menu(self):
        print("DEBUG: Going to main menu...")
        self.set_game_state(STATE_MAIN_MENU)

    def quit_game(self):
        print("DEBUG: Quitting game...")
        self.running = False

    def load_level_assets(self, level_index):
        if not (0 <= level_index < len(config.LEVEL_CONFIGS)):
            print(f"Error: Level index {level_index} out of bounds.")
            self.go_to_main_menu() # Or handle error appropriately
            return

        self.current_level_index = level_index
        level_data = config.LEVEL_CONFIGS[level_index]
        
        self.platforms_list.clear()
        self.monsters_list.clear() # Assuming monsters are also defined in LEVEL_CONFIGS

        for p_data in level_data.get("platforms", []):
            if len(p_data) == 4: # x, y, width, height
                self.platforms_list.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3]))
            elif len(p_data) == 5: # x, y, width, height, color
                self.platforms_list.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3], p_data[4]))
        
        # Example for monsters, if they are defined in config.LEVEL_CONFIGS
        from src.monster import Grunt, Flyer # Import monster classes here to avoid circularity if monsters import Game/config

        for monster_config_group in level_data.get("monsters", []):
            monster_type = monster_config_group["type"]
            count = monster_config_group["count"]
            base_x_positions = monster_config_group.get("x", [100]) # Default x if not specified
            if not isinstance(base_x_positions, list):
                base_x_positions = [base_x_positions] # Ensure it's a list

            y_pos = monster_config_group.get("y") # y should be specified per group or per type default

            # Get drops for this monster group
            drops = monster_config_group.get("drops", [])

            for i in range(count):
                # Determine x position for this specific monster instance
                # If fewer x positions than count, reuse last one or distribute
                current_x = base_x_positions[i % len(base_x_positions)]
                
                if monster_type == "Grunt":
                    stats = config.DEFAULT_GRUNT_STATS.copy()
                    # Override with any specific stats from monster_config_group if needed
                    stats.update({k: v for k, v in monster_config_group.items() if k in stats})
                    # Ensure 'y' is correctly set if not in stats or needs platform adjustment
                    actual_y = y_pos if y_pos is not None else self.screen.get_height() - stats["height"] - 40 # Ground offset
                                        
                    self.monsters_list.append(Grunt(
                        x=current_x, y=actual_y,
                        width=stats["width"], height=stats["height"], color=stats["color"],
                        health=stats["health"], attack_damage=stats["attack_damage"],
                        attack_range=stats["attack_range"], attack_cooldown=stats["attack_cooldown"],
                        speed=stats["speed"], patrol_range_x=stats["patrol_range_x"],
                        gravity_val=config.GRAVITY, screen_height_val=config.SCREEN_HEIGHT,
                        sound_manager=self.sound_manager, # Pass sound_manager
                        possible_drops=drops
                    ))
                elif monster_type == "Flyer":
                    stats = config.DEFAULT_FLYER_STATS.copy()
                    stats.update({k: v for k, v in monster_config_group.items() if k in stats})
                    actual_y = y_pos if y_pos is not None else stats["y_offset"]

                    self.monsters_list.append(Flyer(
                        x=current_x, y=actual_y,
                        width=stats["width"], height=stats["height"], color=stats["color"],
                        health=stats["health"], attack_damage=stats["attack_damage"],
                        attack_range=stats["attack_range"], attack_cooldown=stats["attack_cooldown"],
                        speed=stats["speed"], 
                        vertical_amplitude=stats["vertical_amplitude"],
                        vertical_speed_factor=stats["vertical_speed_factor"],
                        patrol_range_x=stats["patrol_range_x"],
                        y_offset=actual_y, # Pass the calculated y as y_offset for consistency or initial_y
                        sound_manager=self.sound_manager, # Pass sound_manager
                        possible_drops=drops
                    ))
        
        print(f"Assets for level {level_index + 1} loaded. Platforms: {len(self.platforms_list)}, Monsters: {len(self.monsters_list)}")
        
        # If GameplayScreen is active, it needs to be updated with these new assets.
        # This is handled by set_game_state which re-creates GameplayScreen with new lists.
        if self.current_game_state == STATE_GAMEPLAY and isinstance(self.current_screen, GameplayScreen):
             # Update the references in the existing GameplayScreen instance
            self.current_screen.platforms_list = self.platforms_list
            self.current_screen.monsters_list = self.monsters_list
            # self.current_screen.player = self.player # Player instance might also be new if loaded game
            # Consider a method in GameplayScreen to refresh its internal state from these lists


    def set_game_state(self, new_state):
        if self.current_game_state == new_state:
            return

        previous_state = self.current_game_state
        self.current_game_state = new_state
        print(f"DEBUG: Transitioning from {previous_state} to {new_state}")

        # Handle Music Transitions
        if new_state == STATE_MAIN_MENU:
            if previous_state != STATE_MAIN_MENU: # Avoid stopping and restarting if already in main menu (e.g. fallback)
                self.sound_manager.stop_music()
                self.sound_manager.play_music(config.MUSIC_PATH_MAIN_MENU, loops=-1)
        elif new_state == STATE_GAMEPLAY:
            if previous_state == STATE_PAUSED:
                self.sound_manager.unpause_music()
            elif previous_state != STATE_GAMEPLAY: # e.g. from MainMenu, GameOver, GameWon
                self.sound_manager.stop_music() # Ensure any other music (like main menu) is stopped
                self.sound_manager.play_music(config.MUSIC_PATH_GAMEPLAY, loops=-1)
            # If already in STATE_GAMEPLAY (e.g. level transition), music continues
        elif new_state == STATE_PAUSED:
            if previous_state == STATE_GAMEPLAY:
                self.sound_manager.pause_music()
        elif new_state == STATE_GAME_OVER:
            self.sound_manager.stop_music()
            self.sound_manager.play_sound(config.SOUND_GAME_OVER)
        elif new_state == STATE_GAME_WON:
            self.sound_manager.stop_music()
            self.sound_manager.play_sound(config.SOUND_GAME_WON)

        # Set Current Screen
        if new_state == STATE_MAIN_MENU:
            self.current_screen = MainMenuScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAMEPLAY:
            if not self.player: # Should be handled by start_new_game or load_saved_game
                print("CRITICAL: Player not initialized before transitioning to GameplayScreen.")
                self.player = Player(config.PLAYER_START_X, config.PLAYER_START_Y, 
                                     config.PLAYER_WIDTH, config.PLAYER_HEIGHT, 
                                     config.PLAYER_COLOR, self.sound_manager)
            self.current_screen = GameplayScreen(self.screen, self, self.player, self.platforms_list, self.monsters_list, self.ui_font)
        elif new_state == STATE_PAUSED:
            self.current_screen = PauseScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAME_OVER:
            self.current_screen = GameOverScreen(self.screen, self, self.ui_font)
        elif new_state == STATE_GAME_WON:
            self.current_screen = GameWonScreen(self.screen, self, self.ui_font)
        else:
            print(f"Warning: Unknown game state {new_state}. Falling back to Main Menu.")
            self.current_game_state = STATE_MAIN_MENU # Correct the state variable
            self.current_screen = MainMenuScreen(self.screen, self, self.ui_font)
            if not pygame.mixer.music.get_busy() or self.sound_manager.current_music_path != config.MUSIC_PATH_MAIN_MENU:
                self.sound_manager.stop_music() # Ensure other music is stopped
                self.sound_manager.play_music(config.MUSIC_PATH_MAIN_MENU, loops=-1)

    def save_game_state(self, filename=None): # Allow dynamic filename
        if filename is None:
            filename = config.SAVE_GAME_FILENAME # Use from config
        if self.player is None:
            print("DEBUG: Player object does not exist, cannot save game state.")
            return False # Or handle more gracefully, maybe save non-player data

        player_data = {
            "health": self.player.health,
            "max_health": self.player.max_health,
            "level": self.player.level,
            "xp": self.player.experience_points,
            "xp_to_next_level": self.player.xp_to_next_level,
            "inventory": self.player.inventory.get_serializable_data(),
            "position": [self.player.rect.x, self.player.rect.y],
            # Note: Player's width, height, color are usually part of its definition
            # if they are static. If they can change (e.g. power-ups), they should be saved.
        }

        if self.player.pet:
            player_data["pet_data"] = {
                "health": self.player.pet.health,
                "position": [self.player.pet.rect.x, self.player.pet.rect.y]
            }
        
        game_state_data = {
            "current_level_index": self.current_level_index,
            "player_data": player_data,
            # Add other game-wide states here (e.g., game time, overall progress flags)
        }
        
        if self.save_manager.save_data(game_state_data, filename): # Pass filename along
            print(f"Game state saved successfully to {filename}.")
            return True
        else:
            print(f"Failed to save game state to {filename}.")
            return False

    def load_game_state(self, filename=None): # Allow dynamic filename
        if filename is None:
            filename = config.SAVE_GAME_FILENAME # Use from config
        loaded_data = self.save_manager.load_data(filename)
        if loaded_data is None:
            print(f"DEBUG: No save data found at '{filename}' or error loading.")
            return False

        self.current_level_index = loaded_data.get("current_level_index", 0)
        
        loaded_player_data = loaded_data.get("player_data")
        if loaded_player_data:
            player_pos = loaded_player_data.get("position", [config.PLAYER_START_X, config.PLAYER_START_Y])
            # Ensure player instance exists. If not, create it.
            if self.player is None:
                self.player = Player(
                    x=player_pos[0], y=player_pos[1], 
                    width=config.PLAYER_WIDTH, 
                    height=config.PLAYER_HEIGHT, 
                    color=config.PLAYER_COLOR, # Direct from config
                    sound_manager=self.sound_manager
                )
            else: # Player exists, update its position before other attributes
                self.player.rect.x = player_pos[0]
                self.player.rect.y = player_pos[1]

            self.player.level = loaded_player_data.get("level", 1)
            self.player.experience_points = loaded_player_data.get("xp", 0)
            self.player.max_health = loaded_player_data.get("max_health", config.PLAYER_MAX_HEALTH)
            # Ensure xp_to_next_level is correctly calculated or loaded
            # This might involve calling a method on player if it's complex logic
            self.player.xp_to_next_level = loaded_player_data.get("xp_to_next_level", self.player.calculate_xp_for_next_level())
            self.player.health = loaded_player_data.get("health", self.player.max_health)
            
            inventory_data = loaded_player_data.get("inventory")
            if inventory_data is not None and hasattr(self.player, 'inventory'):
                self.player.inventory.load_from_serializable_data(inventory_data)

            # Load pet data if available
            loaded_pet_data = loaded_player_data.get("pet_data")
            if loaded_pet_data and self.player.pet:
                self.player.pet.health = loaded_pet_data.get("health", self.player.pet.health)
                pet_pos = loaded_pet_data.get("position")
                if pet_pos and len(pet_pos) == 2:
                    self.player.pet.rect.x = pet_pos[0]
                    self.player.pet.rect.y = pet_pos[1]
                print("Pet data loaded and applied.")
            elif loaded_pet_data and not self.player.pet:
                # This case is less likely if Pet is always created with Player.
                # If it can happen, one might recreate the pet here.
                print("Warning: Pet data found in save, but no Pet instance on Player.")
            
            print("Player data loaded and applied.")
        else:
            print("Warning: No player data found in save file. Player state not restored.")
            # If no player data, and self.player is None, a new default player is created by start_new_game or by direct transition to Gameplay.
            # If self.player exists but no data for it, it keeps its current state. This path implies an issue with the save file.

        print(f"Game state loaded from {filename}. Current level index: {self.current_level_index}")
        return True

    @staticmethod
    def draw_text(surface, text, size, x, y, color=config.WHITE, font_name=None, font_object=None):
        # Priority: 1. Provided font_object, 2. font_name, 3. default font
        if font_object:
            current_font = font_object
        elif font_name:
            try:
                current_font = pygame.font.Font(font_name, size)
            except pygame.error:
                current_font = pygame.font.Font(None, size) # Fallback to default
        else:
            current_font = pygame.font.Font(None, size) # Default font

        text_surface = current_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)


    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_game() # Use the new method
                
                if self.current_screen:
                    self.current_screen.handle_event(event) # Pass single event

            if not self.running: # Check if quit_game was called
                break

            if self.current_screen:
                self.current_screen.update(dt)

            self.screen.fill(self.colors.get("BLACK", config.BLACK)) # Use defined color
            if self.current_screen:
                self.current_screen.draw() # Screens should draw on the surface passed to them
            
            pygame.display.flip()

        pygame.quit()
