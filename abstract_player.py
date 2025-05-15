from collections import Counter
from typing import Dict, List, Optional

from game_context import GameContext
from Map import Route
from decks import DestinationTicket


class AbstractPlayer:
    def __init__(self, player_id: str, context: GameContext):
        self.player_id = player_id
        self.train_hand: Counter[str] = Counter()
        self._exposed: Dict[str, int] = {}
        self.tickets: List[DestinationTicket] = []
        self.trains_remaining: int = 45
        self.context = context

    # ────────────────────────────────────────────────────────
    # Executors: Require implementation per player type
    # ────────────────────────────────────────────────────────

    def choose_turn_action(self) -> int:
        '''Decides whether to draw trains (1), claim a route (2), or draw destination tickets (3).'''
        raise NotImplementedError

    def choose_draw_train_action(self) -> int:
        '''Decides which train card to draw: index 0-4 for face-up, -1 for face-down.'''
        raise NotImplementedError


    def choose_route_to_claim(self) -> Optional[Route]:
        raise NotImplementedError

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        '''Selects which destination tickets to keep from the given offer. Must keep at least 1.'''
        raise NotImplementedError

    def take_turn(self) -> None:
        '''Core turn loop: select and execute exactly one action (draw, claim, or destination).'''
        turn_choice = self.choose_turn_action()

        if turn_choice == 1:
            # Handle train card drawing (may involve second draw internally)
            first_draw_card = self.draw_train_cards(first_draw=True)
            if first_draw_card != 'locomotive':  # Eligible for second draw unless first draw is loco
                self.draw_train_cards(first_draw=False)

        elif turn_choice == 2:
            success = self.claim_available_route()
            if not success:
                print(f"{self.player_id} could not claim a route.")

        elif turn_choice == 3:
            success = self.draw_destination_tickets()
            if not success:
                print(f"{self.player_id} could not draw destination tickets.")

        else:
            print(f"Invalid action choice '{turn_choice}' by player {self.player_id}.")

    # ────────────────────────────────────────────────────────
    # Shared Turn Actions
    # ────────────────────────────────────────────────────────

    def draw_train_cards(self, first_draw: bool = True) -> str:
        '''Handles drawing up to 2 train cards based on player choice. Draws are indices: 0-4 for face-up, -1 for face-down.
        If a locomotive is chosen as the first draw, the second draw is skipped.'''
        draw_choices = [self.choose_draw_train_action() for _ in range(2)]

        # First draw
        first_choice = draw_choices[0]
        if first_choice >= 0:
            try:
                card = self.context.get_train_deck().draw_face_up(first_choice)
                self.add_cards([card])
                if card == 'locomotive':
                    return card  # End draw phase early
            except IndexError:
                print(f"Invalid face-up index '{first_choice}' by player {self.player_id}.")
                return 'invalid'

        elif first_choice == -1:
            try:
                card = self.context.get_train_deck().draw_face_down()
                self.add_cards([card])
            except Exception as e:
                print(f"Face-down draw failed for player {self.player_id}: {e}")
                return 'invalid'

        else:
            print(f"Invalid draw choice '{first_choice}' by player {self.player_id}.")
            return 'invalid'

        # Second draw (only if first was not locomotive)
        second_choice = draw_choices[1]
        if second_choice >= 0:
            try:
                card = self.context.get_train_deck().draw_face_up(second_choice)
                if card == 'locomotive':
                    print(f"{self.player_id} attempted to draw a locomotive on second draw. Action cancelled.")
                    return 'invalid'
                self.add_cards([card])
            except IndexError:
                print(f"Invalid face-up index '{second_choice}' by player {self.player_id}.")
                return 'invalid'

        elif second_choice == -1:
            try:
                card = self.context.get_train_deck().draw_face_down()
                self.add_cards([card])
            except Exception as e:
                print(f"Face-down draw failed for player {self.player_id}: {e}")
                return 'invalid'

        else:
            print(f"Invalid draw choice '{second_choice}' by player {self.player_id}.")
            return 'invalid'

        return 'success'

    def claim_available_route(self) -> bool:
        '''Attempts to claim a route, returns success status.'''
        route = self.choose_route_to_claim()
        if route is None:
            return False

        required = Counter({route.colour: route.length})
        if self.train_hand >= required:
            try:
                self.spend_cards([route.colour] * route.length)
                self.claim_route(route)
                return True
            except Exception as e:
                print(f"Error claiming route {route}: {e}")
                return False

        print(f"{self.player_id} lacks cards to claim {route}.")
        return False





    def draw_destination_tickets(self) -> bool:
        '''Handles drawing destination tickets and selecting which to keep. Returns success status.'''
        try:
            offer = self.context.get_ticket_deck().deal_unique(3)
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
        self.context.get_ticket_deck().return_tickets(returned)
        return True

    # ────────────────────────────────────────────────────────
    # Helpers: Shared logic and utilities
    # ────────────────────────────────────────────────────────

    def add_cards(self, cards: List[str]) -> None:
        self.train_hand.update(cards)

    def spend_cards(self, cards: List[str]) -> None:
        self.train_hand.subtract(cards)
        self.train_hand += Counter()  # Clean up zero-counts

    def claim_route(self, route: Route) -> None:
        self.trains_remaining -= route.length
        self.context.get_map().claim_route(route, self.player_id)

    def hand_counts(self) -> Counter[str]:
        return self.train_hand.copy()

    def get_exposed(self) -> Dict[str, int]:
        return dict(self._exposed)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self.player_id}, trains={self.trains_remaining}, "
                f"hand={dict(self.train_hand)}, tickets={self.tickets})")
