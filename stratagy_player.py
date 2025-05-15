from typing import List, Optional, Dict
from collections import Counter
from abstract_player import AbstractPlayer
from dataclasses import dataclass
from typing import Tuple


@dataclass
class DesiredRoute:
    city_a: str
    city_b: str
    expected_utility: float
    committed_colour: str | None = None  # used only for grey routes

    def key(self) -> Tuple[str, str]:
        return tuple(sorted((self.city_a, self.city_b)))


class StrategyPlayer(AbstractPlayer):
    def choose_turn_action(self) -> int:
        # Decide whether to draw cards, claim a route, or draw destination tickets
        raise NotImplementedError

    def choose_draw_train_action(self) -> int:
        # Decide which train card to draw: face-up index (0-4) or -1 for face-down
        raise NotImplementedError

    def choose_route_to_claim(self) -> Optional[Route]:
        # Decide which route to claim, if any
        raise NotImplementedError

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        # Decide which destination tickets to keep
        raise NotImplementedError

    def post_turn_update(self) -> None:
        # Perform any updates needed after a turn
        raise NotImplementedError

    def allocate_for_desired_routes(self) -> None:
        # Allocate resources for desired routes
        raise NotImplementedError

    def utility(self, route: RouteInfo) -> float:
        # Compute the utility of a given route
        raise NotImplementedError

    def estimate_turns(self, route: RouteInfo) -> float:
        # Estimate how many turns are needed to claim a given route
        raise NotImplementedError
    def __init__(self, player_id: str, context):
        super().__init__(player_id, context)
        self.desired_routes: List[DesiredRoute] = []
        self._alloc: Dict[str, Counter[str]] = {}

    def choose_turn_action(self) -> int:
        # Placeholder heuristic decision-making
        # Example: prioritize route claiming if possible, else draw cards
        return 2 if self.claim_available_route() else 1

    def choose_draw_train_action(self) -> int:
        # Placeholder: draw facedown by default
        return -1

    def choose_route_to_claim(self) -> Optional[Route]:
        # Placeholder: pick first unclaimed desired route
        for desired in self.desired_routes:
            for route in self.context.get_map().routes:
                if route.city_a == desired.city_a and route.city_b == desired.city_b and not route.claimed_by:
                    return route
        return None

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        # Placeholder: keep all offered tickets
        return offer

    def post_turn_update(self) -> None:
        # Placeholder for post-turn adjustments
        pass

    def allocate_for_desired_routes(self) -> None:
        # Placeholder for resource allocation logic
        pass

    def utility(self, route: RouteInfo) -> float:
        # Placeholder utility function
        return 0.0

    def estimate_turns(self, route: RouteInfo) -> float:
        # Placeholder estimation logic
        return 0.0
