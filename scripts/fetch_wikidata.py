#!/usr/bin/env python3
"""Map UNESCO World Heritage IDs to Wikidata items with coordinates and images.

Wikidata's P757 ("World Heritage Site ID") is also used by component parts of
serial sites, so several items can share one UNESCO ID.  The helper picks the
best item per ID: Chinese label first, English label second, then the item with
the most sitelinks.

Output: data/raw/unesco_wikidata.json
"""
from __future__ import annotations

import json
import subprocess
import sys
import time

from common import RAW, load_json, now_iso, save_json

UA = "wh-travel-guide/1.0"
CHUNK = 300


def query(ids: list[str]) -> list[dict]:
    values = " ".join(f'"{i}"' for i in ids)
    sparql = f"""
SELECT ?item ?id ?labelEn ?labelZh ?coord ?image ?category ?sitelinks WHERE {{
  ?item wdt:P757 ?id. VALUES ?id {{ {values} }}
  OPTIONAL {{ ?item rdfs:label ?labelEn. FILTER(LANG(?labelEn)="en") }}
  OPTIONAL {{ ?item rdfs:label ?labelZh. FILTER(LANG(?labelZh)="zh") }}
  OPTIONAL {{ ?item wdt:P625 ?coord. }}
  OPTIONAL {{ ?item wdt:P18 ?image. }}
  OPTIONAL {{ ?item wdt:P373 ?category. }}
  OPTIONAL {{ ?item wikibase:sitelinks ?sitelinks. }}
}}
"""
    for attempt in range(4):
        # curl transport: python-requests stalls on wikidata.org TLS on this
        # network (same workaround as common.wiki_api / backfill_wikidata).
        out = subprocess.run(
            ["curl", "-sSL", "--max-time", "170",
             "-H", "Accept: application/sparql-results+json",
             "-H", f"User-Agent: {UA}",
             "--data-urlencode", f"query={sparql}",
             "https://query.wikidata.org/sparql"],
            capture_output=True, text=True, timeout=180)
        if out.returncode == 0 and out.stdout.startswith("{"):
            try:
                return json.loads(out.stdout)["results"]["bindings"]
            except (ValueError, KeyError):
                pass
        time.sleep(10 * (attempt + 1))
    return []


def coord_value(value: str) -> tuple[float, float] | None:
    # "Point(27.072206 44.111116)"
    try:
        inner = value.split("(", 1)[1].split(")", 1)[0].strip()
        lon, lat = inner.split()[:2]
        return float(lat), float(lon)
    except Exception:
        return None


def main() -> int:
    unesco = load_json(RAW / "unesco_sites.json", {}) or {}
    sites = unesco.get("sites", [])
    # P757 stores the dossier number ("174quater"), which differs from the
    # list id for many inscriptions — match against both.
    ids = []
    for s in sites:
        ids.append(s["id"])
        d = s.get("dossier")
        if d and d != s["id"]:
            ids.append(d)
    rows: list[dict] = []
    for i in range(0, len(ids), CHUNK):
        part = ids[i:i + CHUNK]
        result = query(part)
        rows.extend(result)
        print(f"Wikidata {i + len(part)}/{len(ids)} ids, {len(result)} rows")
        time.sleep(1.0)
    if not rows:
        print("Wikidata unavailable; keeping previous mapping", file=sys.stderr)
        return 1

    id_to_dossier = {s["id"]: s.get("dossier") for s in sites}
    dossier_to_id = {d: sid for sid, d in id_to_dossier.items() if d}

    grouped: dict[str, list[dict]] = {}
    for b in rows:
        d = {k: v["value"] for k, v in b.items()}
        sid = dossier_to_id.get(d["id"], d["id"])
        grouped.setdefault(sid, []).append(d)

    def score(d: dict) -> tuple:
        return (
            bool(d.get("labelZh")), bool(d.get("labelEn")),
            int(d.get("sitelinks") or 0),
            bool(d.get("coord")),
        )

    out: dict[str, dict] = {}
    for sid, items in grouped.items():
        best = max(items, key=score)
        coord = coord_value(best["coord"]) if best.get("coord") else None
        out[sid] = {
            "item": best["item"].rsplit("/", 1)[-1],
            "label_en": best.get("labelEn", ""),
            "label_zh": best.get("labelZh", ""),
            "lat": coord[0] if coord else None,
            "lon": coord[1] if coord else None,
            "image": best.get("image", "").rsplit("/", 1)[-1] if best.get("image") else "",
            "commons_category": best.get("category", ""),
            "sitelinks": int(best.get("sitelinks") or 0),
        }

    previous = load_json(RAW / "unesco_wikidata.json", {}) or {}
    # Never drop a previously known coordinate just because WDQS timed out on
    # one chunk.
    for sid, rec in out.items():
        old = previous.get(sid) or {}
        if rec["lat"] is None and old.get("lat") is not None:
            rec["lat"], rec["lon"] = old["lat"], old["lon"]
        if not rec["image"] and old.get("image"):
            rec["image"] = old["image"]
        if not rec["label_zh"] and old.get("label_zh"):
            rec["label_zh"] = old["label_zh"]

    save_json(RAW / "unesco_wikidata.json", {
        "source": "https://query.wikidata.org/",
        "fetched_at": now_iso(),
        "count": len(out),
        "items": out,
    })
    print(f"saved {len(out)} Wikidata mappings; "
          f"{sum(1 for v in out.values() if v['lat'] is not None)} with coordinates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
