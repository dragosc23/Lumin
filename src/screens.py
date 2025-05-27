import pygame
from src.ui_elements import Button # Assuming Button is in ui_elements.py
import os # Standard practice to import at the top
import math # For Flyer's vertical bobbing in GameplayScreen's conceptual _load_level_logic
import random # For item drop chance
from src.items import create_item_from_dict, ITEM_CLASS_MAP # For creating item instances
import config # For GENERIC_ITEM_DEFAULTS if needed for item creation
import logging

# Logger for this module
logger = logging.getLogger(__name__)

class BaseScreen:
    def __init__(self, game_manager):
        self.game_manager = game_manager # To interact with main game logic (e.g., change state, access managers)

    def handle_events(self, events):
        """Process all events from the Pygame event queue."""
        pass

    def update(self, dt):
        """Update game state for this screen. dt is delta time in seconds."""
        pass

    def render(self, surface):
        """Draw everything on this screen."""
        pass


class MainMenuScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = self.game_manager.ui_font # Get font from game_manager
        self.sound_manager = self.game_manager.sound_manager # Get sound_manager
        self.confirming_new_game = False
        self.showing_offline_summary = False # New state for offline summary
        self.offline_summary_details = None  # To store details from game_manager

        button_width = config.MAIN_MENU_BUTTON_WIDTH
        button_height = config.MAIN_MENU_BUTTON_HEIGHT
        spacing = config.MAIN_MENU_BUTTON_SPACING
        # Adjusted start_y to dynamically calculate based on number of buttons
        num_buttons = 2
        if self.game_manager.save_manager and os.path.exists(self.game_manager.save_manager.save_filename):
            num_buttons = 3
        
        total_button_height = (button_height * num_buttons) + (spacing * (num_buttons - 1))
        start_y = self.game_manager.screen_height // 2 - total_button_height // 2


        self.buttons = []
        current_y = start_y

        self.buttons.append(Button(
            text="New Game",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, current_y, button_width, button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(0, 150, 0),
            hover_color=(0, 200, 0),
            sound_manager=self.sound_manager,
            action=self.handle_new_game_press # Changed action
        ))
        self.new_game_button_ref = self.buttons[-1] # Keep a reference if needed later
        current_y += button_height + spacing

        if self.game_manager.save_manager and os.path.exists(self.game_manager.save_manager.save_filename):
            self.buttons.append(Button(
                text="Load Game",
                rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, current_y, button_width, button_height),
                font=self.font,
                text_color=(255, 255, 255),
                button_color=(0, 0, 150),
                hover_color=(0, 0, 200),
                sound_manager=self.sound_manager,
                action=self.game_manager.load_saved_game
            ))
            current_y += button_height + spacing

        self.buttons.append(Button(
            text="Quit",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, current_y, button_width, button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(150, 0, 0),
            hover_color=(200, 0, 0),
            sound_manager=self.sound_manager,
            action=self.game_manager.quit_game
        ))

        # Confirmation Dialog Buttons
        confirm_button_width = config.CONFIRM_DIALOG_BUTTON_WIDTH
        confirm_button_height = config.CONFIRM_DIALOG_BUTTON_HEIGHT
        confirm_spacing = config.CONFIRM_DIALOG_BUTTON_SPACING
        dialog_center_x = self.game_manager.screen_width // 2
        dialog_center_y = self.game_manager.screen_height // 2

        self.confirm_yes_button = Button(
            text="Yes, Overwrite",
            rect=pygame.Rect(dialog_center_x - confirm_button_width - confirm_spacing // 2, dialog_center_y + 30, confirm_button_width, confirm_button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(180, 0, 0), # Reddish for confirmation
            hover_color=(220, 0, 0),
            sound_manager=self.sound_manager,
            action=self.confirm_new_game_yes
        )
        self.confirm_no_button = Button(
            text="No, Cancel",
            rect=pygame.Rect(dialog_center_x + confirm_spacing // 2, dialog_center_y + 30, confirm_button_width, confirm_button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(80, 80, 80), # Grayish
            hover_color=(120, 120, 120),
            sound_manager=self.sound_manager,
            action=self.confirm_new_game_no
        )
        self.confirmation_buttons = [self.confirm_yes_button, self.confirm_no_button]
        self.confirmation_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.CONFIRM_DIALOG_FONT_SIZE)
        
        # Offline Summary Pop-up elements
        self.summary_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.UI_FONT_SIZE) # Using general UI_FONT_SIZE for details
        summary_button_width = 200
        summary_button_height = 50
        summary_center_x = self.game_manager.screen_width // 2
        summary_center_y = self.game_manager.screen_height // 2
        
        self.dismiss_summary_button = Button(
            text="Okay",
            rect=pygame.Rect(summary_center_x - summary_button_width // 2, summary_center_y + 60, summary_button_width, summary_button_height),
            font=self.font,
            text_color=config.WHITE,
            button_color=(0, 100, 0), # Greenish
            hover_color=(0, 150, 0),
            sound_manager=self.sound_manager,
            action=self.dismiss_offline_summary
        )

    def dismiss_offline_summary(self):
        self.showing_offline_summary = False
        self.offline_summary_details = None # Clear details
        if self.game_manager: # Clear the flag in game_manager
            self.game_manager.offline_rewards_to_display = None
        if self.sound_manager:
            self.sound_manager.play_sound("ui_click")

    def handle_new_game_press(self):
        if self.game_manager.save_manager and os.path.exists(self.game_manager.save_manager.save_filename):
            self.confirming_new_game = True
            if self.sound_manager: self.sound_manager.play_sound("ui_prompt") # Optional: sound for prompt
        else:
            self.game_manager.start_new_game()

    def confirm_new_game_yes(self):
        self.game_manager.start_new_game()
        self.confirming_new_game = False

    def confirm_new_game_no(self):
        self.confirming_new_game = False
        if self.sound_manager: self.sound_manager.play_sound("ui_cancel") # Optional: sound for cancel

    def handle_events(self, events):
        if self.showing_offline_summary:
            for event in events:
                if event.type == pygame.QUIT:
                    self.game_manager.quit_game()
                if self.dismiss_summary_button.handle_event(event):
                    return # Event handled by dismiss button
        elif self.confirming_new_game:
            for event in events:
                if event.type == pygame.QUIT:
                    self.game_manager.quit_game()
                for button in self.confirmation_buttons:
                    if button.handle_event(event):
                        return # Event handled by confirmation button
        else:
            for event in events:
                if event.type == pygame.QUIT: # Allow quitting from menu via window X
                    self.game_manager.quit_game()
                for button in self.buttons:
                    if button.handle_event(event):
                        break # Event handled by a main menu button

    def update(self, dt):
        # Check for offline summary data at the start of update/render cycle
        if self.game_manager and hasattr(self.game_manager, 'offline_rewards_to_display') and \
           self.game_manager.offline_rewards_to_display and not self.showing_offline_summary:
            self.offline_summary_details = self.game_manager.offline_rewards_to_display.copy()
            self.showing_offline_summary = True
            # Optional: Play a sound when the summary appears
            # if self.sound_manager: self.sound_manager.play_sound("summary_appears")


    def render(self, surface):
        surface.fill((50, 50, 70)) # TODO: Make this a config constant if desired, e.g., config.MAIN_MENU_BG_COLOR
        title_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.TITLE_FONT_SIZE)
        title_surface = title_font.render(config.GAME_TITLE, True, (200, 200, 255)) # Using game title from config; color can be config
        title_rect = title_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 4))
        surface.blit(title_surface, title_rect)

        # Render main menu buttons (they will be overlaid if a dialog is active)
        for button in self.buttons:
            button.draw(surface)

        if self.showing_offline_summary and self.offline_summary_details:
            # Draw overlay for offline summary
            overlay = pygame.Surface((self.game_manager.screen_width, self.game_manager.screen_height), pygame.SRCALPHA)
            overlay.fill(config.CONFIRM_DIALOG_OVERLAY_COLOR_ALPHA) # Using same overlay as confirm for now
            surface.blit(overlay, (0,0))

            # Offline Summary Dialog
            summary_title_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.CONFIRM_DIALOG_FONT_SIZE) # Using confirm dialog font size for title
            summary_title_surface = summary_title_font.render("Offline Progress!", True, config.WHITE)
            summary_title_rect = summary_title_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 2 - 80))
            surface.blit(summary_title_surface, summary_title_rect)

            gold_text = f"Gold Earned: {self.offline_summary_details.get('gold_earned', 0)}"
            gold_surface = self.summary_font.render(gold_text, True, config.WHITE)
            gold_rect = gold_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 2 - 30))
            surface.blit(gold_surface, gold_rect)

            xp_text = f"XP Earned: {self.offline_summary_details.get('xp_earned', 0)}"
            xp_surface = self.summary_font.render(xp_text, True, config.WHITE)
            xp_rect = xp_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 2 + 10))
            surface.blit(xp_surface, xp_rect)
            
            self.dismiss_summary_button.draw(surface)

        elif self.confirming_new_game:
            # Draw semi-transparent overlay for new game confirmation
            overlay = pygame.Surface((self.game_manager.screen_width, self.game_manager.screen_height), pygame.SRCALPHA)
            overlay.fill(config.CONFIRM_DIALOG_OVERLAY_COLOR_ALPHA) 
            surface.blit(overlay, (0, 0))

            # Draw confirmation message
            msg_text = config.CONFIRM_NEW_GAME_MESSAGE
            msg_surface = self.confirmation_font.render(msg_text, True, (255, 255, 255)) # Text color can be config
            msg_rect = msg_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 2 - 40))
            surface.blit(msg_surface, msg_rect)

            # Draw confirmation buttons
            for button in self.confirmation_buttons:
                button.draw(surface)
        # If neither summary nor confirmation is active, main menu buttons are already drawn.

class PauseScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = self.game_manager.ui_font 
        self.title_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.PAUSED_FONT_SIZE) 
        self.sound_manager = self.game_manager.sound_manager

        button_width = config.PAUSE_MENU_BUTTON_WIDTH
        button_height = config.PAUSE_MENU_BUTTON_HEIGHT
        spacing = config.PAUSE_MENU_BUTTON_SPACING
        start_y = self.game_manager.screen_height // 2 - (button_height * 2 + spacing * 1) // 2

        self.buttons = []
        self.buttons.append(Button(
            text="Resume",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, start_y, button_width, button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(0, 150, 0),
            hover_color=(0, 200, 0),
            sound_manager=self.sound_manager,
            action=self.game_manager.resume_game 
        ))

        self.buttons.append(Button(
            text="Quit to Main Menu",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height),
            font=self.font,
            text_color=(255, 255, 255),
            button_color=(150, 0, 0),
            hover_color=(200, 0, 0),
            sound_manager=self.sound_manager,
            action=self.game_manager.go_to_main_menu 
        ))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game_manager.quit_game() 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.sound_manager: 
                        self.sound_manager.play_sound("ui_click") 
                    self.game_manager.resume_game()
                    return 

            for button in self.buttons:
                if button.handle_event(event):
                    break 

    def update(self, dt):
        pass 

    def render(self, surface):
        overlay = pygame.Surface((self.game_manager.screen_width, self.game_manager.screen_height), pygame.SRCALPHA)
        overlay.fill(config.PAUSE_SCREEN_OVERLAY_COLOR_ALPHA) 
        surface.blit(overlay, (0,0)) 

        paused_text_surface = self.title_font.render("Paused", True, (255, 255, 255)) # Text color can be from config
        paused_text_rect = paused_text_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 3))
        surface.blit(paused_text_surface, paused_text_rect)

        for button in self.buttons:
            button.draw(surface)

class GameplayScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.player = self.game_manager.player
        self.monsters = self.game_manager.monsters_list 
        self.platforms = self.game_manager.platforms_list
        self.sound_manager = self.game_manager.sound_manager
        self.save_manager = self.game_manager.save_manager
        self.ui_font = self.game_manager.ui_font
        self.screen_width = self.game_manager.screen_width
        self.screen_height = self.game_manager.screen_height
        
        self.WHITE = self.game_manager.colors.get("WHITE", (255, 255, 255))
        self.RED = self.game_manager.colors.get("RED", (255, 0, 0))
        self.GREEN = self.game_manager.colors.get("GREEN", (0, 255, 0))
        # Assuming HIT_COLOR is also in game_manager.colors or accessible
        self.HIT_COLOR = self.game_manager.colors.get("HIT_COLOR", (255,100,100))


    def _load_level_logic(self, level_idx):
        print(f"GameplayScreen: Loading level {level_idx + 1}")

        if self.save_manager:
            save_data_dict = {
                "current_level_index": level_idx,
                "player_health": self.game_manager.PLAYER_MAX_HEALTH, 
                "player_inventory": list(self.player.inventory),
                "player_position": (self.game_manager.PLAYER_START_X, self.game_manager.PLAYER_START_Y)
            }
            self.save_manager.save_data(save_data_dict)

        self.game_manager.current_level_index = level_idx 
        self.player.rect.topleft = (self.game_manager.PLAYER_START_X, self.game_manager.PLAYER_START_Y)
        self.player.health = self.game_manager.PLAYER_MAX_HEALTH
        self.player.velocity_y = 0
        self.player.is_jumping = False
        self.monsters.clear() 

        level_config = self.game_manager.LEVEL_CONFIGS[level_idx]
        print(level_config["message"])

        monster_spawn_offset_x = 0
        for monster_group_config in level_config["monsters"]:
            monster_type_str = monster_group_config["type"]
            count = monster_group_config["count"]
            
            for i in range(count):
                monster_width = 40
                monster_height = 40
                
                monster_x = 0
                monster_y = 0

                if self.platforms: 
                    base_x_on_platform = self.platforms[0].rect.left + config.GAMEPLAY_MONSTER_DEFAULT_SPAWN_OFFSET_X
                    monster_x = base_x_on_platform + i * (monster_width + config.GAMEPLAY_MONSTER_DEFAULT_SPACING_X) + monster_spawn_offset_x
                    monster_y = self.platforms[0].rect.top - monster_height
                    if monster_x + monster_width > self.platforms[0].rect.right - 20: # -20 is a buffer, could be a config
                         monster_x = self.platforms[0].rect.left + 20 + i * 10 + monster_spawn_offset_x # 20, 10 are buffers/small spacing
                else: 
                    monster_x = config.GAMEPLAY_MONSTER_FALLBACK_SPAWN_START_X + i * config.GAMEPLAY_MONSTER_FALLBACK_SPAWN_SPACING_X + monster_spawn_offset_x
                    monster_y = self.screen_height - monster_height - 5 # -5 is a small offset from bottom

                creation_args = monster_group_config.copy()
                creation_args.pop("type", None) # Remove keys not part of constructor
                creation_args.pop("count", None)
                
                creation_args['x'] = monster_x
                creation_args['y'] = monster_y
                
                # Map config keys to constructor param names if different
                if "damage" in creation_args:
                    creation_args["attack_damage"] = creation_args.pop("damage")
                if "patrol_range" in creation_args:
                    creation_args["patrol_range_x"] = creation_args.pop("patrol_range")
                
                # Add possible_drops from the monster_group_config
                creation_args['possible_drops'] = monster_group_config.get('drops')

                new_monster = None
                if monster_type_str == "Grunt":
                    creation_args['color'] = creation_args.get('color', self.RED)
                    creation_args['gravity_val'] = self.game_manager.GRAVITY
                    creation_args['screen_height_val'] = self.screen_height
                    # Grunt width/height are now defaults in Grunt.__init__ via config.DEFAULT_GRUNT_STATS
                    new_monster = self.game_manager.Grunt(**creation_args) # Pass x,y and other overrides
                elif monster_type_str == "Flyer":
                    flyer_y_offset = monster_group_config.get("spawn_y_offset", config.GAMEPLAY_FLYER_DEFAULT_SPAWN_Y_OFFSET) 
                    creation_args['y'] = self.screen_height // 2 + flyer_y_offset 
                    # Flyer color will default from config.DEFAULT_FLYER_STATS if not in creation_args
                    # Flyer width/height are now defaults in Flyer.__init__ via config.DEFAULT_FLYER_STATS
                    new_monster = self.game_manager.Flyer(**creation_args) # Pass x,y and other overrides
                
                if new_monster:
                    self.monsters.append(new_monster)
            monster_spawn_offset_x += count * (monster_width + config.GAMEPLAY_MONSTER_DEFAULT_SPACING_X) + 100 # 100 is additional group spacing


    def start_level(self, level_idx):
        self._load_level_logic(level_idx)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game_manager.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.game_manager.pause_game()
                    return 
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.player.is_jumping:
                    self.player.is_jumping = True
                    self.player.velocity_y = self.game_manager.JUMP_STRENGTH
                    if self.player.sound_manager:
                        self.player.sound_manager.play_sound("player_jump")

        keys = pygame.key.get_pressed()
        player_dx = 0
        if keys[pygame.K_LEFT]:
            player_dx -= self.player.speed
        if keys[pygame.K_RIGHT]:
            player_dx += self.player.speed
        self.player.move(player_dx, 0, self.platforms)

    def update(self, dt):
        self.player.update(self.platforms, self.monsters) 
        if self.player.pet:
            self.player.pet.update(self.platforms, self.monsters, self.player)

        for monster in list(self.monsters): # Iterate over a copy for safe removal
            monster.update(self.platforms, self.player)
            if monster.health <= 0:
                logger.info(f"Monster {type(monster).__name__} (ID: {id(monster)}) defeated.")
                # Handle item drops
                if hasattr(monster, 'possible_drops') and monster.possible_drops:
                    for drop_info in monster.possible_drops:
                        item_id = drop_info.get("item_id")
                        chance = drop_info.get("chance", 0)
                        quantity = drop_info.get("quantity", 1)
                        data_used_for_creation = None # To store context for logging

                        if random.random() < chance:
                            logger.info(f"Monster {type(monster).__name__} (ID: {id(monster)}) dropped {item_id} (Quantity: {quantity})")
                            
                            # Create item instance
                            # Option 1: Using create_item_from_dict with item_id as class name
                            # This assumes item_id in config.LEVEL_CONFIGS matches a class name in ITEM_CLASS_MAP
                            item_data_for_creation = {"item_class_name": item_id} # Default data
                            
                            # Option 2: If item_id is a key for GENERIC_ITEM_DEFAULTS
                            # and those defaults provide all necessary constructor args.
                            # This is more robust if item_id is "MonsterPart" and Item class needs name, desc, etc.
                            generic_item_config = config.GENERIC_ITEM_DEFAULTS.get(item_id)
                            if generic_item_config:
                                # We need to ensure the item_class_name is correct if item_id is not the class name
                                # For "MonsterPart", item_class_name is "Item".
                                # For "HealthPotion", item_id is "HealthPotion", class name is "HealthPotion".
                                item_class_name_for_factory = ITEM_CLASS_MAP.get(item_id).__name__ if ITEM_CLASS_MAP.get(item_id) else item_id

                                factory_data = generic_item_config.copy() # Start with defaults from GENERIC_ITEM_DEFAULTS
                                factory_data["item_class_name"] = item_class_name_for_factory # Ensure correct class name
                                data_used_for_creation = factory_data
                                item_to_drop = create_item_from_dict(factory_data)
                            else:
                                # Fallback if item_id is not in GENERIC_ITEM_DEFAULTS but might be a direct class name
                                data_used_for_creation = item_data_for_creation
                                item_to_drop = create_item_from_dict(item_data_for_creation)

                            if item_to_drop:
                                was_added = self.game_manager.player.inventory.add_item(item_to_drop, quantity)
                                if was_added:
                                    # Log successful pickup (optional, could be info or debug)
                                    logger.info(f"Player picked up {item_to_drop.name} (Quantity: {quantity}) from monster {type(monster).__name__} (ID: {id(monster)})")
                                    if self.sound_manager:
                                        self.sound_manager.play_sound("item_pickup")
                                else:
                                    logger.warning(f"Inventory full, could not add {item_id} (Quantity: {quantity}) from monster {type(monster).__name__} (ID: {id(monster)})")
                            else:
                                # This is the enhanced logging part
                                logger.error(
                                    f"Failed to create item instance for drop. Item ID: '{item_id}', "
                                    f"Monster: {type(monster).__name__} (ID: {id(monster)}), "
                                    f"Attempted with data: {data_used_for_creation}"
                                )
                        # else: # Optional: Log missed drops for debugging
                        #     logger.info(f"Monster {type(monster).__name__} (ID: {id(monster)}) did NOT drop {item_id} (Chance: {chance})")
                
                self.monsters.remove(monster) # Remove the defeated monster from the list

        # After processing all monsters, check for level clear condition
        if not self.monsters and self.player.health > 0:
            print(f"Level {self.game_manager.current_level_index + 1} cleared!")
            self.game_manager.current_level_index += 1
            if self.game_manager.current_level_index < len(self.game_manager.LEVEL_CONFIGS):
                self.start_level(self.game_manager.current_level_index)
            else:
                print("Congratulations! All levels completed!")
                self.game_manager.set_game_state(self.game_manager.STATE_GAME_WON) 
                return

        if self.player.health <= 0:
            print("Game Over! Player has been defeated.")
            self.game_manager.set_game_state(self.game_manager.STATE_GAME_OVER) 

    def render(self, surface):
        surface.fill((0,0,0)) # Black background (assuming BLACK is (0,0,0) from game_manager or global)
        for plat in self.platforms:
            plat.draw(surface)
        
        # Player and Pet drawing are handled by game_manager if they are part of a sprite group
        # Or draw them directly if GameplayScreen manages them
        self.player.draw(surface)
        if self.player.pet:
            self.player.pet.draw(surface)

        for monster in self.monsters:
            monster.draw(surface, self.HIT_COLOR)

        # UI Text (Health, Level, XP, Inventory)
        player = self.game_manager.player # Convenience reference
        draw_text_utility = self.game_manager.draw_text_utility # Convenience reference
        ui_font = self.ui_font # Already available in GameplayScreen
        white_color = self.game_manager.config.WHITE # Assuming WHITE is in config
        # If config is not directly on game_manager, adjust access e.g. self.game_manager.config.WHITE

        # Health (using get_total_max_health)
        health_text = f"Health: {player.health}/{player.get_total_max_health()}"
        draw_text_utility(surface, health_text, ui_font, white_color, 10, 10)

        # Level (using player.level directly - not affected by equipment)
        level_text = f"Level: {player.level}"
        draw_text_utility(surface, level_text, ui_font, white_color, 10, 40)

        # XP Display (not affected by equipment)
        xp_text = f"XP: {player.experience_points} / {player.xp_to_next_level}"
        xp_text_y_position = 70 
        draw_text_utility(surface, xp_text, ui_font, white_color, 10, xp_text_y_position)

        # Attack Power Display (using get_total_attack_power)
        attack_text_y_position = xp_text_y_position + 30 # Y = 100
        attack_text = f"Attack: {player.get_total_attack_power()}"
        draw_text_utility(surface, attack_text, ui_font, white_color, 10, attack_text_y_position)

        # Defense Display (using get_total_defense)
        defense_text_y_position = attack_text_y_position + 30 # Y = 130
        defense_text = f"Defense: {player.get_total_defense()}"
        draw_text_utility(surface, defense_text, ui_font, white_color, 10, defense_text_y_position)

        # Gold Display
        gold_text_y_position = defense_text_y_position + 30 # Y = 160
        gold_text = f"Gold: {player.gold}" # Assuming player.gold exists
        draw_text_utility(surface, gold_text, ui_font, white_color, 10, gold_text_y_position)

        # Adjusted Inventory Display Logic
        inventory_y_start = gold_text_y_position + 30 # Shift inventory down to Y = 190
        line_height = config.UI_INVENTORY_LINE_HEIGHT

        if hasattr(player, 'inventory') and hasattr(player.inventory, 'get_all_items'):
            item_slots = self.game_manager.player.inventory.get_all_items()
            
            inventory_title_text = "Inventory:"
            draw_text_utility(surface, inventory_title_text, ui_font,
                                                white_color, 10, inventory_y_start)
            
            if not item_slots:
                inventory_empty_text = "  Empty" # Indent "Empty"
                draw_text_utility(surface, inventory_empty_text, ui_font, 
                                                    white_color, 10, inventory_y_start + line_height) # Using config.UI_INVENTORY_LINE_HEIGHT indirectly
            else:
                current_y = inventory_y_start + line_height # Using config.UI_INVENTORY_LINE_HEIGHT indirectly
                for slot in item_slots:
                    item = slot.get('item')
                    quantity = slot.get('quantity')
                    if item and quantity is not None: 
                        item_line = f"  - {item.name}: {quantity}" # Indent item list
                        draw_text_utility(surface, item_line, ui_font, 
                                                            white_color, 10, current_y)
                        current_y += line_height # Using config.UI_INVENTORY_LINE_HEIGHT indirectly
                        if current_y > self.game_manager.screen_height - 20: 
                            break 
        else:
            draw_text_utility(surface, "Inventory: N/A", ui_font,
                                                self.game_manager.config.RED, 10, inventory_y_start)


class GameOverScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.GAME_OVER_FONT_SIZE)
        self.button_font = self.game_manager.ui_font # Use standard UI font for buttons
        self.sound_manager = self.game_manager.sound_manager
        self.message_font = self.game_manager.ui_font # Could be another config font
        self.message_color = config.WHITE # Use config.WHITE
        self.title_color = config.RED # Use config.RED
        self.background_color = config.GAME_OVER_BACKGROUND_COLOR

        button_width = config.GAME_OVER_BUTTON_WIDTH
        button_height = config.GAME_OVER_BUTTON_HEIGHT
        spacing = config.GAME_OVER_BUTTON_SPACING
        # Buttons are centered below the "Game Over" message
        start_y = self.game_manager.screen_height // 2 

        self.buttons = []
        self.buttons.append(Button(
            text="Try Again",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, start_y, button_width, button_height),
            font=self.button_font,
            text_color=(255, 255, 255),
            button_color=(0, 100, 150), # A bluish color
            hover_color=(0, 150, 200),
            sound_manager=self.sound_manager,
            action=self.game_manager.start_new_game # This will reset and start from level 0
        ))

        self.buttons.append(Button(
            text="Main Menu",
            rect=pygame.Rect(self.game_manager.screen_width // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height),
            font=self.button_font,
            text_color=(255, 255, 255),
            button_color=(100, 100, 100), # A gray color
            hover_color=(150, 150, 150),
            sound_manager=self.sound_manager,
            action=self.game_manager.go_to_main_menu 
        ))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game_manager.quit_game()
            for button in self.buttons:
                if button.handle_event(event):
                    break # Event handled, no need to process further for this event

    def update(self, dt):
        # No specific update logic needed for a static game over screen
        pass

    def render(self, surface):
        surface.fill(self.background_color) 
        
        game_over_text_surface = self.title_font.render("Game Over", True, self.title_color)
        game_over_text_rect = game_over_text_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 3))
        surface.blit(game_over_text_surface, game_over_text_rect)

        # Optional: A sub-message
        sub_message_surface = self.message_font.render(config.GAME_OVER_SUB_MESSAGE, True, self.message_color)
        sub_message_rect = sub_message_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 3 + 60))
        surface.blit(sub_message_surface, sub_message_rect)

        for button in self.buttons:
            button.draw(surface)
