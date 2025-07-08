from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
import weakref
from copy import deepcopy








@dataclass
class OpponentInfo:
    player_id: str
    exposed_hand: Dict[str, int]
    num_cards_in_hand: int



class PlayerContext:

    turn_index: int
    face_up_cards: List[str]
    available_routes: List
    opponents: List[OpponentInfo]
    unknown_counts: Counter[str]
    total_unknown: int


    def __init__(self,context):
        self.map = deepcopy(context.get_map())
        self.train_deck = deepcopy(context.context.get_train_deck())
        self.ticket_deck = deepcopy(context.context.get_ticket_deck())
        self.context = context



    def build_player_view(self,context):

        face_up_cards = self.context.get_train_deck().face_up()
        available_routes = self.context.get_map().get_available_routes()
        ticket_deck = self.context.get_ticket_deck()

        opponents = [
            OpponentInfo(
                player_id=p.player_id,
                exposed_hand=p.get_exposed()
            ) for p in self.players if p.player_id != self.player_id
        ]


        game_snapshot = self.build_snapshot()

        return PlayerViewContext(
            face_up_cards=face_up_cards,
            available_routes=available_routes,
            ticket_deck=ticket_deck,
            opponents=opponents,
            map=map,
            game_snapshot = game_snapshot
        )

    def build_snapshot(self) -> GameSnapshot:
        known = Counter(self.context.get_train_deck().face_up()) + Counter(self.context.get_train_deck().get_discard_pile()) + self.hand_counts()
        for p in self.players:
            if p.player_id != self.player_id:
                known.update(p.get_exposed())

        unseen = Counter(self.context.get_train_deck().get_full_deck()) - known
        pool = UnknownPoolSnapshot(counts=unseen, total=sum(unseen.values()))
        turn = self.turn_index

        return GameSnapshot(
            turn_index = turn,
            unknown_pool=pool
        )

