import random
from collections import Counter
from typing import List, Optional, Sequence, Union, Dict


class TrainCardDeck:
    """Ticket to Ride train‑car deck managed as a single list.

    The first five entries (indices **0–4**) are the public face‑up market.
    Indices **5 +** form the hidden draw pile.  Spent cards are placed in
    :pyattr:`discard_pile` and are automatically reshuffled back into the
    draw pile when needed.

    Methods
    -------
    face_up() -> List[str]
        Current five face‑up cards (defensive copy).
    draw_face_up(idx) -> str
        Remove *idx*‑th face‑up card, instantly refill the row, and enforce
        the “three locomotives” redraw rule.
    draw_face_down() -> str
        Draw the top hidden card (index5).  Reshuffles if the hidden pile
        is empty.
    hidden_counts() -> Dict[str, int]
        Frequency of each card type currently in the hidden draw pile.
    discard(cards)
        Add one or several cards to the discard pile.
    remaining() -> int
        Count of cards in the hidden draw pile (excludes the face‑up row).

    Notes
    -----
    • Base‑game composition: 12 cards each of 8 colors + 14 locomotives.
    • All randomization is handled by an internal :pyclass:`random.Random`
      instance so you can pass a *seed* for reproducible tests.
    """

    COLORS = [
        "red", "orange", "yellow", "green",
        "blue", "purple", "black", "white",
    ]
    NUM_PER_COLOR = 12
    NUM_LOCOMOTIVE = 14
    LOCOMOTIVE = "locomotive"

    # ──────────────────────────────────────────────────────────────────────
    # Construction
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)

        # Build and shuffle the deck once at start‑up.
        self.cards: List[str] = (
            [c for color in self.COLORS for c in [color] * self.NUM_PER_COLOR]
            + [self.LOCOMOTIVE] * self.NUM_LOCOMOTIVE
        )
        self._rng.shuffle(self.cards)

        # Discard pile starts empty and is reshuffled back as needed.
        self.discard_pile: List[str] = []

    # ──────────────────────────────────────────────────────────────────────
    # Public helpers
    # ──────────────────────────────────────────────────────────────────────

    def face_up(self) -> List[str]:
        """Return a *copy* of the current 5‑card market."""
        return list(self.cards[:5])

    def draw_face_up(self, idx: int) -> str:
        """Draw the *idx*‑th face‑up card (0–4) and auto‑replenish the row."""
        if idx < 0 or idx >= min(5, len(self.cards)):
            raise IndexError("Face‑up index out of range")

        card = self.cards.pop(idx)
        self._replenish_face_up()
        self._apply_three_locomotive_rule()
        return card

    def draw_face_down(self) -> str:
        """Draw the top hidden card (element 5).

        Reshuffles the discard pile into the deck if the hidden pile is
        exhausted.  Raises :class:`RuntimeError` if no cards remain at all.
        """
        if len(self.cards) <= 5:
            self._reshuffle()
            if len(self.cards) <= 5:
                raise RuntimeError("No cards left to draw")

        card = self.cards.pop(5)
        self._apply_three_locomotive_rule()
        return card

    def hidden_counts(self) -> Dict[str, int]:
        """Return a dictionary counting each card type in the hidden pile.

        Notes
        -----
        • The face‑up market **is not** included.
        • The discard pile is **not** included until it gets reshuffled back
          into the draw pile.
        """
        return Counter(self.cards[5:])

    def discard(self, cards: Union[str, Sequence[str]]):
        """Add one or more cards to the discard pile."""
        if isinstance(cards, str):
            self.discard_pile.append(cards)
        else:
            self.discard_pile.extend(cards)

    def remaining(self) -> int:
        """Number of cards left in the hidden draw pile (excl. face‑up)."""
        return max(0, len(self.cards) - 5)

    # ──────────────────────────────────────────────────────────────────────
    # Internal utilities
    # ──────────────────────────────────────────────────────────────────────

    def _replenish_face_up(self):
        """Ensure the face‑up row shows five cards whenever possible."""
        while len(self.cards) < 5 and self.discard_pile:
            self._reshuffle()
        # After a pop(), the element previously at index 5 slides into 4, so
        # the row is automatically refilled when enough cards exist.

    def _apply_three_locomotive_rule(self):
        """If 3+ locomotives show, scrap row & reveal five new cards."""
        while self._count_locomotives() >= 3 and len(self.cards) >= 5:
            # Discard the current face‑up cards.
            self.discard(self.cards[:5])
            del self.cards[:5]
            # Bring in fresh cards; reshuffle if we run out.
            if len(self.cards) < 5:
                self._reshuffle()

    def _count_locomotives(self) -> int:
        """Count locomotives currently showing in the market."""
        return sum(1 for c in self.cards[:5] if c == self.LOCOMOTIVE)

    def _reshuffle(self):
        """Shuffle the discard pile and append it to the bottom of the deck."""
        if not self.discard_pile:
            return
        self._rng.shuffle(self.discard_pile)
        self.cards.extend(self.discard_pile)
        self.discard_pile.clear()

    # ──────────────────────────────────────────────────────────────────────
    # Dunder helpers
    # ──────────────────────────────────────────────────────────────────────

    def __len__(self):
        """Total cards (deck + discard)."""
        return len(self.cards) + len(self.discard_pile)

    def __repr__(self):
        return (
            f"<TrainCardDeck face_up={self.face_up()} "
            f"draw_pile={self.remaining()} discard={len(self.discard_pile)}>"
        )

