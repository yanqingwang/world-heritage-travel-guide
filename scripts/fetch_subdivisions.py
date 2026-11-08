#!/usr/bin/env python3
"""Resolve the ISO 3166-2 first-level subdivision for every UNESCO site.

The site's Wikidata item is walked up to three P131 ("located in the
administrative territorial entity") levels looking for an entity that carries a
P300 ("ISO 3166-2 code").  That yields a standard code such as ``US-AZ`` or
``JP-26`` instead of a free-text UNESCO location string, so the UI can offer the
same country -> province/state cascade for China and for overseas records.

Output: data/raw/unesco_subdivisions.json
"""
from __future__ import annotations

import sys
import time

from common import RAW, http_post, load_json, now_iso, save_json

CHUNK = 80
WD_ENTITY = "http://www.wikidata.org/entity/"


def sparql(qids: list[str]) -> list[dict]:
    values = " ".join(f"wd:{q}" for q in qids)
    query = f"""
SELECT ?item ?sub ?iso ?labEn ?labZhHans ?labZh ?depth WHERE {{
  VALUES ?item {{ {values} }}
  {{
    ?item wdt:P131 ?sub. ?sub wdt:P300 ?iso. BIND(1 AS ?depth)
  }} UNION {{
    ?item wdt:P131/wdt:P131 ?sub. ?sub wdt:P300 ?iso. BIND(2 AS ?depth)
  }} UNION {{
    ?item wdt:P131/wdt:P131/wdt:P131 ?sub. ?sub wdt:P300 ?iso. BIND(3 AS ?depth)
  }}
  OPTIONAL {{ ?sub rdfs:label ?labEn. FILTER(LANG(?labEn)="en") }}
  OPTIONAL {{ ?sub rdfs:label ?labZhHans. FILTER(LANG(?labZhHans)="zh-hans") }}
  OPTIONAL {{ ?sub rdfs:label ?labZh. FILTER(LANG(?labZh)="zh") }}
}}
"""
    for attempt in range(4):
        r = http_post(
            "https://query.wikidata.org/sparql",
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=180,
            retries=1,
        )
        if r is not None and r.status_code == 200:
            try:
                return r.json()["results"]["bindings"]
            except Exception:
                pass
        time.sleep(10 * (attempt + 1))
    return []


def main() -> int:
    sites = (load_json(RAW / "unesco_sites.json", {}) or {}).get("sites", [])
    wd = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
    cache = (load_json(RAW / "unesco_subdivisions.json", {}) or {}).get("items", {})
    countries = load_json(RAW / "countries.json", {}) or {}

    todo = []
    for site in sites:
        sid = site["id"]
        qid = (wd.get(sid) or {}).get("item")
        if not qid or (cache.get(sid) or {}).get("iso"):
            continue
        todo.append((sid, qid, [c.upper() for c in (site.get("iso") or [])]))

    print(f"{len(todo)} sites need an ISO 3166-2 subdivision")
    resolved = 0
    for i in range(0, len(todo), CHUNK):
        part = todo[i:i + CHUNK]
        by_qid = {qid: (sid, isos) for sid, qid, isos in part}
        rows = sparql([qid for _, qid, _ in part])
        best: dict[str, tuple] = {}
        for row in rows:
            d = {k: v["value"] for k, v in row.items()}
            qid = d["item"].rsplit("/", 1)[-1]
            if qid not in by_qid:
                continue
            iso = d["iso"].upper()
            prefix = iso.split("-", 1)[0]
            if prefix not in by_qid[qid][1]:
                continue  # cross-border P131 chain (e.g. an exclave)
            depth = int(d.get("depth") or 9)
            name_en = d.get("labEn", "")
            name_zh = d.get("labZhHans") or d.get("labZh") or ""
            key = (depth, iso)
            if qid not in best or key < best[qid][0]:
                best[qid] = (key, iso, name_en, name_zh, depth)

        for qid, (_, iso, name_en, name_zh, depth) in best.items():
            sid = by_qid[qid][0]
            cache[sid] = {
                "iso": iso,
                "name_en": name_en,
                "name_zh": name_zh,
                "depth": depth,
                "source": "wikidata_p131_p300",
                "updated_at": now_iso(),
            }
            resolved += 1
        save_json(RAW / "unesco_subdivisions.json", {
            "source": "https://query.wikidata.org/",
            "fetched_at": now_iso(),
            "count": len(cache),
            "items": cache,
        })
        print(f"[{min(i + CHUNK, len(todo))}/{len(todo)}] resolved {resolved}")
        time.sleep(1.2)

    total = len([s for s in sites if (wd.get(s["id"]) or {}).get("item")])
    have = len([s for s in sites if (cache.get(s["id"]) or {}).get("iso")])
    print(f"ISO 3166-2 subdivision for {have}/{total} mapped sites "
          f"({have / max(total, 1):.0%}); {len(sites) - total} without a Wikidata item")

    # Quick distribution by country, useful for spotting gaps.
    by_country: dict[str, int] = {}
    for sid, rec in cache.items():
        if rec.get("iso"):
            prefix = rec["iso"].split("-", 1)[0]
            by_country[prefix] = by_country.get(prefix, 0) + 1
    print("top countries:", sorted(by_country.items(), key=lambda kv: -kv[1])[:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
