# Manages the player's inventory, including adding, removing, and using items.
from src.items import Item # Assuming Item class is in src.items

class InventoryManager:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.slots = [] # Each slot will be a dictionary: {'item': ItemObject, 'quantity': int}
        # print(f"InventoryManager initialized with capacity {self.capacity}.")

    def add_item(self, item_to_add, quantity=1):
        """Adds an item to the inventory. Handles stacking.
        Returns True if item (or part of it) was added, False otherwise (e.g., full).
        """
        if not isinstance(item_to_add, Item):
            print(f"DEBUG: Attempted to add non-Item object: {item_to_add}")
            return False

        added_all = False
        # Try to stack with existing items first
        if item_to_add.stackable:
            for slot in self.slots:
                if slot['item'].name == item_to_add.name and slot['quantity'] < slot['item'].max_stack:
                    can_add_to_stack = slot['item'].max_stack - slot['quantity']
                    add_now = min(quantity, can_add_to_stack)
                    slot['quantity'] += add_now
                    quantity -= add_now
                    # print(f"DEBUG: Stacked {add_now} of {item_to_add.name}. Remaining to add: {quantity}")
                    if quantity == 0:
                        added_all = True
                        break 
            if quantity == 0:
                return True # All items stacked

        # If items remain (or item not stackable with existing), try new slots
        while quantity > 0:
            if len(self.slots) < self.capacity:
                add_to_new_slot = min(quantity, item_to_add.max_stack) if item_to_add.stackable else 1
                # Create a new instance of the item for the new slot if it's a new item type being added
                # or if we are adding to a new slot. This is important if items can have unique IDs or states.
                # For now, assume item_to_add is a prototype or a single instance being distributed.
                # A better way for multiple additions of same item type: pass item_class and create new.
                # For this implementation, we assume item_to_add is 'one' item, and if quantity > 1, it's 'that many of this one item type'.
                self.slots.append({'item': item_to_add, 'quantity': add_to_new_slot})
                quantity -= add_to_new_slot
                # print(f"DEBUG: Added {add_to_new_slot} of {item_to_add.name} to new slot. Remaining to add: {quantity}")
                added_all = (quantity == 0) # True if all were added in this last step
            else:
                print(f"DEBUG: Inventory full. Could not add remaining {quantity} of {item_to_add.name}.")
                return quantity == 0 # Returns True if all were added before becoming full, False otherwise
        return added_all

    def remove_item(self, item_name, quantity=1):
        """Removes a specified quantity of an item by name.
        Returns True if removal was successful, False otherwise.
        Removes from stacks in reverse order of finding them (or could be front).
        """
        removed_count = 0
        # Iterate backwards to make slot removal by index easier if a slot becomes empty
        for i in range(len(self.slots) - 1, -1, -1):
            slot = self.slots[i]
            if slot['item'].name == item_name:
                if slot['quantity'] >= quantity - removed_count:
                    slot['quantity'] -= (quantity - removed_count)
                    removed_count = quantity
                else: # Take all from this stack and continue
                    removed_count += slot['quantity']
                    slot['quantity'] = 0
                
                if slot['quantity'] == 0:
                    self.slots.pop(i)
                
                if removed_count == quantity:
                    # print(f"DEBUG: Removed {quantity} of {item_name}.")
                    return True
        
        # If not all items were removed (e.g. not enough in inventory)
        # We might want to revert changes or handle partial removal based on game design.
        # For now, if we couldn't remove the full quantity, consider it a failure.
        if removed_count > 0 and removed_count < quantity:
             print(f"DEBUG: Could only remove {removed_count} of {quantity} requested for {item_name}. Operation failed as incomplete.")
             # This part would need logic to 'put back' the partially removed items if strict transaction needed.
             # For simplicity now, partial removal is not automatically reverted.
             return False # Or True if partial removal is acceptable
        
        print(f"DEBUG: Item {item_name} not found in sufficient quantity to remove {quantity}.")
        return False

    def has_item(self, item_name, quantity=1):
        """Checks if the inventory contains at least a certain quantity of an item."""
        return self.get_item_count(item_name) >= quantity

    def get_item_count(self, item_name):
        """Returns the total quantity of an item by name across all stacks."""
        count = 0
        for slot in self.slots:
            if slot['item'].name == item_name:
                count += slot['quantity']
        return count

    def get_all_items(self):
        """Returns a list of all item slots (list of dicts)."""
        return self.slots

    def __str__(self):
        if not self.slots:
            return "Inventory (0/" + str(self.capacity) + "): Empty"
        items_str = ", ".join([f"{slot['item'].name}({slot['quantity']})" for slot in self.slots])
        return f"Inventory ({len(self.slots)}/" + str(self.capacity) + f" slots): {items_str}"

    def get_serializable_data(self):
        """
        Returns a list of dictionaries representing the inventory slots,
        suitable for JSON serialization.
        """
        serializable_slots = []
        for slot in self.slots:
            serializable_slots.append({
                "item_data": slot['item'].to_dict(), # Uses the item's own serialization method
                "quantity": slot['quantity']
            })
        return serializable_slots

    def load_from_serializable_data(self, data_list):
        """
        Clears the current inventory and repopulates it from a list of
        serialized slot data.
        Requires `create_item_from_dict` from `src.items`.
        """
        from src.items import create_item_from_dict # Local import to avoid circular dependencies at module level if any

        self.slots.clear()
        if data_list is None: # Handle cases where inventory data might be missing
            print("DEBUG: No inventory data provided to load.")
            return

        for slot_data in data_list:
            item_dict = slot_data.get("item_data")
            quantity = slot_data.get("quantity")

            if item_dict and quantity is not None:
                item_instance = create_item_from_dict(item_dict)
                if item_instance:
                    # The add_item method handles stacking and new slots correctly.
                    # It expects an item instance and quantity.
                    self.add_item(item_instance, quantity)
                else:
                    print(f"Warning: Failed to create item from data: {item_dict}")
            else:
                print(f"Warning: Invalid slot data encountered: {slot_data}")

    def pop_item_at_index(self, index):
        """
        Removes and returns the item object from the slot at the specified index.
        Assumes equipment is non-stackable (quantity 1 per slot).
        Returns the ItemObject if successful, None otherwise.
        """
        if 0 <= index < len(self.slots):
            slot_to_pop = self.slots.pop(index) # Removes the slot and returns it
            item_object = slot_to_pop['item']
            # quantity = slot_to_pop['quantity'] # Should be 1 for equipment
            # print(f"DEBUG: Popped {item_object.name} (qty {quantity}) from inventory index {index}")
            return item_object
        else:
            print(f"DEBUG: Invalid index {index} for pop_item_at_index. Inventory size: {len(self.slots)}")
            return None


if __name__ == '__main__':
    from items import Item, ConsumableItem, HealthPotion, create_item_from_dict # For testing

    print("Testing InventoryManager...")
    inv_manager = InventoryManager(capacity=5)
    print(inv_manager)

    # Items for testing
    hp_potion_prototype = HealthPotion()
    monster_part_prototype = Item("Monster Part", "A common part from a monster.", value=5, stackable=True, max_stack=20)
    sword = Item("Basic Sword", "A simple sword.", value=10, stackable=False)

    print("\nAdding items...")
    inv_manager.add_item(hp_potion_prototype, 3) # Add 3 potions
    print(inv_manager)
    inv_manager.add_item(monster_part_prototype, 15) # Add 15 monster parts
    print(inv_manager)
    inv_manager.add_item(sword)
    print(inv_manager)
    inv_manager.add_item(hp_potion_prototype, 10) # Try to add more potions (stacks and new slot)
    print(inv_manager)
    inv_manager.add_item(monster_part_prototype, 10) # Try to stack more monster parts
    print(inv_manager)

    # Test adding to full inventory
    stone = Item("Pebble", "A small pebble.", value=1, stackable=True, max_stack=50)
    added_stone = inv_manager.add_item(stone, 1) # Should fail if inventory is full (5 slots used: HP, MP, Sword, HP, MP)
    print(f"Attempted to add stone: {added_stone}")
    print(inv_manager)

    print("\n--- Testing Serialization ---")
    serialized_inventory = inv_manager.get_serializable_data()
    print("Serialized Inventory:")
    import json
    print(json.dumps(serialized_inventory, indent=2))

    print("\n--- Testing Deserialization ---")
    # Simulate clearing and loading
    inv_manager_new = InventoryManager(capacity=5)
    inv_manager_new.load_from_serializable_data(serialized_inventory)
    print("New Inventory after loading:")
    print(inv_manager_new)
    
    # Verify counts in the new inventory
    print(f"New Inv: Health Potion count: {inv_manager_new.get_item_count('Health Potion')}") # Expected 13
    print(f"New Inv: Monster Part count: {inv_manager_new.get_item_count('Monster Part')}")   # Expected 25
    print(f"New Inv: Basic Sword count: {inv_manager_new.get_item_count('Basic Sword')}")     # Expected 1

    print("\n--- Testing pop_item_at_index ---")
    # Assuming inv_manager_new has: [HP(10), MP(20), Sword(1), HP(3), MP(5)]
    # Let's pop the sword (index 2)
    popped_sword = inv_manager_new.pop_item_at_index(2)
    if popped_sword:
        print(f"Popped item: {popped_sword.name}") # Expected: Basic Sword
    print(inv_manager_new) # Sword should be gone
    print(f"New Inv: Basic Sword count: {inv_manager_new.get_item_count('Basic Sword')}")     # Expected 0

    # Pop another item, e.g., the first stack of HP potions (now at index 0)
    popped_hp_stack = inv_manager_new.pop_item_at_index(0)
    if popped_hp_stack:
         # Note: pop_item_at_index returns the Item object. The original slot had quantity.
         # For equipment, quantity is 1. For stackable, it's the whole stack's item prototype.
        print(f"Popped item: {popped_hp_stack.name}") 
    print(inv_manager_new)


    print("\nChecking items...")
    print(f"Has Health Potion (1)?: {inv_manager.has_item('Health Potion', 1)}")
    print(f"Health Potion count: {inv_manager.get_item_count('Health Potion')}") # Expected 13 (one stack of 10, one of 3)
    print(f"Has Monster Part (20)?: {inv_manager.has_item('Monster Part', 20)}") # Expected 25 (15+10)
    print(f"Monster Part count: {inv_manager.get_item_count('Monster Part')}")

    print("\nRemoving items...")
    inv_manager.remove_item("Health Potion", 5) # Remove 5 potions
    print(inv_manager)
    print(f"Health Potion count: {inv_manager.get_item_count('Health Potion')}") # Expected 8

    inv_manager.remove_item("Monster Part", 25) # Remove all monster parts
    print(inv_manager)
    print(f"Monster Part count: {inv_manager.get_item_count('Monster Part')}") # Expected 0

    removed_sword = inv_manager.remove_item("Basic Sword")
    print(f"Removed sword: {removed_sword}")
    print(inv_manager)

    print("InventoryManager test complete.")
