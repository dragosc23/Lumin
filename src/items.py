# Defines game items (base Item class, specific item types like consumables, etc.)

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
        # raise NotImplementedError("Subclasses must implement the use() method.") 
        # For now, let's not raise an error, just return False so it's not consumed by default.
        return False

# Update __main__ block to test ConsumableItem if desired
if __name__ == '__main__':
    generic_item = Item("Rock", "A common rock.", value=1)
    print(generic_item)
    print(repr(generic_item))

    stackable_item = Item("Monster Part", "A piece of a defeated monster.", value=5, stackable=True, max_stack=99)
    print(stackable_item)
    print(repr(stackable_item))

    non_stackable_unique = Item("Legendary Sword", "A unique powerful sword.", value=1000, stackable=True, max_stack=5) # max_stack ignored if not stackable by default logic
    print(non_stackable_unique) # self.max_stack will be 1
    non_stackable_unique.stackable = False # Correcting it if it was meant to be non-stackable
    non_stackable_unique.max_stack = 1 if not non_stackable_unique.stackable else 5 # Re-apply logic
    print(repr(non_stackable_unique))
    
    print("-" * 20)
    generic_consumable = ConsumableItem("Mysterious Brew", "What does it do?", value=10)
    print(generic_consumable)
    print(repr(generic_consumable))
    # In a real scenario, 'target' would be a Player or Pet object
    class MockPlayer:
        def __init__(self, name="TestPlayer"):
            self.name = name
        def __str__(self):
            return self.name

    mock_player_target = MockPlayer()
    was_consumed = generic_consumable.use(mock_player_target)
    print(f"'{generic_consumable.name}' was consumed: {was_consumed}")
