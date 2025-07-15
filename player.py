from copy import deepcopy
from typing import List, Dict, Optional
from collections import Counter
import weakref
from context.Map import Route
from context.decks import DestinationTicket
from context.player_context import PlayerContext




class Player:
    def __init__(self, player_id: str,interface, name: str, color: str):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.__train_hand: Counter[str] = Counter()
        self.exposed: Counter[str] = Counter()
        self.__tickets: List[DestinationTicket] = []
        self.trains_remaining: int = 45
        self.context: PlayerContext
        self.__interface = interface
        self.__interface.set_player(self)
        self.has_longest_path: bool = False
        self.my_longest_path_length: int


    def get_context(self):
        return self.context

    def get_interface(self):
        return self.__interface

    # sets the context for the player
    def set_context(self, context: PlayerContext):
        self.context = context
        if context.turn_number == 0:
            for i in range(0,4):
                self.__draw_train_cards()


    #prompts interface for turn option
    def take_turn(self, fault_flags: Dict[str, bool]) -> None:
        turn_choice = self.__interface.choose_turn_action()

        if turn_choice == 1: ## Draw Cards
            first_draw_card = self.__draw_train_cards()
            if first_draw_card != 'locomotive':
                self.__draw_train_cards()

        elif turn_choice == 2: ## Claim Route
            if not fault_flags['claim_route']:
                success = self.__claim_available_route()
                if success is None:
                    fault_flags["claim_route"] = True
                    print(f"{self.player_id} could not claim a route.")
                    self.take_turn(fault_flags) #chose returns to the turn menu
                else:
                    self.update_longest_path(success)
                    self.check_ticket_completion()

            else:
                self.__add_cards([self.context.train_deck.draw_face_down() for i in range(0, 2)])

        elif turn_choice == 3: ## Draw Destination tickets
            if not fault_flags['draw_destination']:
                success = self.__draw_destination_tickets()
                if not success:
                    fault_flags["draw_destination"] = True
                    print(f"{self.player_id} could not draw destination tickets.")
                    self.take_turn(fault_flags)
            else:
                self.__add_cards([self.context.train_deck.draw_face_down() for i in range(0, 2)])

        else:
            print(f"Invalid action choice '{turn_choice}' by player {self.player_id}.")

    # handlers for each option
    def __draw_train_cards(self) -> str:
        draw_choices = [self.__interface.choose_draw_train_action() for _ in range(2)]

        train_deck = self.context.train_deck # Assuming ticket_deck includes train draw functionality

        first_choice = draw_choices[0]
        if first_choice >= 0:
            try:
                card = train_deck.draw_face_up(first_choice)
                self.__add_cards([card])
                if card == 'L':
                    return card
            except IndexError:
                print(f"Invalid face-up index '{first_choice}' by player {self.player_id}.")
                return 'invalid'

        elif first_choice == -1:
            try:
                card = train_deck.draw_face_down()
                self.__add_cards([card])
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
                self.__add_cards([card])
            except IndexError:
                print(f"Invalid face-up index '{second_choice}' by player {self.player_id}.")
                return 'invalid'

        elif second_choice == -1:
            try:
                card = train_deck.draw_face_down()
                self.__add_cards([card])
            except Exception as e:
                print(f"Face-down draw failed for player {self.player_id}: {e}")
                return 'invalid'

        else:
            print(f"Invalid draw choice '{second_choice}' by player {self.player_id}.")
            return 'invalid'

        return 'success'
    
    def __claim_available_route(self) -> 'Route | None':
        route = self.__interface.choose_route_to_claim(self.get_affordable_routes())
        if route is None:
            return None
        if route.color == "X":
            color_options = [c for c in self.__train_hand.keys() if self.__train_hand.get(c) >= route.length]
            if len(color_options) >= 1:
                chosen_color = self.__interface.choose_color_to_spend(route, color_options)
                # set color_to_spend to chosen_color if chosen_color is a valid color that they have enough of; otherwise set it to the one they have the most of
                color_to_spend = chosen_color if self.__train_hand.get(chosen_color, 0) >= route.length else self.__train_hand.most_common(1)[0][0]
            else:
                color_to_spend = color_options[0]
        else:
            color_to_spend = route.color
        try:
            self.__spend_cards([color_to_spend] * route.length)
            self.__claim_route(route)
            return route
        except Exception as e:
            print(f"Error claiming route {route}: {e}")
            return None

    def __draw_destination_tickets(self) -> bool:
        try:
            offer = self.context.ticket_deck.deal_unique(3)
        except Exception as e:
            print(f"Ticket draw failed for player {self.player_id}: {e}")
            return False

        if not offer:
            print(f"No destination tickets available for {self.player_id}.")
            return False

        indices_kept = self.__interface.select_ticket_offer(offer)
        if not indices_kept or len(indices_kept) == 0:
            print(f"{self.player_id} kept no tickets from offer.")
            return False

        tickets_kept = [offer[i] for i in indices_kept]
        self.__tickets.extend(tickets_kept)
        returned = [t for t in offer if t not in tickets_kept]
        self.context.ticket_deck.return_tickets(returned)
        return True

    # Helpers
    def __add_cards(self, cards: List[str]) -> None:
        self.__train_hand.update(cards)

    def __spend_cards(self, cards: List[str]) -> None:
        self.__train_hand.subtract(cards)
        self.__train_hand += Counter()

    def __claim_route(self, route: Route) -> None:
        self.trains_remaining -= route.length
        self.context.map.claim_route(route, self.player_id)

    def __hand_counts(self) -> 'Counter[str]':
        return self.__train_hand.copy()

    def get_exposed(self) -> 'Counter[str]':
        return self.exposed
    
    def get_hand(self) -> 'Counter[str]':
        return self.__train_hand

    def get_card_count(self) -> int:
        return sum(self.__train_hand.values())
    
    def get_tickets(self) -> List[DestinationTicket]:
        return self.__tickets

    def get_affordable_routes(self) -> List[Route]:
        affordable_routes = []
        available_routes = self.context.map.get_available_routes()
        for r in available_routes:
            # if the player has enough of the color in hand or if the color is gray and the player has enough of their most common color in hand
            if self.__train_hand[r.color] >= r.length or (r.color == "X" and self.__train_hand.most_common(1)[0][1] >= r.length):
                affordable_routes.append(r)
        return affordable_routes
    
    def update_longest_path(self, new_route: Route):
        self.context.map.update_longest_path(self.player_id, new_route)
        my_longest_path = self.context.map.longest_paths[self.player_id]
        has_longest_path = (self.context.map.longest_path_holder == self.player_id)

    def check_ticket_completion(self):
        path_info = self.context.map.paths[self.player_id]
        for t in [t for t in self.__tickets if not t.is_completed]:
            city_1_group = next((group for group in path_info if t.city1 in group), None)
            if city_1_group != None and t.city2 in city_1_group:
                t.is_completed = True

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self.player_id}, trains={self.trains_remaining}, "
                f"hand={dict(self.__train_hand)}, tickets={self.__tickets})")


