from typing import List, Dict
from context.player_context import PlayerContext
from context.game_context import GameContext
from player import Player
from pathlib import Path
from context.decks import DestinationTicket
from context.Map import MapGraph
import json

class GameLogger:
    player_list: List[Player]
    def __init__(self, players: List[Player]):
        self.player_list = players
        self.log = {
            "rounds": [], 
            "players": [{
                "playerId": p.player_id,
                "name": p.name,
                "color": p.color
            } for p in players],
            "averageScores": [{
                "playerId": p.player_id,
                "scores": []
            } for p in players]
        }

    def set_player_list(self, players: List[Player]):
        self.player_list = players


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
        
        # logs the current player's information
        player = next((player for player in self.player_list if player.player_id == context.player_id))
        player_data = ({ 
            "playerId": context.player_id,
            "score": context.score,
            "remainingTrains": player.trains_remaining,
            "claimedRoutes": [f"{r}" for r in context.map.get_claimed_routes(player.player_id)],
            "destinationTickets": [
                {
                    "from": t.city1,
                    "to": t.city2,
                    "points": t.value,
                    "completed": t.is_completed
                } for t in player.get_tickets()
            ],
            "hand": {
                "black": player.get_hand().get("B", 0),
                "blue": player.get_hand().get("U", 0),
                "green": player.get_hand().get("G", 0),
                "locomotive": player.get_hand().get("L", 0),
                "orange": player.get_hand().get("O", 0),
                "purple": player.get_hand().get("P", 0),
                "red": player.get_hand().get("R", 0),
                "white": player.get_hand().get("W", 0),
                "yellow": player.get_hand().get("Y", 0)
            }
        })

        # log each opponent's information
        opponents_data = [({
            "playerId": p.player_id,
            "score": p.score,
            "trainCarCount": p.remaining_trains,
            "claimedRoutes": [f"{r}" for r in context.map.get_claimed_routes(p.player_id)],
            "destinationTicketCount": p.destination_ticket_count,
            "hand": {
                "public": {
                    "black": p.exposed_hand.get("B", 0),
                    "blue": p.exposed_hand.get("U", 0),
                    "green": p.exposed_hand.get("G", 0),
                    "locomotive": p.exposed_hand.get("L", 0),
                    "orange": p.exposed_hand.get("O", 0),
                    "purple": p.exposed_hand.get("P", 0),
                    "red": p.exposed_hand.get("R", 0),
                    "white": p.exposed_hand.get("W", 0),
                    "yellow": p.exposed_hand.get("Y", 0)
                },
                "hidden": p.num_cards_in_hand - p.exposed_hand.total()
            }
        }) for p in context.opponents]

        turn_state = {
            "player": player_data,
            "opponents": opponents_data,
            "gameObjects": {
                "decks": {
                    "marketCards": context.face_up_cards
                }
            }
        }
        self.log["rounds"][round_number]["turns"].append(turn_state)

    def find_player_score(self, turn: Dict, player_id: str) -> int:
        if (turn["player"]["playerId"] == player_id):
            # print("It was player's turn this turn and their score was", turn["player"]["score"])
            return turn["player"]["score"]
        else:
            player_score = next((p["score"] for p in turn["opponents"] if p["playerId"] == player_id))
            # print("It was someone else's turn this turn, but the player you're asking about scored", player_score, "this turn")
            return player_score
    
    def log_match_stats(self):
        for turn in range(0, max([len(r["turns"]) for r in self.log["rounds"]])):
            for p in self.player_list:
                # print("Getting average scores for", p.name)
                player_scores = next((player for player in self.log["averageScores"] if player["playerId"] == p.player_id))["scores"]
                # print("looking for score on turn", turn)
                turn_scores = [self.find_player_score(r["turns"][turn], p.player_id) for r in self.log["rounds"] if (turn < len(r["turns"]))]
                # print("Scores list:", turn_scores)
                player_scores.append(round(sum(turn_scores) / len(turn_scores)))
    
    def export_log(self, file_name: str):
        with open(f"display/web display/html1/logs/{file_name}.json", "w") as f:
            json.dump(self.log, f, indent=2)