from typing import List
from Intefaces.abstract_interface import Interface
import random

from context.Map import MapGraph
from context.Map import Route
from context.decks import DestinationTicket

class YourBotName(Interface):
    # used to determine weather to
    # 1 = Draw
    # 2 = Claim
    # 3 = draw a destination ticket
    def choose_turn_action(self):
        pass




    ##############################################################################################
    # now that you`ve decided what action to take on your turn, decide how to handle each action #
    ##############################################################################################


    # choose what cards to draw
    def choose_draw_train_action(self):
        pass

    # choose what routes to claim -------------------------------------------------------------------#
    # claimable_routes is a list of tuples( Route , number of locomotives needed to claim)           #
    # return a tuple (route, number of locomotives you wish to spend)                                #
    # so to buy a route that costs 2 of a color using 1 locomotive you could return tuple(route, 1)  #
    # error handling is done on the back end --------------------------------------------------------#
    def choose_route_to_claim(self,claimable_routes: List[tuple[Route,int]]) -> 'tuple[Route,int]':
        pass

    # choose what color to spend on a gray route (will spend most common color on input of None or on invalid color input)
    def choose_color_to_spend(self, route: Route, color_options: List[str]) -> 'str | None':
        pass

    # choose which destination tickets to keep must keep at least 1
    def select_ticket_offer(self,offer):
        pass