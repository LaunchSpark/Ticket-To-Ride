
from typing import List, Optional
from collections import Counter
import copy

from player_view_context import PlayerViewContext, OpponentInfo, UnknownPoolSnapshot, GameSnapshot
from abstract_player import AbstractPlayer
from game_context import GameContext


class Game:
    def __init__(self, context: GameContext, players: List[AbstractPlayer]):
        self.context = context
        self.players = players
        self.turn_index = 0
        self.PlayerViewContext = self.build_player_view(players[0])


    def current_player(self) -> AbstractPlayer:
        return self.players[self.turn_index % len(self.players)]

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self) -> None:
        for player in self.players:
            score = self.context.get_map().score_tickets(player.tickets, player.player_id)
            print(f"{player.player_id} final score: {score}")

    def build_player_view(self, active_player: AbstractPlayer) -> PlayerViewContext:
        face_up_cards = self.context.get_train_deck().face_up()
        available_routes = self.context.get_map().get_available_routes()
        ticket_deck = self.context.get_ticket_deck()

        opponents = [
            OpponentInfo(
                player_id=p.player_id,
                exposed_hand=p.get_exposed()
            ) for p in self.players if p.player_id != active_player.player_id
        ]

        map_view = copy.deepcopy(self.context.get_map())
        game_snapshot = self.build_snapshot(active_player)

        return PlayerViewContext(
            face_up_cards=face_up_cards,
            available_routes=available_routes,
            ticket_deck=ticket_deck,
            opponents=opponents,
            map_view=map_view,
            game_snapshot = game_snapshot
        )

    def build_snapshot(self, active_player: AbstractPlayer) -> GameSnapshot:
        known = Counter(self.context.get_train_deck().face_up()) + Counter(self.context.get_train_deck().get_discard_pile()) + active_player.hand_counts()
        for p in self.players:
            if p.player_id != active_player.player_id:
                known.update(p.get_exposed())

        unseen = Counter(self.context.get_train_deck().get_full_deck()) - known
        pool = UnknownPoolSnapshot(counts=unseen, total=sum(unseen.values()))
        turn = self.turn_index

        return GameSnapshot(
            turn_index = turn,
            unknown_pool=pool
        )

    def next_turn(self) -> None:
        player = self.current_player()
        snapshot = self.build_snapshot(player)
        view = self.build_player_view(player)
        view.game_snapshot = snapshot
        player.take_turn(view)
        self.turn_index += 1

    def play(self, turns: Optional[int] = None) -> None:
        rounds = turns if turns else float('inf')
        while not self._is_game_over() and rounds > 0:
            self.next_turn()
            rounds -= 1

        self._score_game()

    def __repr__(self) -> str:
        return f"Game(turn={self.turn_index}, players={[p.player_id for p in self.players]})"
