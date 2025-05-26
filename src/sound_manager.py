import pygame
import os # For joining paths if used internally, though paths are passed in

class SoundManager:
    def __init__(self):
        self.mixer_initialized = False
        self.sounds = {}
        self.music_playing = False
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
            print("SoundManager: pygame.mixer initialized successfully.")
        except pygame.error as e:
            print(f"SoundManager Error: Failed to initialize pygame.mixer: {e}")
            print("SoundManager: All sound and music methods will be disabled.")

    def load_sound(self, sound_name, file_path):
        if not self.mixer_initialized:
            return
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[sound_name] = sound
            print(f"SoundManager: Loaded sound '{sound_name}' from '{file_path}'")
        except pygame.error as e:
            print(f"SoundManager Error: Loading sound '{sound_name}' from '{file_path}': {e}")
        except FileNotFoundError:
            print(f"SoundManager Error: Sound file not found for '{sound_name}' at '{file_path}'")

    def play_sound(self, sound_name):
        if not self.mixer_initialized:
            return
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                # print(f"SoundManager: Playing sound: {sound_name}") # Can be too verbose
            except pygame.error as e:
                print(f"SoundManager Error: Playing sound '{sound_name}': {e}")
        else:
            print(f"SoundManager Warning: Sound '{sound_name}' not found/loaded.")

    def play_music(self, file_path, loops=-1, volume=0.5):
        if not self.mixer_initialized:
            return
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self.music_playing = True
            print(f"SoundManager: Playing music from '{file_path}'")
        except pygame.error as e:
            print(f"SoundManager Error: Playing music from '{file_path}': {e}")
        except FileNotFoundError:
            print(f"SoundManager Error: Music file not found at '{file_path}'")

    def stop_music(self):
        if not self.mixer_initialized or not self.music_playing:
            return
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
            print("SoundManager: Music stopped.")
        except pygame.error as e:
            print(f"SoundManager Error: Stopping music: {e}")

    def set_music_volume(self, volume):
        if not self.mixer_initialized:
            return
        try:
            # Clamp volume between 0.0 and 1.0
            clamped_volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(clamped_volume)
            # print(f"SoundManager: Music volume set to {clamped_volume}")
        except pygame.error as e:
            print(f"SoundManager Error: Setting music volume: {e}")


# Example usage (for testing - this part won't be in the final file if run by main)
if __name__ == '__main__':
    pygame.init() # Initialize main pygame module first
    screen = pygame.display.set_mode([200, 200]) # Mixer needs a display context sometimes

    print("Testing SoundManager with actual Pygame mixer...")
    sound_mgr = SoundManager()

    if sound_mgr.mixer_initialized:
        # Create dummy sound files for testing if they don't exist
        # This part is tricky in a sandboxed env; assume files would exist in local dev.
        print("\nNOTE: For local testing, create dummy .wav/.ogg files in ./assets subdirs or expect errors.")
        DUMMY_SOUNDS_DIR = 'assets/sounds'
        DUMMY_MUSIC_DIR = 'assets/music'
        if not os.path.exists(DUMMY_SOUNDS_DIR):
            os.makedirs(DUMMY_SOUNDS_DIR)
        if not os.path.exists(DUMMY_MUSIC_DIR):
            os.makedirs(DUMMY_MUSIC_DIR)

        # Example: sound_mgr.load_sound("test_effect", "assets/sounds/dummy_effect.wav")
        # sound_mgr.play_sound("test_effect")

        # Example: sound_mgr.play_music("assets/music/dummy_theme.ogg")
        # pygame.time.wait(2000) # Wait for 2 seconds
        # sound_mgr.stop_music()
        print("\nSoundManager test finished. If no errors about missing files, good.")
        print("If you saw 'File not found' errors, that's expected if dummy files aren't present.")
    else:
        print("\nSoundManager mixer failed to initialize. Sound tests skipped.")

    pygame.quit()
