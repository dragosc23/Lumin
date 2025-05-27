import pygame
import config 
from src.pet import Pet 
from src.inventory_manager import InventoryManager # Import InventoryManager
from src.items import Item, EQUIPMENT_SLOTS, Equipment # Import Equipment class
# Placeholder constants previously here have been removed.

# Player class and related logic.
# This class will be updated in subsequent steps to use 'config.CONSTANT_NAME'
# Placeholder constants previously here have been removed.

# Player class and related logic.
# This class will be updated in subsequent steps to use 'config.CONSTANT_NAME'
# for all constants currently hardcoded or previously accessed as globals.

class Player:
    def __init__(self, x, y, width, height, color, sound_manager=None): # Added sound_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color 
        # Stats and properties from config (or defaults if config not used yet)
        self.speed = config.PLAYER_SPEED # Changed
        self.velocity_y = 0
        self.is_jumping = False
        self.max_health = config.PLAYER_MAX_HEALTH 
        self.health = self.max_health 
        
        # Combat Stats
        self.attack_range = config.PLAYER_ATTACK_RANGE 
        self.attack_damage = config.PLAYER_ATTACK_DAMAGE # Legacy, may be refactored
        self.attack_power = config.PLAYER_BASE_ATTACK_POWER # New primary attack stat
        self.defense = config.PLAYER_BASE_DEFENSE # New defense stat
        self.attack_cooldown = config.PLAYER_ATTACK_COOLDOWN 
        self.last_attack_time = 0

        # XP and Leveling attributes
        self.level = 1
        self.experience_points = 0
        self.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.level
        self.gold = config.PLAYER_STARTING_GOLD # Added gold attribute
        
        self.inventory = InventoryManager(capacity=config.PLAYER_INVENTORY_CAPACITY)
        
        # Equipment slots
        self.equipment = {}
        for slot_key in EQUIPMENT_SLOTS.keys():
            self.equipment[slot_key] = None # e.g., self.equipment['weapon'] = None
        
        self.original_color = self.color 
        self.is_hit = False
        self.hit_flash_duration = config.PLAYER_HIT_FLASH_DURATION # Changed
        self.hit_flash_timer = 0

        self.is_attacking = False
        self.attack_visual_duration = config.PLAYER_ATTACK_VISUAL_DURATION # Changed
        self.attack_visual_timer = 0
        self.direction = 1 

        self.sound_manager = sound_manager

        # Pet instantiation using constants from config.py
        pet_start_x = self.rect.x - config.PET_SPAWN_OFFSET_X
        pet_start_y = self.rect.y # Assuming pet spawns at the same y-level as player's top
                                  # Adjust if pet should be centered or offset differently.
                                  # For example, to align centers:
                                  # pet_start_y = self.rect.centery - config.PET_HEIGHT // 2
        
        self.pet = Pet(
            x=pet_start_x,
            y=pet_start_y,
            width=config.PET_WIDTH,
            height=config.PET_HEIGHT,
            color=config.PET_COLOR,
            owner=self,
            sound_manager=self.sound_manager
        )


    def draw(self, screen):
        current_player_color = self.original_color
        if self.is_hit and self.hit_flash_timer > 0:
            # This will become config.HIT_COLOR in the next step
            current_player_color = config.HIT_COLOR 
            self.hit_flash_timer -= 1
        elif self.is_hit and self.hit_flash_timer <= 0:
            self.is_hit = False
        
        pygame.draw.rect(screen, current_player_color, self.rect)


        if self.is_attacking:
            attack_rect_width = config.PLAYER_ATTACK_VISUAL_WIDTH # Changed
            attack_rect_height = self.rect.height * config.PLAYER_ATTACK_VISUAL_HEIGHT_RATIO # Changed
            attack_rect_y = self.rect.centery - attack_rect_height / 2
            if self.direction == 1: 
                attack_rect_x = self.rect.right
            else: 
                attack_rect_x = self.rect.left - attack_rect_width
            attack_visual_rect = pygame.Rect(attack_rect_x, attack_rect_y, attack_rect_width, attack_rect_height)
            # This will become config.ATTACK_VISUAL_COLOR in the next step
            pygame.draw.rect(screen, config.ATTACK_VISUAL_COLOR, attack_visual_rect) 


    def move(self, dx, dy, platforms):
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1

        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0: 
                    self.rect.right = platform.rect.left
                elif dx < 0: 
                    self.rect.left = platform.rect.right
        
        old_rect_bottom = self.rect.bottom 
        old_rect_top = self.rect.top       
        self.rect.y += dy                  
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dy > 0:  
                    if old_rect_bottom <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                elif dy < 0:  
                    if old_rect_top >= platform.rect.bottom:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0 

        if self.rect.left < 0:
            self.rect.left = 0
        # These will become config.SCREEN_WIDTH in the next step
        if self.rect.right > config.SCREEN_WIDTH: 
            self.rect.right = config.SCREEN_WIDTH 
        
        if self.rect.top < 0:
            self.rect.top = 0
            if dy < 0: 
                 self.velocity_y = 0


    def update(self, platforms, monsters): 
        # This will become config.GRAVITY in the next step
        self.velocity_y += config.GRAVITY 
        if self.velocity_y > config.PLAYER_MAX_FALL_SPEED: # Changed
            self.velocity_y = config.PLAYER_MAX_FALL_SPEED # Changed
        
        self.move(0, self.velocity_y, platforms)

        # This will become config.SCREEN_HEIGHT in the next step
        if self.rect.bottom >= config.SCREEN_HEIGHT: 
            self.rect.bottom = config.SCREEN_HEIGHT 
            self.velocity_y = 0
            self.is_jumping = False

        self.last_attack_time += 1
        if self.last_attack_time >= self.attack_cooldown:
            attack_occurred = False
            for monster in monsters:
                effective_attack_rect = self.rect.inflate(self.attack_range, self.attack_range)
                if effective_attack_rect.colliderect(monster.rect):
                    # Player deals damage based on total attack_power
                    # Monster's defense is not yet implemented here, but could be:
                    # damage_to_monster = max(1, self.get_total_attack_power() - monster.defense)
                    damage_to_monster = self.get_total_attack_power() # Use total attack power
                    monster.health -= damage_to_monster
                    monster.is_hit = True
                    
                    if hasattr(monster, 'hit_flash_duration'):
                         monster.hit_flash_timer = monster.hit_flash_duration
                    else: 
                         monster.hit_flash_timer = config.MONSTER_HIT_FLASH_DURATION # Changed Fallback


                    if self.sound_manager:
                        self.sound_manager.play_sound("monster_hit")
                    print(f"Player attacked monster (ID: {id(monster)}) for {damage_to_monster} damage. Monster health: {monster.health}")
                    
                    if monster.health <= 0:
                        if self.sound_manager:
                            self.sound_manager.play_sound("monster_die")
                        
                        # Award XP for defeating the monster
                        self.gain_xp(config.XP_PER_MONSTER_DEFEAT)

                        # Item creation and adding logic is now moved to GameplayScreen.update
                        print(f"Monster (ID: {id(monster)}) defeated by player.")
                        
                    self.last_attack_time = 0
                    attack_occurred = True
                    break 
            
            if attack_occurred: 
                if self.sound_manager:
                    self.sound_manager.play_sound("player_attack")
                self.is_attacking = True
                self.attack_visual_timer = self.attack_visual_duration
        
        if self.is_attacking:
            self.attack_visual_timer -= 1
            if self.attack_visual_timer <= 0:
                self.is_attacking = False

    def gain_xp(self, amount):
        self.experience_points += amount
        print(f"Player gained {amount} XP. Total XP: {self.experience_points}/{self.xp_to_next_level}")
        self.check_for_level_up()

    def check_for_level_up(self):
        while self.experience_points >= self.xp_to_next_level:
            self.level += 1
            # Carry over excess XP: subtract the cost of the level just completed
            self.experience_points -= self.xp_to_next_level 
            
            # Update xp_to_next_level for the NEW level
            self.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.level 
            
            # Apply level-up benefits
            self.max_health += config.HEALTH_GAIN_PER_LEVEL
            self.health = self.max_health # Heal to new max health
            self.attack_power += config.ATTACK_POWER_GAIN_PER_LEVEL
            self.defense += config.DEFENSE_GAIN_PER_LEVEL
            
            if self.sound_manager:
                self.sound_manager.play_sound("level_up") # Assuming a 'level_up' sound exists
            print(f"Player reached Level {self.level}! Base Max Health: {self.max_health}, Base Attack: {self.attack_power}, Base Defense: {self.defense}. XP for next level: {self.xp_to_next_level}.")
            # If experience_points is still >= new xp_to_next_level, the loop continues

    def get_total_attack_power(self):
        total_ap = self.attack_power # Start with base attack power (includes level-up gains)
        if self.equipment.get("weapon") and hasattr(self.equipment["weapon"], 'stat_modifiers'):
            total_ap += self.equipment["weapon"].stat_modifiers.get("attack_power", 0)
        # Can be extended to other slots if they can grant attack_power
        # for slot_key, item in self.equipment.items():
        #     if item and hasattr(item, 'stat_modifiers'):
        #         total_ap += item.stat_modifiers.get("attack_power", 0)
        return total_ap

    def get_total_defense(self):
        total_def = self.defense # Start with base defense (includes level-up gains)
        for slot_key, item in self.equipment.items():
            # Iterate through all equipment slots, not just armor-specific ones,
            # as some unique items might grant defense from non-traditional slots.
            if item and hasattr(item, 'stat_modifiers'):
                total_def += item.stat_modifiers.get("defense", 0)
        return total_def

    def get_total_max_health(self):
        total_mh = self.max_health # Start with base max_health (includes level-up gains)
        for slot_key, item in self.equipment.items():
            if item and hasattr(item, 'stat_modifiers'):
                total_mh += item.stat_modifiers.get("max_health", 0)
        return total_mh

    def equip_item(self, inventory_index):
        """Equips an item from the given inventory index."""
        if not (0 <= inventory_index < len(self.inventory.slots)):
            print(f"DEBUG: Invalid inventory index: {inventory_index}")
            return

        inventory_slot = self.inventory.slots[inventory_index]
        item_to_equip = inventory_slot['item'] # This is the ItemObject

        if not isinstance(item_to_equip, Equipment):
            print(f"DEBUG: {item_to_equip.name} is not equippable.")
            return

        target_slot = item_to_equip.slot
        if target_slot not in self.equipment: # Should not happen if EQUIPMENT_SLOTS is comprehensive
            print(f"DEBUG: Invalid equipment slot '{target_slot}' for {item_to_equip.name}.")
            return

        # Store current health percentage relative to current total max health
        # This happens BEFORE any un-equipping or equipping changes total_max_health
        current_total_max_health_before_change = self.get_total_max_health()
        health_percentage = self.health / current_total_max_health_before_change if current_total_max_health_before_change > 0 else 1.0

        # If something is already equipped in that slot, unequip it first.
        if self.equipment[target_slot] is not None:
            print(f"DEBUG: Unequipping {self.equipment[target_slot].name} from {target_slot} to make space.")
            # The unequip_item method now handles health adjustment for the removal part.
            # It also returns True/False based on whether it could add the item to inventory.
            if not self.unequip_item(target_slot, adjust_health_after_unequip=False): # Health will be adjusted once after equipping
                print(f"DEBUG: Cannot equip {item_to_equip.name}, failed to unequip previous item in {target_slot}.")
                # Restore health percentage calculation if unequip failed and changed max_health temporarily
                # However, unequip_item should ideally not change player state if it fails.
                # For now, assume unequip_item is transactional or its health impact is fine.
                return 

        # Now that the slot is clear (or was already empty), equip the new item.
        # Remove item from inventory - using pop_item_at_index
        # Note: pop_item_at_index should return the ItemObject itself.
        popped_item_object = self.inventory.pop_item_at_index(inventory_index)
        
        if popped_item_object is not item_to_equip: # Sanity check
             print(f"DEBUG: Mismatch when popping item from inventory. Expected {item_to_equip.name}, got {popped_item_object.name if popped_item_object else 'None'}.")
             # Attempt to add it back if it was popped, though this is tricky.
             if popped_item_object: self.inventory.add_item(popped_item_object, 1) # Add it back
             return

        self.equipment[target_slot] = item_to_equip
        print(f"DEBUG: Equipped {item_to_equip.name} in {target_slot} slot.")

        # Adjust health based on the new max health from all equipment changes
        new_total_max_health = self.get_total_max_health()
        self.health = int(new_total_max_health * health_percentage)
        self.health = max(1, min(self.health, new_total_max_health)) # Ensure health is at least 1 and not over new max.
        print(f"DEBUG: Player health adjusted to {self.health}/{new_total_max_health} after equipping.")


    def unequip_item(self, slot_name, adjust_health_after_unequip=True):
        """Unequips an item from the specified slot and attempts to add it to inventory."""
        if slot_name not in self.equipment:
            print(f"DEBUG: Invalid slot name: {slot_name}")
            return False

        item_to_unequip = self.equipment.get(slot_name)
        if item_to_unequip is None:
            print(f"DEBUG: No item equipped in {slot_name} slot.")
            return True # Nothing to unequip, so operation is trivially successful

        # Attempt to add the item back to inventory
        if self.inventory.add_item(item_to_unequip, 1): # Quantity is 1 for equipment
            print(f"DEBUG: Successfully added {item_to_unequip.name} back to inventory.")
            
            # Store current health percentage relative to current total max health
            # This happens BEFORE the item is removed from the slot.
            current_total_max_health_before_change = self.get_total_max_health()
            health_percentage = self.health / current_total_max_health_before_change if current_total_max_health_before_change > 0 else 1.0

            self.equipment[slot_name] = None # Remove from equipment slot
            print(f"DEBUG: Unequipped {item_to_unequip.name} from {slot_name} slot.")

            if adjust_health_after_unequip:
                # Adjust health based on the new max health
                new_total_max_health = self.get_total_max_health() # Recalculate after item is removed
                self.health = int(new_total_max_health * health_percentage)
                self.health = max(1, min(self.health, new_total_max_health)) # Ensure health is at least 1 and not over new max.
                print(f"DEBUG: Player health adjusted to {self.health}/{new_total_max_health} after unequipping.")
            return True
        else:
            print(f"DEBUG: Inventory full. Cannot unequip {item_to_unequip.name}.")
            return False
