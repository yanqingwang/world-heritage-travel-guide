#!/usr/bin/env python3
"""Add Chinese names to the airports used by the site.

OurAirports carries English names only.  One Wikidata SPARQL query maps every
airport's IATA code (P238) to its Chinese label — 4,900+ airports in a single
request, no per-airport lookups.  Stored in data/raw/airport_names.json keyed
by IATA for transport.nearest() to attach as `name_zh`.
"""
from __future__ import annotations

import sys

from common import RAW, get_json, save_json, now_iso

SPARQL = """
SELECT ?iata ?zh WHERE {
  ?item wdt:P238 ?iata ; rdfs:label ?zh .
  FILTER(LANG(?zh) = "zh")
}
"""


def main() -> int:
    used = set()
    for name in ("china.json", "world.json"):
        doc = load_doc(name)
        for site in doc.get("sites", []):
            for ap in (site.get("transport") or {}).get("airports") or []:
                if ap.get("iata"):
                    used.add(ap["iata"])

    data = get_json("https://query.wikidata.org/sparql", params={
        "query": SPARQL,
    }, headers={
        "Accept": "application/sparql-results+json",
    }, timeout=120, retries=3)
    rows = ((data or {}).get("results") or {}).get("bindings") or []
    mapping = {}
    for r in rows:
        iata = (r.get("iata") or {}).get("value")
        zh = (r.get("zh") or {}).get("value")
        if iata and zh and iata not in mapping:
            mapping[iata] = zh

    names = {}
    try:
        from opencc import OpenCC
        t2s = OpenCC("t2s")
        conv = lambda s: t2s.convert(s)
    except Exception:
        conv = lambda s: s
    for k in sorted(used):
        if k in mapping:
            names[k] = conv(mapping[k])
    print(f"airports used by sites: {len(used)}; zh labels from Wikidata: {len(names)}")
    if not names:
        print("SPARQL returned nothing; keeping the previous mapping", file=sys.stderr)
        return 1
    save_json(RAW / "airport_names.json", {
        "fetched_at": now_iso(),
        "source": "Wikidata SPARQL: ?item wdt:P238 ?iata ; rdfs:label ?zh (LANG=zh)",
        "count": len(names),
        "names": names,
    })
    return 0


def load_doc(name: str) -> dict:
    import json
    path = RAW.parent / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


if __name__ == "__main__":
    sys.exit(main())
