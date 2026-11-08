#!/usr/bin/env python3
"""Build the small GeoJSON files used by the interactive globe.

Sources (both public domain, Natural Earth):
  * ne_110m_admin_0_countries  -> country outlines + ISO 3166-1 alpha-2
  * ne_50m_admin_1_states_provinces -> Chinese provinces + ISO 3166-2

Coordinates are rounded to 2 decimals (~1 km), tiny rings are dropped and only
the properties the globe needs are kept, which takes the payload from ~3.2 MB to
well under 1 MB.

Output: site/assets/geo/world-110m.json, site/assets/geo/china-provinces.json
"""
from __future__ import annotations

import json
import sys

from common import SITE, http_get

WORLD_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
             "master/geojson/ne_110m_admin_0_countries.geojson")
ADMIN1_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
              "master/geojson/ne_50m_admin_1_states_provinces.geojson")
OUT = SITE / "assets" / "geo"


def round_coords(node):
    if isinstance(node, (int, float)):
        return round(node, 2)
    if isinstance(node, list):
        return [round_coords(x) for x in node]
    return node


def clean_geometry(geom: dict, min_points: int = 4) -> dict | None:
    kind = geom.get("type")
    coords = round_coords(geom.get("coordinates"))
    if kind == "Polygon":
        rings = [r for r in coords if len(r) >= min_points]
        return {"type": "Polygon", "coordinates": rings} if rings else None
    if kind == "MultiPolygon":
        polys = []
        for poly in coords:
            rings = [r for r in poly if len(r) >= min_points]
            if rings:
                polys.append(rings)
        return {"type": "MultiPolygon", "coordinates": polys} if polys else None
    return geom


def fetch(url: str) -> dict:
    r = http_get(url, timeout=180, retries=3)
    if r is None or r.status_code != 200:
        raise SystemExit(f"failed to download {url}")
    return r.json()


def iso2(props: dict) -> str:
    for key in ("ISO_A2", "ISO_A2_EH"):
        value = (props.get(key) or "").strip()
        if value and value != "-99":
            return value.upper()
    return ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    world = fetch(WORLD_URL)
    countries = []
    for feat in world["features"]:
        props = feat.get("properties") or {}
        geom = clean_geometry(feat.get("geometry") or {})
        if not geom:
            continue
        code = iso2(props)
        if not code:
            continue
        countries.append({
            "type": "Feature",
            "properties": {
                "iso2": code,
                "name": props.get("NAME") or props.get("NAME_EN") or code,
                "name_zh": props.get("NAME_ZH") or "",
            },
            "geometry": geom,
        })
    (OUT / "world-110m.json").write_text(json.dumps(
        {"type": "FeatureCollection", "features": countries},
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    admin1 = fetch(ADMIN1_URL)
    provinces = []
    for feat in admin1["features"]:
        props = feat.get("properties") or {}
        if props.get("adm0_a3") != "CHN":
            continue
        iso = (props.get("iso_3166_2") or "").upper()
        # Natural Earth carries an extra "CN-X01~" feature for the Xisha
        # islands; real ISO codes never contain "~".
        if not iso.startswith("CN-") or "~" in iso:
            continue
        geom = clean_geometry(feat.get("geometry") or {})
        if not geom:
            continue
        provinces.append({
            "type": "Feature",
            "properties": {
                "iso": iso,
                "name_zh": props.get("name_zh") or props.get("name") or "",
                "name_en": props.get("name_en") or props.get("name") or "",
            },
            "geometry": geom,
        })
    (OUT / "china-provinces.json").write_text(json.dumps(
        {"type": "FeatureCollection", "features": provinces},
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    for name in ("world-110m.json", "china-provinces.json"):
        p = OUT / name
        print(f"{name}: {p.stat().st_size / 1024:.0f} KB, "
              f"{len(json.loads(p.read_text(encoding='utf-8'))['features'])} features")
    return 0


if __name__ == "__main__":
    sys.exit(main())
