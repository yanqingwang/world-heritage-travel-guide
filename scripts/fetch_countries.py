#!/usr/bin/env python3
"""Fetch country metadata (ISO codes, bilingual names, official languages).

Output: data/raw/countries.json
"""
from __future__ import annotations

import sys
import time

from common import RAW, http_post, load_json, now_iso, save_json

QUERY = """
SELECT ?country ?iso2 ?iso3 ?en ?zh ?lang ?len ?lzh ?langCode WHERE {
  ?country wdt:P31 wd:Q6256; wdt:P297 ?iso2.
  OPTIONAL { ?country wdt:P298 ?iso3. }
  OPTIONAL { ?country rdfs:label ?en. FILTER(LANG(?en)="en") }
  OPTIONAL { ?country rdfs:label ?zh. FILTER(LANG(?zh)="zh") }
  OPTIONAL { ?country wdt:P37 ?lang. }
  OPTIONAL { ?lang rdfs:label ?len. FILTER(LANG(?len)="en") }
  OPTIONAL { ?lang rdfs:label ?lzh. FILTER(LANG(?lzh)="zh") }
  OPTIONAL { ?lang wdt:P424 ?langCode. }
}
"""


def main() -> int:
    r = None
    for attempt in range(5):
        r = http_post(
            "https://query.wikidata.org/sparql",
            data={"query": QUERY},
            headers={"Accept": "application/sparql-results+json"},
            timeout=180,
            retries=1,
        )
        if r is not None and r.status_code == 200:
            break
        time.sleep(10 * (attempt + 1))
    if r is None or r.status_code != 200:
        print("Wikidata unavailable; keeping previous countries snapshot", file=sys.stderr)
        return 1

    rows = r.json()["results"]["bindings"]
    countries: dict[str, dict] = {}
    for b in rows:
        d = {k: v["value"] for k, v in b.items()}
        iso = d["iso2"]
        rec = countries.setdefault(iso, {
            "iso2": iso, "iso3": d.get("iso3", ""), "en": "", "zh": "", "langs": [],
        })
        if d.get("en") and not rec["en"]:
            rec["en"] = d["en"]
        if d.get("zh") and not rec["zh"]:
            rec["zh"] = d["zh"]
        if d.get("lang"):
            code = d.get("langCode", "").split("-")[0].lower()
            lang = {"code": code, "en": d.get("len", ""), "zh": d.get("lzh", "")}
            if code and lang not in rec["langs"]:
                rec["langs"].append(lang)

    previous = load_json(RAW / "countries.json", {}) or {}
    for iso, rec in countries.items():
        if previous.get(iso):
            if not rec["en"]:
                rec["en"] = previous[iso].get("en", "")
            if not rec["zh"]:
                rec["zh"] = previous[iso].get("zh", "")
            if not rec["langs"]:
                rec["langs"] = previous[iso].get("langs", [])

    save_json(RAW / "countries.json", countries)
    print(f"saved {len(countries)} countries ({sum(1 for v in countries.values() if v['zh'])} with Chinese names)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
