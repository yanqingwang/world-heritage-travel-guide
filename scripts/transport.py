#!/usr/bin/env python3
"""Airport lookup helpers backed by OurAirports (fallback: OpenFlights).

The filtered dataset is stored at data/raw/airports.json and contains only
currently scheduled commercial airports with an IATA code.  Distances are
great-circle distances, not flight routing distances.
"""
from __future__ import annotations

import csv
from functools import lru_cache

from common import RAW, haversine_km, load_json

PEK = (40.080101, 116.584999)


def _parse_coord(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def airports() -> list[dict]:
    filtered = load_json(RAW / "airports.json", {}) or {}
    if filtered.get("airports"):
        return filtered["airports"]

    path = RAW / "airports.dat"
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for row in csv.reader(fh):
            if len(row) < 14 or row[12] != "airport":
                continue
            iata = (row[4] or "").strip()
            if not iata or iata == "\\N":
                continue
            lat, lon = _parse_coord(row[6]), _parse_coord(row[7])
            if lat is None or lon is None:
                continue
            out.append({
                "name": row[1].strip(),
                "city": row[2].strip(),
                "country": row[3].strip(),
                "iata": iata,
                "lat": lat,
                "lon": lon,
            })
    return out


def nearest(lat: float, lon: float, limit: int = 3, max_km: float = 300.0) -> list[dict]:
    zh_names = (load_json(RAW / "airport_names.json", {}) or {}).get("names") or {}
    scored = []
    for ap in airports():
        dist = haversine_km(lat, lon, ap["lat"], ap["lon"])
        if dist <= max_km:
            rec = {**ap, "distance_km": round(dist, 1)}
            if ap.get("iata") in zh_names:
                rec["name_zh"] = zh_names[ap["iata"]]
            scored.append(rec)
    scored.sort(key=lambda x: x["distance_km"])
    return scored[:limit]


def distance_from_beijing(lat: float, lon: float) -> tuple[float, dict | None]:
    """Great-circle distance from PEK to the nearest airport at the site."""
    near = nearest(lat, lon, limit=1, max_km=1000.0)
    if near:
        ap = near[0]
        return round(haversine_km(PEK[0], PEK[1], ap["lat"], ap["lon"]), 1), ap
    return round(haversine_km(PEK[0], PEK[1], lat, lon), 1), None
