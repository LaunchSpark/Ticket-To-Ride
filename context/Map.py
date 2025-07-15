import csv
from typing import List, Dict, Optional, Set

class Route:
    city1: str
    city2: str
    length: int
    color: str
    claimed_by: str

    def __init__(self, city1: str, city2: str, length: int, color: str):
        self.city1 = city1
        self.city2 = city2
        self.length = length
        self.color = color

class MapGraph:
    def __init__(self):
        self.routes: List[Route] = []
        self._load_routes_from_csv("data/map.csv")  # <-- Hardcoded path

        #paths hold dicts that accociate player_ids with a list comprised of tuples containing (sets of connected cities, longest path length)
        self.paths: Dict[str,List[tuple[set[str],int]]]
        self.longest_paths: Dict[str,int]
        self.longest_path_holder: str

        self._adj: Dict[str, List[Route]] = {}
        self._build_adjacency()


    def _load_routes_from_csv(self, csv_path: str):
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city1 = row["city1"]
                city2 = row["city2"]
                length = int(row["Distance"])
                color = row["Color"]

                route = Route(city1, city2, length, color)
                self.routes.append(route)

    def _build_adjacency(self,player_id = None) -> Dict[str, List[Route]]:
        if player_id != None:
            player_adj: Dict[str, List[Route]] = {}
            for route in self.routes:
                if route.claimed_by == player_id:
                    player_adj.setdefault(route.city1, []).append(route)
                    player_adj.setdefault(route.city2, []).append(route)
            return player_adj
        for route in self.routes:
            self._adj.setdefault(route.city1, []).append(route)
            self._adj.setdefault(route.city2, []).append(route)
        return self._adj

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

    def update_longest_path(self, player_ids: List[str]):
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

            self.longest_paths[player_id] = max_length


    def get_highest_path_only(self,results: Dict[str, int]) -> Dict[str, int]: #TODO change this to use the attribute instead of the return
        """
        Returns a dictionary containing only the player(s) with the highest path length.

        Args:
            results (Dict[str, int]): Dictionary mapping player_id to their longest path length.

        Returns:
            Dict[str, int]: Filtered dictionary with only the player(s) with the maximum path length.
        """
        if not results:
            return {}

        max_length = max(results.values())
        return {pid: length for pid, length in results.items() if length == max_length}
    
    

