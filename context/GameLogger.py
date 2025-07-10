from typing import List, Dict, Optional
from player_context import PlayerContext
import game_context
import player
import json

class GameLogger:
    def __init__(self, players: List):
        self.log = {
                "rounds": [], 
                    "players": [
                {
                    "playerId": p.player_id,
                    "name": p.name,
                    "color": p.color
                } for p in players
            ]}

    def add_round(context:PlayerContext, players: List, self):
        self.log["rounds"].append({
            "players": [
                {
                    "playerId": p.player_id,
                    "name": p.name,
                    "color": p.color
                } for p in players
            ],
            "turns": []
        })

    def add_turn(roundNumber:int, context:PlayerContext, self):
        """
        Export a PlayerContext + full player list to JSON format.
        Assumes each player object has:
          - .player_id, .name, .color, .get_score(), .trains_remaining
          - .get_claimed_routes(), .get_exposed(), .get_card_count(), .get_hidden_card_count()
          - .get_tickets() returning .start, .end, .points, .completed
        """
        player_data = []
        opponents_data = {}
        claimed_routes = []
        longest_path = context.map.get_longest_path()
        
        
        for player in self.log["rounds"]["players"]:
            player_data.append({
                "playerId": context.player_id,
                "score": context.score,
                "trainCarCounts": player.trains_remaining,
                "claimedRoutes": player.get_claimed_routes(),
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
                    "hidden": player.get_hidden_card_count()
                }
            })

            for route in player.get_claimed_routes():
                claimed_routes.append({
                    "routeID": route,
                    "claimedBy": player.player_id
                })

        turn_state = {
            "gameObjects": {
                "map": {
                    "claimedRoutes": claimed_routes,
                    "longestPath": longest_path
                },
                "decks": {
                    "trainDeckCount": context.train_deck.remaining(),
                    "destinationDeckCount": context.ticket_deck.remaining(),
                    "faceUpTrainCards": context.face_up_cards
                }
            },
            "playerInfo": player_data,
            "opponentInfo": opponents_data
        }
        self.log["rounds"]["turns"].append(turn_state)

    def add_round_to_json(context: PlayerContext, players: List) -> dict:
        """
        Export a PlayerContext + full player list to JSON format.
        Assumes each player object has:
          - .player_id, .name, .color, .get_score(), .trains_remaining
          - .get_claimed_routes(), .get_exposed(), .get_card_count(), .get_hidden_card_count()
          - .get_tickets() returning .start, .end, .points, .completed
        """
        players_data = []
        claimed_routes = []
        longest_path = context.map.get_longest_path_players()  # e.g., ["p1"]

        for player in players:
            players_data.append({
                "playerId": player.player_id,
                "score": player.get_score(),
                "trainCarCounts": player.trains_remaining,
                "claimedRoutes": player.get_claimed_routes(),
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
                    "hidden": player.get_hidden_card_count()
                }
            })

            for route in player.get_claimed_routes():
                claimed_routes.append({
                    "routeID": route,
                    "claimedBy": player.player_id
                })

        turn_state = {
            "turnNumber": context.turn_number,
            "gameObjects": {
                "map": {
                    "claimedRoutes": claimed_routes,
                    "longestPath": longest_path
                },
                "decks": {
                    "trainDeckCount": context.train_deck.remaining(),
                    "destinationDeckCount": context.ticket_deck.remaining(),
                    "faceUpTrainCards": context.face_up_cards
                }
            },
            "playerInfo": players_data
        }

        game_state = {
            "roundID": context.context.get_round_id(),
            "players": [
                {
                    "playerId": p.player_id,
                    "name": p.name,
                    "color": p.color
                } for p in players
            ],
            "turns": [turn_state]
        }

        return game_state
    
    def log_turn_for_all_players(self, context, players):
        for player in players:
            pc = PlayerContext(player.player_id, context, players)
            self.log = append_turn_to_game_log(self.log, pc, players)
            with open(f"logs/game_log_p{player.player_id}.json", "w") as f:
                json.dump(self.log, f, indent=2)