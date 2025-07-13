from typing import List, Dict, Optional
from player_context import PlayerContext
from game_context import GameContext
from player import Player
from pathlib import Path
from decks import DestinationTicket
import json

class GameLogger:
    player_list: List[Player]
    file: Path = "../../display/web display/html1/logs"
    def __init__(self, players: List[Player]):
        self.player_list = players
        self.log = {
            "rounds": [], 
            "players": [{
                "playerId": p.player_id,
                "name": p.name,
                "color": p.color
            } for p in players
        ]}

    def add_round(self):
        self.log["rounds"].append({
            "turns": []
        })

    def add_turn(self, round_number:int, context:PlayerContext):
        """
        Export a PlayerContext + full player list to JSON format.
        Assumes each player object has:
          - .player_id, .name, .color, .get_score(), .trains_remaining
          - .get_claimed_routes(), .get_exposed(), .get_card_count(), .get_hidden_card_count()
          - .get_tickets() returning .start, .end, .points, .completed
        """
        longest_path = context.map.get_longest_path(self.player_list)
        claimed_routes = []
        
        # logs the current player's information
        player_data = ({ 
            "playerId": context.player_id,
            "score": context.score,
            "remainingTrains": context.remaining_trains,
            "claimedRoutes": [route for route in context.map.routes if route.claimed_by is context.player_id],
            "longestPath": context.longest_path,
            "hasLongestPath": context.has_longest_path, 
            "destinationTickets": [
                {
                    "from": ticket.city1,
                    "to": ticket.city2,
                    "points": ticket.value,
                    "completed": None # TODO replace "None" with a function call PENDING a function to check completion of destination tickets
                } for ticket in player.get_tickets() # TODO implement DestinationTicket.get_tickets()
            ],
            "hand": { # TODO implement player.get_hand() function
                "black": ,
                "blue": ,
                "green": ,
                "locomotive": ,
                "orange": ,
                "purple": ,
                "red": ,
                "white": ,
                "yellow": 
            }
        })

        # log each opponent's information
        opponents_data = [({ # Log the 
            "playerId": context.player_id,
            "score": context.score,
            "trainCarCount": p.trains_remaining,
            "claimed_routes": [route for route in context.map.routes if route.claimed_by is playerId],
            "longest_path": context.longest_path,
            "destinationTickets": [
                {
                    "from": t.start,
                    "to": t.end,
                    "points": t.points,
                    "completed": t.completed
                } for t in p.get_tickets() # TODO: add player.get_tickets()
            ],
            "hand": {
                "public": dict(p.get_exposed()),
                "hidden": p.get_card_count() - p.get_exposed().length()
            }
        }) for p in self.player_list if p.player_id != context.player_id]

        longest_paths = context.map.get_longest_path(self.player_list)
        longest_path_length = max(list(longest_paths.values))
        turn_state = {
            "player": player_data,
            "opponents": opponents_data,
            "game_objects": {
                "map": {
                    "claimed_routes": context.map.get_claimed_routes(),
                    "longest_path": {
                        "length": longest_path_length,
                        "player_id": None
                    }
                },
                "decks": {
                    "train_deck_count": context.train_deck.remaining(),
                    "destination_deck_count": context.ticket_deck.remaining(),
                    "marketCards": context.face_up_cards
                }
            }
        }
        self.log["rounds"][round_number]["turns"].append(turn_state)
    
    def log_turn_for_all_players(self, context, players):
        for player in players:
            pc = PlayerContext(player.player_id, context, players)
            self.log = add_turn(self.log, pc, players)
            with open(f"logs/game_log_p{player.player_id}.json", "w") as f:
                json.dump(self.log, f, indent=2)