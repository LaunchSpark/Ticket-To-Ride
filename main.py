from ticket_to_ride.Intefaces.example_bot import ExampleBot
from ticket_to_ride.player import Player
from ticket_to_ride.Game import Game
from ticket_to_ride.context.game_context import GameContext



def main():
    setup()







def setup():
    print("=== Game Setup ===")

    while True:
        try:
            player_count = int(input("Enter number of players: "))
            if 0 <= player_count <= 4:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a non-negative integer 1-4.")

    # Initialize GameContext
    context = GameContext()


    players = []
    for i in range(player_count):
        player_id = f"bot_{i}"
        players.append(Player(player_id,ExampleBot()))

    for p in players:
        p.set_context(context)
    # Instantiate Game with created context and players
    game = Game(context=context, players=players)

    game.play()

if __name__ == "__main__":
    main()
