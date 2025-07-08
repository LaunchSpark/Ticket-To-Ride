from typing import List, Optional
from ticket_to_ride.Intefaces.abstract_interface import Interface

from ticket_to_ride.context.Map import Route
from ticket_to_ride.context.decks import DestinationTicket

class ExampleBot(Interface):
    # used to determine weather to
    # 1 = Draw
    # 2 = Claim
    # 3 = draw a destination ticket
    def choose_turn_action(self):
        if self.context.players
            return 1


    ##############################################################################################
    # now that you`ve decided what action to take on your turn, decide how to handle each action #
    ##############################################################################################


    # choose what cards to draw
    def choose_draw_train_action(self):


    # choose what routes to claim
    def choose_route_to_claim(self,claimable_routes):


    # choose which destination tickets to keep
    def select_ticket_offer(self,offer):
