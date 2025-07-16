from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Player

class Interface:
    def __init__(self):
        self.player: Player

    def set_player(self,player):
        self.player = player