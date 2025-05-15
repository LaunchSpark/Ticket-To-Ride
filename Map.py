from typing import List, Dict, Optional, Tuple, Set

class Route:
    def __init__(self, city1: str, city2: str, length: int, color: Optional[str] = None, claimed_by: Optional[str] = None):
        self.city1 = city1
        self.city2 = city2
        self.length = length
        self.color = color
        self.colour = color
        self.claimed_by = claimed_by

class MapGraph:
    def __init__(self, routes: List[Route], csv_path: Optional[str] = None):
        self.routes = routes
        self.csv_path = csv_path
        self._adj: Dict[str, List[Route]] = {}
        self._build_adjacency()

    def _build_adjacency(self):
        for route in self.routes:
            self._adj.setdefault(route.city1, []).append(route)
            self._adj.setdefault(route.city2, []).append(route)

    def claim_route(self, route: Route, player_id: str):
        if route in self.routes and route.claimed_by is None:
            route.claimed_by = player_id

    def unclaim_route(self, route: Route):
        if route in self.routes:
            route.claimed_by = None

    def cities(self) -> Set[str]:
        return set(self._adj.keys())

    def neighbours(self, city: str) -> List[Tuple[str, Route]]:
        neighbours = []
        for route in self._adj.get(city, []):
            other_city = route.city2 if route.city1 == city else route.city1
            neighbours.append((other_city, route))
        return neighbours
