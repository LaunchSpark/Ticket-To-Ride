from typing import List, Optional

from abstract_player import AbstractPlayer
from ..context.Map import Route
from ..context.decks import DestinationTicket


class HumanPlayer(AbstractPlayer):
    def choose_turn_action(self) -> int:
        self._display_player_state()
        self._display_market()
        self._display_available_routes()
        options = {
            1: "Draw Train Cards",
            2: "Claim a Route",
            3: "Draw Destination Tickets"
        }
        return self._display_menu("Choose an action", options)

    def choose_draw_train_action(self) -> int:
        self._display_player_state()
        self._display_market()
        options = {
            -1: "Face-down deck",
            0: "Face-up card 0",
            1: "Face-up card 1",
            2: "Face-up card 2",
            3: "Face-up card 3",
            4: "Face-up card 4"
        }
        return self._display_menu("Choose a train card to draw", options)

    def choose_route_to_claim(self) -> Optional[Route]:
        self._display_player_state()
        self._display_available_routes()
        available_routes = [r for r in self.context.get_map().routes if not r.claimed_by]
        if not available_routes:
            print("No unclaimed routes available.")
            return None

        options = {idx: f"{route.city1} - {route.city2} ({route.length} trains, {route.colour})" for idx, route in enumerate(available_routes)}
        options[-1] = "Skip claiming a route"

        choice = self._display_menu("Choose a route to claim", options)
        return None if choice == -1 else available_routes[choice]

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        self._display_player_state()
        print("\nSelect destination tickets to keep (must keep at least 1):")
        for idx, ticket in enumerate(offer):
            print(f"{idx}: {ticket.city1} → {ticket.city2} ({ticket.value} pts)")

        while True:
            try:
                choices = input("Enter indices to keep (comma-separated): ")
                indices = [int(x.strip()) for x in choices.split(',')]
                if len(indices) >= 1 and all(0 <= i < len(offer) for i in indices):
                    return [offer[i] for i in indices]
                print("Invalid selection. Must keep at least 1 valid ticket.")
            except ValueError:
                print("Please enter valid indices.")

    def interactive_menu(self) -> None:
        self._display_player_state()
        self._display_market()
        self._display_available_routes()

    def _display_menu(self, title: str, options: dict) -> int:
        print(f"\n{self.player_id}, {title}:")
        for key, description in sorted(options.items()):
            print(f"{key}) {description}")

        while True:
            try:
                choice = int(input("Enter choice: "))
                if choice in options:
                    return choice
                print(f"Invalid choice. Please choose from {list(options.keys())}.")
            except ValueError:
                print("Please enter a valid number.")

    def _display_player_state(self) -> None:
        print(f"\n--- {self.player_id}'s Current State ---")
        print(f"Hand: {dict(self.train_hand)}")
        print(f"Tickets: {[f'{t.city1}->{t.city2} ({t.value})' for t in self.tickets]}")
        print(f"Trains Remaining: {self.trains_remaining}")
        print("----------------------------------")

    def _display_market(self) -> None:
        face_up = self.train_deck.face_up()
        print("\n--- Current Face-Up Market ---")
        for idx, card in enumerate(face_up):
            print(f"{idx}: {card}")
        print("----------------------------------")

    def _display_available_routes(self) -> None:
        available_routes = [r for r in self.map.routes if not r.claimed_by]
        print("\n--- Available Routes ---")
        if not available_routes:
            print("No unclaimed routes available.")
        else:
            for idx, route in enumerate(available_routes):
                print(f"{idx}: {route.city1} - {route.city2} ({route.length} trains, {route.colour})")
        print("----------------------------------")
