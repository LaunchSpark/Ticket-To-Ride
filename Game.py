
from typing import List, Optional

from ticket_to_ride.context.player_context import PlayerContext
from ticket_to_ride.player import Player
from ticket_to_ride.context.game_context import GameContext


class Game:
    def __init__(self, context: GameContext, players: List[Player]):
        self.context = context
        self.players = players
        self.turn_index = 0



    def play(self, turns: Optional[int] = None) -> None:
        while not self._is_game_over():
            self.next_turn()
            self._score_game()

    def next_turn(self) -> None:
        # set current player
        player = self.current_player()
        #
        # build and load player context into player
        player.set_context(PlayerContext(self.current_player(),self.context,self.players))

        # have that player take their turn
        player.take_turn()

        # incriment the turn counter
        self.turn_index += 1

    def current_player(self) -> Player:
        return self.players[self.turn_index % len(self.players)]

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self) -> None:
        for player in self.players:
            score = self.context.get_map().score_tickets(player.tickets, player.player_id)
            print(f"{player.player_id} final score: {score}")

    def __repr__(self) -> str:
        return f"Game(turn={self.turn_index}, players={[p.player_id for p in self.players]})"
