from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

__all__ = [
    "Route",
    "MapGraph",
]


@dataclass
class Route:
    """One undirected edge between *city_a* and *city_b* on the map.

    A *parallel* connection (identical endpoints) in the CSV becomes a
    separate :class:`Route` instance so it can be claimed independently.
    """

    city_a: str
    city_b: str
    distance: int
    colour: str  # as written in CSV (e.g., "X", "Y", colour name, etc.)
    claimed_by: Optional[str] = field(default=None, repr=False)

    # ──────────────────────────────────────────────────────────────────────
    # Public helpers
    # ──────────────────────────────────────────────────────────────────────

    def other(self, city: str) -> str:
        """Return the opposite endpoint given *city* or raise ``ValueError``."""
        if city == self.city_a:
            return self.city_b
        if city == self.city_b:
            return self.city_a
        raise ValueError(f"{city!r} is not an endpoint of this route")

    # ------------------------------------------------------------------
    # Claim management – keeps state inside the Route instance so MapGraph
    # can remain a thin wrapper.
    # ------------------------------------------------------------------

    def is_claimed(self) -> bool:  # noqa: D401 (keep short name)
        """True if some player_id already owns this track."""
        return self.claimed_by is not None

    def claim(self, player_id: str):
        """Mark the route as taken by *player_id*.

        Raises
        ------
        RuntimeError
            If the route is already claimed by someone (cannot be stolen).
        """
        if self.claimed_by is not None:
            raise RuntimeError(
                f"Route {self.city_a}–{self.city_b} already claimed by {self.claimed_by}"
            )
        self.claimed_by = player_id

    def unclaim(self):
        """Free the route (used by undo‑/simulation engines)."""
        self.claimed_by = None

    # ------------------------------------------------------------------
    # Dunder / debugging helpers
    # ------------------------------------------------------------------

    def __repr__(self):
        owner = self.claimed_by or "❌"
        return (
            f"Route({self.city_a!r}, {self.city_b!r}, {self.distance}, "
            f"{self.colour!r}, owner={owner})"
        )


class MapGraph:
    """Undirected multigraph plus simple ownership tracking for routes."""

    DEFAULT_PATH = Path("data") / "map.csv"

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, csv_path: Path | str | None = None):
        self.csv_path = Path(csv_path) if csv_path else self.DEFAULT_PATH
        self.routes: List[Route] = []  # includes parallels
        self._adj: Dict[str, List[Route]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Claim / ownership API
    # ------------------------------------------------------------------

    def claim_route(
        self,
        player_id: str,
        city_a: str,
        city_b: str,
        *,
        colour: Optional[str] = None,
        distance: Optional[int] = None,
    ) -> Route:
        """Claim the *first* unclaimed route matching the criteria.

        Parameters
        ----------
        player_id
            The identifier of the player_id (string or any hashable printed as str).
        city_a, city_b
            Endpoints (order irrelevant).
        colour, distance
            Optional extra filters so you can target a specific parallel track.

        Returns
        -------
        Route
            Reference to the route instance now owned by *player_id*.

        Raises
        ------
        RuntimeError
            If no matching unclaimed route exists.
        """
        for r in self.routes_between(city_a, city_b):
            if r.is_claimed():
                continue
            if colour is not None and r.colour != colour:
                continue
            if distance is not None and r.distance != distance:
                continue
            r.claim(player_id)
            return r
        raise RuntimeError(
            f"No unclaimed route between {city_a} and {city_b} matching criteria"
        )

    def unclaim_route(self, route: Route):
        """Undo ownership (helper for AI simulations / setup resets)."""
        route.unclaim()

    def routes_claimed_by(self, player_id: str) -> List[Route]:
        """All tracks currently owned by *player_id*."""
        return [r for r in self.routes if r.claimed_by == player_id]

    def unclaimed_routes(self) -> List[Route]:
        """Convenience list of routes still available to claim."""
        return [r for r in self.routes if not r.is_claimed()]

    # ------------------------------------------------------------------
    # Read‑only helpers (cities, adjacency, look‑ups)
    # ------------------------------------------------------------------

    @property
    def cities(self) -> Set[str]:
        return set(self._adj.keys())

    def neighbours(self, city: str) -> List[Tuple[str, int, str, Optional[str]]]:
        """Return ``(other_city, distance, colour, owner)`` for each adjacent edge."""
        return [
            (r.other(city), r.distance, r.colour, r.claimed_by)
            for r in self._adj.get(city, [])
        ]

    def routes_between(self, city_a: str, city_b: str) -> List[Route]:
        return [
            r
            for r in self._adj.get(city_a, [])
            if r.other(city_a) == city_b
        ]

    def distance_options(self, city_a: str, city_b: str) -> List[int]:
        return [r.distance for r in self.routes_between(city_a, city_b)]

    # ------------------------------------------------------------------
    # Internal CSV‑loading logic
    # ------------------------------------------------------------------

    def _load(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Map file not found: {self.csv_path}")

        with self.csv_path.open(newline="", encoding="utf-8-sig") as fh:
            rdr = csv.reader(fh)
            header = next(rdr, None)
            if header is None or [h.lower() for h in header[:4]] != [
                "citya",
                "cityb",
                "distance",
                "color",
            ]:
                raise ValueError(
                    "map.csv must begin with header 'cityA,cityB,Distance,Color'"
                )

            for row_num, row in enumerate(rdr, start=2):
                if len(row) < 4:
                    raise ValueError(f"Row {row_num}: expecting 4 columns, got {row}")
                city_a, city_b, distance_str, colour = [col.strip() for col in row[:4]]
                if city_a == city_b:
                    raise ValueError(f"Row {row_num}: self‑loop {city_a}")
                try:
                    distance = int(distance_str)
                except ValueError:
                    raise ValueError(
                        f"Row {row_num}: distance not an integer → {distance_str!r}"
                    )

                route = Route(city_a, city_b, distance, colour)
                self.routes.append(route)
                self._adj.setdefault(city_a, []).append(route)
                self._adj.setdefault(city_b, []).append(route)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self):
        return len(self.routes)

    def __repr__(self):
        taken = sum(r.is_claimed() for r in self.routes)
        return (
            f"<MapGraph cities={len(self.cities)} routes={len(self.routes)} "
            f"claimed={taken}>"
        )


# ---------------------------------------------------------------------------
# Smoke‑test – run `python map_graph.py` directly to try ownership mechanics.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    try:
        board = MapGraph()
        print(board)
        # Claim a sample route.
        r0 = board.routes[2]
        board.claim_route("alice", r0.city_a, r0.city_b, distance=r0.distance, colour=r0.colour)
        print("After Alice claims first route:", board)
        print("Alice owns:", board.routes_claimed_by("alice"))
        # Attempt illegal double‑claim.
        try:
            board.claim_route("bob", r0.city_a, r0.city_b, distance=r0.distance, colour=r0.colour)
        except RuntimeError as e:
            print("Expected error:", e)
        # List unclaimed counts.
        print("Unclaimed routes left:", len(board.unclaimed_routes()))
    except Exception as exc:
        print("Error:", exc, file=sys.stderr)
        sys.exit(1)
