import csv
from typing import List, Dict, Optional, Set

class Route:
    city1: str
    city2: str
    length: int
    color: str
    claimed_by: 'str | None'

    def __init__(self, city1: str, city2: str, length: int, color: str):
        """Represent a single route on the map."""
        self.city1 = city1
        self.city2 = city2
        self.length = length
        self.color = color
        self.claimed_by = None

    def other_city(self, city: str) -> str:
        """Return the opposite endpoint of the route."""
        return self.city1 if self.city1 != city else self.city2

    def get_cities(self) -> 'set[str]':
        """Return a set containing both connected cities."""
        return {self.city1, self.city2}
    
    def __repr__(self):
        return f"{self.city1.replace(' ', '_')}-{self.city2.replace(' ', '_')}-{self.color}"

class MapGraph:
    def __init__(self):
        """Load the map and prepare tracking of routes and paths."""
        self.longest_path_holder: str = ""
        self.longest_paths: Dict[str,int] = {}
        self.routes: List[Route] = []
        self._load_routes_from_csv("data/map.csv")  # <-- Hardcoded path

        #paths hold dicts that associate player_ids with a list comprised of tuples containing (sets of connected cities, longest path length)
        self.paths: 'Dict[str,List[tuple[set[str],int]]]' = {}
        self.longest_paths: Dict[str,int]
        self.longest_path_holder: str

        self._adj: Dict[str, List[Route]] = {}
        self._build_adjacency()


    def _load_routes_from_csv(self, csv_path: str):
        """Load all map routes from a CSV file."""
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city1 = row["city1"]
                city2 = row["city2"]
                length = int(row["Distance"])
                color = row["Color"]

                route = Route(city1, city2, length, color)
                self.routes.append(route)

    def _build_adjacency(self, player_id=None) -> Dict[str, List[Route]]:
        """Generate adjacency lists used for path finding."""
        if player_id is not None:
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
        """Mark a route as claimed by the given player."""
        if route in self.routes and route.claimed_by is None:
            route.claimed_by = player_id

    def cities(self) -> Set[str]:
        """Return a set of every city on the map."""
        return set(self._adj.keys())




    def get_available_routes(self) -> List[Route]:
        """Return all routes that have not been claimed."""
        return [route for route in self.routes if route.claimed_by is None]

    def get_claimed_routes(self, player_id: str) -> List[Route]:
        """Return all routes claimed by the specified player."""
        return [route for route in self.routes if route.claimed_by == player_id]

    def update_longest_path(self, player_id: str, new_route: Route):
        """Update tracking for longest continuous path after a claim."""
        # 1. Gather the endpoints of the newly claimed route
        starting_points: Set[str] = {new_route.city1, new_route.city2}

        # 2. Merge existing components that touch these cities
        if player_id not in self.paths.keys():
            self.paths[player_id] = []
        for (cities, length) in self.paths[player_id]:
            if new_route.city1 in cities or new_route.city2 in cities:
                starting_points.update(cities)
                self.paths[player_id].remove((cities,length))


        # 3. Recompute this component's longest path length
        new_length = self.get_longest_path(player_id, starting_points)

        # 4. Update player's overall longest
        other_best = max((l for (_, l) in self.paths[player_id]), default=0)
        self.longest_paths[player_id] = max(new_length, other_best)

        # 5. Store the merged component
        self.paths[player_id].append((starting_points, new_length))

        # 6. Possibly update the global longest-path holder
        holder_len = self.longest_paths.get(self.longest_path_holder, 0)
        if self.longest_paths[player_id] > holder_len:
            self.longest_path_holder = player_id

    def get_longest_path(self, player_id: str, cities: Set[str]) -> int:
        """Return the longest path length for a connected set of cities."""
        # Build adjacency for this player
        adj = self._build_adjacency(player_id)
        max_length = 0
        for city in cities:
            length = self.dfs(city, set(), 0,player_id)
            max_length = max(max_length, length)
        return max_length

    def dfs(self, current_city: str, visited: Set[Route], current_best: int, player_id: str) -> int:
        """Depth-first search used by longest path calculations."""
        # Explore all unvisited routes from current_city
        adj = self._build_adjacency(player_id)
        best = 0
        children = [r for r in adj.get(current_city, []) if r not in visited]
        if len(children) > 0:
            for r in children:
                nxt = r.other_city(current_city)
                new_length = self.dfs(nxt, visited | {r},current_best + r.length, player_id)
                best = max(best, new_length)
        else:
            group = self.is_city_in_groups(current_city, player_id)
            set_to_add = set()
            for r in visited:
                set_to_add.update(r.get_cities())
            if group:
                group.update(set_to_add)
            else:
                self.paths[player_id].append((set_to_add,best))
        return best

    

    def is_city_in_groups(self,city: str,player_id:str) -> 'set[str] | None':
        """Helper for tracking connected components on the map."""
        for (g,l) in self.paths[player_id]:
            if city in g:
                return g
        return None