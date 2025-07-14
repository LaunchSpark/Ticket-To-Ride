from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
from copy import deepcopy
from game_context import GameContext
from Map import MapGraph, Route
from decks import TicketDeck, TrainCardDeck, DestinationTicket

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
        player = next((player for player in players if player.player_id == player_id), None)
        self.player_id: str = player_id
        self.map: MapGraph = deepcopy(context.get_map())
        self.train_deck: TicketDeck = deepcopy(context.get_train_deck())
        self.face_up_cards: TrainCardDeck = context.get_train_deck().face_up()
        self.available_routes: List[Route] = context.get_map().get_available_routes()
        self.longest_path: int = context.get_map().get_longest_path([self.player_id])[self.player_id]
        self.has_longest_path: bool = self.player_id in context.get_map().get_longest_path([p.player_id for p in players])
        self.turn_number: int = context.turn_num
        self.score: int = context.get_score(player_id)

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




