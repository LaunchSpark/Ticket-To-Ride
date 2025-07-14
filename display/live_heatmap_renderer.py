import os
import json
from typing import Dict, Tuple, List, Optional, Set, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from PIL import Image

if TYPE_CHECKING:  # avoid runtime circular deps
    from player import Player  # noqa: F401


class LiveHeatmapRenderer:
    """Interactive heat‑map visualiser for Ticket‑to‑Ride routes.

    Draws pre‑computed quadratic/cubic Bézier curves for each board edge.
    Can colour them by *utility* or highlight already‑claimed routes.
    Added robustness so that **route keys are now orientation‑agnostic** –
    missing lines should no longer occur if your `(city1, city2)` tuples are
    in the opposite order to the JSON file.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        map_image_path: str,
        *,
        cmap_name: str = "viridis",
        background_alpha: float = 0.6,
        claim_line_width: float = 6,
        figsize: Tuple[int, int] = (8, 6),
        control_points_path: Optional[str] = None,
    ) -> None:
        # Base map
        img = Image.open(map_image_path).convert("RGBA")
        self.img = np.asarray(img)
        self.h, self.w = self.img.shape[:2]

        # Figure
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.imshow(self.img, alpha=background_alpha)
        self.ax.axis("off")

        # Colour mapping
        self.cmap = mpl.colormaps[cmap_name]
        self.norm = mpl.colors.Normalize(vmin=0, vmax=1)
        self.claim_line_width = claim_line_width
        self.sm = mpl.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        self.sm.set_array([])
        self.cbar = self.fig.colorbar(self.sm, ax=self.ax, fraction=0.046, pad=0.04)
        self.cbar.set_label("Route Utility")

        # Control points
        self.control_points: List[Dict] = []
        if control_points_path and os.path.exists(control_points_path):
            with open(control_points_path, "r", encoding="utf-8") as fh:
                self.control_points = json.load(fh)

        # Runtime storage
        self._patches: List[PathPatch] = []

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _canon(pair: Tuple[str, str]) -> frozenset:
        """Return orientation‑independent representation for set membership."""
        return frozenset(pair)

    # ------------------------------------------------------------------
    # Public update APIs
    # ------------------------------------------------------------------

    def update_curved(
        self,
        route_utilities: Dict[Tuple[str, str], float],
        enemy_claims: Optional[Set[Tuple[str, str]]] = None,
        my_claims: Optional[Set[Tuple[str, str]]] = None,
    ) -> None:
        """Redraw board overlay.

        *route_utilities* may contain (A,B) **or** (B,A); orientation no longer
        matters.  *enemy_claims* / *my_claims* are likewise order‑free.
        """
        enemy_sets = {self._canon(k) for k in (enemy_claims or set())}
        my_sets = {self._canon(k) for k in (my_claims or set())}

        # Clear previous frame
        for p in self._patches:
            p.remove()
        self._patches.clear()

        # Draw each stored curve
        for entry in self.control_points:
            a, b = entry["cities"]
            key_dir = (a, b)  # as stored in JSON
            key_rev = (b, a)
            util = route_utilities.get(key_dir, route_utilities.get(key_rev))
            if util is None:
                continue  # utility not supplied – skip

            key_set = self._canon(key_dir)
            if key_set in enemy_sets:
                colour, lw = "red", self.claim_line_width
            elif key_set in my_sets:
                colour, lw = "blue", self.claim_line_width
            else:
                colour, lw = self.cmap(self.norm(util)), self.claim_line_width

            p1, p2 = entry["p1"], entry["p2"]
            c1, c2 = entry.get("ctrl"), entry.get("ctrl2")

            if c2 is not None:  # cubic Bézier
                verts = [tuple(p1), tuple(c1), tuple(c2), tuple(p2)]
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
            else:  # quadratic
                verts = [tuple(p1), tuple(c1), tuple(p2)]
                codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]

            patch = PathPatch(Path(verts, codes), edgecolor=colour, facecolor="none", linewidth=lw, zorder=4)
            self.ax.add_patch(patch)
            self._patches.append(patch)

        # Rescale colour‑bar if we have any utilities
        if route_utilities:
            vals = list(route_utilities.values())
            if vals:  # avoid empty list
                self.norm.vmin, self.norm.vmax = min(vals), max(vals)
                self.cbar.update_normal(self.sm)
                self.cbar.set_ticks([self.norm.vmin, self.norm.vmax])
                self.cbar.set_ticklabels([f"{self.norm.vmin:.1f}", f"{self.norm.vmax:.1f}"])

        self.fig.canvas.draw_idle()
        plt.pause(0.01)

    # ------------------------------------------------------------------
    # Convenience wrapper – feed from Player.desired_routes
    # ------------------------------------------------------------------

    def update_from_player(
        self,
        player: "Player",
        *,
        enemy_claims: Optional[Set[Tuple[str, str]]] = None,
        my_claims: Optional[Set[Tuple[str, str]]] = None,
    ) -> None:
        route_utils = {tuple(d.key()): float(d.expected_utility) for d in player.desired_routes.values()}
        self.update_curved(route_utils, enemy_claims, my_claims)


# --------------------------------------------------------------------------
# Smoke‑test (unchanged)
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import pandas as pd
    import random
    import time

    MAP_IMG = "USA_map.jpg"
    MAP_CSV = os.path.join("..", "data", "map.csv")
    CP_JSON = "route_control_points.json"

    # ─── Load utilities from CSV ───────────────────────────────────────────
    df = pd.read_csv(MAP_CSV)
    utils = {(r.city1, r.city2): float(r.Distance) for r in df.itertuples(index=False)}

    # ─── Choose a handful of claimed routes for demo ──────────────────────
    all_keys = list(utils.keys())
    random.shuffle(all_keys)
    enemy_claims = set(all_keys[:5])   # draw these in RED
    my_claims    = set(all_keys[5:10]) # draw these in BLUE

    # ─── Renderer ─────────────────────────────────────────────────────────
    rend = LiveHeatmapRenderer(MAP_IMG, control_points_path=CP_JSON)
    print("Initial draw with claimed routes …")
    rend.update_curved(utils, enemy_claims=enemy_claims, my_claims=my_claims)
    time.sleep(2)

    # ─── Animate heat‑map updates ─────────────────────────────────────────
    for i in range(5):
        utils = {k: max(0.0, v + np.random.randint(-2, 3)) for k, v in utils.items()}
        print(f"Frame {i + 1}")
        rend.update_curved(utils, enemy_claims=enemy_claims, my_claims=my_claims)
        time.sleep(1)

    print("Demo complete – close the window to exit.")
    plt.ioff()
    plt.show()
