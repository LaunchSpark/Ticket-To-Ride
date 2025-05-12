from __future__ import annotations

"""AI Strategy framework for Ticket‑to‑Ride with a lightweight smoke test.

This module defines an abstract `Strategy` base class plus immutable snapshot
containers.  The test block at the bottom (`python strategy.py`) ensures that
basic instantiation and method calls work without the full game engine.
"""

from collections import Counter
from dataclasses import dataclass
from enum import Enum, auto
from functools import lru_cache
from statistics import mean, pstdev
from typing import Callable, Dict, List, Optional, Sequence
import random

# ---------------------------------------------------------------------------
# Immutable snapshot dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UnknownPoolSnapshot:
    counts: Counter[str]
    total: int


@dataclass(frozen=True)
class PlayerSnapshot:
    player_id: str
    hand: Counter[str]
    exposed: Dict[str, int]
    tickets: Sequence


@dataclass(frozen=True)
class RouteInfo:
    city_a: str
    city_b: str
    distance: int
    colour: str
    reward: float
    claimed_by: Optional[str]

    def endpoints(self) -> tuple[str, str]:
        return tuple(sorted((self.city_a, self.city_b)))


@dataclass(frozen=True)
class GameSnapshot:
    board: 'MapGraph'
    deck_face_up: List[str]
    deck_discard: Counter[str]
    unknown_pool: UnknownPoolSnapshot
    players: Dict[str, PlayerSnapshot]
    turn_index: int


# ---------------------------------------------------------------------------
# Supporting enums / config stubs
# ---------------------------------------------------------------------------


class DrawActionType(Enum):
    BLIND = auto()
    MARKET = auto()
    LOCO_MARKET = auto()


@dataclass(frozen=True)
class DrawAction:
    type: DrawActionType
    market_index: Optional[int] = None


@dataclass(frozen=True)
class Ruleset:
    colours: Sequence[str]
    loco_code: str
    num_per_colour: int
    num_locomotive: int
    market_size: int = 5


# ---------------------------------------------------------------------------
# Strategy base class
# ---------------------------------------------------------------------------


class Strategy:
    """Encapsulates draw/claim policy plus utility estimation."""

    def __init__(
        self,
        ruleset: Ruleset,
        cost_fn: Callable[[float, float, float], float],
        rng: Optional[random.Random] = None,
        *,
        params: Optional[dict] = None,
    ) -> None:
        self.rules = ruleset
        self.cost_fn = cost_fn
        self.rng = rng or random.Random()
        self.params = params or {}
        self.opponent_model = None  # placeholder for future use

    # ------------------------------------------------------------------
    # Public decision hooks (override in subclasses)
    # ------------------------------------------------------------------

    def choose_draw_action(self, snapshot: GameSnapshot) -> DrawAction:
        """Naive default draw policy."""
        return DrawAction(DrawActionType.BLIND)

    def choose_route_to_claim(self, snapshot: GameSnapshot) -> Optional[RouteInfo]:
        """Naive default: claim nothing."""
        return None

    def post_turn_update(self, real_events):
        pass

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def _target_card_set(self, route: RouteInfo, hand: Counter[str]) -> Counter[str]:
        need = Counter({route.colour: route.distance}) if route.colour != "X" else Counter()
        return need - hand

    @lru_cache(maxsize=1024)
    def estimate_turns(
        self,
        target_hash: str,
        pool_hash: str,
        *,
        trials: int = 2000,
    ) -> tuple[float, float]:
        target = Counter(eval(target_hash))
        pool = Counter(eval(pool_hash))
        if not target:
            return 0.0, 0.0
        tot_unknown = sum(pool.values())
        samples: List[int] = []
        for _ in range(trials):
            hand = Counter()
            unknown = pool.copy()
            turns = 0
            while target - hand:
                turns += 1
                for _ in range(2):
                    if not unknown:
                        break
                    colour = self.rng.choices(list(unknown.keys()), weights=unknown.values())[0]
                    hand[colour] += 1
                    unknown[colour] -= 1
                    if unknown[colour] == 0:
                        del unknown[colour]
            samples.append(turns)
        return mean(samples), pstdev(samples)

    def utility(
        self,
        route: RouteInfo,
        snapshot: GameSnapshot,
        you: PlayerSnapshot,
    ) -> float:
        need = self._target_card_set(route, you.hand)
        target_hash = str(need)
        pool_hash = str(snapshot.unknown_pool.counts)
        mu, sigma = self.estimate_turns(target_hash, pool_hash)
        return self.cost_fn(route.reward, mu, sigma)


# ---------------------------------------------------------------------------
# Convenience linear cost function
# ---------------------------------------------------------------------------

def linear_cost(reward: float, mu_turns: float, sd_turns: float, *, c: float = 1.0) -> float:
    return reward - c * mu_turns


# ---------------------------------------------------------------------------
# Smoke‑test (run: `python strategy.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Minimal stubs so the Strategy can run without the full engine.
    class DummyBoard:
        def __init__(self):
            self.routes: List[RouteInfo] = [
                RouteInfo("A", "B", 3, "R", reward=4, claimed_by=None),
                RouteInfo("B", "C", 2, "L", reward=7, claimed_by=None),
            ]

    # Build snapshots.
    rules = Ruleset(colours=list("ROYGBPKW"), loco_code="L", num_per_colour=12, num_locomotive=14)
    unknown_pool = UnknownPoolSnapshot(Counter({"R": 10, "L": 14}), total=24)
    you_ps = PlayerSnapshot("you", Counter(), {}, [])
    opp_ps = PlayerSnapshot("opp", Counter(), {"R": 1}, [])
    snap = GameSnapshot(
        board=DummyBoard(),
        deck_face_up=["R", "O", "Y", "G", "L"],
        deck_discard=Counter(),
        unknown_pool=unknown_pool,
        players={"you": you_ps, "opp": opp_ps},
        turn_index=0,
    )

    # Instantiate strategy and exercise methods.
    strat = Strategy(rules, linear_cost, params={"you_id": "you"})

    draw_act = strat.choose_draw_action(snap)
    route_choice = strat.choose_route_to_claim(snap)

    print("Smoke‑test results:")
    print("  Draw action:", draw_act)
    print("  Route choice:", route_choice)
    print("  Utility of first route:", strat.utility(snap.board.routes[0], snap, you_ps))

    print("\nSmoke test completed ✓")
