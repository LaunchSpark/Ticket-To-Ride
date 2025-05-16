from dataclasses import dataclass
from typing import List, Dict
from collections import Counter




@dataclass
class UnknownPoolSnapshot:
    counts: Counter[str]
    total: int


@dataclass
class GameSnapshot:
    turn_index: int
    unknown_pool: UnknownPoolSnapshot

@dataclass
class OpponentInfo:
    player_id: str
    exposed_hand: Dict[str, int]

@dataclass
class PlayerViewContext:
    face_up_cards: List[str]
    available_routes: List
    ticket_deck: object
    opponents: List[OpponentInfo]
    map_view: object
    game_snapshot: GameSnapshot
