#!/usr/bin/env python3
"""Copy generated data into the static site and write Markdown entries.

The HTML app is deliberately dependency-free and is served directly by GitHub
Pages.  Markdown mirrors of every record live under entries/ for people who
prefer plain text or want to diff a single destination.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from common import DATA, ENTRIES, SITE, load_json, now_iso, save_json

SITE_DATA = SITE / "data"


def clean_slug(value: str, fallback: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value or "").strip("-").lower()
    return value or fallback


def yaml_value(value) -> str:
    """Quote frontmatter strings so colons, # and quotes cannot break YAML."""
    if value is None or value == "":
        return '""'
    return json.dumps(value, ensure_ascii=False)


def credit(img: dict) -> str:
    bits = [img.get("title"), img.get("author"), img.get("license")]
    return " · ".join([b for b in bits if b])


def markdown(site: dict) -> str:
    name_zh = site.get("name_zh") or ""
    name_en = site.get("name_en") or ""
    title = " / ".join([x for x in (name_zh, name_en) if x])
    where = ""
    if site.get("dataset") == "china_5a":
        where = " · ".join([x for x in (site.get("province_zh"), site.get("city_zh"), site.get("category_zh")) if x])
    else:
        where = " · ".join([x for x in (site.get("country_zh"), site.get("region"), site.get("category_zh")) if x])

    fm = [
        "---",
        f"id: {yaml_value(site.get('id'))}",
        f"dataset: {yaml_value(site.get('dataset'))}",
        f"name_zh: {yaml_value(name_zh)}",
        f"name_en: {yaml_value(name_en)}",
        f"name_local: {yaml_value(site.get('name_local') or '')}",
        f"country: {yaml_value(site.get('country'))}",
        f"country_zh: {yaml_value(site.get('country_zh') or '')}",
        f"country_en: {yaml_value(site.get('country_en') or '')}",
    ]
    if site.get("dataset") == "china_5a":
        fm += [f"province_zh: {yaml_value(site.get('province_zh'))}", f"city_zh: {yaml_value(site.get('city_zh'))}",
               f"province_en: {yaml_value(site.get('province_en'))}", f"city_en: {yaml_value(site.get('city_en'))}"]
    else:
        fm += [f"unesco_id: {yaml_value(site.get('unesco_id'))}", f"tier: {yaml_value(site.get('tier'))}",
               f"category: {yaml_value(site.get('category'))}", f"year: {yaml_value(site.get('year'))}",
               f"criteria: {yaml_value(site.get('criteria'))}"]
    fm += [
        f"lat: {json.dumps(site.get('lat'))}",
        f"lon: {json.dumps(site.get('lon'))}",
        f"updated_at: {yaml_value(site.get('updated_at'))}",
        "---",
    ]
    lines = ["\n".join(fm), "", f"# {title}", "", f"> {where}", ""]

    if site.get("images"):
        lines.append("## 图片 / Images")
        lines.append("")
        for img in site["images"][:5]:
            lines.append(f"![{img.get('title') or title}]({img.get('url')})")
            lines.append("")
            lines.append(f"*{credit(img)}*")
            lines.append("")

    lines += ["## 简介 / Introduction", "", "### 中文", "", site.get("intro_zh") or "—", "",
              "### English", "", site.get("intro_en") or "—", ""]
    if site.get("intro_en_source") == "machine_translation":
        lines += ["*English introduction: machine translation.*", ""]
    if site.get("intro_zh_source") == "machine_translation":
        lines += ["*中文简介：机器翻译。*", ""]

    if site.get("intro_local"):
        lang = site.get("local_lang_name") or site.get("local_lang") or ""
        lines += [f"## 本地语言 / Local language ({lang})", "", f"**{site.get('name_local') or ''}**", "",
                  site.get("intro_local") or "—", ""]

    tr = site.get("transport") or {}
    lines += ["## 交通 / Transport", ""]
    for ap in tr.get("airports") or []:
        lines.append(f"- ✈ **{ap.get('name')} ({ap.get('iata') or ''})** — {ap.get('distance_km')} km")
    for st in tr.get("high_speed_stations") or []:
        lines.append(f"- 🚄 **{st.get('name')}** — {st.get('distance_km')} km")
    for st in tr.get("railway_stations") or []:
        lines.append(f"- 🚉 **{st.get('name')}** — {st.get('distance_km')} km")
    for f in tr.get("ferry_terminals") or []:
        lines.append(f"- ⛴ **{f.get('name')}** — {f.get('distance_km')} km")
    if tr.get("distance_beijing_km") is not None:
        lines.append(f"- ✈ 距北京直线距离 / great-circle from Beijing: **{tr['distance_beijing_km']} km**")
    if not any(tr.get(k) for k in ("airports", "high_speed_stations", "railway_stations", "ferry_terminals")):
        lines.append("- —")
    lines.append("")

    if site.get("dataset") == "china_5a" or site.get("tier") == "full":
        lines += ["## 附近酒店 / Nearby hotels", ""]
        if site.get("hotels"):
            for h in site["hotels"]:
                extra = " · ".join([x for x in (h.get("name_en"), f"{h.get('stars')}★" if h.get("stars") else "", h.get("brand")) if x])
                lines.append(f"- **{h.get('name')}** — {h.get('distance_km')} km — {h.get('kind')}" + (f" — {extra}" if extra else ""))
        else:
            lines.append("- 暂无 / none")
        lines += ["", "*来源：OpenStreetMap；星级与连锁信息可能不完整。*", ""]

    if site.get("dataset") != "china_5a":
        v = site.get("visa") or {}
        lines += ["## 签证（中国护照） / Visa (Chinese passport)", "",
                  f"**{v.get('status', 'unknown')}**" + (f" · {v.get('days')} days" if v.get("days") else ""), "",
                  f"{v.get('requirement') or ''} {v.get('notes') or ''}".strip() or "—", "",
                  "*签证政策会变化，出行前请核实。*", ""]

    il = site.get("info_languages") or {}
    langs = ", ".join(k for k in ("zh", "en", "ja", "ko", "local") if il.get(k))
    lines += ["## 多语言信息 / Language availability", "", f"- 可用语言 / Available: {langs or '—'}", ""]
    if il.get("official_unesco"):
        lines += [f"- UNESCO 官方文本 / official editions: {', '.join(il['official_unesco'])}", ""]

    lines += ["## 来源 / Sources", ""]
    for s in site.get("sources") or []:
        if s.get("url"):
            lines.append(f"- [{s.get('name')}]({s.get('url')})")
    lines.append("")
    return "\n".join(lines)


def write_entries(sites: list[dict], folder: str) -> int:
    out_dir = ENTRIES / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    used = set()
    count = 0
    for site in sites:
        base = clean_slug(site.get("slug") or site.get("id"), site.get("id", "site"))
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        (out_dir / f"{slug}.md").write_text(markdown(site), encoding="utf-8")
        count += 1
    return count


def index_record(site: dict) -> dict:
    """Card/filter fields only: keeps the first screen payload small.

    The deployed world payload used to be ~7.8 MB, which times out on slow
    connections.  The list view only needs a handful of fields; the rest is
    fetched per site when a card is opened.
    """
    tr = site.get("transport") or {}
    images = site.get("images") or []
    first_image = images[0] if images else None
    if site.get("dataset") == "china_5a":
        transport = {
            "high_speed_stations": (tr.get("high_speed_stations") or [])[:1],
            "airports": (tr.get("airports") or [])[:1],
            "nearest_airport_km": tr.get("nearest_airport_km"),
        }
    else:
        transport = {
            "distance_beijing_km": tr.get("distance_beijing_km"),
        }
    rec = {
        "id": site.get("id"),
        "dataset": site.get("dataset"),
        "tier": site.get("tier"),
        "name_zh": site.get("name_zh") or "",
        "name_en": site.get("name_en") or "",
        "name_local": site.get("name_local") or "",
        "country": site.get("country") or "",
        "country_zh": site.get("country_zh") or "",
        "country_en": site.get("country_en") or "",
        "region": site.get("region") or "",
        "category": site.get("category") or "",
        "category_zh": site.get("category_zh") or "",
        "category_en": site.get("category_en") or "",
        "year": site.get("year") or "",
        "lat": site.get("lat"),
        "lon": site.get("lon"),
        "images": [first_image] if first_image else [],
        "transport": transport,
        "popularity_rank": site.get("popularity_rank"),
        "visa_summary": site.get("visa_summary"),
    }
    if site.get("dataset") == "china_5a":
        rec.update({
            "province_zh": site.get("province_zh") or "",
            "province_en": site.get("province_en") or "",
            "province_iso": site.get("province_iso") or "",
            "city_zh": site.get("city_zh") or "",
            "city_en": site.get("city_en") or "",
        })
    else:
        rec.update({
            "subdivision_iso": site.get("subdivision_iso") or "",
            "subdivision_zh": site.get("subdivision_zh") or "",
            "subdivision_en": site.get("subdivision_en") or "",
        })
    return rec


def write_dataset(doc: dict, folder: str) -> int:
    """Write a compact index plus one JSON file per record."""
    sites = doc.get("sites") or []
    out_dir = SITE_DATA / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    for site in sites:
        save_json(out_dir / f"{site.get('id')}.json", site)
    index = {
        "generated_at": doc.get("generated_at"),
        "count": doc.get("count", len(sites)),
        "full_tier": doc.get("full_tier"),
        "unesco_lang_count": len({
            lang
            for s in sites
            for lang in ((s.get("info_languages") or {}).get("official_unesco") or [])
        }),
        "sites": [index_record(s) for s in sites],
    }
    save_json(SITE_DATA / f"{folder}-index.json", index)
    return len(sites)


def main() -> int:
    china = load_json(DATA / "china.json", {}) or {"count": 0, "sites": []}
    world = load_json(DATA / "world.json", {}) or {"count": 0, "sites": []}
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    # Canonical machine-readable files stay at the repo root (data/*.json); the
    # site only ships the compact index + per-record details.
    save_json(SITE_DATA / "meta.json", {
        "generated_at": now_iso(),
        "china_count": china.get("count", 0),
        "world_count": world.get("count", 0),
        "full_tier": world.get("full_tier", 0),
        "sources": ["MCT", "UNESCO", "Wikipedia", "Wikidata", "Wikimedia Commons", "OpenStreetMap", "OurAirports"],
    })
    write_dataset(china, "china")
    write_dataset(world, "world")
    # Older builds shipped the full 7.8 MB world.json to Pages; drop it so the
    # deploy artifact stays small.
    for stale in ("china.json", "world.json"):
        p = SITE_DATA / stale
        if p.exists():
            p.unlink()
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    cn = write_entries(china.get("sites", []), "cn")
    wh = write_entries(world.get("sites", []), "world")
    (ENTRIES / "README.md").write_text(
        "# Markdown entries\n\n"
        f"- `cn/` — {cn} China 5A records\n"
        f"- `world/` — {wh} UNESCO records (full + basic tiers)\n\n"
        "The canonical machine-readable data is `data/china.json` and "
        "`data/world.json`; the HTML app is in `site/`.\n",
        encoding="utf-8",
    )
    print(f"site data written; {cn} China + {wh} world markdown entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
