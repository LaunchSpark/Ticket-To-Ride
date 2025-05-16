
from typing import List, Optional

from abstract_player import AbstractPlayer
from game_context import GameContext


class Game:
    def __init__(self, context: GameContext, players: List[AbstractPlayer]):
        self.context = context
        self.players = players
        self.turn_index = 0



    def current_player(self) -> AbstractPlayer:
        return self.players[self.turn_index % len(self.players)]

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self) -> None:
        for player in self.players:
            score = self.context.get_map().score_tickets(player.tickets, player.player_id)
            print(f"{player.player_id} final score: {score}")

    def next_turn(self) -> None:
        player = self.current_player()
        player.set_context(self.context)
        player.take_turn()
        self.turn_index += 1

    def play(self, turns: Optional[int] = None) -> None:
        rounds = turns if turns else float('inf')
        while not self._is_game_over() and rounds > 0:
            self.next_turn()
            rounds -= 1

        self._score_game()

    def __repr__(self) -> str:
        return f"Game(turn={self.turn_index}, players={[p.player_id for p in self.players]})"
