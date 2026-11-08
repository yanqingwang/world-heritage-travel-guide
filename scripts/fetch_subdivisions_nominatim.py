#!/usr/bin/env python3
"""Fill ISO 3166-2 subdivisions that Wikidata's P131/P300 path missed.

Nominatim's reverse geocoder exposes ``ISO3166-2-lvl4`` for most countries, so
it is a good second source.  The public instance allows at most one request per
second; results are cached per site and only missing records are fetched.

Output: merges into data/raw/unesco_subdivisions.json
"""
from __future__ import annotations

import sys
import time

from common import RAW, get_json, http_post, load_json, now_iso, save_json

NOMINATIM = "https://nominatim.openstreetmap.org/reverse"
UA = "world-heritage-travel-guide/1.0 (+https://github.com/yanqingwang/world-heritage-travel-guide)"
WD_ENTITY = "http://www.wikidata.org/entity/"


def labels_for_codes(codes: list[str]) -> dict[str, dict]:
    """Resolve zh/en labels for ISO 3166-2 codes in one SPARQL round-trip."""
    values = " ".join(f'"{c}"' for c in codes)
    query = f"""
SELECT ?code ?labEn ?labZhHans ?labZh WHERE {{
  VALUES ?code {{ {values} }}
  ?item wdt:P300 ?code.
  OPTIONAL {{ ?item rdfs:label ?labEn. FILTER(LANG(?labEn)="en") }}
  OPTIONAL {{ ?item rdfs:label ?labZhHans. FILTER(LANG(?labZhHans)="zh-hans") }}
  OPTIONAL {{ ?item rdfs:label ?labZh. FILTER(LANG(?labZh)="zh") }}
}}
"""
    out: dict[str, dict] = {}
    for attempt in range(3):
        r = http_post("https://query.wikidata.org/sparql",
                      data={"query": query},
                      headers={"Accept": "application/sparql-results+json"},
                      timeout=120, retries=1)
        if r is not None and r.status_code == 200:
            for row in r.json()["results"]["bindings"]:
                d = {k: v["value"] for k, v in row.items()}
                code = d["code"].upper()
                cur = out.setdefault(code, {"name_en": "", "name_zh": ""})
                cur["name_en"] = cur["name_en"] or d.get("labEn", "")
                cur["name_zh"] = cur["name_zh"] or d.get("labZhHans") or d.get("labZh") or ""
            return out
        time.sleep(8 * (attempt + 1))
    return out


def main() -> int:
    sites = (load_json(RAW / "unesco_sites.json", {}) or {}).get("sites", [])
    wd = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
    geocode = load_json(RAW / "unesco_geocode.json", {}) or {}
    doc = load_json(RAW / "unesco_subdivisions.json", {}) or {}
    cache = doc.get("items", {})

    todo = []
    for site in sites:
        sid = site["id"]
        iso = [c.upper() for c in (site.get("iso") or [])]
        if not iso or "CN" in iso:
            continue  # China provinces come from the 5A dataset
        if (cache.get(sid) or {}).get("iso"):
            continue
        lat = (wd.get(sid) or {}).get("lat")
        lon = (wd.get(sid) or {}).get("lon")
        if lat is None:
            lat, lon = (geocode.get(sid) or {}).get("lat"), (geocode.get(sid) or {}).get("lon")
        if lat is None:
            continue
        todo.append((sid, lat, lon, iso))

    print(f"{len(todo)} sites need a Nominatim fallback")
    codes: set[str] = set()
    found = 0
    for i, (sid, lat, lon, iso) in enumerate(todo, 1):
        data = get_json(NOMINATIM, params={
            "lat": lat, "lon": lon, "format": "jsonv2", "zoom": 6,
            "accept-language": "en",
        }, headers={"User-Agent": UA}, timeout=30, retries=2)
        addr = (data or {}).get("address") or {}
        code = ""
        for key in ("ISO3166-2-lvl4", "ISO3166-2-lvl3", "ISO3166-2-lvl5"):
            value = (addr.get(key) or "").upper()
            if value.startswith(tuple(iso)):
                code = value
                break
        if code:
            cache[sid] = {
                "iso": code,
                "name_en": addr.get("state") or addr.get("region") or "",
                "name_zh": "",
                "depth": None,
                "source": "nominatim_reverse",
                "updated_at": now_iso(),
            }
            codes.add(code)
            found += 1
        else:
            cache[sid] = {
                "iso": "",
                "name_en": addr.get("state") or addr.get("region") or "",
                "name_zh": "",
                "depth": None,
                "source": "nominatim_reverse",
                "updated_at": now_iso(),
            }
        if i % 25 == 0:
            save_json(RAW / "unesco_subdivisions.json", {
                "source": "wikidata+nominatim", "fetched_at": now_iso(),
                "count": len(cache), "items": cache,
            })
            print(f"[{i}/{len(todo)}] {found} resolved")
        time.sleep(1.1)

    # zh/en names for the codes Nominatim returned (it only gives English).
    labels = labels_for_codes(sorted(codes)) if codes else {}
    for sid, rec in cache.items():
        code = rec.get("iso") or ""
        lab = labels.get(code)
        if lab:
            rec["name_en"] = rec.get("name_en") or lab["name_en"]
            rec["name_zh"] = rec.get("name_zh") or lab["name_zh"]

    save_json(RAW / "unesco_subdivisions.json", {
        "source": "wikidata+nominatim", "fetched_at": now_iso(),
        "count": len(cache), "items": cache,
    })
    have = sum(1 for s in sites if (cache.get(s["id"]) or {}).get("iso"))
    print(f"subdivision coverage now {have}/{len(sites)} ({have / len(sites):.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
