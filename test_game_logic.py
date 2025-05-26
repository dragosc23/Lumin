import unittest
from main import Player, PLAYER_MAX_HEALTH, load_level, PLAYER_START_X, PLAYER_START_Y, RED, GRAVITY, SCREEN_HEIGHT, WHITE # Added WHITE
from pet import Pet 
from monster import Grunt, Flyer, BaseMonster 
import pygame # Import pygame for pygame.Rect used in Platform class for tests

# Mock Platform class for testing load_level if needed, or create simple ones
class MockPlatform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Add any other attributes/methods load_level might interact with
        # For current load_level, only self.rect.left and self.rect.top are used for positioning.


class TestPlayerLogic(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        # Player.__init__ is: Player(self, x, y, width, height, color)
        # Global constants like SCREEN_WIDTH, SCREEN_HEIGHT are used internally by Player methods
        # but not required for basic instantiation for these specific tests.
        # Pet is instantiated within Player.
        self.player = Player(x=50, y=50, width=40, height=40, color=(255, 255, 255)) # Using WHITE as color

    def test_player_initial_health(self):
        """Test that the player's health is initialized to PLAYER_MAX_HEALTH."""
        self.assertEqual(self.player.health, PLAYER_MAX_HEALTH)

    def test_player_take_damage(self):
        """Test that the player's health decreases correctly when taking damage."""
        initial_health = self.player.health
        damage_taken = 10
        
        self.player.health -= damage_taken
        self.assertEqual(self.player.health, initial_health - damage_taken)
        
        # Test taking more damage
        self.player.health -= damage_taken
        self.assertEqual(self.player.health, initial_health - 2 * damage_taken)

    def test_player_add_to_inventory(self):
        """Test adding items to the player's inventory."""
        self.assertEqual(len(self.player.inventory), 0) # Starts empty
        
        self.player.inventory.append("Monster Part")
        self.assertEqual(len(self.player.inventory), 1)
        self.assertIn("Monster Part", self.player.inventory)
        
        self.player.inventory.append("Another Part")
        self.assertEqual(len(self.player.inventory), 2)
        self.assertIn("Another Part", self.player.inventory)

    def test_player_attack_cooldown_initial(self):
        """Test that the player's attack cooldown is initialized correctly."""
        # Player.__init__ sets self.last_attack_time = 0
        self.assertEqual(self.player.last_attack_time, 0)


class TestMonsterLogic(unittest.TestCase):
    def setUp(self):
        """Set up for monster test methods."""
        # Using Grunt's default stats from monster.py for these tests
        # Grunt defaults: health=120, attack_damage=8, attack_range=60, 
        # attack_cooldown=90, speed=2, patrol_range_x=50
        self.monster = Grunt(x=100, y=100, width=40, height=40, color=RED,
                             gravity_val=GRAVITY, screen_height_val=SCREEN_HEIGHT)
        self.grunt_default_health = 120 # Matching Grunt's class default

    def test_monster_initial_health(self):
        """Test that the monster's health is initialized to its default."""
        self.assertEqual(self.monster.health, self.grunt_default_health)

    def test_monster_take_damage(self):
        """Test that the monster's health decreases correctly when taking damage."""
        initial_health = self.monster.health
        damage_taken = 10
        self.monster.health -= damage_taken # Simulate damage
        self.assertEqual(self.monster.health, initial_health - damage_taken)


class TestLevelLoading(unittest.TestCase):
    def setUp(self):
        """Set up for level loading test methods."""
        # Player needs (x, y, width, height, color)
        self.player = Player(x=0, y=0, width=40, height=40, color=WHITE)
        self.monsters_list_for_test = []
        
        # Define test level configurations
        # Monster class defaults: Grunt (H:120, D:8), Flyer (H:60, D:6)
        self.test_level_configs = [
            {
                "monsters": [{"type": "Grunt", "count": 1}], # Uses Grunt class defaults
                "message": "Test Level 1: One Grunt"
            },
            {
                "monsters": [{"type": "Grunt", "count": 2, "health": 150, "damage": 10, "patrol_range": 30}], # Overridden Grunt
                "message": "Test Level 2: Two Strong Grunts"
            },
            {
                "monsters": [{"type": "Flyer", "count": 1, "speed": 3.0, "patrol_range": 60}], # Flyer with speed override
                "message": "Test Level 3: One Fast Flyer"
            }
        ]
        # Create a mock platform list for load_level to use for positioning
        self.mock_platforms = [MockPlatform(100, SCREEN_HEIGHT - 100, 200, 20)]


    def test_load_level_monster_count_and_types(self):
        """Test that load_level spawns the correct number and types of monsters."""
        # Test Level 1
        load_level(0, self.player, self.monsters_list_for_test, self.test_level_configs, self.mock_platforms)
        self.assertEqual(len(self.monsters_list_for_test), 1)
        self.assertIsInstance(self.monsters_list_for_test[0], Grunt)
        # Check if default health for Grunt is applied (120)
        self.assertEqual(self.monsters_list_for_test[0].health, 120) 
        self.monsters_list_for_test.clear()

        # Test Level 2
        load_level(1, self.player, self.monsters_list_for_test, self.test_level_configs, self.mock_platforms)
        self.assertEqual(len(self.monsters_list_for_test), 2)
        self.assertIsInstance(self.monsters_list_for_test[0], Grunt)
        self.assertIsInstance(self.monsters_list_for_test[1], Grunt)
        # Check overridden health for Grunts in Level 2
        self.assertEqual(self.monsters_list_for_test[0].health, 150)
        self.assertEqual(self.monsters_list_for_test[1].health, 150)
        self.assertEqual(self.monsters_list_for_test[0].attack_damage, 10) # Check overridden damage
        self.assertEqual(self.monsters_list_for_test[0].patrol_range_x, 30) # Check overridden patrol_range
        self.monsters_list_for_test.clear()

        # Test Level 3
        load_level(2, self.player, self.monsters_list_for_test, self.test_level_configs, self.mock_platforms)
        self.assertEqual(len(self.monsters_list_for_test), 1)
        self.assertIsInstance(self.monsters_list_for_test[0], Flyer)
         # Check if default health for Flyer is applied (60)
        self.assertEqual(self.monsters_list_for_test[0].health, 60)
        self.assertEqual(self.monsters_list_for_test[0].speed, 3.0) # Check overridden speed
        self.assertEqual(self.monsters_list_for_test[0].patrol_range_x, 60) # Check overridden patrol_range

    def test_load_level_player_reset(self):
        """Test that load_level resets player's health and position."""
        self.player.health = 50
        self.player.rect.topleft = (100, 100)
        
        load_level(0, self.player, self.monsters_list_for_test, self.test_level_configs, self.mock_platforms)
        
        self.assertEqual(self.player.health, PLAYER_MAX_HEALTH)
        self.assertEqual(self.player.rect.topleft, (PLAYER_START_X, PLAYER_START_Y))


if __name__ == '__main__':
    unittest.main()
