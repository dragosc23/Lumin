import pygame
from src.ui_elements import Button # Assuming Button is in ui_elements.py
import os # Standard practice to import at the top
import math # For Flyer's vertical bobbing in GameplayScreen's conceptual _load_level_logic

import pygame
import config # Import config
from src.ui_elements import Button
import os
import math
import random # Added for loot drop chance

from src.items import create_item_from_dict # For creating item instances from drops

# Note: The BaseScreen in the provided code uses game_manager for screen, fonts, colors.
# This refactoring will assume game_manager provides these, initialized from config.
# The screen classes will directly use config for values not expected to change dynamically
# or not part of the game_manager's direct responsibility (like specific screen bg colors).

class BaseScreen:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.screen = game_manager.screen # Convenience
        self.ui_font = game_manager.ui_font # Standard UI font from Game
        self.title_font = game_manager.title_font # Title font from Game
        self.sound_manager = game_manager.sound_manager

    def handle_event(self, event): # Changed from handle_events to match Game's loop
        """Process a single event."""
        pass

    def update(self, dt):
        """Update game state for this screen. dt is delta time in seconds."""
        pass

    def draw(self): # Changed from render(surface) to draw(), surface is self.screen
        """Draw everything on this screen."""
        pass


class MainMenuScreen(BaseScreen):
    def __init__(self, screen_surface, game_manager, font_object): # Matching Game's instantiation
        super().__init__(game_manager)
        # font_object is game_manager.ui_font, already set in BaseScreen
        # self.font = font_object # This would be game_manager.ui_font

        button_width = 250 # This could be a config value, e.g., config.UI_BUTTON_WIDTH
        button_height = config.UI_BUTTON_HEIGHT
        spacing = config.UI_BUTTON_PADDING
        
        num_buttons = 2
        # Check for save file using game_manager's save_manager and config filename
        if self.game_manager.save_manager and os.path.exists(config.SAVE_GAME_FILENAME):
            num_buttons = 3
        
        total_button_height = (button_height * num_buttons) + (spacing * (num_buttons - 1))
        start_y = self.screen.get_height() // 2 - total_button_height // 2

        self.buttons = []
        current_y = start_y

        self.buttons.append(Button(
            text="New Game",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, current_y, button_width, button_height),
            font=self.ui_font, # Use font from BaseScreen
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.start_new_game
        ))
        current_y += button_height + spacing

        if self.game_manager.save_manager and os.path.exists(config.SAVE_GAME_FILENAME):
            self.buttons.append(Button(
                text="Load Game",
                rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, current_y, button_width, button_height),
                font=self.ui_font,
                text_color=config.UI_BUTTON_TEXT_COLOR,
                button_color=config.UI_BUTTON_COLOR, # Could vary this for different buttons
                hover_color=config.UI_BUTTON_HOVER_COLOR,
                sound_manager=self.sound_manager,
                action=self.game_manager.load_saved_game
            ))
            current_y += button_height + spacing

        self.buttons.append(Button(
            text="Quit",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, current_y, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR, # Could vary this
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.quit_game
        ))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game_manager.quit_game()
        for button in self.buttons:
            if button.handle_event(event): # Button itself plays the sound
                # self.sound_manager.play_sound(config.SOUND_UI_CLICK) # Removed
                break 

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(config.MAIN_MENU_BG_COLOR) 
        # Use title_font from BaseScreen (initialized from game_manager)
        # game_manager.draw_text is static, so can be called via class or instance
        self.game_manager.draw_text(
            self.screen, "My Autobattler Game", 
            config.UI_TITLE_FONT_SIZE, # Size from config
            self.screen.get_width() // 2, 
            self.screen.get_height() // 4, 
            color=config.WHITE, # Text color from config
            font_object=self.title_font # Pass the specific font object
        )

        for button in self.buttons:
            button.draw(self.screen)

class PauseScreen(BaseScreen):
    def __init__(self, screen_surface, game_manager, font_object): # Matching Game's instantiation
        super().__init__(game_manager)
        # self.font = font_object # game_manager.ui_font, already in BaseScreen.ui_font
        # self.title_font is game_manager.title_font from BaseScreen

        button_width = 250 # config.UI_BUTTON_WIDTH
        button_height = config.UI_BUTTON_HEIGHT
        spacing = config.UI_BUTTON_PADDING
        start_y = self.screen.get_height() // 2 - (button_height * 2 + spacing * 1) // 2

        self.buttons = []
        self.buttons.append(Button(
            text="Resume",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.resume_game 
        ))

        self.buttons.append(Button(
            text="Quit to Main Menu",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.go_to_main_menu 
        ))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game_manager.quit_game() 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                if self.sound_manager: 
                    self.sound_manager.play_sound(config.SOUND_UI_CLICK) 
                self.game_manager.resume_game()
                return 

        for button in self.buttons:
            if button.handle_event(event): # Button itself plays the sound
                # self.sound_manager.play_sound(config.SOUND_UI_CLICK) # Removed
                break 

    def update(self, dt):
        pass 

    def draw(self):
        # Draw current gameplay screen underneath (optional, if not done by Game class)
        # For now, Game class fills background then calls screen.draw().
        # So, GameplayScreen would have drawn. PauseScreen just overlays.
        
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill(config.PAUSE_OVERLAY_COLOR) 
        self.screen.blit(overlay, (0,0)) 

        self.game_manager.draw_text(
            self.screen, "Paused", 
            config.UI_PAUSED_FONT_SIZE, 
            self.screen.get_width() // 2, 
            self.screen.get_height() // 3, 
            color=config.WHITE,
            font_object=self.title_font # Use larger title font for "Paused"
        )

        for button in self.buttons:
            button.draw(self.screen)

class GameplayScreen(BaseScreen):
    # Parameters match Game's instantiation of GameplayScreen
    def __init__(self, screen_surface, game_manager, player, platforms, monsters, font_object):
        super().__init__(game_manager)
        self.player = player # game_manager.player
        self.monsters_list = monsters # game_manager.monsters_list
        self.platforms_list = platforms # game_manager.platforms_list
        # self.ui_font is from BaseScreen (game_manager.ui_font)
        
        # Colors are accessed via config directly or through game_manager.colors if dynamic
        # self.HIT_COLOR = config.HIT_COLOR # Direct from config

        # If this screen needs to load/reload level assets, it should use game_manager methods
        # self._load_level_logic(self.game_manager.current_level_index) # Example: initial load if game starts here
        # Game.set_game_state for STATE_GAMEPLAY now handles player and asset setup *before* creating GameplayScreen.
        # GameplayScreen receives them ready.

    # _load_level_logic is mostly moved to Game.load_level_assets and Game.start_new_game/load_saved_game
    # Monster instantiation details remain a concern for config usage.

    def handle_event(self, event): # Changed from handle_events
        if event.type == pygame.QUIT:
            self.game_manager.quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.game_manager.pause_game() # Transition to PauseScreen
                return 
            if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.player.is_jumping:
                self.player.is_jumping = True
                self.player.velocity_y = config.JUMP_STRENGTH # Use config
                if self.player.sound_manager:
                    self.player.sound_manager.play_sound(config.SOUND_PLAYER_JUMP) # Use config key
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Example attack key
                self.player.attempt_attack(self.monsters_list)


        keys = pygame.key.get_pressed()
        player_dx = 0
        if keys[pygame.K_LEFT]:
            player_dx -= self.player.speed # Player speed already from config via Player class
        if keys[pygame.K_RIGHT]:
            player_dx += self.player.speed
        
        # Player.move now handles horizontal platform collision
        self.player.move(player_dx, 0, self.platforms_list)


    def update_monsters(self, dt):
        """Handles monster updates, death, and XP/drop mechanics."""
        for monster in list(self.monsters_list): # Iterate on a copy if modifying list
            if monster.health <= 0:
                # Award XP
                self.player.gain_xp(config.XP_PER_MONSTER_DEFEAT) # Use config
                
                # Handle drops
                if monster.possible_drops:
                    for drop_info in monster.possible_drops:
                        if random.random() < drop_info["chance"]:
                            item_id = drop_info["item_id"]
                            quantity = drop_info.get("quantity", 1) # Default to 1 if not specified
                            
                            base_item_config = config.GENERIC_ITEM_DEFAULTS.get(item_id)
                            if not base_item_config:
                                print(f"Warning: Item ID '{item_id}' not found in GENERIC_ITEM_DEFAULTS.")
                                continue

                            # Determine the class name for item creation
                            # This could be stored in GENERIC_ITEM_DEFAULTS or inferred
                            item_class_name = "Item" # Default to base Item class
                            if item_id == "HealthPotion": # Specific case
                                item_class_name = "HealthPotion"
                            # Add more specific items here if they have their own classes
                            # Or, better: add "item_class_name" to GENERIC_ITEM_DEFAULTS entries

                            item_data_for_creation = base_item_config.copy()
                            item_data_for_creation["item_class_name"] = item_class_name 
                            # name, description, value etc. are already in item_data_for_creation

                            new_item_instance = create_item_from_dict(item_data_for_creation)
                            
                            if new_item_instance:
                                # The add_item method in InventoryManager handles stacking.
                                # It needs the item instance and the quantity to add.
                                self.player.inventory.add_item(new_item_instance, quantity)
                                print(f"Player obtained {quantity}x {new_item_instance.name}!")
                                if self.sound_manager:
                                    self.sound_manager.play_sound(config.SOUND_ITEM_PICKUP)
                            else:
                                print(f"Warning: Could not create item instance for {item_id}.")
                
                self.monsters_list.remove(monster)
                if self.sound_manager:
                    self.sound_manager.play_sound(config.SOUND_MONSTER_DEATH) # Use config key
                print(f"Monster (ID: {id(monster)}) removed.")
            else:
                monster.update(self.platforms_list, self.player)


    def update(self, dt):
        self.player.update(self.platforms_list, self.monsters_list) 
        if self.player.pet:
            self.player.pet.update(self.platforms_list, self.monsters_list, self.player)

        self.update_monsters(dt) # Call new monster update method
        
        if not self.monsters_list and self.player.health > 0: # Check if all monsters are defeated
            print(f"Level {self.game_manager.current_level_index + 1} cleared!")
            self.game_manager.current_level_index += 1
            if self.game_manager.current_level_index < len(config.LEVEL_CONFIGS):
                # Game manager should handle loading next level's assets and then
                # potentially re-configuring this screen or transitioning.
                # For now, let's assume Game.start_new_game or similar would be called by a higher logic
                # or GameplayScreen tells Game to load next level.
                self.game_manager.load_level_assets(self.game_manager.current_level_index)
                # Player position might need resetting by game_manager or here
                self.player.rect.topleft = (config.PLAYER_START_X, config.PLAYER_START_Y)
                # If GameplayScreen needs to be "restarted" for the new level data:
                # self.game_manager.set_game_state(config.STATE_GAMEPLAY) might be one way if it reconstructs.
            else:
                print("Congratulations! All levels completed!")
                self.game_manager.set_game_state(config.STATE_GAME_WON) 
                return

        if self.player.health <= 0:
            print("Game Over! Player has been defeated.")
            self.game_manager.set_game_state(config.STATE_GAME_OVER) 

    def draw(self):
        self.screen.fill(config.BLACK) # Use config color
        for plat in self.platforms_list: # Use the list passed in __init__
            plat.draw(self.screen)
        
        self.player.draw(self.screen)
        if self.player.pet:
            self.player.pet.draw(self.screen)

        for monster in self.monsters_list: # Use the list passed in __init__
            monster.draw(self.screen) # Monster.draw now uses config.HIT_COLOR internally

        # UI Text (Health, Level, XP, Inventory)
        # game_manager.draw_text is static, can be called via self.game_manager
        
        # Health
        health_text = f"Health: {self.player.health}/{self.player.max_health}"
        self.game_manager.draw_text(self.screen, health_text, config.UI_FONT_SIZE, 10, 10, 
                                    color=config.WHITE, font_object=self.ui_font)

        # Level
        level_text = f"Level: {self.player.level}"
        self.game_manager.draw_text(self.screen, level_text, config.UI_FONT_SIZE, 10, 40, 
                                    color=config.WHITE, font_object=self.ui_font)

        # XP Display
        xp_text = f"XP: {self.player.experience_points} / {self.player.xp_to_next_level}"
        xp_text_y_position = 70 
        self.game_manager.draw_text(self.screen, xp_text, config.UI_FONT_SIZE, 10, xp_text_y_position, 
                                    color=config.WHITE, font_object=self.ui_font)

        # Inventory Display
        inventory_y_start = xp_text_y_position + 30 
        line_height = config.UI_FONT_SIZE + 5 # Dynamic line height based on font

        if hasattr(self.player, 'inventory') and hasattr(self.player.inventory, 'get_all_items'):
            item_slots = self.player.inventory.get_all_items()
            
            inventory_title_text = "Inventory:"
            self.game_manager.draw_text(self.screen, inventory_title_text, config.UI_FONT_SIZE,
                                        10, inventory_y_start, color=config.WHITE, font_object=self.ui_font)
            
            if not item_slots:
                inventory_empty_text = "  Empty"
                self.game_manager.draw_text(self.screen, inventory_empty_text, config.UI_FONT_SIZE, 
                                            10, inventory_y_start + line_height, color=config.WHITE, font_object=self.ui_font)
            else:
                current_y = inventory_y_start + line_height
                for slot_idx, slot in enumerate(item_slots):
                    item = slot.get('item')
                    quantity = slot.get('quantity')
                    if item and quantity is not None: 
                        item_line = f"  {slot_idx+1}. {item.name}: {quantity}" # Numbered list
                        self.game_manager.draw_text(self.screen, item_line, config.UI_FONT_SIZE, 
                                                    10, current_y, color=config.WHITE, font_object=self.ui_font)
                        current_y += line_height
                        if current_y > self.screen.get_height() - 20: 
                            break 
        else:
            self.game_manager.draw_text(self.screen, "Inventory: N/A", config.UI_FONT_SIZE,
                                        10, inventory_y_start, color=config.RED, font_object=self.ui_font)


class GameOverScreen(BaseScreen):
    def __init__(self, screen_surface, game_manager, font_object): # Matching Game's instantiation
        super().__init__(game_manager)
        # self.title_font is from BaseScreen (game_manager.title_font)
        # self.button_font is self.ui_font from BaseScreen (game_manager.ui_font)
        
        self.message_font = self.ui_font # For "Better luck next time"
        self.message_color = config.WHITE
        self.title_color = config.RED
        self.background_color = config.GAME_OVER_BG_COLOR # From config

        button_width = 250 # config.UI_BUTTON_WIDTH
        button_height = config.UI_BUTTON_HEIGHT
        spacing = config.UI_BUTTON_PADDING
        start_y = self.screen.get_height() // 2 

        self.buttons = []
        self.buttons.append(Button(
            text="Try Again",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y, button_width, button_height),
            font=self.ui_font, # Button font is standard UI font
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.start_new_game
        ))

        self.buttons.append(Button(
            text="Main Menu",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.go_to_main_menu 
        ))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game_manager.quit_game()
        for button in self.buttons:
            if button.handle_event(event): # Button itself plays the sound
                # self.sound_manager.play_sound(config.SOUND_UI_CLICK) # Removed
                break

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(self.background_color) 
        
        self.game_manager.draw_text(
            self.screen, "Game Over", 
            config.UI_GAME_OVER_FONT_SIZE, 
            self.screen.get_width() // 2, 
            self.screen.get_height() // 3, 
            color=self.title_color,
            font_object=self.game_manager.title_font # Use the larger title font from game_manager
        )

        self.game_manager.draw_text(
            self.screen, "Better luck next time!", 
            config.UI_SUBTITLE_FONT_SIZE, # Subtitle size
            self.screen.get_width() // 2, 
            self.screen.get_height() // 3 + config.UI_GAME_OVER_FONT_SIZE // 2 + 10, # Position below title
            color=self.message_color,
            font_object=self.ui_font # Regular UI font for subtitle
        )

        for button in self.buttons:
            button.draw(self.screen)

class GameWonScreen(BaseScreen): # New Screen
    def __init__(self, screen_surface, game_manager, font_object):
        super().__init__(game_manager)
        self.message_font = self.ui_font
        self.message_color = config.WHITE
        self.title_color = config.GREEN # Green for winning
        self.background_color = config.GAME_WON_BG_COLOR

        button_width = 250 # config.UI_BUTTON_WIDTH
        button_height = config.UI_BUTTON_HEIGHT
        spacing = config.UI_BUTTON_PADDING
        
        # Position buttons: Play Again above Main Menu
        total_buttons_height = (button_height * 2) + spacing
        start_y = self.screen.get_height() // 2 + 50 # Start buttons lower to make space for title
        
        self.buttons = []

        # Play Again Button
        play_again_button_y = start_y
        self.buttons.append(Button(
            text="Play Again",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, play_again_button_y, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.start_new_game # Action to start a new game
        ))

        # Main Menu Button
        main_menu_button_y = play_again_button_y + button_height + spacing
        self.buttons.append(Button(
            text="Main Menu",
            rect=pygame.Rect(self.screen.get_width() // 2 - button_width // 2, main_menu_button_y, button_width, button_height),
            font=self.ui_font,
            text_color=config.UI_BUTTON_TEXT_COLOR,
            button_color=config.UI_BUTTON_COLOR,
            hover_color=config.UI_BUTTON_HOVER_COLOR,
            sound_manager=self.sound_manager,
            action=self.game_manager.go_to_main_menu
        ))


    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game_manager.quit_game()
        for button in self.buttons:
            if button.handle_event(event): # Button itself plays the sound
                # self.sound_manager.play_sound(config.SOUND_UI_CLICK) # Removed
                break # Event handled

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(self.background_color)
        
        self.game_manager.draw_text(
            self.screen, "You Won!", 
            config.UI_GAME_OVER_FONT_SIZE, # Same large size as Game Over
            self.screen.get_width() // 2, 
            self.screen.get_height() // 3, 
            color=self.title_color,
            font_object=self.game_manager.title_font # Use large title font
        )

        self.game_manager.draw_text(
            self.screen, "Congratulations!", 
            config.UI_SUBTITLE_FONT_SIZE, 
            self.screen.get_width() // 2, 
            self.screen.get_height() // 3 + config.UI_GAME_OVER_FONT_SIZE // 2 + 10, 
            color=self.message_color,
            font_object=self.ui_font
        )
        for button in self.buttons:
            button.draw(self.screen)
