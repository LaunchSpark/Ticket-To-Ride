from ticket_to_ride.Intefaces.random_bot import RandomBot
from ticket_to_ride.Intefaces.example_bot import ExampleBot
from ticket_to_ride.player import Player
from ticket_to_ride.Game import Game
from ticket_to_ride.context.game_context import GameContext

from glob import glob
import sys
import pathlib
import importlib.util




def main():
    setup()







def setup():
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
    for i in range(player_count):
        player_id = f"bot_{i}"
        players.append(Player(player_id,RandomBot()))

        #for the game context
        player_ids.append(player_id)

    # Initialize GameContext
    context = GameContext(player_ids)

    game = Game(context=context, players=players)

    game.play()

if __name__ == "__main__":
    main()
