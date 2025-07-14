
from typing import List, Optional
from ticket_to_ride.context.Map import MapGraph , Route
from ticket_to_ride.context.player_context import PlayerContext
from ticket_to_ride.player import Player
from ticket_to_ride.context.game_context import GameContext
from ticket_to_ride.context.GameLogger import GameLogger

class Game:
    def __init__(self, context: GameContext, players: List[Player], logger: GameLogger, round_number: int):
        # logging variables
        self.round_number = round_number
        self.logger = logger
        
        #logic variables
        self.context = context
        self.players = players
        self.turn_index = 0
        self.score_table = dict[int: int]
        self.score_table= {1:1,
                           2:2,
                           3:4,
                           4:7,
                           5:10,
                           6:15}




    def play(self, turns: Optional[int] = None) -> None:
        while not self._is_game_over():
            self.next_turn()
            self._score_game()

    def next_turn(self) -> None:
        # set current player
        player = self.current_player()
        #
        # build and load player context into player
        player_ids = [p.player_id for p in self.players]
        player.set_context(PlayerContext(self.current_player().player_id, self.context, self.players))
        self.logger.add_turn(self.round_number, self.current_player().context)

        # have that player take their turn
        player.take_turn()

        # incriment the turn counter
        self.turn_index += 1

    def current_player(self) -> Player:
        return self.players[self.turn_index % len(self.players)]

    def _is_game_over(self) -> bool:
        return any(p.trains_remaining <= 2 for p in self.players)

    def _score_game(self) -> None:
      for p in self.players:
        values = []
        for r in self.context.get_map().get_claimed_routes(p):
            #refrence the score tabel to get score value
            values.append(self.score_table[r.length])

        score  = sum(values) + self.context.get_map().get_longest_path([p.player_id])[p.player_id] #TODO add destination ticket checking
        self.context.set_score(p.player_id,score)



    def __repr__(self) -> str:
        return f"Game(turn={self.turn_index}, players={[p.player_id for p in self.players]})"
