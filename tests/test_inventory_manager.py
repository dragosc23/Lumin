import unittest
import sys
import os

# Adjust sys.path to allow imports from the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inventory_manager import InventoryManager
from src.items import Item, HealthPotion, Weapon, Equipment # Added Equipment for completeness

class TestInventoryManager(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.inventory_cap_5 = InventoryManager(capacity=5)
        self.inventory_cap_2 = InventoryManager(capacity=2)
        self.inventory_cap_1 = InventoryManager(capacity=1)

        # Common test items
        self.potion1 = HealthPotion(name="Minor Healing Potion", heal_amount=20, max_stack=10)
        self.potion2 = HealthPotion(name="Greater Healing Potion", heal_amount=50, max_stack=5)
        self.sword1 = Weapon(name="Iron Sword", description="A basic iron sword.", stat_modifiers={"attack_power": 5})
        self.sword2 = Weapon(name="Steel Sword", description="A sturdy steel sword.", stat_modifiers={"attack_power": 8})
        self.shield = Equipment(name="Wooden Shield", description="A basic shield.", slot="shield", stat_modifiers={"defense": 3}) # Assuming 'shield' is a valid slot or Item can handle it
        self.stackable_gem = Item(name="Ruby", description="A shiny ruby.", stackable=True, max_stack=20)
        self.unique_artifact = Item(name="Ancient Tablet", description="An old tablet.", stackable=False)


    def test_initialization(self):
        self.assertEqual(self.inventory_cap_5.capacity, 5)
        self.assertEqual(self.inventory_cap_5.slots, [])
        
        inventory_default_cap = InventoryManager() # Assuming default capacity is 10 or some other value
        self.assertTrue(inventory_default_cap.capacity > 0) # Check if default capacity is set
        self.assertEqual(inventory_default_cap.slots, [])


    def test_add_new_item_simple(self):
        # Add a single non-stackable item
        added = self.inventory_cap_5.add_item(self.unique_artifact, 1)
        self.assertTrue(added)
        self.assertEqual(len(self.inventory_cap_5.slots), 1)
        self.assertEqual(self.inventory_cap_5.slots[0]['item'].name, "Ancient Tablet")
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 1)
        self.assertEqual(self.inventory_cap_5.get_item_count("Ancient Tablet"), 1)

        # Add a single stackable item
        self.inventory_cap_5.slots.clear() # Clear for next test part
        added_stackable = self.inventory_cap_5.add_item(self.potion1, 1)
        self.assertTrue(added_stackable)
        self.assertEqual(len(self.inventory_cap_5.slots), 1)
        self.assertEqual(self.inventory_cap_5.slots[0]['item'].name, "Minor Healing Potion")
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 1)
        self.assertEqual(self.inventory_cap_5.get_item_count("Minor Healing Potion"), 1)


    def test_add_item_stacking(self):
        self.inventory_cap_5.add_item(self.potion1, 2)
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 2)
        
        self.inventory_cap_5.add_item(self.potion1, 3)
        self.assertEqual(len(self.inventory_cap_5.slots), 1) # Should still be one slot
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 5)
        self.assertEqual(self.inventory_cap_5.get_item_count("Minor Healing Potion"), 5)


    def test_add_item_exceed_stack_capacity(self):
        # potion2 has max_stack = 5
        self.inventory_cap_5.add_item(self.potion2, 3) # Add 3 potions
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 3)
        
        self.inventory_cap_5.add_item(self.potion2, 4) # Add 4 more (total 7, but max_stack is 5)
        # Expected: one stack of 5, another stack of 2
        self.assertEqual(len(self.inventory_cap_5.slots), 2)
        
        # Check quantities in slots (order might vary depending on implementation)
        quantities = sorted([s['quantity'] for s in self.inventory_cap_5.slots if s['item'].name == "Greater Healing Potion"])
        self.assertEqual(quantities, [2, 5])
        self.assertEqual(self.inventory_cap_5.get_item_count("Greater Healing Potion"), 7)


    def test_add_item_inventory_full(self):
        # Use inventory_cap_2 (capacity 2)
        self.inventory_cap_2.add_item(self.sword1, 1)
        self.inventory_cap_2.add_item(self.unique_artifact, 1)
        self.assertEqual(len(self.inventory_cap_2.slots), 2)

        # Attempt to add a third non-stackable item
        added_fail = self.inventory_cap_2.add_item(self.sword2, 1)
        self.assertFalse(added_fail)
        self.assertEqual(len(self.inventory_cap_2.slots), 2) # Still 2 slots
        self.assertEqual(self.inventory_cap_2.get_item_count(self.sword2.name), 0)

        # Attempt to add a stackable item that would require a new slot
        added_stackable_fail = self.inventory_cap_2.add_item(self.potion1, 1)
        self.assertFalse(added_stackable_fail)
        self.assertEqual(len(self.inventory_cap_2.slots), 2)
        self.assertEqual(self.inventory_cap_2.get_item_count(self.potion1.name), 0)


    def test_add_item_partial_add_inventory_full(self):
        # inventory_cap_1 (capacity 1), potion1 (max_stack 10)
        self.inventory_cap_1.add_item(self.potion1, 5) # Fills the one slot with 5/10
        self.assertEqual(self.inventory_cap_1.slots[0]['quantity'], 5)
        
        # Attempt to add 7 more. Should add 5 to fill stack (total 10/10), remaining 2 cannot be added.
        added_partial = self.inventory_cap_1.add_item(self.potion1, 7)
        self.assertFalse(added_partial) # Returns False because not all 7 were added
        self.assertEqual(self.inventory_cap_1.slots[0]['quantity'], 10) # Slot is now full
        self.assertEqual(self.inventory_cap_1.get_item_count(self.potion1.name), 10)
        self.assertEqual(len(self.inventory_cap_1.slots), 1) # Still only one slot


    def test_remove_item_simple(self):
        self.inventory_cap_5.add_item(self.potion1, 3)
        removed = self.inventory_cap_5.remove_item(self.potion1.name, 2)
        self.assertTrue(removed)
        self.assertEqual(self.inventory_cap_5.slots[0]['quantity'], 1)
        self.assertEqual(self.inventory_cap_5.get_item_count(self.potion1.name), 1)


    def test_remove_item_exact_quantity_empties_stack(self):
        self.inventory_cap_5.add_item(self.potion1, 3)
        removed = self.inventory_cap_5.remove_item(self.potion1.name, 3)
        self.assertTrue(removed)
        # Slot should be removed
        found_item = any(slot['item'].name == self.potion1.name for slot in self.inventory_cap_5.slots)
        self.assertFalse(found_item)
        self.assertEqual(self.inventory_cap_5.get_item_count(self.potion1.name), 0)
        self.assertEqual(len(self.inventory_cap_5.slots), 0)


    def test_remove_item_more_than_exists(self):
        self.inventory_cap_5.add_item(self.potion1, 2)
        # Current behavior of remove_item: it removes what it can and returns True if any amount was removed.
        # If it's intended to be transactional (all or nothing), the implementation and this test would change.
        # Based on `remove_item` finding first stack and decrementing:
        removed = self.inventory_cap_5.remove_item(self.potion1.name, 3)
        self.assertFalse(removed) # Should return False as it couldn't remove the full quantity
        # Check state after: The current implementation removes from the first stack found,
        # and if that stack is depleted, it stops. It doesn't try other stacks for the same item name.
        # Given the current remove_item logic, if we try to remove 3 from a stack of 2, it will empty that stack.
        # The loop in remove_item: `for slot in self.slots:`
        # `if slot['item'].name == item_name:`
        # `  if slot['quantity'] >= quantity_to_remove:` -> this is false (2 < 3)
        # `  else: quantity_actually_removed = slot['quantity'] ... slot['quantity'] = 0 ... remaining_to_remove = quantity_to_remove - quantity_actually_removed`
        # This part of `remove_item` seems to imply it *tries* to remove more after emptying a stack, but the loop structure
        # and `return True` after first partial removal means it doesn't.
        # Let's assume the provided code's `remove_item` has a bug or specific behavior:
        # If it tries to remove 3 from a stack of 2:
        # It calculates `quantity_actually_removed = 2`, `slot['quantity'] = 0`, `remaining_to_remove = 1`.
        # Then `self.slots.remove(slot)`. `return True` (because `quantity_actually_removed > 0`).
        # This means if we try to remove more than in one stack, it empties that stack and says true.
        # The problem statement implies a return False if not all can be removed.
        # Let's test against the problem statement's expectation of `remove_item` returning False.
        # And that the inventory state should be unchanged if it returns False.
        # This requires `remove_item` to be transactional or check total count first.
        # For now, I will test the *current* behavior of the provided InventoryManager.
        # If the current `remove_item` is used, it will remove the 2 items and return True.
        # The subtask asks to verify "item quantity is still 2 (or that the removal was transactional and reverted)"
        # This indicates a desired transactional behavior.
        # Let's assume a corrected transactional `remove_item` for the test, or test current behavior and note it.
        # Given the prompt: "Verify remove_item returns False." and "Verify the item quantity is still 2"
        # This implies the test should expect a transactional remove_item.
        # My current `inventory_manager.py`'s `remove_item` is NOT transactional.
        # I will write the test assuming the *desired* transactional behavior.
        # This means the test might fail with the current `remove_item` implementation.
        
        # Assuming transactional remove_item (or one that checks total count first):
        self.assertFalse(removed, "remove_item should return False if not all items can be removed.")
        self.assertEqual(self.inventory_cap_5.get_item_count(self.potion1.name), 2, "Item quantity should be unchanged if full removal failed.")


    def test_remove_item_not_in_inventory(self):
        removed = self.inventory_cap_5.remove_item("Unknown Gem", 1)
        self.assertFalse(removed)


    def test_has_item(self):
        self.inventory_cap_5.add_item(self.potion1, 3)
        self.assertTrue(self.inventory_cap_5.has_item(self.potion1.name, 2))
        self.assertTrue(self.inventory_cap_5.has_item(self.potion1.name, 3))
        self.assertFalse(self.inventory_cap_5.has_item(self.potion1.name, 4))
        self.assertFalse(self.inventory_cap_5.has_item("Unknown Potion", 1))


    def test_get_item_count(self):
        # potion2 has max_stack = 5
        self.inventory_cap_5.add_item(self.potion2, 3) # Slot 1: 3
        self.inventory_cap_5.add_item(self.potion2, 4) # Slot 1: 5, Slot 2: 2
        self.assertEqual(self.inventory_cap_5.get_item_count(self.potion2.name), 7)
        self.assertEqual(self.inventory_cap_5.get_item_count("NonExistentItem"), 0)


    def test_get_all_items(self):
        self.inventory_cap_5.add_item(self.potion1, 2)
        self.inventory_cap_5.add_item(self.sword1, 1)
        
        all_items = self.inventory_cap_5.get_all_items()
        self.assertEqual(len(all_items), 2)
        
        names_quantities = sorted([(d['item'].name, d['quantity']) for d in all_items])
        expected = sorted([(self.potion1.name, 2), (self.sword1.name, 1)])
        self.assertEqual(names_quantities, expected)


    def test_pop_item_at_index(self):
        self.inventory_cap_5.add_item(self.potion1, 1)
        self.inventory_cap_5.add_item(self.sword1, 1)
        self.inventory_cap_5.add_item(self.stackable_gem, 5)
        self.assertEqual(len(self.inventory_cap_5.slots), 3)

        # Assuming order of addition is preserved: Potion1, Sword1, Ruby
        popped_item_obj = self.inventory_cap_5.pop_item_at_index(1) # Sword1
        self.assertIsNotNone(popped_item_obj)
        self.assertEqual(popped_item_obj.name, self.sword1.name)
        self.assertEqual(len(self.inventory_cap_5.slots), 2)
        self.assertEqual(self.inventory_cap_5.get_item_count(self.sword1.name), 0)
        
        # Check remaining items
        remaining_names = [s['item'].name for s in self.inventory_cap_5.slots]
        self.assertNotIn(self.sword1.name, remaining_names)
        self.assertIn(self.potion1.name, remaining_names)
        self.assertIn(self.stackable_gem.name, remaining_names)

        # Pop from invalid index
        invalid_pop = self.inventory_cap_5.pop_item_at_index(99)
        self.assertIsNone(invalid_pop)
        invalid_pop_negative = self.inventory_cap_5.pop_item_at_index(-1)
        self.assertIsNone(invalid_pop_negative)
        
        # Pop last item
        self.inventory_cap_5.pop_item_at_index(1) # Ruby (was at index 2, now 1)
        self.assertEqual(len(self.inventory_cap_5.slots), 1)
        
        # Pop first item
        self.inventory_cap_5.pop_item_at_index(0) # Potion1
        self.assertEqual(len(self.inventory_cap_5.slots), 0)
        
        # Pop from empty inventory
        empty_pop = self.inventory_cap_5.pop_item_at_index(0)
        self.assertIsNone(empty_pop)


    def test_serialization_deserialization(self):
        self.inventory_cap_5.add_item(self.potion1, 3) # Heal Potion, stackable
        self.inventory_cap_5.add_item(self.sword1, 1)   # Weapon, non-stackable
        self.inventory_cap_5.add_item(self.potion2, 5) # Another Heal Potion, fills stack
        self.inventory_cap_5.add_item(self.potion2, 2) # Overflow to new stack for potion2
        
        serialized_data = self.inventory_cap_5.get_serializable_data()
        
        new_inventory = InventoryManager(capacity=5)
        new_inventory.load_from_serializable_data(serialized_data)
        
        self.assertEqual(new_inventory.capacity, self.inventory_cap_5.capacity)
        self.assertEqual(len(new_inventory.slots), len(self.inventory_cap_5.slots))
        
        self.assertEqual(new_inventory.get_item_count(self.potion1.name), 3)
        self.assertEqual(new_inventory.get_item_count(self.sword1.name), 1)
        self.assertEqual(new_inventory.get_item_count(self.potion2.name), 7) # 5 + 2
        
        # More detailed check of slot structure if necessary
        original_items_repr = sorted([ (s['item'].to_dict(), s['quantity']) for s in self.inventory_cap_5.get_all_items() ], key=lambda x: (x[0]['name'], x[1]))
        new_items_repr = sorted([ (s['item'].to_dict(), s['quantity']) for s in new_inventory.get_all_items() ], key=lambda x: (x[0]['name'], x[1]))
        self.assertEqual(new_items_repr, original_items_repr)


if __name__ == '__main__':
    unittest.main()
