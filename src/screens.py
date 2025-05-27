import pygame
from src.ui_elements import Button # Assuming Button is in ui_elements.py
import os # Standard practice to import at the top
import math # For Flyer's vertical bobbing in GameplayScreen's conceptual _load_level_logic

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

        button_width = 250
        button_height = 50
        spacing = 20
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
            action=self.game_manager.start_new_game
        ))
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

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: # Allow quitting from menu via window X
                self.game_manager.quit_game()
            for button in self.buttons:
                if button.handle_event(event):
                    break # Event handled by a button

    def update(self, dt):
        pass # Main menu buttons don't have much to update beyond hover state handled by events

    def render(self, surface):
        surface.fill((50, 50, 70)) # Background color for main menu
        title_font = pygame.font.SysFont("arial", 50) 
        title_surface = title_font.render("My Autobattler Game", True, (200, 200, 255))
        title_rect = title_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 4))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

class PauseScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = self.game_manager.ui_font 
        self.title_font = pygame.font.SysFont("arial", 48) 
        self.sound_manager = self.game_manager.sound_manager

        button_width = 250
        button_height = 50
        spacing = 20
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
        overlay.fill((0, 0, 0, 180)) 
        surface.blit(overlay, (0,0)) 

        paused_text_surface = self.title_font.render("Paused", True, (255, 255, 255))
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
                    base_x_on_platform = self.platforms[0].rect.left + 70 
                    monster_x = base_x_on_platform + i * (monster_width + 80) + monster_spawn_offset_x
                    monster_y = self.platforms[0].rect.top - monster_height
                    if monster_x + monster_width > self.platforms[0].rect.right - 20:
                         monster_x = self.platforms[0].rect.left + 20 + i * 10 + monster_spawn_offset_x
                else: 
                    monster_x = 150 + i * 150 + monster_spawn_offset_x
                    monster_y = self.screen_height - monster_height - 5

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
                    new_monster = self.game_manager.Grunt(width=monster_width, height=monster_height, **creation_args)
                elif monster_type_str == "Flyer":
                    flyer_y_offset = monster_group_config.get("spawn_y_offset", -100) 
                    creation_args['y'] = self.screen_height // 2 + flyer_y_offset 
                    creation_args['color'] = creation_args.get('color', self.game_manager.colors.get("YELLOW", (255,255,0)))
                    new_monster = self.game_manager.Flyer(width=monster_width, height=monster_height, **creation_args)
                
                if new_monster:
                    self.monsters.append(new_monster)
            monster_spawn_offset_x += count * (monster_width + 80) + 100


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

        for monster in list(self.monsters): 
            monster.update(self.platforms, self.player)
        
        new_monsters_list = [m for m in self.monsters if m.health > 0]
        if len(new_monsters_list) < len(self.monsters):
             self.monsters[:] = new_monsters_list 

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

        # Health
        # Ensure player.max_health is used, not game_manager.PLAYER_MAX_HEALTH if it can change per player
        health_text = f"Health: {player.health}/{player.max_health}"
        draw_text_utility(surface, health_text, ui_font, white_color, 10, 10)

        # Level (using player.level directly)
        level_text = f"Level: {player.level}"
        draw_text_utility(surface, level_text, ui_font, white_color, 10, 40)

        # XP Display (New)
        xp_text = f"XP: {player.experience_points} / {player.xp_to_next_level}"
        xp_text_y_position = 70 
        draw_text_utility(surface, xp_text, ui_font, white_color, 10, xp_text_y_position)

        # Adjusted Inventory Display Logic
        inventory_y_start = xp_text_y_position + 30 # Shift inventory down to 100
        line_height = 25       # Height for each line of text (adjust based on font size)

        if hasattr(player, 'inventory') and hasattr(player.inventory, 'get_all_items'):
            item_slots = self.game_manager.player.inventory.get_all_items()
            
            inventory_title_text = "Inventory:"
            draw_text_utility(surface, inventory_title_text, ui_font,
                                                white_color, 10, inventory_y_start)
            
            if not item_slots:
                inventory_empty_text = "  Empty" # Indent "Empty"
                draw_text_utility(surface, inventory_empty_text, ui_font, 
                                                    white_color, 10, inventory_y_start + line_height)
            else:
                current_y = inventory_y_start + line_height
                for slot in item_slots:
                    item = slot.get('item')
                    quantity = slot.get('quantity')
                    if item and quantity is not None: 
                        item_line = f"  - {item.name}: {quantity}" # Indent item list
                        draw_text_utility(surface, item_line, ui_font, 
                                                            white_color, 10, current_y)
                        current_y += line_height
                        if current_y > self.game_manager.screen_height - 20: 
                            break 
        else:
            draw_text_utility(surface, "Inventory: N/A", ui_font,
                                                self.game_manager.config.RED, 10, inventory_y_start)


class GameOverScreen(BaseScreen):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = pygame.font.SysFont("arial", 72) # Large font for "Game Over"
        self.button_font = self.game_manager.ui_font # Use standard UI font for buttons
        self.sound_manager = self.game_manager.sound_manager
        self.message_font = self.game_manager.ui_font
        self.message_color = self.game_manager.colors.get("WHITE", (255, 255, 255))
        self.title_color = self.game_manager.colors.get("RED", (255, 0, 0))
        self.background_color = (30, 30, 30)

        button_width = 250
        button_height = 50
        spacing = 20
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
        sub_message_surface = self.message_font.render("Better luck next time!", True, self.message_color)
        sub_message_rect = sub_message_surface.get_rect(center=(self.game_manager.screen_width // 2, self.game_manager.screen_height // 3 + 60))
        surface.blit(sub_message_surface, sub_message_rect)

        for button in self.buttons:
            button.draw(surface)
