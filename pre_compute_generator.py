from context.Map import MapGraph, Route
import heapq
import csv


map = MapGraph()

def dijkstra(start: str) -> dict[str,tuple[list[Route],int]]:
    # Create adjacency list
    adj = map._adj
    dist: 'dict[str, tuple[list[Route], int]]'= {start: ([], 0)}
    heap = [(0, start)]
    while heap:
        cost, city = heapq.heappop(heap)
        for route in adj.get(city, []):
            neighbor = route.other_city(city)
            new_dist = cost + route.length
            if city not in dist.keys():
                new_route_list: list[Route] = []
            else:
                new_route_list: list[Route] = dist[city][0]
            new_route_list.append(route)
            if neighbor in dist.keys() and not new_dist < dist[neighbor][1]:
                continue
            dist[neighbor] = (new_route_list, new_dist)
            heapq.heappush(heap, (new_dist, neighbor))
    return dist

def route_to_str(route: Route) -> str:
    return f"{route.city1}-{route.city2}:{route.length}:{route.color}"

def write_routes_to_csv(data, filename="shortest_paths.csv"):
    with open(filename, mode="w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["start_city", "end_city", "route_str", "length"])
        for start, destinations in data.items():
            for end, (routes, total_length) in destinations.items():
                route_str = "|".join(route_to_str(r) for r in routes)
                writer.writerow([start, end, route_str, total_length])

data: dict[str,dict[str,tuple[list[Route],int]]] = {}
for start in map.cities():
    data[start] = dijkstra(start)

write_routes_to_csv(data, filename="shortest_paths_precompute.csv")