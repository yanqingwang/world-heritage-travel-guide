#!/usr/bin/env python3
"""Best-effort detection of language switchers on official 5A websites.

Wikipedia language editions are the reliable signal used in every record;
this script adds a second, official-website signal for Chinese sites.  Many
Chinese scenic-area sites are slow, block automated requests, or use a single
Chinese page, so failures are recorded without overwriting previous results.

Output: data/raw/website_langs.json
"""
from __future__ import annotations

import concurrent.futures as futures
import re
import sys
import time

from common import RAW, http_get, load_json, now_iso, save_json

PATTERNS = {
    "en": [r'hreflang=["\']en', r"English", r"[?&]lang=en", r'href=["\'][^"\']*/en/'],
    "ja": [r"日本語", r'hreflang=["\']ja', r"[?&]lang=ja", r'href=["\'][^"\']*/ja/'],
    "ko": [r"한국어", r'hreflang=["\']ko', r"[?&]lang=ko", r'href=["\'][^"\']*/ko/'],
}


def check(url: str) -> dict:
    if not url:
        return {"status": "no_url", "checked_at": now_iso()}
    r = http_get(url, timeout=18, retries=2)
    if r is None or r.status_code != 200:
        return {"status": f"http_{getattr(r, 'status_code', 'error')}", "checked_at": now_iso()}
    text = r.text[:400_000]
    found = {}
    for lang, pats in PATTERNS.items():
        found[lang] = any(re.search(p, text, re.I) for p in pats)
    found["zh"] = True
    found.update({"status": "ok", "checked_at": now_iso(), "url": url})
    return found


def main() -> int:
    official = load_json(RAW / "china_official.json", {}) or {}
    sites = official.get("sites", [])
    previous = load_json(RAW / "website_langs.json", {}) or {}
    out = dict(previous)
    todo = [s for s in sites if (previous.get(s["id"], {}) or {}).get("status") != "ok"]
    print(f"{len(todo)} websites to check")
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        fmap = {pool.submit(check, s.get("web", "")): s for s in todo}
        done = 0
        for fut in futures.as_completed(fmap):
            site = fmap[fut]
            try:
                result = fut.result()
            except Exception as exc:  # noqa: BLE001
                result = {"status": f"error_{type(exc).__name__}", "checked_at": now_iso()}
            if result.get("status") == "ok" or not out.get(site["id"]):
                out[site["id"]] = result
            done += 1
            if done % 25 == 0:
                print(f"checked {done}/{len(todo)}", flush=True)
                if done % 25 == 0:
                    save_json(RAW / "website_langs.json", out)
    save_json(RAW / "website_langs.json", out)
    ok = sum(1 for v in out.values() if v.get("status") == "ok")
    print(f"website language check: {ok} reachable / {len(out)} checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
