
from typing import List, Optional, Dict
from context.Map import MapGraph , Route
from context.player_context import PlayerContext
from player import Player
from context.game_context import GameContext
from context.GameLogger import GameLogger

class Game:
    def __init__(self, context: GameContext, players: List[Player], logger: GameLogger, round_number: int):
        # logging variables
        self.round_number = round_number
        self.logger = logger
        
        #logic variables
        self.context = context
        self.players = players
        self.turn_index = 0
        self.score_table: Dict[int, int] = {
            1:1,
            2:2,
            3:4,
            4:7,
            5:10,
            6:15
        }




    def play(self, turns: Optional[int] = None) -> None:
        while not self._is_game_over():
            self.next_turn()
            self._score_game(False)
        self._score_game(True)

    def next_turn(self) -> None:
        # set current player
        player = self.current_player()
        # build and load player context into player
        player_ids = [p.player_id for p in self.players]
        player.set_context(PlayerContext(self.current_player().player_id, self.context, self.players))
        self.logger.add_turn(self.round_number, self.current_player().context)

        # pseudo-progress-bar:
        if not self.turn_index % 15:
            print("Turn", self.turn_index, "reached")
        # have that player take their turn
        player.take_turn({
            "draw_train": False,
            "claim_route": False,
            "draw_destination": False
        })

        # incriment the turn counter
        self.turn_index += 1
        self.context.turn_num = self.turn_index

    def current_player(self) -> Player:
        return self.players[self.turn_index % len(self.players)]

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self, penalize_incomplete_tickets: bool) -> None:
        for p in self.players:
            # reference the score table to get score value
            route_values = [self.score_table[r.length] for r in self.context.get_map().get_claimed_routes(p.player_id)]
            # print (f"Scoring player {p.player_id}")
            tickets = p.get_tickets()
            # print(f"Tickets: {tickets}")
            
            if tickets is None:
                raise ValueError(f"Player {p.player_id} has no tickets (NoneType)")
            
            completed_ticket_values = [t.value for t in p.get_tickets() if t.is_completed]
            incomplete_ticket_values = [t.value for t in p.get_tickets() if not t.is_completed]
            
            score = sum(route_values) + (10 * p.has_longest_path) + sum(completed_ticket_values)
            if penalize_incomplete_tickets:
                score -= sum(incomplete_ticket_values)
            self.context.set_score(p.player_id, score)


    def __repr__(self) -> str:
        return f"Game(turn={self.turn_index}, players={[p.player_id for p in self.players]})"
