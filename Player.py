from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from Map import MapGraph, Route  # type hints only

__all__ = ["DestinationTicket", "DesiredRoute", "Player"]

LOCO = "L"  # locomotive one‑letter code shared project‑wide

# ---------------------------------------------------------------------------
# Simple data holders
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DestinationTicket:
    city_a: str
    city_b: str
    value: int  # positive score if completed


@dataclass
class DesiredRoute:
    city_a: str
    city_b: str
    expected_utility: float
    committed_colour: str | None = None  # used only for grey routes

    def key(self) -> Tuple[str, str]:
        return tuple(sorted((self.city_a, self.city_b)))


# ---------------------------------------------------------------------------
# Player class with CARD‑ALLOCATION system
# ---------------------------------------------------------------------------


class Player:
    """Stateful representation of a Ticket‑to‑Ride participant.

    New features:
    • **`_alloc`** maps *route‑key* → Counter of **reserved cards**. Reserved
      cards are still in `train_hand` but cannot be double‑spent.
    • **`allocate_for_desired_routes()`** runs each turn to reserve cards for
      high‑priority routes (colour routes first, then greys using a heuristic
      that minimises locomotive usage).
    • `spend_cards()` and `claim_route()` consume reserved cards first and keep
      allocation tables in sync.
    """

    def __init__(self, player_id: str):
        self.player_id: str = str(player_id)
        self.train_hand: Counter[str] = Counter()
        self._exposed: Counter[str] = Counter()
        self.tickets: List[DestinationTicket] = []
        self.desired_routes: Dict[Tuple[str, str], DesiredRoute] = {}

        self.trains_remaining: int = 45
        self._alloc: Dict[Tuple[str, str], Counter[str]] = {}

    # ------------------------------------------------------------------
    # Card management & visibility
    # ------------------------------------------------------------------

    def add_cards(self, cards: Sequence[str], *, from_market: bool = False):
        self.train_hand.update(cards)
        if from_market:
            self._exposed.update(cards)

    def _available_for_allocation(self) -> Counter[str]:
        """Hand minus *currently* allocated cards (but before spending)."""
        free = self.train_hand.copy()
        for cnt in self._alloc.values():
            free.subtract(cnt)
        free += Counter()  # drop zeros
        return free

    def spend_cards(self, cards: Sequence[str]):
        """Spend cards – preferentially takes from allocations when possible."""
        need = Counter(cards)
        # First, deduct from any allocations that include these cards
        for key, reserved in list(self._alloc.items()):
            overlap = need & reserved
            if overlap:
                reserved.subtract(overlap)
                reserved += Counter()
                need.subtract(overlap)
                if not reserved:
                    self._alloc.pop(key)
        # Now deduct remaining from hand
        missing = need - self.train_hand
        if missing:
            raise ValueError(f"Player lacks required cards: {missing}")
        self.train_hand.subtract(need)
        self.train_hand += Counter()
        # Keep exposed counts accurate
        overlap_exp = need & self._exposed
        self._exposed.subtract(overlap_exp)
        self._exposed += Counter()

    def get_exposed(self) -> Dict[str, int]:
        return dict(self._exposed)

    def hand_counts(self) -> Dict[str, int]:
        return dict(self.train_hand)

    def unallocated_hand(self) -> Counter[str]:
        return self._available_for_allocation()

    # ------------------------------------------------------------------
    # Ticket helpers
    # ------------------------------------------------------------------

    def add_ticket(self, ticket: DestinationTicket):
        self.tickets.append(ticket)

    # ------------------------------------------------------------------
    # Desired route helpers
    # ------------------------------------------------------------------

    def set_desired_route(self, city_a: str, city_b: str, utility: float):
        self.desired_routes[(city_a, city_b) if city_a <= city_b else (city_b, city_a)] = DesiredRoute(
            city_a, city_b, utility
        )

    def remove_desired_route(self, city_a: str, city_b: str):
        self.desired_routes.pop(tuple(sorted((city_a, city_b))), None)

    def available_desired_routes(self, board: MapGraph):
        avail: List[DesiredRoute] = []
        for d in self.desired_routes.values():
            for r in board.routes_between(d.city_a, d.city_b):
                if not r.is_claimed():
                    avail.append(d)
                    break
        return avail

    # ------------------------------------------------------------------
    # Allocation engine
    # ------------------------------------------------------------------

    def allocate_for_desired_routes(
        self,
        board: MapGraph,
        colour_probs: Dict[str, float] | None = None,
    ) -> None:
        """Reserve cards for desired routes (greedy priority order).

        *colour_probs* is optional; if provided, used to evaluate grey routes
        when multiple colours have equal locomotive deficits. The dict should
        map colour → probability of drawing that colour before claim time.
        """
        self._alloc.clear()
        free = self._available_for_allocation()
        locos = free[LOCO]

        # Process desired routes sorted by utility
        for d in sorted(self.desired_routes.values(), key=lambda x: x.expected_utility, reverse=True):
            # Skip if already claimed on board
            if any(not r.is_claimed() for r in board.routes_between(d.city_a, d.city_b)) is False:
                continue
            # Choose representative route length/colour from board (take first unclaimed)
            route: Route | None = next((r for r in board.routes_between(d.city_a, d.city_b) if not r.is_claimed()), None)
            if route is None:
                continue
            dist = route.distance

            if route.colour != "X":
                # coloured route
                colour_needed = max(0, dist - locos)
                if free[route.colour] >= colour_needed:
                    payment = Counter({route.colour: colour_needed})
                    payment[LOCO] += dist - colour_needed
                else:
                    continue  # cannot allocate now
            else:
                # grey route – pick colour that minimises loco use
                best_c = None
                best_def = dist + 1
                for c, cnt in free.items():
                    if c == LOCO:
                        continue
                    if cnt + locos < dist:
                        continue
                    deficit = max(0, dist - cnt)
                    if deficit < best_def or (
                        deficit == best_def and (colour_probs or {}).get(c, 0) > (colour_probs or {}).get(best_c, 0)
                    ):
                        best_def = deficit
                        best_c = c
                if best_c is None:
                    continue  # cannot allocate yet
                payment = Counter({best_c: dist - best_def})
                payment[LOCO] += best_def
                d.committed_colour = best_c
            # Reserve cards
            if all(free[k] >= v for k, v in payment.items()):
                self._alloc[d.key()] = payment
                free.subtract(payment)
                free += Counter()
                locos = free[LOCO]

    def allocations(self) -> Dict[Tuple[str, str], Counter[str]]:
        return {k: v.copy() for k, v in self._alloc.items()}

    # ------------------------------------------------------------------
    # Payment & claiming with allocations
    # ------------------------------------------------------------------

    def _select_payment_cards(self, route: Route) -> List[str]:
        """Prepare payment list (prefers allocated cards when available)."""
        key = tuple(sorted((route.city_a, route.city_b)))
        if key in self._alloc:
            # Use reserved cards exactly
            return list(self._alloc[key].elements())
        # Otherwise fall back to the on‑the‑fly algorithm (grey route logic inside)
        return self._select_payment_cards_on_fly(route)

    def _select_payment_cards_on_fly(self, route: Route) -> List[str]:
        dist = route.distance
        colour = route.colour
        hand = self.train_hand
        locos = hand[LOCO]

        if colour != "X":
            colour_needed = max(0, dist - locos)
            if hand[colour] < colour_needed:
                raise ValueError("Insufficient cards to claim route")
            return [colour] * colour_needed + [LOCO] * (dist - colour_needed)

        # Grey – minimise loco usage
        best_colour, best_deficit = None, dist + 1
        for c, cnt in hand.items():
            if c == LOCO:
                continue
            if cnt + locos < dist:
                continue
            deficit = max(0, dist - cnt)
            if deficit < best_deficit or (deficit == best_deficit and cnt > hand.get(best_colour, 0)):
                best_colour = c
                best_deficit = deficit
        if best_colour is None:
            raise ValueError("Cannot pay for grey route with current hand")
        colour_needed = dist - best_deficit
        return [best_colour] * colour_needed + [LOCO] * best_deficit

    def claim_route(self, board: MapGraph, route: Route):
        if route.is_claimed():
            raise RuntimeError("Route already claimed")
        if self.trains_remaining < route.distance:
            raise RuntimeError("Not enough train pieces remaining")

        payment = self._select_payment_cards(route)
        self.spend_cards(payment)
        self.trains_remaining -= route.distance
        route.claim(self.player_id)
        # Remove reservation if it existed
        self._alloc.pop(tuple(sorted((route.city_a, route.city_b))), None)
        return route

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Player {self.player_id} trains={self.trains_remaining} "
            f"cards={sum(self.train_hand.values())} alloc={sum(sum(v.values()) for v in self._alloc.values())} "
            f"tickets={len(self.tickets)} desired={len(self.desired_routes)}>"
        )
