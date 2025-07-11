from ticket_to_ride.context.Map import MapGraph
from ticket_to_ride.context.decks import TrainCardDeck, TicketDeck
from ticket_to_ride.player import Player
from collections import Counter
from typing import Dict, List



class GameContext:
    def __init__(self,player_ids):
        print("Initializing GameContext...")
        self.map_graph = MapGraph()
        self.train_deck = TrainCardDeck()
        self.ticket_deck = TicketDeck()
        self.turn_num = 0
        for p in player_ids:
            self.scores = dict[p: 0]

    def set_score(self,player_id,score):
        self.scores[player_id] = score

    def get_score(self,player_id):
        return self.scores[player_id]

    def get_map(self) -> MapGraph:
        return self.map_graph

    def get_train_deck(self) -> TrainCardDeck:
        return self.train_deck

    def get_ticket_deck(self) -> TicketDeck:
        return self.ticket_deck




