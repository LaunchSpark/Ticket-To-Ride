from Intefaces.random_bot import RandomBot
from Intefaces.example_bot import ExampleBot
from player import Player
from Game import Game
from context.game_context import GameContext
from context.GameLogger import GameLogger
from typing import List

from glob import glob
import sys
import pathlib
import importlib.util




def main():
    players, logger = setup()
    round_number = 0
    round_limit = 10 # Can be changed to adjust how many consecutive rounds to run before the program stops
    
    while (round_number < round_limit):
        # Add empty round to log
        logger.add_round()
        
        # Initialize GameContext
        context = GameContext([p.player_id for p in players])
        game = Game(context, players, logger, round_number)
        game.play()

        round_number += 1

    logger.log_match_stats()
    logger.export_log("-".join([p.name for p in players]))

def setup() -> 'tuple[List[Player],GameLogger]':
    print("=== Game Setup ===")

    # # Step 1: Add the directory to sys.path
    # sys.path.append(r"./ticket_to_ride/Intefaces")
    #
    # # Step 2: Loop through all Python files in the directory
    # for file in glob(r".(Intefaces/*.py"):
    #     file = pathlib.Path(file)  # Convert the string path to a Path object
    # sys.path.append(file)  # Append the file path
    # imported_module = importlib.import_module(file.stem)# Import module by its name
    #
    #
    # globals().update(imported_module.__dict__)  # Update the global namespace with the imported functions
    # # Now you can call any function defined in the imported files

    while True:
        try:
            player_count = int(input("Enter number of players: "))
            if 0 <= player_count <= 4:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a non-negative integer 1-4.")

    player_ids = []
    players = []
    player_names = [
        "test_1",
        "test_2",
        "test_3",
        "test_4",
    ]
    player_colors = [
        "red",
        "blue",
        "green",
        "yellow"
    ]
    for i in range(player_count):
        player_id = f"bot_{i}"
        players.append(Player(player_id,RandomBot(), player_names[i], player_colors[i]))

        #for the game context
        player_ids.append(player_id)

    # Initialize logger and round_number counter
    logger = GameLogger(players)

    return (players, logger)
    

if __name__ == "__main__":
    main()
