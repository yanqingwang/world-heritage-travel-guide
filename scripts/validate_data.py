#!/usr/bin/env python3
"""Validate the generated datasets before publishing.

Hard failures (exit 1) cover structural problems that would break the site:
duplicate ids, missing bilingual names/intros, out-of-range coordinates,
more than five images or hotels, and hotels beyond the tier distance limit.
Record counts are reported but not hard-coded, so upstream additions are fine.

Usage:
    python scripts/validate_data.py
"""
from __future__ import annotations

import sys

from common import DATA, load_json


def check_site(site: dict, dataset: str) -> list[str]:
    errors = []
    sid = site.get("id") or "?"
    for field in ("name_zh", "name_en", "intro_zh", "intro_en"):
        if not (site.get(field) or "").strip():
            errors.append(f"{sid}: empty {field}")
    lat, lon = site.get("lat"), site.get("lon")
    if lat is not None and not (-90 <= lat <= 90):
        errors.append(f"{sid}: latitude out of range ({lat})")
    if lon is not None and not (-180 <= lon <= 180):
        errors.append(f"{sid}: longitude out of range ({lon})")
    images = site.get("images") or []
    if len(images) > 5:
        errors.append(f"{sid}: {len(images)} images (max 5)")
    hotels = site.get("hotels") or []
    if len(hotels) > 5:
        errors.append(f"{sid}: {len(hotels)} hotels (max 5)")
    limit = 30 if dataset == "china" else 50
    for h in hotels:
        if (h.get("distance_km") or 0) > limit + 0.5:
            errors.append(f"{sid}: hotel {h.get('name')} at {h.get('distance_km')} km > {limit} km")
    if dataset == "china":
        cat = site.get("category_zh") or ""
        if len(cat) > 10:
            errors.append(f"{sid}: category_zh longer than 10 characters ({cat})")
        tr = site.get("transport") or {}
        if not tr.get("airports"):
            errors.append(f"{sid}: no airport")
    else:
        if not (site.get("country") or "").strip():
            errors.append(f"{sid}: empty country")
        if site.get("tier") == "full" and not hotels:
            # Not fatal: OSM may be unavailable during a refresh.  Warn only.
            errors.append(f"WARN {sid}: full record without hotels")
    return errors


def main() -> int:
    china = (load_json(DATA / "china.json", {}) or {}).get("sites", [])
    world = (load_json(DATA / "world.json", {}) or {}).get("sites", [])
    errors: list[str] = []
    warnings: list[str] = []

    seen = set()
    for site in china:
        if site["id"] in seen:
            errors.append(f"duplicate id {site['id']}")
        seen.add(site["id"])
        for err in check_site(site, "china"):
            (warnings if err.startswith("WARN ") else errors).append(err)
    for site in world:
        if site["id"] in seen:
            errors.append(f"duplicate id {site['id']}")
        seen.add(site["id"])
        for err in check_site(site, "world"):
            (warnings if err.startswith("WARN ") else errors).append(err)

    print(f"China 5A: {len(china)} records")
    print(f"World UNESCO: {len(world)} records "
          f"({sum(1 for s in world if s.get('tier') == 'full')} full)")
    print(f"Records with hotels: {sum(1 for s in china + world if s.get('hotels'))}")
    print(f"Records with images: {sum(1 for s in china + world if s.get('images'))}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings[:10]:
        print("  " + w)
    if len(warnings) > 10:
        print(f"  ... {len(warnings) - 10} more warnings")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors[:20]:
            print("  " + e)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
