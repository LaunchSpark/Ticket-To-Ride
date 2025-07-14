from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
from copy import deepcopy
from ticket_to_ride.context.game_context import GameContext

@dataclass
class OpponentInfo:
    player_id: str
    exposed_hand: Counter[str]
    num_cards_in_hand: int
    remaining_trains: int
    longest_path: int
    has_longest_path: bool
    score: int

class PlayerContext:
    def __init__(self,player_id: str,context: GameContext, players: List):
        self.player_id = player_id
        self.map = deepcopy(context.get_map())
        self.train_deck = deepcopy(context.get_train_deck())
        self.face_up_cards = context.get_train_deck().face_up()
        self.available_routes = context.get_map().get_available_routes()
        self.longest_path = context.get_map().get_longest_path([player_id])
        self.has_longest_path = context.get_map().get_longest_path(players)
        self.ticket_deck = context.get_ticket_deck()
        self.turn_number = context.turn_num
        self.score = context.get_score(player_id)


        self.opponents = [
            OpponentInfo(
                player_id = p.player_id,
                exposed_hand = p.get_exposed(),
                num_cards_in_hand = p.get_card_count(),
                remaining_trains = p.trains_remaining,
                longest_path = context.get_map().get_longest_path([p.player_id])[p.player_id],
                has_longest_path = context.get_map().get_longest_path(p.player_id),
                score = context.get_score(p.player_id)
            ) for p in players if p.player_id != self.player_id
        ]




