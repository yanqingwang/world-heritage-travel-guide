#!/usr/bin/env python3
"""Fetch the official national 5A scenic-area list from the Ministry of Culture
and Tourism public service platform.

The platform exposes a paginated JSON endpoint behind
https://lyfw.mct.gov.cn/site/special/home.  It returns 359 records (as of the
2026-11 refresh) with coordinates, official address, introduction, website and
booking links.  The raw weather payload is dropped.

Output: data/official.json
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests
from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

API = "https://lyfw.mct.gov.cn/api/marker/list"
UA = "china-5a-scenic-guide/1.0 (+https://github.com/yanqingwang/china-5a-scenic-guide)"
PROVINCE_FULL = {
    "北京": "北京市", "天津": "天津市", "河北": "河北省", "山西": "山西省",
    "内蒙古": "内蒙古自治区", "辽宁": "辽宁省", "吉林": "吉林省",
    "黑龙江": "黑龙江省", "上海": "上海市", "江苏": "江苏省", "浙江": "浙江省",
    "安徽": "安徽省", "福建": "福建省", "江西": "江西省", "山东": "山东省",
    "河南": "河南省", "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省",
    "广西": "广西壮族自治区", "海南": "海南省", "重庆": "重庆市",
    "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "西藏": "西藏自治区",
    "陕西": "陕西省", "甘肃": "甘肃省", "青海": "青海省", "宁夏": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区",
}


def slugify(name: str) -> str:
    name = re.sub(r"[（）()·、，,。.\s]", "", name)
    name = re.sub("(旅游景区|旅游度假区|文化旅游区|旅游区|风景区|景区)$", "", name)
    return "".join(lazy_pinyin(name)).lower()


def clean(row: dict) -> dict:
    name = row["name"].strip()
    return {
        "id": row["id"],
        "name": name,
        "slug": slugify(name),
        "lon": round(float(row["longitude"]), 6),
        "lat": round(float(row["latitude"]), 6),
        "address": row.get("address", "").strip(),
        "intro": row.get("introduce", "").strip(),
        "web": (row.get("web_link_url") or "").strip(),
        "booking": (row.get("appointment_link_url") or "").strip(),
        "province": row.get("province_name", "").strip(),
        "province_full": PROVINCE_FULL.get(row.get("province_name", "").strip(), row.get("province_name", "")),
        "city": row.get("city_name", "").strip(),
        "picture": (row.get("picture") or [None])[0],
    }


def main() -> int:
    first = requests.get(
        API, params={"type_id": 1, "page": 1, "pageSize": 20}, headers={"User-Agent": UA}, timeout=40
    )
    first.raise_for_status()
    payload = first.json()
    last = payload["data"]["last_page"]
    rows = list(payload["data"]["list"])
    for page in range(2, last + 1):
        r = requests.get(
            API,
            params={"type_id": 1, "page": page, "pageSize": 20},
            headers={"User-Agent": UA},
            timeout=40,
        )
        r.raise_for_status()
        rows.extend(r.json()["data"]["list"])
        time.sleep(0.4)

    sites = [clean(row) for row in rows]
    # Slugs must be unique and stable across refreshes.
    seen: dict[str, int] = {}
    for s in sites:
        seen[s["slug"]] = seen.get(s["slug"], 0) + 1
    for s in sites:
        if seen[s["slug"]] > 1:
            s["slug"] = f"{s['slug']}-{s['id']}"

    out = {
        "source": "https://lyfw.mct.gov.cn/site/special/home",
        "source_name": "文化和旅游部大众旅游服务栏目 / MCT public tourism service",
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(sites),
        "sites": sites,
    }
    (DATA / "official.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {len(sites)} sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
