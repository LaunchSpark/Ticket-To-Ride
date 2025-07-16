from typing import List, TYPE_CHECKING
from Intefaces.abstract_interface import Interface
import random

from context.Map import MapGraph
from context.Map import Route
from context.decks import DestinationTicket
if TYPE_CHECKING:
    from player import Player

class ExampleBot(Interface): # TODO: actually build the thing
    # used to determine weather to
    # 1 = Draw
    # 2 = Claim
    # 3 = draw a destination ticket
    def choose_turn_action(self):
        return random.randrange(1,3)


    ##############################################################################################
    # now that you`ve decided what action to take on your turn, decide how to handle each action #
    ##############################################################################################


    # choose what cards to draw
    def choose_draw_train_action(self) -> int:
        return random.randrange(-1,5)

    # choose what routes to claim
    def choose_route_to_claim(self, claimable_routes: List[Route]) -> Route:
        return claimable_routes[random.randrange(0,len(claimable_routes))]

    # choose what color to spend on a gray route (will spend most common color on input of None or on invalid color input)
    def choose_color_to_spend(self, route: Route, color_options: List[str]) -> 'str | None':
        return None

    # choose which destination tickets to keep
    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[int]:
        return [0,1]


    #######################
    #       helpers       #
    #######################

    def path_finder(self,city1,city2):
        return None