from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
import weakref
from copy import deepcopy

@dataclass
class OpponentInfo:
    player_id: str
    exposed_hand: Counter[str]
    num_cards_in_hand: int
    remaining_trains: int

class PlayerContext:
    def __init__(self,player_id,context,players):
        self.player_id = player_id
        self.map = deepcopy(context.get_map())
        self.train_deck = deepcopy(context.context.get_train_deck())
        self.ticket_deck = deepcopy(context.context.get_ticket_deck())
        self.context = context
        self.face_up_cards = face_up_cards = self.context.get_train_deck().face_up()
        self.available_routes = self.context.get_map().get_available_routes()
        self.ticket_deck = self.context.get_ticket_deck()
        self.turn_number = context.turn_num


        self.opponents = [
            OpponentInfo(
                player_id = p.player_id,
                exposed_hand = p.get_exposed(),
                num_cards_in_hand = p.get_card_count(),
                remaining_trains = p.trains_remaining
            ) for p in players if p.player_id != self.player_id
        ]




