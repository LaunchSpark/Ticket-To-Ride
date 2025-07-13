import csv

from typing import List, Dict, Optional, Set




class Route:
    city1: str
    city2: str
    claimed_by: str

    def __init__(self, city1: str, city2: str, length: int, color: Optional[str] = None, claimed_by: Optional[str] = None):
        self.city1 = city1
        self.city2 = city2
        self.length = length
        self.color = color
        self.colour = color
        self.claimed_by = claimed_by

class MapGraph:
    def __init__(self):
        self.routes: List[Route] = []
        self._load_routes_from_csv("../data/map.csv")  # <-- Hardcoded path

        self._adj: Dict[str, List[Route]] = {}
        self._build_adjacency()

    def _load_routes_from_csv(self, csv_path: str):
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city1 = row["city1"]
                city2 = row["city2"]
                length = int(row["Distance"])
                color = row["Color"] or None  # Empty string becomes None

                route = Route(city1=city1, city2=city2, length=length, color=color)
                self.routes.append(route)

    def _build_adjacency(self):
        for route in self.routes:
            self._adj.setdefault(route.city1, []).append(route)
            self._adj.setdefault(route.city2, []).append(route)

    def _build_adjacency(self,player_id):
        player_adj: Dict[str, List[Route]] = {}
        for route in self.routes:
            if route.claimed_by == player_id:
                player_adj.setdefault(route.city1, []).append(route)
                player_adj.setdefault(route.city2, []).append(route)

        return player_adj

    def claim_route(self, route: Route, player_id: str):
        if route in self.routes and route.claimed_by is None:
            route.claimed_by = player_id

    def cities(self) -> Set[str]:
        return set(self._adj.keys())


    def get_available_routes(self) -> List[Route]:
        """
        Returns a list of all unclaimed routes.
        """
        return [route for route in self.routes if route.claimed_by is None]

    def get_claimed_routes(self, player_id: str) -> List[Route]:
        """
        Returns all routes claimed by the specified player.
        """
        return [route for route in self.routes if route.claimed_by == player_id]

    def get_longest_path(self, player_ids: List[str]) -> Dict[str, int]:
        def dfs(city: str, path_length: int, used_routes: Set[Route]):
            nonlocal max_length
            if path_length > max_length:
                max_length = path_length

            for route in adjacency.get(city, []):
                if route not in used_routes:
                    next_city = route.city2 if city == route.city1 else route.city1
                    used_routes.add(route)
                    dfs(next_city, path_length + route.length, used_routes)
                    used_routes.remove(route)

        results: Dict[str, int] = {}

        for player_id in player_ids:
            adjacency = self._build_adjacency(player_id)
            max_length = 0

            for start_city in adjacency:
                dfs(start_city, 0, set())

            results[player_id] = max_length

        return results



