#!/usr/bin/env python3
"""Fetch the official national 5A scenic-area list from the Ministry of Culture
and Tourism public service platform.

The platform exposes a paginated JSON endpoint behind
https://lyfw.mct.gov.cn/site/special/home.  It currently returns 359 records
with coordinates, official address, introduction, website and booking links.

Output: data/raw/china_official.json
"""
from __future__ import annotations

import sys
import time

from common import DATA, RAW, UA, get_json, now_iso, pinyin_slug, save_json

API = "https://lyfw.mct.gov.cn/api/marker/list"

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


def clean(row: dict) -> dict:
    name = (row.get("name") or "").strip()
    province = (row.get("province_name") or "").strip()
    city = (row.get("city_name") or "").strip()
    picture = (row.get("picture") or [None])[0]
    return {
        "id": str(row.get("id")),
        "name": name,
        "slug": pinyin_slug(name),
        "lon": round(float(row.get("longitude") or 0), 6),
        "lat": round(float(row.get("latitude") or 0), 6),
        "address": (row.get("address") or "").strip(),
        "intro": (row.get("introduce") or "").strip(),
        "web": (row.get("web_link_url") or "").strip(),
        "booking": (row.get("appointment_link_url") or "").strip(),
        "province": province,
        "province_full": PROVINCE_FULL.get(province, province),
        "city": city,
        "picture": picture,
        "province_code": row.get("province"),
        "city_code": row.get("city"),
    }


def main() -> int:
    first = get_json(API, params={"type_id": 1, "page": 1, "pageSize": 20}, timeout=50, retries=5)
    if not first or "data" not in first:
        print("MCT API unavailable; keeping previous snapshot", file=sys.stderr)
        return 1
    last = int(first["data"].get("last_page") or 1)
    rows = list(first["data"].get("list") or [])
    for page in range(2, last + 1):
        payload = get_json(API, params={"type_id": 1, "page": page, "pageSize": 20}, timeout=50, retries=5)
        if not payload or "data" not in payload:
            print(f"MCT page {page} failed; keeping previous snapshot", file=sys.stderr)
            return 1
        rows.extend(payload["data"].get("list") or [])
        time.sleep(0.35)

    sites = [clean(row) for row in rows if row.get("name")]
    # Stable unique slugs across refreshes.
    used: dict[str, int] = {}
    for s in sites:
        used[s["slug"]] = used.get(s["slug"], 0) + 1
    for s in sites:
        if used[s["slug"]] > 1:
            s["slug"] = f"{s['slug']}-{s['id']}"

    out = {
        "source": "https://lyfw.mct.gov.cn/site/special/home",
        "source_name": "文化和旅游部大众旅游服务栏目 / MCT public tourism service",
        "fetched_at": now_iso(),
        "count": len(sites),
        "sites": sites,
    }
    save_json(RAW / "china_official.json", out)
    save_json(DATA / "official.json", out)  # backward-compatible alias
    print(f"saved {len(sites)} China 5A sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
