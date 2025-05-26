import json
import os

class SaveManager:
    def __init__(self, save_filename="savegame.json"):
        self.save_filename = save_filename

    def save_data(self, data):
        try:
            with open(self.save_filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving game data to {self.save_filename}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while saving data: {e}")
            return False

    def load_data(self):
        if not os.path.exists(self.save_filename):
            return None
        try:
            with open(self.save_filename, 'r') as f:
                data = json.load(f)
            return data
        except IOError as e:
            print(f"Error loading game data from {self.save_filename}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.save_filename}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading data: {e}")
            return None

    def delete_save(self):
        if os.path.exists(self.save_filename):
            try:
                os.remove(self.save_filename)
                return True
            except OSError as e:
                print(f"Error deleting save file {self.save_filename}: {e}")
                return False
        else:
            return False

# Basic test structure, can be expanded later
if __name__ == '__main__':
    print("SaveManager module loaded. Run tests separately if needed.")
