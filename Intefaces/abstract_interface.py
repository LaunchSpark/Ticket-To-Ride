import weakref

class Interface:
    def __init__(self):
        self.player = None

    def set_player(self,Player):
        self.player = weakref.ref(Player)