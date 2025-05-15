from typing import List, Optional

from abstract_player import AbstractPlayer
from Map import Route
from decks import DestinationTicket


class HumanPlayer(AbstractPlayer):
    def choose_turn_action(self) -> int:
        print(f"\n{self.player_id}, choose an action:")
        print("1) Draw Train Cards")
        print("2) Claim a Route")
        print("3) Draw Destination Tickets")
        while True:
            try:
                choice = int(input("Enter choice (1-3): "))
                if choice in [1, 2, 3]:
                    return choice
                print("Invalid input. Choose 1, 2, or 3.")
            except ValueError:
                print("Please enter a number.")

    def choose_draw_train_action(self) -> int:
        print("\nChoose a train card to draw:")
        print("0-4: Face-up card index")
        print("-1: Face-down deck")
        while True:
            try:
                choice = int(input("Enter index (0-4 for face-up, -1 for face-down): "))
                if choice in [-1, 0, 1, 2, 3, 4]:
                    return choice
                print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    def choose_route_to_claim(self) -> Optional[Route]:
        available_routes = [r for r in self.context.get_map().routes if not r.claimed_by]
        if not available_routes:
            print("No unclaimed routes available.")
            return None

        print("\nAvailable Routes:")
        for idx, route in enumerate(available_routes):
            print(f"{idx}: {route.city_a} - {route.city_b} ({route.length} trains, {route.colour})")

        while True:
            try:
                choice = int(input("Enter route index to claim (or -1 to skip): "))
                if choice == -1:
                    return None
                if 0 <= choice < len(available_routes):
                    return available_routes[choice]
                print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    def select_ticket_offer(self, offer: List[DestinationTicket]) -> List[DestinationTicket]:
        print("\nSelect destination tickets to keep (must keep at least 1):")
        for idx, ticket in enumerate(offer):
            print(f"{idx}: {ticket.city_a} → {ticket.city_b} ({ticket.value} pts)")

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
        print(f"\n{self.player_id}'s Current Hand: {dict(self.train_hand)}")
        print(f"Tickets: {[f'{t.city_a}->{t.city_b} ({t.value})' for t in self.tickets]}")
        print(f"Trains Remaining: {self.trains_remaining}")
