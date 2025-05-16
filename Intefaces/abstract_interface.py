import weakref

class Interface:
    def __init__(self,Player):
        self.player = weakref.ref(Player)

