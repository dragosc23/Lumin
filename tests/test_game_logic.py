import unittest
from src.player import Player
from src.monster import BaseMonster
from src.items import Item, Weapon, Armor, EQUIPMENT_SLOTS # Added Weapon, Armor, EQUIPMENT_SLOTS
from src.inventory_manager import InventoryManager # Added InventoryManager
import config

# Mock SoundManager if Player expects it and it's not easily available
class MockSoundManager:
    def play_sound(self, sound_name):
        # print(f"MockSoundManager: Play sound '{sound_name}' (suppressed)")
        pass

class TestPlayerLeveling(unittest.TestCase):

    def setUp(self):
        """Set up a new player instance before each test."""
        self.mock_sound_manager = MockSoundManager()
        self.player = Player(x=0, y=0, width=config.PLAYER_WIDTH, height=config.PLAYER_HEIGHT, color=config.PLAYER_COLOR, sound_manager=self.mock_sound_manager)
        
        # Reset player stats to a known initial state before each test
        self.player.level = 1
        self.player.experience_points = 0
        self.player.max_health = config.PLAYER_MAX_HEALTH
        self.player.health = self.player.max_health
        self.player.attack_power = config.PLAYER_BASE_ATTACK_POWER 
        self.player.defense = config.PLAYER_BASE_DEFENSE         
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.player.level

    def test_xp_gain_from_monster(self):
        self.player.gain_xp(config.XP_PER_MONSTER_DEFEAT)
        self.assertEqual(self.player.experience_points, config.XP_PER_MONSTER_DEFEAT)
        if config.XP_PER_MONSTER_DEFEAT < self.player.xp_to_next_level:
            self.assertEqual(self.player.level, 1)

    def test_level_up_single(self):
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        self.player.experience_points = self.player.xp_to_next_level - config.XP_PER_MONSTER_DEFEAT
        
        old_max_health = self.player.max_health
        old_attack_power = self.player.attack_power
        old_defense = self.player.defense
        
        self.player.gain_xp(config.XP_PER_MONSTER_DEFEAT)
        
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.experience_points, 0) 
        self.assertEqual(self.player.max_health, old_max_health + config.HEALTH_GAIN_PER_LEVEL)
        self.assertEqual(self.player.attack_power, old_attack_power + config.ATTACK_POWER_GAIN_PER_LEVEL)
        self.assertEqual(self.player.defense, old_defense + config.DEFENSE_GAIN_PER_LEVEL)
        self.assertEqual(self.player.health, self.player.get_total_max_health()) # Check against total max health
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 2)

    def test_level_up_multiple(self):
        initial_max_health = self.player.max_health
        initial_attack_power = self.player.attack_power
        initial_defense = self.player.defense
        
        xp_for_level_1_to_2 = config.XP_PER_LEVEL_BASE * 1
        xp_for_level_2_to_3 = config.XP_PER_LEVEL_BASE * 2
        extra_xp = 10
        
        total_xp_gain = xp_for_level_1_to_2 + xp_for_level_2_to_3 + extra_xp
        
        self.player.gain_xp(total_xp_gain) # Should reach level 3
        
        self.assertEqual(self.player.level, 3)
        self.assertEqual(self.player.experience_points, extra_xp)
        self.assertEqual(self.player.max_health, initial_max_health + (config.HEALTH_GAIN_PER_LEVEL * 2))
        self.assertEqual(self.player.attack_power, initial_attack_power + (config.ATTACK_POWER_GAIN_PER_LEVEL * 2))
        self.assertEqual(self.player.defense, initial_defense + (config.DEFENSE_GAIN_PER_LEVEL * 2))
        self.assertEqual(self.player.health, self.player.get_total_max_health()) # Check against total max health
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 3)

    def test_xp_carry_over(self):
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        xp_to_gain = self.player.xp_to_next_level + 20 
        self.player.gain_xp(xp_to_gain)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.experience_points, 20)
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 2)

    def test_no_level_up_if_xp_not_enough(self):
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        xp_less_than_needed = self.player.xp_to_next_level - 10
        self.assertTrue(0 < xp_less_than_needed < self.player.xp_to_next_level)
        self.player.gain_xp(xp_less_than_needed)
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.experience_points, xp_less_than_needed)
        self.assertEqual(self.player.health, self.player.get_total_max_health()) # Check against total max health
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 1)


class TestEquipmentSystem(unittest.TestCase):
    def setUp(self):
        self.sound_manager = MockSoundManager()
        self.player = Player(x=0, y=0, width=config.PLAYER_WIDTH, height=config.PLAYER_HEIGHT, color=config.PLAYER_COLOR, sound_manager=self.sound_manager)
        
        # Reset player to a known state
        self.player.level = 1
        self.player.experience_points = 0
        self.player.attack_power = config.PLAYER_BASE_ATTACK_POWER
        self.player.defense = config.PLAYER_BASE_DEFENSE
        self.player.max_health = config.PLAYER_MAX_HEALTH # This is base max_health
        self.player.health = self.player.max_health       # Current health set to base max_health
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.player.level
        self.player.inventory = InventoryManager(capacity=config.PLAYER_INVENTORY_CAPACITY)
        for slot_key in EQUIPMENT_SLOTS.keys():
            self.player.equipment[slot_key] = None

        self.basic_sword = Weapon(name="Test Sword", description="A sword for testing.", stat_modifiers={"attack_power": 5})
        self.leather_armor = Armor(name="Test Armor", description="Armor for testing.", slot="body", stat_modifiers={"defense": 3, "max_health": 10})
        self.another_sword = Weapon(name="Another Sword", description="...", stat_modifiers={"attack_power": 8})

    def test_equip_item_updates_stats_and_slot(self):
        self.player.inventory.add_item(self.basic_sword) # Assumes quantity 1 for equipment
        self.player.equip_item(inventory_index=0)
        self.assertIs(self.player.equipment["weapon"], self.basic_sword)
        self.assertEqual(self.player.get_total_attack_power(), config.PLAYER_BASE_ATTACK_POWER + 5)
        self.assertEqual(self.player.inventory.get_item_count("Test Sword"), 0)

    def test_equip_item_replaces_existing_and_returns_old_to_inventory(self):
        self.player.equipment["weapon"] = self.basic_sword # Manually equip first sword
        
        self.player.inventory.add_item(self.another_sword)
        self.player.equip_item(inventory_index=0) # Equip another_sword from inventory
        
        self.assertIs(self.player.equipment["weapon"], self.another_sword)
        self.assertEqual(self.player.get_total_attack_power(), config.PLAYER_BASE_ATTACK_POWER + 8)
        self.assertEqual(self.player.inventory.get_item_count("Test Sword"), 1) # Basic sword returned
        self.assertEqual(self.player.inventory.get_item_count("Another Sword"), 0)

    def test_unequip_item_updates_stats_and_inventory(self):
        self.player.equipment["body"] = self.leather_armor # Manually equip armor
        
        self.player.unequip_item("body")
        
        self.assertIsNone(self.player.equipment["body"])
        self.assertEqual(self.player.get_total_defense(), config.PLAYER_BASE_DEFENSE)
        self.assertEqual(self.player.get_total_max_health(), config.PLAYER_MAX_HEALTH) # Back to base max_health
        self.assertEqual(self.player.inventory.get_item_count("Test Armor"), 1)

    def test_health_adjustment_on_equip_unequip(self):
        self.player.max_health = 100 # Base max health for easier percentage
        self.player.health = 50      # Current health at 50%
        
        # Equip self.leather_armor (adds 10 max_health)
        self.player.inventory.add_item(self.leather_armor)
        self.player.equip_item(0) 
        
        # New total max health is 100 (base) + 10 (armor) = 110.
        # Player health should be int(110 * (50/100)) = 55.
        self.assertEqual(self.player.get_total_max_health(), 110)
        self.assertEqual(self.player.health, 55)
        
        # Unequip self.leather_armor
        self.player.unequip_item("body")
        
        # Total max health back to 100. Player health should be int(100 * (55/110)) = 50.
        self.assertEqual(self.player.get_total_max_health(), 100)
        self.assertEqual(self.player.health, 50)

    def test_equip_fail_if_item_not_equipment(self):
        non_equipment_item = Item("Rock", "A plain rock")
        self.player.inventory.add_item(non_equipment_item)
        self.player.equip_item(0) # Attempt to equip the rock
        
        # Check that no equipment slot was filled with the rock
        for slot_key in EQUIPMENT_SLOTS.keys():
            self.assertIsNot(self.player.equipment.get(slot_key), non_equipment_item, f"Rock incorrectly equipped in {slot_key}")
        self.assertEqual(self.player.inventory.get_item_count("Rock"), 1) # Rock should remain in inventory

    def test_unequip_fail_if_inventory_full(self):
        # Fill inventory
        for i in range(config.PLAYER_INVENTORY_CAPACITY):
            self.player.inventory.add_item(Item(f"Dummy Item {i}", "fills a slot"))
            
        self.player.equipment["weapon"] = self.basic_sword # Equip sword
        
        result = self.player.unequip_item("weapon") # Attempt to unequip
        
        self.assertFalse(result) # unequip_item should return False on failure
        self.assertIs(self.player.equipment["weapon"], self.basic_sword) # Sword still equipped


class TestCombatSystem(unittest.TestCase):

    def setUp(self):
        self.mock_sound_manager = MockSoundManager()
        
        self.player = Player(x=0, y=0, width=config.PLAYER_WIDTH, height=config.PLAYER_HEIGHT, color=config.PLAYER_COLOR, sound_manager=self.mock_sound_manager)
        self.player.health = config.PLAYER_MAX_HEALTH # Use base max_health
        self.player.attack_power = config.PLAYER_BASE_ATTACK_POWER
        self.player.defense = config.PLAYER_BASE_DEFENSE
        self.player.last_attack_time = self.player.attack_cooldown 

        self.monster = BaseMonster(x=100, y=0, width=40, height=40, color=config.RED, 
                                   health=100, attack_damage=10, attack_range=50, 
                                   attack_cooldown=60, speed=2)
        self.monster.last_attack_time = self.monster.attack_cooldown

    def test_player_damage_uses_total_attack_power(self): # Renamed for clarity
        # Equip a weapon
        weapon = Weapon("Test Dagger", "", {"attack_power": 3})
        self.player.equipment["weapon"] = weapon # Directly equip
        
        initial_monster_health = self.monster.health
        expected_damage = config.PLAYER_BASE_ATTACK_POWER + 3
        
        # Simulate Player.update() relevant part
        damage_dealt_by_player = self.player.get_total_attack_power()
        self.monster.health -= damage_dealt_by_player
        
        self.assertEqual(self.monster.health, initial_monster_health - expected_damage)
        self.assertEqual(damage_dealt_by_player, expected_damage)


    def test_player_total_defense_reduces_damage(self): # Renamed for clarity
        # Equip armor
        armor = Armor("Test Shield", "", "body", {"defense": 2})
        self.player.equipment["body"] = armor # Directly equip

        self.monster.attack_damage = 10 # Monster deals 10 base damage
        initial_player_health = self.player.health
        
        expected_player_defense = config.PLAYER_BASE_DEFENSE + 2
        expected_damage_taken = max(1, self.monster.attack_damage - expected_player_defense)
        
        # Simulate BaseMonster.attack() relevant part
        player_total_defense = self.player.get_total_defense()
        effective_damage_to_player = max(1, self.monster.attack_damage - player_total_defense)
        self.player.health -= effective_damage_to_player
        
        self.assertEqual(player_total_defense, expected_player_defense)
        self.assertEqual(self.player.health, initial_player_health - effective_damage_to_player)
        self.assertEqual(effective_damage_to_player, expected_damage_taken)


    def test_player_defense_minimum_damage(self): # No change needed here, already tests total defense implicitly if setup changes
        self.player.defense = 15 # Base defense set high for this test
        self.monster.attack_damage = 10 
        initial_player_health = self.player.health
        
        expected_damage = max(1, self.monster.attack_damage - self.player.get_total_defense())
        self.player.health -= expected_damage
        
        self.assertEqual(self.player.health, initial_player_health - 1)
        self.assertEqual(expected_damage, 1)

if __name__ == '__main__':
    unittest.main()
