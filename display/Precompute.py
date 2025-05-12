import os
import json
import numpy as np
import pandas as pd

# This script precomputes quadratic Bezier control points for each route, adjusting
# the bow height inversely proportional to the proximity of parallel routes.

def load_data(coords_path: str, map_csv: str):
    """
    Load city coordinates and route list.

    Returns:
        city_coords: Dict[str, Tuple[float,float]] normalized [0,1]
        routes: List[Tuple[str,str]] city pairs
    """
    with open(coords_path, 'r') as f:
        city_coords = json.load(f)
    df = pd.read_csv(map_csv)
    routes = [(row.cityA, row.cityB) for row in df.itertuples(index=False)]
    return city_coords, routes


def compute_control_points(city_coords: dict,
                           routes: list,
                           img_shape: tuple,
                           base_height: float = 0.05,
                           proximity_threshold: float = 100.0):
    """
    For each route, compute a control point for a quadratic Bezier curve.
    The bow height increases as the route's midpoint gets closer to any other route's midpoint.

    Args:
        city_coords: normalized coordinates {city: [x,y]}
        routes: list of (cityA, cityB)
        img_shape: (height, width) in pixels
        base_height: minimal curve height factor
        proximity_threshold: distance in pixels within which bows increase

    Returns:
        List of dicts: [{ 'cities': (A,B), 'p1':..., 'ctrl':..., 'p2':... }, ...]
    """
    h, w = img_shape
    # Compute pixel endpoints and midpoints
    segs = []
    for (a, b) in routes:
        x1, y1 = city_coords[a]
        x2, y2 = city_coords[b]
        p1 = np.array([x1 * w, (1-y1) * h])
        p2 = np.array([x2 * w, (1-y2) * h])
        mid = (p1 + p2) / 2
        direction = p2 - p1
        perp = np.array([-direction[1], direction[0]])
        perp = perp / np.linalg.norm(perp)
        segs.append({'cities': (a, b), 'p1': p1, 'p2': p2, 'mid': mid, 'perp': perp})

    # For each segment, find min distance to any other midpoint
    mids = np.array([s['mid'] for s in segs])
    cps = []
    for i, s in enumerate(segs):
        # compute distances to all other mids
        dists = np.linalg.norm(mids - s['mid'], axis=1)
        dists[i] = np.inf
        dmin = dists.min()
        # height factor increases as dmin decreases
        if dmin < proximity_threshold:
            factor = 1 + (proximity_threshold - dmin) / proximity_threshold
        else:
            factor = 1.0
        height = base_height * factor * np.linalg.norm(s['p2'] - s['p1'])
        # control point
        ctrl = s['mid'] + s['perp'] * height
        cps.append({
            'cities': s['cities'],
            'p1': tuple(s['p1']),
            'ctrl': tuple(ctrl),
            'p2': tuple(s['p2']),
        })
    return cps


if __name__ == '__main__':
    # Updated file paths
    coords_path = os.path.join('city_locations.json')
    map_csv = os.path.join('..', 'data', 'map.csv')
    # load map image to get shape
    from PIL import Image
    img_path = os.path.join('USA_map.jpg')
    img = Image.open(img_path)
    h, w = img.size[1], img.size[0]

    city_coords, routes = load_data(coords_path, map_csv)
    control_points = compute_control_points(city_coords, routes, (h, w))

    # save to JSON for later use
    out_path = 'route_control_points.json'
    with open(out_path, 'w') as f:
        json.dump(control_points, f, indent=2)

    print(f"Computed {len(control_points)} control points saved to {out_path}")
