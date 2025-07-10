import weakref

class Interface:
    def __init__(self):
        self.context = None
        self.player = None




    def set_context(self,context):
        self.context = context

    def set_player(self,player):
        self.player = weakref.ref(player)