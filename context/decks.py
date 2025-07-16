import random
import csv
from collections import deque
from typing import List, Union, Deque

# ────────────────────────────────────────────────────────────────────────────────
# TrainCardDeck – with 1-letter abbreviations
# ────────────────────────────────────────────────────────────────────────────────
class TrainCardDeck:
    COLOR_COUNTS = {
        "W": 12,  # White
        "B": 12,  # Black
        "U": 12,  # Blue
        "G": 12,  # Green
        "Y": 12,  # Yellow
        "O": 12,  # Orange
        "R": 12,  # Red
        "P": 12,  # Purple
        "L": 14   # Locomotive (wild)
    }

    def __init__(self):
        self._deck: List[str] = []
        self._discard_pile: List[str] = []
        self._face_up: List[str] = []

        # Build deck using abbreviations
        for abbrev, count in self.COLOR_COUNTS.items():
            self._deck.extend([abbrev] * count)

        random.shuffle(self._deck)
        self._refill_face_up_slot()

        # Mulligan rule enforcement
        while self._too_many_locomotives():
            self._mulligan_face_up()

    def get_face_up(self) -> List[str]:
        return self._face_up[:]

    def get_discard_pile(self) -> List[str]:
        return self._discard_pile[:]

    def __get_full_deck(self) -> List[str]:
        return self._deck[:]

    def draw_face_up(self, idx: int) -> str:
        card = self._face_up.pop(idx)
        self._refill_face_up_slot()
        if len(self.get_face_up()) < 5 and len(self._deck) >= 1:
            print("unable to refill")
        return card

    def draw_face_down(self) -> str:
        if not self._deck:
            self._reshuffle_discard()
        if not self._deck:
            raise ValueError("No train cards left to draw!")
        return self._deck.pop()

    def discard(self, cards: Union[str, List[str]]):
        if isinstance(cards, str):
            self._discard_pile.append(cards)
        else:
            self._discard_pile.extend(cards)

    def _refill_face_up_slot(self):
        while len(self.get_face_up()) < 5:
            if not self._deck:
                self._reshuffle_discard()
            if self._deck:
                self._face_up.append(self._deck.pop())
            if self._too_many_locomotives():
                self._mulligan_face_up()

    def _reshuffle_discard(self):
        if not self._discard_pile:
            return
        self._deck = self._discard_pile[:]
        random.shuffle(self._deck)
        self._discard_pile.clear()

    def _too_many_locomotives(self) -> bool:
        return self._face_up.count("L") >= 3

    def _mulligan_face_up(self):
        self._discard_pile.extend(self._face_up)
        self._face_up.clear()
        self._refill_face_up_slot()

# ────────────────────────────────────────────────────────────────────────────────
# DestinationTicket – as originally defined
# ────────────────────────────────────────────────────────────────────────────────
class DestinationTicket:
    def __init__(self, city1: str, city2: str, value: int):
        self.city1 = city1
        self.city2 = city2
        self.value = value
        self.is_completed = False

    def __repr__(self):
        return f"{self.city1} → {self.city2} ({self.value} pts)"

# ────────────────────────────────────────────────────────────────────────────────
# TicketDeck – loads tickets from CSV and manages draws
# ────────────────────────────────────────────────────────────────────────────────
class TicketDeck:
    def __init__(self, csv_path: str = "data/Destination_tickets.csv"):
        self._master: List[DestinationTicket] = self._load_tickets_from_csv(csv_path)
        self._stack: Deque[DestinationTicket] = deque(self._master)
        self._rng = random.Random()
        self._shuffle_stack()

    def deal_unique(self, n: int) -> List[DestinationTicket]:
        drawn = []
        while n > 0 and self._stack:
            drawn.append(self._stack.popleft())
            n -= 1
        return drawn

    def return_tickets(self, tickets: List[DestinationTicket]):
        self._stack.extend(tickets)
        self._shuffle_stack()

    def _shuffle_stack(self):
        temp_list = list(self._stack)
        self._rng.shuffle(temp_list)
        self._stack = deque(temp_list)

    @staticmethod
    def _load_tickets_from_csv(csv_path: str) -> List[DestinationTicket]:
        tickets = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city1 = row["city1"]
                city2 = row["city2"]
                value = int(row["value"])
                tickets.append(DestinationTicket(city1, city2, value))
        return tickets
