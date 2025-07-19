from player import Player
from Game import Game
from context.game_context import GameContext
from context.GameLogger import GameLogger
from typing import List

import inspect
import pkgutil
import importlib
import Interfaces
from Interfaces.abstract_interface import Interface


def load_bots() -> dict:
    """Dynamically load all bot classes from the Interfaces package."""
    bots = {}
    for _, module_name, _ in pkgutil.iter_modules(Interfaces.__path__):
        if module_name == "abstract_interface":
            continue
        module = importlib.import_module(f"Interfaces.{module_name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Interface) and obj is not Interface:
                bots[name] = obj
    return bots




def main():
    """Entry point for running a full match via the command line."""
    players, logger = setup()
    round_number = 0
    round_limit = 10 # Can be changed to adjust how many consecutive rounds to run before the program stops
    
    while (round_number < round_limit):
        # Add empty round to log
        logger.add_round()
        
        # Initialize GameContext
        context = GameContext([p.player_id for p in players])
        game = Game(context, players, logger, round_number)
        print(f"Starting round {round_number}")
        game.play()

        round_number += 1
        if round_number != round_limit:
            players = [Player(p.player_id, p.get_interface(), p.name, p.color) for p in players]
            logger.set_player_list(players)

    logger.log_match_stats()
    logger.export_log("-".join([p.name for p in players]))

def setup() -> 'tuple[List[Player],GameLogger]':
    """Gather setup information and instantiate all players."""
    print("=== Game Setup ===")


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

    available_bots = load_bots()
    bot_names = list(available_bots.keys())

    for i in range(player_count):
        player_id = f"bot_{i}"
        print(f"Select bot for player {i+1}:")
        for idx, name in enumerate(bot_names, start=1):
            print(f"  {idx}. {name}")
        while True:
            try:
                choice = int(input("Enter choice number: ")) - 1
                if 0 <= choice < len(bot_names):
                    break
            except ValueError:
                pass
            print("Invalid choice. Please try again.")

        bot_class = available_bots[bot_names[choice]]
        players.append(Player(player_id, bot_class(), player_names[i], player_colors[i]))

        # for the game context
        player_ids.append(player_id)

    # Initialize logger and round_number counter
    logger = GameLogger(players)

    return (players, logger)
    

if __name__ == "__main__":
    main()
