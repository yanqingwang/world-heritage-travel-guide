#!/usr/bin/env python3
"""Rank UNESCO sites by Wikipedia interest.

Score = 2 * Chinese Wikipedia pageviews + English Wikipedia pageviews over the
last 12 months.  This is a transparent popularity proxy for "most popular
overseas destinations" among Chinese travellers; it is not a visitor-count
dataset.  The top 150 non-China sites receive the full data tier.

Output: data/raw/unesco_rank.json
"""
from __future__ import annotations

import concurrent.futures as futures
import sys
import urllib.parse
from datetime import date, timedelta

from common import CACHE, RAW, get_json, load_json, now_iso, save_json

CACHE_FILE = RAW / "pageviews.json"


def trailing_year() -> tuple[str, str]:
    """First and last day of the 12 full months ending last month."""
    first_this = date.today().replace(day=1)
    last = first_this - timedelta(days=1)
    start = date(last.year - 1, last.month, 1)
    return start.strftime("%Y%m%d"), last.strftime("%Y%m%d")


START, END = trailing_year()


def views(lang: str, title: str) -> int | None:
    title = urllib.parse.quote(title.replace(" ", "_"), safe="")
    data = get_json(
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"{lang}.wikipedia/all-access/user/{title}/monthly/{START}/{END}",
        timeout=30, retries=4,
    )
    if not data:
        return None
    return sum(int(x.get("views") or 0) for x in data.get("items", []))


def main() -> int:
    wiki = load_json(RAW / "unesco_wiki.json", {}) or {}
    templates = load_json(RAW / "unesco_sites.json", {}) or {}
    wiki_items = wiki.get("items", {})
    sites = templates.get("sites", [])
    cached_doc = load_json(CACHE_FILE, {}) or {}
    cache = cached_doc.get("views", {}) if cached_doc.get("period") == f"{START}-{END}" else {}

    tasks = []
    for site in sites:
        sid = site["id"]
        if (site.get("iso") or []) and set(site["iso"]) <= {"cn"}:
            continue  # China is covered by the separate 5A dataset
        sl = (wiki_items.get(sid) or {}).get("sitelinks", {})
        for lang in ("zh", "en"):
            title = sl.get(lang)
            if not title:
                continue
            key = f"{lang}|{title}"
            if key not in cache:
                tasks.append((key, lang, title))

    fetched = 0
    if tasks:
        with futures.ThreadPoolExecutor(max_workers=12) as pool:
            future_map = {pool.submit(views, lang, title): (key, lang, title)
                          for key, lang, title in tasks}
            done = 0
            for fut in futures.as_completed(future_map):
                key, lang, title = future_map[fut]
                try:
                    value = fut.result()
                except Exception:
                    value = None
                if value is None:
                    # Leave failures out of the cache so the next run retries
                    # instead of freezing them at zero.
                    cache.pop(key, None)
                else:
                    cache[key] = value
                    fetched += 1
                done += 1
                if done % 100 == 0:
                    print(f"pageviews {done}/{len(tasks)}")
                    save_json(CACHE_FILE, {"period": f"{START}-{END}", "views": cache})
        save_json(CACHE_FILE, {"period": f"{START}-{END}", "views": cache})

    previous_rank = load_json(RAW / "unesco_rank.json", {}) or {}
    if tasks and fetched < len(tasks) * 0.5 and previous_rank.get("items"):
        print("pageview fetch mostly failed; keeping the previous ranking", file=sys.stderr)
        return 0

    ranked = []
    for site in sites:
        sid = site["id"]
        if (site.get("iso") or []) and set(site["iso"]) <= {"cn"}:
            continue
        sl = (wiki_items.get(sid) or {}).get("sitelinks", {})
        zh = cache.get(f"zh|{sl.get('zh')}") or 0 if sl.get("zh") else 0
        en = cache.get(f"en|{sl.get('en')}") or 0 if sl.get("en") else 0
        score = 2 * zh + en
        ranked.append({"id": sid, "zh_views": zh, "en_views": en, "score": score})

    ranked.sort(key=lambda x: (-x["score"], x["id"]))
    for i, rec in enumerate(ranked, 1):
        rec["rank"] = i
        rec["tier"] = "full" if i <= 150 else "basic"

    save_json(RAW / "unesco_rank.json", {
        "method": "2 * zh.wikipedia pageviews + en.wikipedia pageviews, trailing 12 months",
        "period": f"{START}-{END}",
        "fetched_at": now_iso(),
        "count": len(ranked),
        "items": {r["id"]: r for r in ranked},
    })
    print(f"ranked {len(ranked)} overseas UNESCO sites; full tier = top 150")
    return 0


if __name__ == "__main__":
    sys.exit(main())
