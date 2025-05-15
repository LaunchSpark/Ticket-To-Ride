
from typing import List, Dict, Optional

from abstract_player import AbstractPlayer
from human_player import HumanPlayer
from stratagy_player import StrategyPlayer





class Game:
    def __init__(self, players: Optional[List[AbstractPlayer]], context: GameContext, ruleset: object):
        self.context = context
        self.turn_index = 0
        self.RULESET = ruleset

        if players is None:
            self.setup()
        else:
            self.players = players

    def setup(self):
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

        self.players = []

        for i in range(num_human):
            player_id = f"Human_{i+1}"
            self.players.append(HumanPlayer(player_id, self.context))

        for i in range(num_ai):
            player_id = f"AI_{i+1}"
            self.players.append(StrategyPlayer(player_id, self.context))

    def current_player(self) -> AbstractPlayer:
        return self.players[self.turn_index % len(self.players)]

    def _execute_draw_phase(self, player: AbstractPlayer) -> None:
        action = player.choose_draw_action()
        if action == 'deck':
            card = self.context.get_train_deck().draw_face_down()
            player.add_cards([card])
        elif action.startswith('face_up_'):
            index = int(action.split('_')[-1])
            card = self.context.get_train_deck().draw_face_up(index)
            player.add_cards([card])

    def _execute_claim_phase(self, player: AbstractPlayer) -> None:
        route = player.choose_route_to_claim()
        if route:
            player.claim_route(route)
            self.context.get_map().claim_route(route)

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self) -> None:
        for player in self.players:
            score = self.context.get_map().score_tickets(player.tickets, player.player_id)
            print(f"{player.player_id} final score: {score}")

    def next_turn(self) -> None:
        player = self.current_player()
        snapshot = self.context.build_snapshot(
            active_player=player,
            players=self.players,
            turn_index=self.turn_index,
            full_deck=self.RULESET.full_deck
        )
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
