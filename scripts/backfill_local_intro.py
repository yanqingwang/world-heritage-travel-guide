#!/usr/bin/env python3
"""Fill missing `intro_local` in the UNESCO wiki cache without a full refetch.

`enrich_wiki.py` only fetches a local-language extract when the language is in
LANG_TO_WIKI.  When a code was absent from that table (hi, ta, sq, mt, …) the
site silently ended up with no local intro even though its Wikipedia article
existed.  This script reads the cached sitelinks, refetches extracts only for
the languages that actually have missing text, and writes them back.

    python scripts/backfill_local_intro.py            # fill what's missing
    python scripts/backfill_local_intro.py --dry-run  # report only
"""
from __future__ import annotations

import argparse
import collections
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import load_json, save_json, RAW  # noqa: E402
from enrich_wiki import LANG_TO_WIKI, fetch_extracts, title_clean  # noqa: E402

CACHE = RAW / "unesco_wiki.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cache = load_json(CACHE, {}) or {}
    items = cache.get("items") or {}
    if not items:
        print("no cache items; run scripts/enrich_wiki.py first")
        return 1

    todo: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for sid, rec in items.items():
        if rec.get("intro_local"):
            continue
        lang = rec.get("local_lang")
        title = (rec.get("sitelinks") or {}).get(lang or "")
        if not lang or not title:
            continue
        if lang not in LANG_TO_WIKI:
            continue
        todo[lang].append((sid, title_clean(title)))

    total = sum(len(v) for v in todo.values())
    print(f"{total} sites with a Wikipedia sitelink but no local intro "
          f"across {len(todo)} languages")
    if args.dry_run:
        for lang, pairs in sorted(todo.items(), key=lambda kv: -len(kv[1])):
            print(f"  {lang}: {len(pairs)}")
        return 0
    if not total:
        print("nothing to do")
        return 0

    filled = 0
    for lang, pairs in sorted(todo.items(), key=lambda kv: -len(kv[1])):
        wiki = LANG_TO_WIKI[lang]
        extracts = fetch_extracts(wiki, [t for _, t in pairs])
        got = 0
        for sid, title in pairs:
            text = extracts.get(title)
            if not text:
                continue
            rec = items[sid]
            rec["intro_local"] = text[:1400]
            rec["local_source"] = "wikipedia"
            if not rec.get("name_local"):
                rec["name_local"] = (rec.get("sitelinks") or {}).get(lang) or title
            got += 1
        filled += got
        print(f"  {lang} ({wiki}): {got}/{len(pairs)} filled", flush=True)
        time.sleep(0.4)

    if filled:
        cache["items"] = items
        save_json(CACHE, cache)
    print(f"filled {filled} local intros; cache updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
