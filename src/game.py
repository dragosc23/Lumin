import pygame

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

    def save_game_state(self, filename="savegame.json"):
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
            # Note: Player's width, height, color are usually part of its definition,
            # not dynamic state, unless they can change and need saving.
        }
        
        game_state_data = {
            "current_level_index": self.current_level_index,
            "player_data": player_data,
            # Add other game-wide states here if necessary (e.g., game time, overall progress flags)
        }
        
        if self.save_manager.save_data(game_state_data): # Filename can be passed if dynamic
            print(f"Game state saved successfully to {self.save_manager.save_filename}.")
            return True
        else:
            print("Failed to save game state.")
            return False

    def load_game_state(self, filename="savegame.json"):
        loaded_data = self.save_manager.load_data() # Filename can be passed
        if loaded_data is None:
            print("DEBUG: No save data found or error loading.")
            # Optionally, start a new game or return to main menu
            # self.start_new_game() # Example method call
            return False

        self.current_level_index = loaded_data.get("current_level_index", 0)
        
        loaded_player_data = loaded_data.get("player_data")
        if loaded_player_data:
            # If player doesn't exist (e.g. loading from main menu directly into game)
            # it needs to be created. This assumes Player constructor can handle it.
            # For a robust system, GameplayScreen might handle player creation.
            # For now, let's assume player is typically created by a screen transition
            # and we are just updating its state. If not, player creation logic is needed here.
            if self.player is None:
                print("DEBUG: Player object is None during load_game_state. Creating new Player instance.")
                # This is a simplified creation. Player needs x,y,width,height,color.
                # Position will be overwritten by save file. Other params might come from config.
                # This part is tricky if load_game_state is called when no player context exists.
                # A common pattern is that GameplayScreen creates the player, then Game.load_game_state updates it.
                # Or, Game.load_game_state signals to GameplayScreen to create player *then* apply data.
                # For now, assuming player exists OR we create a default one and immediately update.
                player_pos = loaded_player_data.get("position", [config.PLAYER_START_X, config.PLAYER_START_Y])
                self.player = Player(x=player_pos[0], y=player_pos[1], 
                                     width=40, height=50, color=config.GREEN) # Example default values
                                     # TODO: width, height, color should ideally come from config or be more robustly defined

            self.player.level = loaded_player_data.get("level", 1)
            self.player.experience_points = loaded_player_data.get("xp", 0)
            self.player.max_health = loaded_player_data.get("max_health", config.PLAYER_MAX_HEALTH)
            # Recalculate xp_to_next_level based on loaded level, or load it if saved precisely
            self.player.xp_to_next_level = loaded_player_data.get("xp_to_next_level", config.XP_PER_LEVEL_BASE * self.player.level)
            self.player.health = loaded_player_data.get("health", self.player.max_health)
            
            # Position
            player_pos = loaded_player_data.get("position")
            if player_pos and len(player_pos) == 2:
                self.player.rect.x = player_pos[0]
                self.player.rect.y = player_pos[1]
            
            # Inventory
            inventory_data = loaded_player_data.get("inventory")
            if inventory_data is not None and hasattr(self.player, 'inventory'):
                self.player.inventory.load_from_serializable_data(inventory_data)
            
            print("Player data loaded and applied.")
        else:
            print("Warning: No player data found in save file.")
            # Decide how to handle this: new player, error, etc.

        # After loading, you might want to load the level entities, switch screens, etc.
        # For example, directly loading into gameplay:
        # self.load_level(self.current_level_index) # This would populate platforms/monsters
        # from src.screens import GameplayScreen # Careful with import cycles
        # self.current_screen = GameplayScreen(self.screen, self, self.player) # Assuming GameplayScreen takes player
        
        print(f"Game state loaded. Current level index: {self.current_level_index}")
        return True

    @staticmethod
    def draw_text(surface, text, size, x, y, color=config.WHITE, font_name=None):
        # If a specific font name is provided, try to load it. Otherwise, use default system font.
        if font_name:
            font = pygame.font.Font(font_name, size)
        else:
            font = pygame.font.Font(None, size) # Default font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y) # Or other positioning as needed, e.g. topleft
        surface.blit(text_surface, text_rect)

    def load_level(self, level_index):
        if 0 <= level_index < len(config.LEVEL_CONFIGS):
            self.current_level_index = level_index
            level_data = config.LEVEL_CONFIGS[level_index]
            
            # Reset/initialize game elements for the new level
            self.platforms = [] # Placeholder for platform objects
            self.monsters = []  # Placeholder for monster objects
            # self.player = Player(...) # Re-initialize player for the level

            # Example of processing level_data (actual implementation will depend on entity classes)
            for p_data in level_data.get("platforms", []):
                # Ensure p_data from config matches Platform constructor (x, y, width, height, [color])
                if len(p_data) == 4: # x, y, width, height
                    self.platforms.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3]))
                elif len(p_data) == 5: # x, y, width, height, color
                    self.platforms.append(Platform(p_data[0], p_data[1], p_data[2], p_data[3], p_data[4]))
            # for m_data in level_data.get("monsters", []):
            #     self.monsters.append(Monster(*m_data)) # Assuming a Monster class
            
            print(f"Loading level {level_index + 1}")
            # Potentially switch to GameplayScreen here if not already on it
            # from src.screens import GameplayScreen # Example, careful with circular imports
            # self.current_screen = GameplayScreen(self.screen, self)
        else:
            print(f"Error: Level index {level_index} out of bounds.")
            # Optionally, go to a game over screen or main menu
            # from src.screens import MainMenuScreen # Example
            # self.current_screen = MainMenuScreen(self.screen, self)


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
