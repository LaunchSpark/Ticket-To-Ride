import random
from collections import deque
from typing import List, Union, Deque

class TrainCardDeck:
    def __init__(self, deck: List[str]):
        self._deck: List[str] = deck[:]
        self._discard_pile: List[str] = []
        self._face_up: List[str] = []
        random.shuffle(self._deck)
        self.refill_face_up()

    def face_up(self) -> List[str]:
        return self._face_up[:]

    def draw_face_up(self, idx: int) -> str:
        card = self._face_up.pop(idx)
        self._refill_face_up_slot()
        return card

    def draw_face_down(self) -> str:
        if not self._deck:
            self._reshuffle_discard()
        return self._deck.pop()

    def discard(self, cards: Union[str, List[str]]):
        if isinstance(cards, str):
            self._discard_pile.append(cards)
        else:
            self._discard_pile.extend(cards)

    def _refill_face_up_slot(self):
        if self._deck:
            self._face_up.append(self._deck.pop())

    def refill_face_up(self):
        while len(self._face_up) < 5 and self._deck:
            self._face_up.append(self._deck.pop())

    def _reshuffle_discard(self):
        self._deck = self._discard_pile[:]
        random.shuffle(self._deck)
        self._discard_pile.clear()

class DestinationTicket:
    def __init__(self, city_a: str, city_b: str, value: int):
        self.city_a = city_a
        self.city_b = city_b
        self.value = value

class TicketDeck:
    def __init__(self, master_tickets: List[DestinationTicket]):
        self._master: List[DestinationTicket] = master_tickets[:]
        self._stack: Deque[DestinationTicket] = deque(master_tickets)
        self._rng = random.Random()

    def deal_unique(self, n: int) -> List[DestinationTicket]:
        drawn = []
        while n > 0 and self._stack:
            drawn.append(self._stack.popleft())
            n -= 1
        return drawn

    def return_tickets(self, tickets: List[DestinationTicket]):
        self._stack.extend(tickets)
        self._rng.shuffle(self._stack)
