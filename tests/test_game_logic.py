import unittest
from src.player import Player # Assuming Player class is in src.player
# from src.monster import BaseMonster # Not strictly needed if only testing player.gain_xp directly
import config # To access config values like XP_PER_MONSTER_DEFEAT, etc.

# Mock SoundManager if Player expects it and it's not easily available
class MockSoundManager:
    def play_sound(self, sound_name):
        # print(f"MockSoundManager: Play sound '{sound_name}' (suppressed)")
        pass

class TestPlayerLeveling(unittest.TestCase):

    def setUp(self):
        """Set up a new player instance before each test."""
        self.mock_sound_manager = MockSoundManager()
        # Player constructor in src/player.py is:
        # def __init__(self, x, y, width, height, color, sound_manager=None):
        # Using placeholder values for x, y, width, height, color as they are not relevant for leveling logic.
        self.player = Player(x=0, y=0, width=50, height=50, color=config.GREEN, sound_manager=self.mock_sound_manager)
        
        # Reset player stats to a known initial state before each test
        self.player.level = 1
        self.player.experience_points = 0
        self.player.max_health = config.PLAYER_MAX_HEALTH # Initial max health from config
        self.player.health = self.player.max_health     # Fully healed
        # XP for next level calculation based on player's current level
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * self.player.level

    def test_xp_gain_from_monster(self):
        """Test basic XP gain without leveling up."""
        self.player.gain_xp(config.XP_PER_MONSTER_DEFEAT)
        self.assertEqual(self.player.experience_points, config.XP_PER_MONSTER_DEFEAT)
        # Ensure level is still 1 if XP is below threshold
        if config.XP_PER_MONSTER_DEFEAT < self.player.xp_to_next_level:
            self.assertEqual(self.player.level, 1)

    def test_level_up_single(self):
        """Test leveling up by one level."""
        # Set initial XP close to leveling
        # Ensure current xp_to_next_level is for level 1
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        self.player.experience_points = self.player.xp_to_next_level - config.XP_PER_MONSTER_DEFEAT
        
        old_max_health = self.player.max_health
        
        self.player.gain_xp(config.XP_PER_MONSTER_DEFEAT)
        
        self.assertEqual(self.player.level, 2)
        # Player's check_for_level_up subtracts xp_to_next_level then recalculates for new level.
        # If XP_PER_MONSTER_DEFEAT exactly meets the requirement, XP should be 0.
        self.assertEqual(self.player.experience_points, 0) 
        self.assertEqual(self.player.max_health, old_max_health + config.HEALTH_GAIN_PER_LEVEL)
        self.assertEqual(self.player.health, self.player.max_health) # Healed on level up
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 2)

    def test_level_up_multiple(self):
        """Test leveling up multiple times with a large XP gain."""
        initial_max_health = self.player.max_health
        
        # XP needed for:
        # Level 1 -> 2: config.XP_PER_LEVEL_BASE * 1
        # Level 2 -> 3: config.XP_PER_LEVEL_BASE * 2
        xp_for_level_1_to_2 = config.XP_PER_LEVEL_BASE * 1
        xp_for_level_2_to_3 = config.XP_PER_LEVEL_BASE * 2
        extra_xp = 10
        
        total_xp_gain = xp_for_level_1_to_2 + xp_for_level_2_to_3 + extra_xp
        
        self.player.gain_xp(total_xp_gain)
        
        self.assertEqual(self.player.level, 3)
        self.assertEqual(self.player.experience_points, extra_xp) # Excess XP carried over
        self.assertEqual(self.player.max_health, initial_max_health + (config.HEALTH_GAIN_PER_LEVEL * 2)) # Gained health for 2 levels
        self.assertEqual(self.player.health, self.player.max_health) # Healed on level up
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 3)

    def test_xp_carry_over(self):
        """Test that XP correctly carries over to the next level's progress."""
        # Assume player is level 1, so xp_to_next_level is config.XP_PER_LEVEL_BASE * 1
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        
        # Gain XP that exceeds current level's requirement by 20
        xp_to_gain = self.player.xp_to_next_level + 20 
        
        self.player.gain_xp(xp_to_gain)
        
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.experience_points, 20) # 20 XP carried over
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 2)

    def test_no_level_up_if_xp_not_enough(self):
        """Test that player does not level up if XP is gained but not enough for next level."""
        self.player.xp_to_next_level = config.XP_PER_LEVEL_BASE * 1
        xp_less_than_needed = self.player.xp_to_next_level - 10
        
        # Ensure xp_less_than_needed is positive and less than needed for level up
        self.assertTrue(0 < xp_less_than_needed < self.player.xp_to_next_level)

        self.player.gain_xp(xp_less_than_needed)
        
        self.assertEqual(self.player.level, 1) # Should remain level 1
        self.assertEqual(self.player.experience_points, xp_less_than_needed)
        self.assertEqual(self.player.health, self.player.max_health) # Health should not change
        self.assertEqual(self.player.xp_to_next_level, config.XP_PER_LEVEL_BASE * 1) # XP to next level unchanged

if __name__ == '__main__':
    unittest.main()
