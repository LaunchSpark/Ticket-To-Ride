import csv
from typing import List, Dict, Optional, Set, Tuple, Type


class Path:
    def __init__(self,routes):
        self.routes = routes

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


    def get_available_routes(self) -> List['Route']:
        """
        Returns a list of all unclaimed routes.
        """
        return [route for route in self.routes if route.claimed_by is None]

    def get_longest_path(self,player_ids:[str]) -> dict[str,int]:
        player_with_longest_path = "NA"
        paths = []
        temp_route_list = []
        temp_city_list = []

        for p in player_ids:
            player_adj = self._build_adjacency(p)
            players_routes = [r for r in self.routes if r.claimed_by == p]
            for R in players_routes:
                to_check = [players_routes[0]]
                for route in to_check:
                    #gets nehibors for both cities
                    city1_neighbirs = player_adj[route.city1]
                    city2_neighbirs = player_adj[route.city2]
                    all_nehibors = city1_neighbirs + city2_neighbirs

                    to_check.append(all_nehibors)









        return player_with_longest_path

    def aggrigate_path(self,routes_to_exclude) -> [] :
        return []