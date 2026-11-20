# -*- coding: utf-8 -*-
"""Build the "31 must-climb mountains" collection from data/mountains.json.

The collection deliberately does not duplicate records: mountains that already
exist as China 5A sites link to them by id, and the front end propagates the
"visited" mark in both directions. Mountains outside the 5A list carry their
own coordinates and a short intro.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE_DATA = ROOT / "site" / "data"

sys.path.insert(0, str(ROOT / "scripts"))
from common import load_json, now_iso, save_json  # noqa: E402


def main() -> int:
    src = load_json(DATA / "mountains.json", {}) or {}
    mountains = src.get("mountains") or []
    china_rows = (load_json(DATA / "china.json", {}) or {}).get("sites", [])
    china = {s["id"]: s for s in china_rows}
    # 省份名 → ISO 3166-2（用于点亮足迹地球）
    province_pairs = []
    for row in china_rows:
        full = row.get("province_zh") or ""
        if full and row.get("province_iso"):
            province_pairs.append((full, row["province_iso"]))

    index, missing = [], []
    out_dir = SITE_DATA / "mountains"
    out_dir.mkdir(parents=True, exist_ok=True)

    for m in mountains:
        site = china.get(m.get("site_id") or "")
        if m.get("site_id") and not site:
            missing.append((m["name_zh"], m["site_id"]))

        lat = m.get("lat") if m.get("lat") is not None else (site or {}).get("lat")
        lon = m.get("lon") if m.get("lon") is not None else (site or {}).get("lon")
        images = (site or {}).get("images") or []
        admission = (site or {}).get("admission") or "unknown"
        iso = (site or {}).get("province_iso") or ""
        if not iso:
            short = (m.get("province_zh") or "").split("·")[0]
            for full, code in province_pairs:
                if full.startswith(short) or short.startswith(full[:2]):
                    iso = code
                    break

        record = {
            "id": m["id"],
            "dataset": "mountain_31",
            "mountain_rank": m["rank"],
            "mountain_group": m["group"],
            "difficulty": m["difficulty"],
            "elevation_m": m["elevation_m"],
            "world_heritage": bool(m.get("world_heritage")),
            "site_id": m.get("site_id"),
            "name_zh": m["name_zh"],
            "name_en": m["name_en"],
            "name_local": "",
            "province_zh": m["province_zh"],
            "province_en": "",
            "province_iso": iso,
            "country": "CN",
            "country_zh": "中国",
            "country_en": "China",
            "category": "mountain",
            "category_zh": "名山",
            "category_en": "Mountain",
            "lat": lat,
            "lon": lon,
            "images": images[:1],
            "admission": admission,
            "admission_note_zh": (site or {}).get("admission_note_zh", ""),
            "admission_checked_at": (site or {}).get("admission_checked_at", ""),
            "intro_zh": m.get("intro_zh") or (site or {}).get("intro_zh") or "",
            "intro_en": m.get("intro_en") or (site or {}).get("intro_en") or "",
            "tip_zh": m.get("tip_zh") or "",
            "address_zh": (site or {}).get("address_zh", ""),
            "address_en": (site or {}).get("address_en", ""),
            "transport": (site or {}).get("transport") or {},
            "sources": [
                {"name": "《此生必爬的31座名山》说明文档", "url": ""},
                *((site or {}).get("sources") or []),
            ],
            "updated_at": now_iso(),
        }
        save_json(out_dir / f"{m['id']}.json", record)
        index.append({
            k: record[k]
            for k in (
                "id", "dataset", "mountain_rank", "mountain_group", "difficulty",
                "elevation_m", "world_heritage", "site_id", "name_zh", "name_en",
                "province_zh", "province_iso", "lat", "lon", "images", "admission", "tip_zh",
            )
        })

    save_json(SITE_DATA / "mountains-index.json", {
        "generated_at": now_iso(),
        "count": len(index),
        "title_zh": src.get("title_zh"),
        "title_en": src.get("title_en"),
        "sites": index,
    })
    print(f"mountains: {len(index)} (linked to 5A: {sum(1 for i in index if i.get('site_id'))})")
    if missing:
        print("warning: linked site ids not found:", missing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
