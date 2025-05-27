import json
import os
import logging
import traceback
import config # Added import

# Configure logging
logging.basicConfig(filename='game_errors.log', # TODO: Consider using a constant from config.py if defined
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a') # Ensure append mode

class SaveManager:
    def __init__(self, save_filename=None): # Changed default to None
        if save_filename is None:
            self.save_filename = config.SAVE_FILENAME
        else:
            self.save_filename = save_filename

    def save_data(self, data):
        try:
            with open(self.save_filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            logging.error(f"Error saving game data to {self.save_filename}: {e}\n{traceback.format_exc()}")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred while saving data: {e}\n{traceback.format_exc()}")
            return False

    def load_data(self):
        if not os.path.exists(self.save_filename):
            return None
        try:
            with open(self.save_filename, 'r') as f:
                data = json.load(f)
            return data
        except IOError as e:
            logging.error(f"Error loading game data from {self.save_filename}: {e}\n{traceback.format_exc()}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {self.save_filename}: {e}\n{traceback.format_exc()}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading data: {e}\n{traceback.format_exc()}")
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
