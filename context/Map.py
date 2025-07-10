import csv
from typing import List, Dict, Optional, Set, Tuple

class Path:
    def __init__(self,routes):
        self.routes = routes

class Route:
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

    def claim_route(self, route: Route, player_id: str):
        if route in self.routes and route.claimed_by is None:
            route.claimed_by = player_id

    def cities(self) -> Set[str]:
        return set(self._adj.keys())

    def neighbours(self, city: str) -> List[Tuple[str, Route]]:
        neighbours = []
        for route in self._adj.get(city, []):
            other_city = route.city2 if route.city1 == city else route.city1
            neighbours.append((other_city, route))
        return neighbours

    def get_available_routes(self) -> List['Route']:
        """
        Returns a list of all unclaimed routes.
        """
        return [route for route in self.routes if route.claimed_by is None]

    def get_longest_path(self,player_ids) -> str:
        player_with_longest_path = "NA"
        paths = []
        temp_route_list = []
        temp_city_list = []
        for p in player_ids:
            players_routes = list(filter(lambda x: x.claimed_by == p,self.routes))
            for route in players_routes:
                #initializes the search when
                if not temp_route_list:
                    temp_route_list.append(players_routes[0])
                    temp_city_list.append(temp_route_list[0].city1)
                    temp_city_list.append(temp_route_list[0].city2)
                #checks if city 1 is attached to this path
                elif route.city1 in temp_city_list:
                    temp_route_list.append(route)
                    temp_city_list.append(route.city1)
                    # remove this route so it isnt revisited
                    temp_route_list.remove(route)

                #checks if city 2 is attached to this path
                elif route.city2 in temp_city_list:
                    temp_route_list.append(route)
                    temp_city_list.append(route.city2)
                    # remove this route so it isnt revisited
                    temp_route_list.remove(route)



        return player_with_longest_path

