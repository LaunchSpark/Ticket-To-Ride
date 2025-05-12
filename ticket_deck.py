from __future__ import annotations

"""Destination‑Ticket deck with uniqueness guarantees.

Always relies on *data/Destination_tickets.csv* (no fallback). The loader
skips a header row if present.
"""

from collections import deque
from pathlib import Path
from typing import Deque, List, Sequence
import random

from Player import DestinationTicket

__all__ = ["TicketDeck", "load_default_tickets"]

# ---------------------------------------------------------------------------
# CSV loader (header‑aware, no fallback)
# ---------------------------------------------------------------------------

def load_default_tickets(path: Path | str = "data/Destination_tickets.csv") -> List[DestinationTicket]:
    """Load destination tickets from CSV.

    File must exist. Accepts an optional *single* header row whose first cell
    contains the word "destination" or "city"; that row will be ignored.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Destination ticket file not found: {p}")

    tickets: List[DestinationTicket] = []
    with p.open(encoding="utf-8-sig") as fh:
        for lineno, line in enumerate(fh, 1):
            parts = [s.strip() for s in line.split(",")]
            if lineno == 1 and parts[0].lower().startswith(("destination", "city")):
                # Header row detected – skip
                continue
            if len(parts) < 3:
                raise ValueError(f"Line {lineno}: expecting 3 columns, got {parts}")
            a, b, v = parts[:3]
            try:
                tickets.append(DestinationTicket(a, b, int(v)))
            except ValueError as e:
                raise ValueError(f"Line {lineno}: reward is not an int → {v!r}") from e
    if not tickets:
        raise ValueError("Destination ticket file contains no valid tickets")
    return tickets

# ---------------------------------------------------------------------------
# TicketDeck class
# ---------------------------------------------------------------------------

def _key(t: DestinationTicket) -> tuple[str, str, int]:
    return (t.city_a, t.city_b, t.value)


class TicketDeck:
    """Manages destination tickets ensuring global uniqueness."""

    def __init__(self, tickets: Sequence[DestinationTicket], *, rng: random.Random):
        if len(tickets) < 3:
            raise ValueError("Ticket list must contain at least 3 unique tickets")
        self._rng = rng
        self._master: list[DestinationTicket] = list(tickets)
        self._stack: Deque[DestinationTicket] = deque(self._master)
        self._rng.shuffle(self._stack)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def deal_unique(self, owned: set[tuple[str, str, int]], count: int = 3) -> List[DestinationTicket]:
        """Return *count* tickets not in *owned*; reshuffle if stack empties."""
        offered: list[DestinationTicket] = []
        while len(offered) < count:
            if not self._stack:
                remaining = [t for t in self._master if _key(t) not in owned and t not in offered]
                if not remaining:
                    raise RuntimeError("No unique destination tickets left to deal")
                self._rng.shuffle(remaining)
                self._stack.extend(remaining)
            t = self._stack.popleft()
            if _key(t) in owned:
                self._stack.append(t)
                continue
            offered.append(t)
            owned.add(_key(t))
        return offered

    def return_tickets(self, tickets: Sequence[DestinationTicket]):
        """Place unclaimed tickets at bottom of stack."""
        self._stack.extend(tickets)

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def __len__(self):
        return len(self._stack)

    def __repr__(self):
        return f"<TicketDeck remaining={len(self)}>"
