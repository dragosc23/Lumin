# 2D Autobattler/Platformer Game

A simple 2D offline Autobattler and Platformer game where you progress through levels, fight monsters, and collect items with the help of a pet. Sprites are generated as basic shapes by the code.

## Features

-   Platformer gameplay (movement, jump, gravity)
-   Autobattler mechanics (auto-attack for player, pet, and monsters)
-   Pet companion that follows and assists in combat
-   Multiple levels with varied monster configurations (Grunts and Flyers)
-   Basic inventory system (collect "Monster Parts")
-   On-screen UI for health, level, and inventory
-   Code-generated visual sprites
-   Unit tests for core game logic

## Requirements

-   Python 3 (tested with Python 3.10+)
-   Pygame library

## Setup

1.  **Ensure Python 3 is installed.**
    You can download it from [python.org](https://www.python.org/).
2.  **Install Pygame:**
    Open a terminal or command prompt and run:
    ```bash
    pip install pygame
    ```
3.  **Clone or download the game source code.**

## How to Run

1.  Navigate to the root directory of the project (where `main.py` is located) in your terminal.
2.  Run the game using the following command:
    ```bash
    python main.py
    ```

## Project Structure

-   `main.py`: Main game script.
-   `src/`: Contains core game logic modules.
    -   `monster.py`: Defines monster classes and behaviors.
    -   `pet.py`: Defines the pet class and behavior.
-   `tests/`: Contains unit tests.
    -   `test_game_logic.py`: Unit tests for game logic.
-   `README.md`: This file.
