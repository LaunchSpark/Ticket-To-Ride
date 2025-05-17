from Intefaces.human_interface import HumanPlayer
from player import Player
from Game import Game
from context.game_context import GameContext



def main():
    setup()

def setup():
    print("=== Game Setup ===")

    while True:
        try:
            num_human = int(input("Enter number of human players: "))
            if num_human >= 0:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a non-negative integer.")

    # Initialize GameContext (replace with actual map/deck initializations as needed)
    context = GameContext()

    interfaces  = []
    players = []

    max_human_id = 0
    for i in range(num_human):
        player_id = f"Human_{i}"
        players.append(Player(player_id,HumanPlayer()))
        max_human_id = i


    for p in players:
        p.set_context(context)
    # Instantiate Game with created context and players
    game = Game(context=context, players=players)

    # Start game loop (you can define this inside Game)
    game.play()

if __name__ == "__main__":
    main()
