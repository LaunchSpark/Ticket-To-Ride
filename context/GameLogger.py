from typing import List, Dict, Optional
from player_context import PlayerContext
from game_context import GameContext
from player import Player
import json

class GameLogger:
    player_list: List[Player]
    def __init__(self, players: List[Players]):
        self.player_list = players
        self.log = {
            "rounds": [], 
            "players": [{
                "playerId": p.player_id,
                "name": p.name,
                "color": p.color
            } for p in players
        ]}

    def add_round(context:PlayerContext, players: List, self):
        self.log["rounds"].append({
            "turns": []
        })

    def add_turn(round_number:int, context:PlayerContext, self):
        """
        Export a PlayerContext + full player list to JSON format.
        Assumes each player object has:
          - .player_id, .name, .color, .get_score(), .trains_remaining
          - .get_claimed_routes(), .get_exposed(), .get_card_count(), .get_hidden_card_count()
          - .get_tickets() returning .start, .end, .points, .completed
        """
        player_data = {}
        opponents_data = []
        longest_path = context.map.get_longest_path()
        
        
        for player in self.log["players"]:
            if player["player_id"] == context.player_id:
                player_data = ({
                    "player_id": context.playerId,
                    "score": context.player,
                    "remaining_trains": context.remaining_trians,
                    "claimed_routes": [route for route in context.map.routes if route.claimed_by is context.player_id],
                    "longest_path": context.longest_path,
                    "has_longest_path": context.has_longest_path, 
                    "destinationTickets": [
                        {
                            "from": ,
                            "to": "Raleigh",
                            "points": ,
                            "completed":  
                        },
                        {
                            "from": ,
                            "to": ,
                            "points": ,
                            "completed": 
                        }
                    ],
                    "hand": { 
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
            else:
                opponents_data.append({
                    "playerId": context.player_id,
                    "score": context.score,
                    "trainCarCount": player.trains_remaining,
                    "claimed_routes": [route for route in context.map.routes if route.claimed_by is playerId],
                    "longest_path": context.longest_path,
                    "destinationTickets": [
                        {
                            "from": t.start,
                            "to": t.end,
                            "points": t.points,
                            "completed": t.completed
                        } for t in player.get_tickets()
                    ],
                    "hand": {
                        "public": dict(player.get_exposed()),
                        "hidden": player.get_card_count() - player.get_exposed().length()
                    }
                })

        turn_state = {
            "player": player_data,
            "opponents": opponents_data,
            "game_objects": {
                "map": {
                    "claimed_routes": claimed_routes,
                    "longest_path": [
                        "length": map.get_longest_path(player_list)["length"],
                        "player_id": map.get_longest_path(player_list)[""]
                    ]
                },
                "decks": {
                    "train_deck_count": context.train_deck.remaining(),
                    "destination_deck_count": context.ticket_deck.remaining(),
                    "face_up_train_cards": context.face_up_cards
                }
            }
        }
        self.log["rounds"][round_number]["turns"].append(turn_state)
    
    def log_turn_for_all_players(self, context, players):
        for player in players:
            pc = PlayerContext(player.player_id, context, players)
            self.log = append_turn_to_game_log(self.log, pc, players)
            with open(f"logs/game_log_p{player.player_id}.json", "w") as f:
                json.dump(self.log, f, indent=2)