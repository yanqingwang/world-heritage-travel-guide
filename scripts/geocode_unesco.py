#!/usr/bin/env python3
"""Fill coordinates for UNESCO sites that have no P757-linked Wikidata item.

Wikidata's search API is used instead of Nominatim (the public Nominatim
instance rate-limits shared IPs aggressively).  When no confident match is
found the site is left without coordinates; build_world.py then falls back to
the country centroid and marks that in the record.

Output: data/raw/unesco_geocode.json
"""
from __future__ import annotations

import difflib
import sys
import time

from common import RAW, get_json, load_json, now_iso, save_json, wiki_page

WD_API = "https://www.wikidata.org/w/api.php"


def coord_from_claims(claims: dict) -> tuple[float, float] | None:
    try:
        value = claims["P625"][0]["mainsnak"]["datavalue"]["value"]
        return float(value["latitude"]), float(value["longitude"])
    except Exception:
        return None


def coord_from_wikipedia(title: str) -> tuple[float, float] | None:
    """Wikipedia's `coordinates` prop is often better than a fuzzy search."""
    if not title:
        return None
    page = wiki_page("en", title, props="coordinates", intro=False)
    try:
        c = (page or {}).get("coordinates", [])[0]
        return float(c["lat"]), float(c["lon"])
    except (IndexError, KeyError, TypeError, ValueError):
        return None


def search(name: str, country: str) -> tuple[float, float] | None:
    queries = [f"{name} {country}".strip(), name]
    for q in queries:
        data = get_json(WD_API, params={
            "action": "wbsearchentities", "search": q, "language": "en",
            "format": "json", "limit": 6, "type": "item",
        }, retries=3)
        hits = ((data or {}).get("search") or [])
        if not hits:
            continue
        ids = [h["id"] for h in hits]
        ent = get_json(WD_API, params={
            "action": "wbgetentities", "ids": "|".join(ids), "format": "json",
            "props": "claims|labels", "languages": "en|zh",
        }, retries=3)
        best = None
        for qid, rec in ((ent or {}).get("entities") or {}).items():
            label = ((rec.get("labels") or {}).get("en") or {}).get("value", "")
            ratio = difflib.SequenceMatcher(None, name.lower(), label.lower()).ratio()
            coord = coord_from_claims(rec.get("claims") or {})
            if coord and ratio >= 0.55:
                if best is None or ratio > best[0]:
                    best = (ratio, coord)
        if best:
            return best[1]
    return None


def main() -> int:
    sites = (load_json(RAW / "unesco_sites.json", {}) or {}).get("sites", [])
    wd = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
    wiki = (load_json(RAW / "unesco_wiki.json", {}) or {}).get("items", {})
    countries = load_json(RAW / "countries.json", {}) or {}
    cache = load_json(RAW / "unesco_geocode.json", {}) or {}
    todo = []
    for site in sites:
        sid = site["id"]
        rec = wd.get(sid) or {}
        if rec.get("lat") is not None or cache.get(sid, {}).get("lat") is not None:
            continue
        iso = (site.get("iso") or [""])[0].upper()
        country = (countries.get(iso) or {}).get("en", "")
        todo.append((sid, site.get("name", {}).get("en", ""), country))

    print(f"{len(todo)} sites need geocoding")
    for i, (sid, name, country) in enumerate(todo, 1):
        title = (wiki.get(sid) or {}).get("sitelinks", {}).get("en")
        coord = coord_from_wikipedia(title)
        source = "wikipedia"
        if coord is None:
            coord = search(name, country) if name else None
            source = "wikidata_search"
        cache[sid] = {
            "lat": coord[0] if coord else None,
            "lon": coord[1] if coord else None,
            "source": source if coord else "none",
            "updated_at": now_iso(),
        }
        if coord:
            print(f"[{i}/{len(todo)}] {name}: {coord[1]:.4f},{coord[0]:.4f}")
        if i % 20 == 0:
            save_json(RAW / "unesco_geocode.json", cache)
        time.sleep(0.35)

    save_json(RAW / "unesco_geocode.json", cache)
    print(f"geocoded {sum(1 for v in cache.values() if v.get('lat') is not None)} sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
