# Defines game items (base Item class, specific item types like consumables, etc.)
import pygame # Added just in case any item might need it for sprites later.

class Item:
    """Base class for all items in the game."""
    def __init__(self, name, description, value=0, stackable=False, max_stack=1, sprite_id=None):
        self.name = name
        self.description = description
        self.value = value  # Monetary value or some other metric
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.sprite_id = sprite_id  # Conceptual, for future sprite rendering

    def __str__(self):
        return f"{self.name}: {self.description}"

    def __repr__(self):
        return f"Item({self.name!r}, {self.description!r}, value={self.value}, stackable={self.stackable}, max_stack={self.max_stack})"

    def to_dict(self):
        """Serializes the item's core attributes to a dictionary."""
        return {
            "item_class_name": self.__class__.__name__, # Store the class name for reconstruction
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
            "sprite_id": self.sprite_id
            # Specific item types might add more to this dict in their overrides
        }

class ConsumableItem(Item):
    """Base class for items that can be consumed (e.g., potions)."""
    def __init__(self, name, description, value=0, stackable=True, max_stack=10, sprite_id=None):
        # Consumables are often stackable by default
        super().__init__(name, description, value, stackable, max_stack, sprite_id)

    def use(self, target):
        """Uses the item on a target (e.g., player, pet). 
        This method should be overridden by specific consumable items.
        Returns True if the item was successfully used and should be consumed, False otherwise.
        """
        print(f"DEBUG: Using {self.name} on {target}. No specific action defined in base ConsumableItem.")
        return False

class HealthPotion(ConsumableItem):
    """A potion that restores health."""
    def __init__(self, name="Health Potion", description="Restores a small amount of health.", 
                 value=25, stackable=True, max_stack=5, heal_amount=50, sprite_id=None, **kwargs):
        super().__init__(name, description, value, stackable, max_stack, sprite_id, **kwargs)
        self.heal_amount = heal_amount

    def to_dict(self):
        """Adds heal_amount to the base item serialization."""
        data = super().to_dict()
        data["heal_amount"] = self.heal_amount
        return data

    def use(self, player): # Target is specifically a player (or object with health/max_health)
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            if player.health < player.max_health:
                player.health += self.heal_amount
                if player.health > player.max_health:
                    player.health = player.max_health
                print(f"DEBUG: Used {self.name} on {player}. Restored {self.heal_amount} health. Current health: {player.health}")
                # if hasattr(player, 'sound_manager') and player.sound_manager:
                #     player.sound_manager.play_sound("heal_potion") # Conceptual
                return True # Item consumed
            else:
                print(f"DEBUG: {player} health already full. {self.name} not used.")
                return False # Item not consumed
        else:
            print(f"DEBUG: Target {player} does not have health attributes. {self.name} not used.")
            return False # Item not consumed

# --- Equipment System ---
EQUIPMENT_SLOTS = {
    "weapon": "Weapon",
    "body": "Body Armor",
    "head": "Helmet",
    "feet": "Boots",
    "ring": "Ring", # Example of another slot
    # Add more slots as needed
}

class Equipment(Item):
    def __init__(self, name, description, slot, stat_modifiers, value=0, sprite_id=None, **kwargs):
        # Equipment is typically not stackable.
        super().__init__(name, description, value, stackable=False, max_stack=1, sprite_id=sprite_id, **kwargs)
        if slot not in EQUIPMENT_SLOTS:
            raise ValueError(f"Invalid equipment slot: {slot}. Valid slots are: {list(EQUIPMENT_SLOTS.keys())}")
        self.slot = slot  # e.g., "weapon", "body"
        self.stat_modifiers = stat_modifiers  # e.g., {"attack_power": 5, "defense": 2}
        # self.item_class_name = self.__class__.__name__ # Already handled by base Item.to_dict()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "slot": self.slot,
            "stat_modifiers": self.stat_modifiers,
        })
        return data

class Weapon(Equipment):
    def __init__(self, name, description, stat_modifiers, value=0, sprite_id=None, **kwargs):
        # Weapons always go in the "weapon" slot
        super().__init__(name, description, "weapon", stat_modifiers, value, sprite_id=sprite_id, **kwargs)
        # self.item_class_name = self.__class__.__name__ # Handled by base

class Armor(Equipment):
    def __init__(self, name, description, slot, stat_modifiers, value=0, sprite_id=None, **kwargs):
        # Armor can go in various slots like "head", "body"
        # The specific slot ('head', 'body') is passed to the constructor
        super().__init__(name, description, slot, stat_modifiers, value, sprite_id=sprite_id, **kwargs)
        # self.item_class_name = self.__class__.__name__ # Handled by base

# --- Item Class Mapping & Creation ---
# ITEM_CLASS_MAP maps class names to the actual classes.
# This is crucial for deserializing items correctly.
ITEM_CLASS_MAP = {
    "Item": Item, 
    "ConsumableItem": ConsumableItem,
    "HealthPotion": HealthPotion,
    "MonsterPart": Item, # MonsterPart will be an instance of Item, name passed via constructor
    "Equipment": Equipment,
    "Weapon": Weapon,
    "Armor": Armor,
    # Add other item class names and their classes here as they are defined
}

def create_item_from_dict(item_data):
    """
    Factory function to create an item instance from its serialized dictionary representation.
    """
    class_name = item_data.get("item_class_name")
    item_class = ITEM_CLASS_MAP.get(class_name)

    if not item_class:
        print(f"Warning: Unknown item class name '{class_name}' during deserialization.")
        return None

    # Prepare constructor arguments by removing 'item_class_name'
    # and potentially other non-constructor args if any were added just for serialization.
    constructor_args = {k: v for k, v in item_data.items() if k != "item_class_name"}
    
    # Specific handling for 'MonsterPart' or other generic items if needed,
    # though the general approach should handle them if their constructor takes these args.
    
    # The `slot` argument for Armor needs to be correctly passed if it's part of constructor_args.
    # The `stat_modifiers` will also be passed.
    # `item_class_name` is already removed from constructor_args.

    try:
        return item_class(**constructor_args)
    except TypeError as e:
        print(f"Error creating item {class_name} with args {constructor_args}: {e}")
        # Example: If 'slot' is missing for Armor, it might cause a TypeError if not handled by default in constructor.
        # However, 'slot' is a required positional argument for Equipment and thus Armor.
        return None

if __name__ == '__main__':
    generic_item = Item("Rock", "A common rock.", value=1)
    print(generic_item)
    print(repr(generic_item))

    stackable_item = Item("Monster Part", "A piece of a defeated monster.", value=5, stackable=True, max_stack=99)
    print(stackable_item)
    print(repr(stackable_item))

    non_stackable_unique = Item("Legendary Sword", "A unique powerful sword.", value=1000, stackable=True, max_stack=5) 
    print(non_stackable_unique) 
    non_stackable_unique.stackable = False 
    non_stackable_unique.max_stack = 1 if not non_stackable_unique.stackable else 5 
    print(repr(non_stackable_unique))
    
    print("-" * 20)
    generic_consumable = ConsumableItem("Mysterious Brew", "What does it do?", value=10)
    print(generic_consumable)
    print(repr(generic_consumable))
    
    class MockPlayer: # Renamed to avoid conflict if Player class is imported here for tests
        def __init__(self, name="TestPlayer", health=70, max_health=100):
            self.name = name
            self.health = health
            self.max_health = max_health
        def __str__(self):
            return self.name

    mock_player_target = MockPlayer()
    was_consumed = generic_consumable.use(mock_player_target)
    print(f"'{generic_consumable.name}' was consumed: {was_consumed}")

    print("-" * 20)
    health_potion = HealthPotion()
    print(health_potion)
    print(repr(health_potion))
    
    player_low_health = MockPlayer("Hero", health=30, max_health=100)
    print(f"{player_low_health.name} health before potion: {player_low_health.health}")
    was_consumed = health_potion.use(player_low_health)
    print(f"Potion used on {player_low_health.name}: {was_consumed}. Health after: {player_low_health.health}")

    player_full_health = MockPlayer("Hero", health=100, max_health=100)
    print(f"{player_full_health.name} health before potion: {player_full_health.health}")
    was_consumed = health_potion.use(player_full_health)
    print(f"Potion used on {player_full_health.name}: {was_consumed}. Health after: {player_full_health.health}")

    player_heal_past_max = MockPlayer("Hero", health=80, max_health=100) # Potion heals 50
    health_potion_strong = HealthPotion(heal_amount=50)
    print(f"{player_heal_past_max.name} health before potion: {player_heal_past_max.health}")
    was_consumed = health_potion_strong.use(player_heal_past_max)
    print(f"Potion used on {player_heal_past_max.name}: {was_consumed}. Health after: {player_heal_past_max.health}")
    assert player_heal_past_max.health == 100

    print("-" * 20)
    print("ITEM_CLASS_MAP:")
    for item_id, item_class in ITEM_CLASS_MAP.items():
        print(f"'{item_id}': {item_class.__name__}")

    print("-" * 20)
    print("Testing Equipment Creation:")
    try:
        basic_sword_data = {
            "item_class_name": "Weapon",
            "name": "Basic Sword",
            "description": "A simple sword.",
            "stat_modifiers": {"attack_power": 3},
            "value": 15
        }
        basic_sword = create_item_from_dict(basic_sword_data)
        print(f"Created: {basic_sword!r}, Slot: {basic_sword.slot}, Modifiers: {basic_sword.stat_modifiers}")
        print(f"Serialized: {basic_sword.to_dict()}")

        leather_armor_data = {
            "item_class_name": "Armor",
            "name": "Leather Vest",
            "description": "Basic protection for the torso.",
            "slot": "body", # This is crucial for Armor
            "stat_modifiers": {"defense": 5},
            "value": 20
        }
        leather_armor = create_item_from_dict(leather_armor_data)
        print(f"Created: {leather_armor!r}, Slot: {leather_armor.slot}, Modifiers: {leather_armor.stat_modifiers}")
        print(f"Serialized: {leather_armor.to_dict()}")

        # Test invalid slot for generic Equipment (should raise ValueError in constructor)
        # invalid_equipment_data = {
        #     "item_class_name": "Equipment",
        #     "name": "Odd Gear",
        #     "description": "Does not fit anywhere.",
        #     "slot": "pocket", # Invalid slot
        #     "stat_modifiers": {"luck": 1},
        #     "value": 5
        # }
        # invalid_gear = create_item_from_dict(invalid_equipment_data) # This would call Equipment constructor
        # print(f"Invalid Gear: {invalid_gear!r}") # Should not print if error raised and caught by create_item_from_dict

    except Exception as e:
        print(f"Error during equipment testing: {e}")
