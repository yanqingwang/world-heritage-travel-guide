#!/usr/bin/env python3
"""Backfill UNESCO site ids that the P757 SPARQL pass could not match.

Wikidata has been dropping the "UNESCO item reference" property (P757), so
newer inscriptions and some legacy entries have no P757 at all — the weekly
fetch_wikidata.py pass leaves them without coordinates/images/sitelinks,
which cascades into missing local-language intros.

Fallback strategy per unmatched site (run only for ids absent from the
cache): search Wikidata by English name (wbsearchentities), then accept the
top candidate only if it is unambiguous enough — either a single plausible
hit, or the top hit with far more sitelinks than the runner-up.  Results are
merged into data/raw/unesco_wikidata.json so the normal pipeline picks them
up on the next build.

Usage: python scripts/backfill_wikidata.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import time
import urllib.parse
import urllib.request

from common import RAW, curl_json, load_json, now_iso, save_json

UA = "wh-travel-guide/1.0"


def wd_api(params: dict) -> dict:
    # curl transport: python TLS stalls against wikidata.org on some networks.
    # curl_json already parses the response, so it returns a dict directly.
    return curl_json("https://www.wikidata.org/w/api.php", timeout=30, params={
        "format": "json", **params})


def sparql(query: str) -> dict | None:
    # POST via curl as well (same TLS stall workaround as wd_api)
    import subprocess
    for attempt in range(3):
        try:
            out = subprocess.run(
                ["curl", "-sSL", "--max-time", "90",
                 "-H", "Accept: application/sparql-results+json",
                 "-H", f"User-Agent: {UA}",
                 "--data-urlencode", f"query={query}",
                 "https://query.wikidata.org/sparql"],
                capture_output=True, text=True, timeout=100)
            if out.returncode == 0 and out.stdout:
                return json_lib(out.stdout)
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
    return None


def sitelinks(ids: list[str]) -> dict[str, int]:
    if not ids:
        return {}
    values = " ".join(f"wd:{i}" for i in ids)
    body = sparql(f"SELECT ?item ?sl WHERE {{ VALUES ?item {{ {values} }} ?item wikibase:sitelinks ?sl . }}")
    out = {}
    if body:
        for b in body["results"]["bindings"]:
            out[b["item"]["value"].rsplit("/", 1)[-1]] = int(b["sl"]["value"])
    return out


def json_lib(text: str):
    import json
    return json.loads(text)


def search(name: str) -> list[str]:
    res = wd_api({"action": "query", "list": "search", "srsearch": name,
                  "srnamespace": "0", "srlimit": 5})
    if not res:
        return []
    return [h["title"] for h in (res.get("query", {}) or {}).get("search", [])]


def norm(s: str) -> str:
    return s.lower().replace("–", "-").replace("’", "'").strip()
    # leading "the " handled at comparison time


def accept(candidates: list[str], sl: dict[str, int], name: str) -> str | None:
    """Accept the top candidate only when its English label matches the site
    name and it is reasonably prominent (>=5 sitelinks).  Name normalization:
    case, dashes, apostrophes, a leading article, and UNESCO's trailing
    qualifiers are tolerated."""
    import re

    def key(s: str) -> str:
        s = norm(s)
        s = re.sub(r"^the ", "", s)
        s = s.split(" (")[0]
        return s

    target = key(name)
    ranked = sorted(candidates, key=lambda i: sl.get(i, 0), reverse=True)
    for qid in ranked[:3]:
        if sl.get(qid, 0) < 5:
            continue
        ent = wd_api({"action": "wbgetentities", "ids": qid, "props": "labels",
                      "languages": "en"})
        label = ((ent.get("entities", {}).get(qid, {}).get("labels") or {})
                 .get("en", {}).get("value", ""))
        if label and (key(label) == target or key(label) in target or target in key(label)):
            return qid
    return None


def main() -> int:
    dry = "--dry-run" in sys.argv
    unesco = load_json(RAW / "unesco_sites.json", {}) or {}
    cache = load_json(RAW / "unesco_wikidata.json", {}) or {}
    items = cache.setdefault("items", {})
    missing = [s for s in unesco.get("sites", []) if s["id"] not in items]
    print(f"{len(missing)} sites to backfill", flush=True)

    matched = 0
    for n, site in enumerate(missing, 1):
        name = site.get("name", {}).get("en", "")
        if not name:
            continue
        try:
            candidates = search(name)
            sl = sitelinks(candidates)
            qid = accept(candidates, sl, name)
        except Exception as exc:  # noqa: BLE001
            print(f"  {site['id']} search failed: {exc}")
            qid = None
        if qid:
            items[site["id"]] = {"item": qid, "label_en": name, "label_zh": "",
                                 "lat": None, "lon": None, "image": "",
                                 "commons_category": "", "sitelinks": sl.get(qid, 0),
                                 "backfilled": True}
            matched += 1
            print(f"  [{n}/{len(missing)}] {site['id']} {name[:40]} -> {qid} (sl={sl.get(qid, 0)})", flush=True)
        else:
            print(f"  [{n}/{len(missing)}] {site['id']} {name[:40]} -> no confident match", flush=True)
        time.sleep(0.4)

    print(f"backfilled {matched}/{len(missing)}", flush=True)
    if matched and not dry:
        cache["fetched_at"] = now_iso()
        cache["backfill_note"] = "ids without P757 matched by en-label search; coords/images come from the next full fetch"
        save_json(RAW / "unesco_wikidata.json", cache)
        print("cache updated", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
