from typing import List, Dict, Optional
from collections import Counter

from player_view_context import PlayerViewContext
from Map import Route
from decks import DestinationTicket



class AbstractPlayer:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.train_hand: Counter[str] = Counter()
        self._exposed: Dict[str, int] = {}
        self.tickets: List[DestinationTicket] = []
        self.trains_remaining: int = 45

    # Executors: Require implementation per player type

    def choose_turn_action(self) -> int:
        raise NotImplementedError

    def choose_draw_train_action(self) -> int:
        raise NotImplementedError

    def choose_route_to_claim(self, view_context: PlayerViewContext) -> Optional[Route]:
        raise NotImplementedError

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        raise NotImplementedError

    def take_turn(self, view_context: PlayerViewContext) -> None:
        turn_choice = self.choose_turn_action()

        if turn_choice == 1:
            first_draw_card = self.draw_train_cards(view_context)
            if first_draw_card != 'locomotive':
                self.draw_train_cards(view_context)

        elif turn_choice == 2:
            success = self.claim_available_route(view_context)
            if not success:
                print(f"{self.player_id} could not claim a route.")

        elif turn_choice == 3:
            success = self.draw_destination_tickets(view_context)
            if not success:
                print(f"{self.player_id} could not draw destination tickets.")

        else:
            print(f"Invalid action choice '{turn_choice}' by player {self.player_id}.")

    # Shared Turn Actions

    def draw_train_cards(self, view_context: PlayerViewContext) -> str:
        draw_choices = [self.choose_draw_train_action() for _ in range(2)]

        train_deck = view_context.ticket_deck  # Assuming ticket_deck includes train draw functionality

        first_choice = draw_choices[0]
        if first_choice >= 0:
            try:
                card = train_deck.draw_face_up(first_choice)
                self.add_cards([card])
                if card == 'locomotive':
                    return card
            except IndexError:
                print(f"Invalid face-up index '{first_choice}' by player {self.player_id}.")
                return 'invalid'

        elif first_choice == -1:
            try:
                card = train_deck.draw_face_down()
                self.add_cards([card])
            except Exception as e:
                print(f"Face-down draw failed for player {self.player_id}: {e}")
                return 'invalid'

        else:
            print(f"Invalid draw choice '{first_choice}' by player {self.player_id}.")
            return 'invalid'

        second_choice = draw_choices[1]
        if second_choice >= 0:
            try:
                card = train_deck.draw_face_up(second_choice)
                if card == 'locomotive':
                    print(f"{self.player_id} attempted to draw a locomotive on second draw. Action cancelled.")
                    return 'invalid'
                self.add_cards([card])
            except IndexError:
                print(f"Invalid face-up index '{second_choice}' by player {self.player_id}.")
                return 'invalid'

        elif second_choice == -1:
            try:
                card = train_deck.draw_face_down()
                self.add_cards([card])
            except Exception as e:
                print(f"Face-down draw failed for player {self.player_id}: {e}")
                return 'invalid'

        else:
            print(f"Invalid draw choice '{second_choice}' by player {self.player_id}.")
            return 'invalid'

        return 'success'

    def claim_available_route(self, view_context: PlayerViewContext) -> bool:
        route = self.choose_route_to_claim(view_context)
        if route is None:
            return False

        required = Counter({route.colour: route.length})
        if self.train_hand >= required:
            try:
                self.spend_cards([route.colour] * route.length)
                self.claim_route(route, view_context)
                return True
            except Exception as e:
                print(f"Error claiming route {route}: {e}")
                return False

        print(f"{self.player_id} lacks cards to claim {route}.")
        return False

    def draw_destination_tickets(self, view_context: PlayerViewContext) -> bool:
        try:
            offer = view_context.ticket_deck.deal_unique(3)
        except Exception as e:
            print(f"Ticket draw failed for player {self.player_id}: {e}")
            return False

        if not offer:
            print(f"No destination tickets available for {self.player_id}.")
            return False

        kept = self.select_ticket_offer(offer)
        if not kept or len(kept) == 0:
            print(f"{self.player_id} kept no tickets from offer.")
            return False

        self.tickets.extend(kept)
        returned = [t for t in offer if t not in kept]
        view_context.ticket_deck.return_tickets(returned)
        return True

    # Helpers

    def add_cards(self, cards: List[str]) -> None:
        self.train_hand.update(cards)

    def spend_cards(self, cards: List[str]) -> None:
        self.train_hand.subtract(cards)
        self.train_hand += Counter()

    def claim_route(self, route: Route, view_context: PlayerViewContext) -> None:
        self.trains_remaining -= route.length
        view_context.map_view.claim_route(route, self.player_id)

    def hand_counts(self) -> Counter[str]:
        return self.train_hand.copy()

    def get_exposed(self) -> Dict[str, int]:
        return dict(self._exposed)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self.player_id}, trains={self.trains_remaining}, "
                f"hand={dict(self.train_hand)}, tickets={self.tickets})")