from typing import List, Dict, Optional
from player_context import PlayerContext
import game_context
import player
import json

class GameLogger:
    def __init__(self):
        self.log = {"games": []}

    def add_game_to_json(context: PlayerContext, players: List) -> dict:
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
            "gameID": context.context.get_game_id(),
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
    
    def append_turn_to_game_log(game_logcontext: PlayerContext, players: List):
        game_log = {"games": []}  # Start or load this from a file

        # For each player at the end of their turn:
        for player in players:
            player_context = PlayerContext(player.player_id, context, players)
            game_log = append_turn_to_game_log(game_log, player_context, players)

        # Then save to file if needed:
        with open(f"game_log_p{player.player_id}.json", "w") as f:
            json.dump(game_log, f, indent=2)
    
    def log_turn_for_all_players(self, context, players):
        for player in players:
            pc = PlayerContext(player.player_id, context, players)
            self.log = append_turn_to_game_log(self.log, pc, players)
            with open(f"logs/game_log_p{player.player_id}.json", "w") as f:
                json.dump(self.log, f, indent=2)