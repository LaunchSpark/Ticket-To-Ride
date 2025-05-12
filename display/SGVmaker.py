import json
import re
import xml.etree.ElementTree as ET
from svgpathtools import parse_path, CubicBezier, QuadraticBezier


def _load_city_lookup(path: str = "city_locations.json") -> dict[str, str]:
    """Return mapping ``"Los_Angeles" → "Los Angeles"`` for strict lookup."""
    try:
        with open(path, "r", encoding="utf-8") as cf:
            city_dict: dict = json.load(cf)
        return {name.replace(" ", "_"): name for name in city_dict}
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Strict validation requires a valid city_locations.json file.") from exc


def _split_route_id(pid_norm: str, city_lookup: dict[str, str]) -> tuple[str, str]:
    """Given a normalised id (underscored / no suffix), find the two cities.

    We try every underscore split until both halves match canonical city keys.
    Raises *ValueError* if no such split exists.
    """
    parts = pid_norm.split("_")
    for i in range(1, len(parts)):
        cityA_key = "_".join(parts[:i])
        cityB_key = "_".join(parts[i:])
        if cityA_key in city_lookup and cityB_key in city_lookup:
            return cityA_key, cityB_key
    raise ValueError(
        f"Cannot determine two valid cities from id '{pid_norm}'. "
        "Ensure it is of the form <CityA>_<CityB> with exact names.")


def parse_svg_control_points(svg_path: str) -> list[dict]:
    """Parse Bezier control points for all valid route paths in *svg_path*.

    A valid route path must have an ``id`` of the form ``CityA_CityB[_n]`` where
    ``CityA`` and ``CityB`` are exact canonical city names (spaces replaced by
    underscores) found in *city_locations.json*. A trailing ``_<digits>``
    suffix (often ``_2`` for overlapping paths) is discarded.

    Returns
    -------
    list[dict]
        One dictionary per route containing ``cities``, ``p1``, ``ctrl``, ``p2``
        and (for cubic Beziers) ``ctrl2``.
    """

    city_lookup = _load_city_lookup()

    cps: list[dict] = []
    root = ET.parse(svg_path).getroot()

    # Optionally warn about mismatched viewBox vs. width/height attributes
    vb, w, h = root.get("viewBox"), root.get("width"), root.get("height")
    if vb and w and h:
        try:
            _, _, vbw, vbh = map(float, vb.split())
            if abs(vbw - float(w)) > 1e-6 or abs(vbh - float(h)) > 1e-6:
                print(f"Warning: viewBox {vb} ≠ width={w}, height={h}")
        except Exception:
            print(f"Warning: cannot parse viewBox '{vb}' for sanity check")

    for elem in root.iter():
        if not elem.tag.endswith("path"):
            continue

        pid = elem.get("id", "").strip()
        if not pid:
            print("Note: <path> without id – skipped.")
            continue

        pid_norm = pid.replace("-", "_").replace(" ", "_")
        if "_" not in pid_norm:
            print(f"Note: id '{pid}' does not describe a city‑to‑city route – skipped.")
            continue

        # Strip optional trailing "_###" (e.g. overlapping route variants)
        pid_core = re.sub(r"_\d+$", "", pid_norm)

        try:
            cityA_key, cityB_key = _split_route_id(pid_core, city_lookup)
        except ValueError as err:
            raise ValueError(f"{err} (in original id '{pid}')") from err

        cityA, cityB = city_lookup[cityA_key], city_lookup[cityB_key]

        # Extract and parse path data
        d_attr = elem.get("d", "").strip()
        if not d_attr:
            raise ValueError(f"Path '{pid}' has empty 'd' attribute.")

        try:
            path = parse_path(d_attr)
        except Exception as err:
            raise ValueError(f"Error parsing path '{pid}': {err}") from err

        beziers = [seg for seg in path if isinstance(seg, (CubicBezier, QuadraticBezier))]
        if not beziers:
            raise ValueError(f"Path '{pid}' contains no Bezier data.")
        seg = beziers[0]

        if seg.start == seg.end:
            raise ValueError(f"Path '{pid}' defines a zero‑length route.")

        p1, p2 = seg.start, seg.end
        if isinstance(seg, CubicBezier):
            ctrl1, ctrl2 = seg.control1, seg.control2
        else:  # Quadratic
            ctrl1, ctrl2 = seg.control, None

        entry: dict = {
            "cities": [cityA, cityB],
            "p1":   [p1.real, p1.imag],
            "ctrl": [ctrl1.real, ctrl1.imag],
            "p2":   [p2.real, p2.imag],
        }
        if ctrl2 is not None:
            entry["ctrl2"] = [ctrl2.real, ctrl2.imag]
        cps.append(entry)

    return cps


if __name__ == "__main__":
    SVG_IN = "routes_for_edit.svg"
    JSON_OUT = "route_control_points.json"

    data = parse_svg_control_points(SVG_IN)
    print(f"✔ Parsed {len(data)} routes.")

    with open(JSON_OUT, "w", encoding="utf-8") as fo:
        json.dump(data, fo, indent=2)
    print(f"✔ Control‑point data → {JSON_OUT}")
