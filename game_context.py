from decks import TrainCardDeck , TicketDeck
from Map import MapGraph
from collections import Counter
from typing import Dict, List
from abstract_player import AbstractPlayer



class GameSnapshot:
    def __init__(self, turn_index: int, player_snapshots: Dict[str, 'PlayerSnapshot'], unknown_pool: 'UnknownPoolSnapshot'):
        self.turn_index = turn_index
        self.player_snapshots = player_snapshots
        self.unknown_pool = unknown_pool

class PlayerSnapshot:
    def __init__(self, player_id: str):
        self.player_id = player_id

class UnknownPoolSnapshot:
    def __init__(self, counts: Counter[str], total: int):
        self.counts = counts
        self.total = total

class GameContext:
    def __init__(self, map_graph: MapGraph, train_deck: TrainCardDeck, ticket_deck: TicketDeck):
        self.map_graph = map_graph
        self.train_deck = train_deck
        self.ticket_deck = ticket_deck

    def get_map(self) -> MapGraph:
        return self.map_graph

    def get_train_deck(self) -> TrainCardDeck:
        return self.train_deck

    def get_ticket_deck(self) -> TicketDeck:
        return self.ticket_deck

    def build_snapshot(self, active_player: AbstractPlayer, players: List[AbstractPlayer], turn_index: int, full_deck: Counter[str]) -> GameSnapshot:
        known = Counter(self.train_deck.face_up()) + self.train_deck.discard_pile + active_player.hand_counts()
        for p in players:
            if p.player_id != active_player.player_id:
                known.update(p.get_exposed())
        unseen = full_deck - known
        pool = UnknownPoolSnapshot(counts=unseen, total=sum(unseen.values()))

        player_snapshots: Dict[str, PlayerSnapshot] = {}
        for p in players:
            player_snapshots[p.player_id] = PlayerSnapshot(player_id=p.player_id)

        return GameSnapshot(
            turn_index=turn_index,
            player_snapshots=player_snapshots,
            unknown_pool=pool
        )

    def get_opponent_snapshots(self, current_player_id: str, players: List[AbstractPlayer]) -> List[PlayerSnapshot]:
        return [PlayerSnapshot(player_id=p.player_id) for p in players if p.player_id != current_player_id]

