import pygame

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sounds = {}
            self.music_playing = False
            print("SoundManager initialized successfully.")
        except pygame.error as e:
            print(f"Error initializing pygame.mixer: {e}")
            print("SoundManager will be disabled (no sounds or music).")
            # Fallback: disable methods if mixer failed to init
            self.play_sound = lambda sound_name: None
            self.load_sound = lambda sound_name, file_path: None
            self.play_music = lambda file_path, loops=-1: None
            self.stop_music = lambda: None


    def load_sound(self, sound_name, file_path):
        # In a real scenario, you'd load the sound file here:
        # try:
        #     sound = pygame.mixer.Sound(file_path)
        #     self.sounds[sound_name] = sound
        #     print(f"Loaded sound: {sound_name} from {file_path}")
        # except pygame.error as e:
        #     print(f"Error loading sound {sound_name} from {file_path}: {e}")
        print(f"DEBUG: Conceptually loading sound '{sound_name}' from '{file_path}'")
        self.sounds[sound_name] = file_path # Store path for now for debug

    def play_sound(self, sound_name):
        # In a real scenario, you'd play the loaded sound:
        # if sound_name in self.sounds:
        #     self.sounds[sound_name].play()
        # else:
        #     print(f"Sound '{sound_name}' not found.")
        if hasattr(self, 'sounds') and sound_name in self.sounds:
            print(f"DEBUG: Playing sound: {sound_name} (path: {self.sounds[sound_name]})")
        else:
            # This case handles if mixer init failed or sound not loaded
            if not hasattr(self, 'sounds'): # Mixer init failed
                 pass # Method was replaced by lambda, no print needed here
            else: # Sound not loaded
                 print(f"DEBUG: Sound '{sound_name}' not loaded/found.")


    def play_music(self, file_path, loops=-1):
        # In a real scenario:
        # try:
        #     pygame.mixer.music.load(file_path)
        #     pygame.mixer.music.play(loops)
        #     self.music_playing = True
        #     print(f"Playing music: {file_path}")
        # except pygame.error as e:
        #     print(f"Error playing music {file_path}: {e}")
        print(f"DEBUG: Playing music from '{file_path}' with loops={loops}")
        self.music_playing = True

    def stop_music(self):
        # In a real scenario:
        # pygame.mixer.music.stop()
        # self.music_playing = False
        print("DEBUG: Stopping music.")
        self.music_playing = False

if __name__ == '__main__':
    # Basic test
    pygame.init() # Pygame needs to be initialized for mixer to work if run standalone
    sm = SoundManager()
    if hasattr(sm, 'sounds'): # Check if mixer initialized properly
        sm.load_sound("test_ping", "sounds/ping.wav") # Conceptual path
        sm.play_sound("test_ping")
        sm.play_sound("non_existent_sound")
        sm.play_music("music/background.mp3")
        print(f"Music playing: {sm.music_playing}")
        sm.stop_music()
        print(f"Music playing: {sm.music_playing}")
    pygame.quit()
