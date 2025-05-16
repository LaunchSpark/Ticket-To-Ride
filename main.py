from player_types.stratagy_player import StrategyPlayer
from player_types.human_player import HumanPlayer
from Game import Game
from game_context import GameContext



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

    while True:
        try:
            num_ai = int(input("Enter number of AI players: "))
            if num_ai >= 0:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a non-negative integer.")

    # Initialize GameContext (replace with actual map/deck initializations as needed)
    context = GameContext()

    players = []
    max_huma_id = 0
    for i in range(num_human):
        player_id = f"Human_{i}"
        players.append(HumanPlayer(player_id))
        max_huma_id = i

    for i in range(num_ai):
        player_id = f"AI_{i + max_huma_id + 1}"
        players.append(StrategyPlayer(player_id))

    for p in players:
        p.set_context(context)
    # Instantiate Game with created context and players
    game = Game(context=context, players=players)

    # Start game loop (you can define this inside Game)
    game.play()

if __name__ == "__main__":
    main()
