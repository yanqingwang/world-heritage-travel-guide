#!/usr/bin/env python3
"""Merge the UNESCO dataset into the public JSON model.

Output: data/world.json

Tiering:
  * top 300 overseas sites by Wikipedia interest: full record, including
    hotels (<=50 km), ferry terminals, railway stations and up to 5 images.
  * every other overseas site: basic record with official multilingual text,
    nearest airports and Beijing distance, but no hotel list.
"""
from __future__ import annotations

import math
import os
import sys
import urllib.parse

from common import (
    CACHE, DATA, RAW, commons_category, commons_file, commons_search, load_json,
    now_iso, save_json, strip_html, translate,
)
from transport import distance_from_beijing, nearest

CATEGORY_ZH = {"Cultural": "文化遗产", "Natural": "自然遗产", "Mixed": "混合遗产"}
CATEGORY_EN = {"Cultural": "Cultural", "Natural": "Natural", "Mixed": "Mixed"}
LANG_NAME_EN = {
    "fr": "French", "es": "Spanish", "de": "German", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "ar": "Arabic", "ja": "Japanese",
    "ko": "Korean", "th": "Thai", "tr": "Turkish", "vi": "Vietnamese",
    "id": "Indonesian", "nl": "Dutch", "pl": "Polish", "sv": "Swedish",
    "da": "Danish", "no": "Norwegian", "fi": "Finnish", "cs": "Czech",
    "hu": "Hungarian", "ro": "Romanian", "el": "Greek", "he": "Hebrew",
    "fa": "Persian", "uk": "Ukrainian", "sr": "Serbian", "hr": "Croatian",
    "bg": "Bulgarian", "sk": "Slovak", "sl": "Slovenian", "lt": "Lithuanian",
    "lv": "Latvian", "et": "Estonian", "ms": "Malay", "tl": "Filipino",
    "sw": "Swahili", "af": "Afrikaans", "am": "Amharic", "ka": "Georgian",
    "hy": "Armenian", "az": "Azerbaijani", "kk": "Kazakh", "uz": "Uzbek",
    "mn": "Mongolian", "ne": "Nepali", "si": "Sinhala", "km": "Khmer",
    "lo": "Lao", "my": "Burmese", "bn": "Bengali", "ur": "Urdu", "hi": "Hindi",
    "fil": "Filipino", "mt": "Maltese", "cy": "Welsh", "ga": "Irish",
    "ta": "Tamil", "sq": "Albanian", "is": "Icelandic", "tk": "Turkmen",
    "tg": "Tajik", "ha": "Hausa", "mos": "Mossi", "la": "Latin",
    "bm": "Bambara", "st": "Sesotho", "ca": "Catalan", "ny": "Chichewa",
    "ky": "Kyrgyz", "jam": "Jamaican Patois", "nb": "Norwegian Bokmål",
    "nn": "Norwegian Nynorsk", "oc": "Occitan", "be": "Belarusian",
    "bs": "Bosnian", "mk": "Macedonian", "ps": "Pashto", "sd": "Sindhi",
    "te": "Telugu", "ml": "Malayalam", "kn": "Kannada", "mr": "Marathi",
    "gu": "Gujarati", "pa": "Punjabi", "bo": "Tibetan", "dz": "Dzongkha",
    "ug": "Uyghur", "za": "Zhuang", "yue": "Cantonese",
}


def pct_center(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if not points:
        return None
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def image_from_p18(filename: str) -> dict | None:
    if not filename:
        return None
    filename = urllib.parse.unquote(filename)
    quoted = urllib.parse.quote(filename)
    return {
        "url": f"https://commons.wikimedia.org/wiki/Special:FilePath/{quoted}?width=1280",
        "title": filename,
        "author": "",
        "license": "see Wikimedia Commons file page",
        "source": f"https://commons.wikimedia.org/wiki/File:{quoted}",
        "provider": "wikimedia_commons",
    }


# Curated Chinese names for properties whose Wikidata item / Wikipedia langlinks
# do not carry a zh label (often because UNESCO's Wikidata id points at a
# sub-entity such as a park rather than the property itself).  These are the
# names used by the Chinese Wikipedia / UNESCO zh edition where one exists.
NAME_ZH_FIX = {
    "32": "维利奇卡和博赫尼亚皇家盐矿",
    "33": "比亚沃维耶扎原始森林",
    "203": "萨兰莱班大盐场与阿尔克-塞南皇家盐场",
    "247": "拉贾斯坦邦的山地堡垒",
    "383": "塞维利亚大教堂、城堡和西印度群岛档案馆",
    "422": "英格兰湖区",
    "495": "斯特拉斯堡大岛和新城区",
    "710": "格拉蒂修道院",
    "766": "中锡霍特-阿林",
    "1060": "肯尼亚裂谷湖泊系统",
    "1061": "卡拉克穆尔古玛雅城与坎佩切热带森林保护区",
    "1100": "里约热内卢：山与海之间的卡里奥克景观",
    "1102": "萨里亚尔卡——哈萨克斯坦北部的草原和湖泊",
    "1194": "巴厘岛文化景观：苏巴克体系",
    "1225": "洛罗佩尼遗址",
    "1231": "米吉肯达卡亚圣林",
    "1237": "多洛米蒂山",
    "1245": "圣马力诺历史中心和蒂塔诺山",
    "1268": "阿加德兹历史中心",
    "1270": "卡马圭历史中心",
    "1274": "圣米格尔保护镇和耶稣纳萨雷诺阿托托尼尔科圣殿",
    "1278": "开城历史古迹",
    "1280": "罗伊·马达酋长的领地",
    "1287": "曼托瓦和萨比奥内塔",
    "1302": "拉绍德封/勒洛克勒，钟表制造城镇规划",
    "1314": "瓦登海",
    "1321": "勒·柯布西耶的建筑作品",
    "1322": "大巴萨姆历史古镇",
    "1364": "采珠业，岛屿经济的见证",
    "1380": "桑加三国保护区",
    "1386": "洛克群岛南部泻湖",
    "1387": "科英布拉大学—阿尔塔和索菲亚",
    "1403": "哈米吉坦山野生动物保护区",
    "1410": "皮纳卡特和格兰德沙漠阿尔塔生物圈保护区",
    "1412": "红湾巴斯克捕鲸站",
    "1427": "埃特纳火山",
    "1452": "布尔萨和居马勒克兹克：奥斯曼帝国的诞生",
    "1453": "迪基斯前哥伦布时期酋长聚落与石球",
    "1457": "帕加马及其多层文化景观",
    "1492": "巴勒斯坦：橄榄和葡萄之乡——南耶路撒冷巴蒂尔文化景观",
    "1499": "安提瓜海军船坞及相关考古遗址",
    "1500": "戈勒姆洞穴群",
    "1504": "斯特茨中世纪墓碑墓地",
    "1529": "塔普塔普阿泰",
    "1544": "亚兹德历史城",
    "1550": "阿斯马拉：现代主义非洲城市",
    "1608": "罗马帝国边界——多瑙河界墙（西段）",
    "1715": "格丁尼亚现代主义市中心",
    "1774": "亚马孙剧院",
    # Wikidata zh labels that were Traditional Chinese or literal mistranslations.
    "498": "苏塞老城",
    "951": "峰牙-己榜国家公园",
    "1252": "塔吉克国家公园（帕米尔山脉）",
    "1269": "卡拉尔-苏佩圣城",
    "1273": "斯洛伐克喀尔巴阡山区木教堂",
    "1282": "海尔辛兰装饰农舍",
    "1315": "舒什塔尔历史水力系统",
    "1361": "吉达历史古城（通往麦加之门）",
    "1369": "宁格罗海岸",
    "1370": "马雷沙和贝特古夫林洞穴",
    "1396": "玲珑谷考古遗产",
    "1406": "大喜马拉雅山脉国家公园保护区",
    "1413": "威廉高地公园",
    "1418": "富士山——信仰之对象与艺术之源",
    "1424": "喀尔巴阡地区木教堂（波兰和乌克兰）",
    "1435": "波弗蒂角纪念土丘",
    "1437": "埃尔比勒城堡",
    "1447": "科尔维修道院西部建筑",
    "1448": "达乌里亚景观",
    "1449": "富冈制丝厂及相关遗址",
    "1472": "沙特阿拉伯哈伊勒地区岩画",
    "1513": "干城章嘉国家公园",
    "1535": "「神宿之岛」宗像·冲之岛及相关遗产群",
    "1605": "斋浦尔城",
    "1702": "拉希德·卡拉米国际博览会（的黎波里）",
}

INTRO_ZH_FIX = {
    "1809": "塞巴斯蒂亚是巴勒斯坦纳布卢斯省的一个村庄，位于纳布卢斯西北约 12 公里，被视为约旦河西岸最古老的持续有人居住地之一。公元前 9 世纪，这里被称为撒马利亚，曾是北以色列王国的都城；罗马时期由希律大帝扩建并改名为塞巴斯蒂亚。基督教和伊斯兰教传统均将这里视为施洗者约翰的埋葬地。",
}

OFFLINE = os.environ.get("OFFLINE") == "1"


def world_images(site: dict, rec: dict, tier: str, cache_file) -> list[dict]:
    cached = load_json(cache_file)
    if cached:
        return cached
    if cached is not None:
        # An empty list is a deliberate "no Commons image found" marker; do not
        # re-query Commons on every weekly run for sites that have none.
        return []
    images = []
    p18 = image_from_p18(rec.get("image", ""))
    if p18:
        images.append(p18)
    if tier == "full" and not OFFLINE:
        cat = rec.get("commons_category")
        if cat:
            images.extend(commons_category(cat, 8))
        else:
            name = site.get("name", {}).get("en", "")
            country = rec.get("country_en", "")
            images.extend(commons_search(f"{name} {country}", 6))
    deduped, seen = [], set()
    for img in images:
        if img.get("url") and img["url"] not in seen:
            seen.add(img["url"])
            deduped.append(img)
    if len(deduped) < 5 and site.get("image_url"):
        unesco_img = {
            "url": site["image_url"],
            "title": site.get("name", {}).get("en", ""),
            "author": "UNESCO World Heritage Centre",
            "license": "UNESCO / linked thumbnail",
            "source": site.get("http_url", ""),
            "provider": "unesco",
        }
        if unesco_img["url"] not in seen:
            deduped.append(unesco_img)
    # Cache full-tier results too — including the empty list when Commons has
    # nothing — so a hung/blocked Commons request never wedges the weekly job
    # the way repeated un-cached retries did.
    save_json(cache_file, deduped[:5])
    return deduped[:5]


def main() -> int:
    unesco = load_json(RAW / "unesco_sites.json", {}) or {}
    wd = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
    wiki = (load_json(RAW / "unesco_wiki.json", {}) or {}).get("items", {})
    rank = (load_json(RAW / "unesco_rank.json", {}) or {}).get("items", {})
    visa = (load_json(RAW / "visa.json", {}) or {}).get("countries", {})
    countries = load_json(RAW / "countries.json", {}) or {}
    geocode = load_json(RAW / "unesco_geocode.json", {}) or {}
    subdivisions = (load_json(RAW / "unesco_subdivisions.json", {}) or {}).get("items", {})
    previous = {s["id"]: s for s in (load_json(DATA / "world.json", {}) or {}).get("sites", [])}
    sites = unesco.get("sites", [])

    # Country centroids for the handful of sites without Wikidata coordinates.
    by_country: dict[str, list[tuple[float, float]]] = {}
    for site in sites:
        rec = wd.get(site["id"]) or {}
        if rec.get("lat") is not None and site.get("iso"):
            by_country.setdefault(site["iso"][0], []).append((rec["lat"], rec["lon"]))
    centroids = {iso: pct_center(pts) for iso, pts in by_country.items()}

    out = []
    for i, site in enumerate(sites, 1):
        iso = site.get("iso") or []
        if iso and set(iso) <= {"cn"}:
            continue  # China is covered by the 5A dataset
        sid = site["id"]
        prev_site = previous.get(f"wh-{sid}", {})
        rec = wd.get(sid) or {}
        w = wiki.get(sid) or {}
        sub = subdivisions.get(sid) or {}
        rank_rec = rank.get(sid) or {}
        tier = rank_rec.get("tier") or prev_site.get("tier") or "basic"
        primary = iso[0] if iso else ""
        country = countries.get(primary.upper(), {})
        country_en = country.get("en", primary)
        country_zh = country.get("zh") or country_en
        if not primary:
            # UNESCO lists Jerusalem separately and does not name a state party.
            primary = "XJ"
            country_en = "Jerusalem (proposed by Jordan)"
            country_zh = "耶路撒冷（约旦提名）"
        lat, lon = rec.get("lat"), rec.get("lon")
        coord_accuracy = "site"
        geo = geocode.get(sid) or {}
        if lat is None and geo.get("lat") is not None:
            lat, lon = geo["lat"], geo["lon"]
            coord_accuracy = geo.get("source") or "wikidata_search"
        if lat is None and primary in centroids:
            lat, lon = centroids[primary]
            coord_accuracy = "country_centroid"

        name_en = strip_html(site.get("name", {}).get("en", ""))
        name_zh_raw = site.get("name", {}).get("zh")
        name_zh = strip_html(name_zh_raw) or strip_html(w.get("name_zh")) or rec.get("label_zh")
        name_zh_source = "unesco_official" if name_zh_raw else (
            "wikipedia" if w.get("name_zh") else ("wikidata" if rec.get("label_zh") else None)
        )
        if sid in NAME_ZH_FIX:
            name_zh = NAME_ZH_FIX[sid]
            name_zh_source = "curated"
        if not name_zh and name_en and not OFFLINE:
            name_zh = translate(name_en, "zh")
            name_zh_source = "machine_translation" if name_zh else None
        if not name_zh and prev_site.get("name_zh"):
            name_zh = prev_site["name_zh"]
            name_zh_source = prev_site.get("name_zh_source")

        intro_en_raw = site.get("description", {}).get("en")
        intro_en = strip_html(intro_en_raw) or w.get("intro_en") or ""
        intro_en_source = "unesco_official" if intro_en_raw else (
            "wikipedia" if w.get("intro_en") else None
        )
        if not intro_en and prev_site.get("intro_en"):
            intro_en = prev_site["intro_en"]
            intro_en_source = prev_site.get("intro_en_source")
        intro_zh_raw = site.get("description", {}).get("zh")
        intro_zh = strip_html(intro_zh_raw) or w.get("intro_zh") or ""
        intro_zh_source = w.get("zh_source") or (
            "unesco_official" if intro_zh_raw else None
        )
        if not intro_zh and sid in INTRO_ZH_FIX:
            intro_zh = INTRO_ZH_FIX[sid]
            intro_zh_source = "curated"
        if not intro_zh and prev_site.get("intro_zh"):
            intro_zh = prev_site["intro_zh"]
            intro_zh_source = prev_site.get("intro_zh_source")

        local_lang = w.get("local_lang") or prev_site.get("local_lang")
        local_lang_name = LANG_NAME_EN.get(local_lang or "", local_lang or "") or prev_site.get("local_lang_name")
        name_local = strip_html(w.get("name_local")) or prev_site.get("name_local")
        intro_local = strip_html(w.get("intro_local")) or prev_site.get("intro_local")
        local_source = w.get("local_source") or prev_site.get("intro_local_source")

        airports = (nearest(lat, lon, limit=3, max_km=400) if lat is not None else []) or \
            (prev_site.get("transport") or {}).get("airports", [])
        if not airports and lat is not None:
            # Remote islands/deserts: the nearest scheduled airport may be far,
            # but it is still the realistic gateway for planning.
            airports = nearest(lat, lon, limit=2, max_km=6000)
        distance_km, _ = distance_from_beijing(lat, lon) if lat is not None else (None, None)
        if distance_km is None:
            distance_km = (prev_site.get("transport") or {}).get("distance_beijing_km")
        osm = load_json(RAW / "osm" / f"world_{sid}.json", {}) or {}
        hotels = (osm.get("hotels", [])[:5] if tier == "full" else []) or (prev_site.get("hotels", []) if tier == "full" else [])
        ferry = (osm.get("ferry_terminals", [])[:5] if tier == "full" else []) or \
            ((prev_site.get("transport") or {}).get("ferry_terminals", []) if tier == "full" else [])
        stations = (osm.get("stations", [])[:5] if tier == "full" else []) or \
            ((prev_site.get("transport") or {}).get("railway_stations", []) if tier == "full" else [])

        visas = []
        for code in iso:
            v = visa.get(code.upper())
            visas.append({
                "iso2": code.upper(),
                "country_zh": countries.get(code.upper(), {}).get("zh") or countries.get(code.upper(), {}).get("en", code.upper()),
                "country_en": countries.get(code.upper(), {}).get("en", code.upper()),
                "status": (v or {}).get("status", "unknown"),
                "days": (v or {}).get("days"),
                "requirement": (v or {}).get("requirement", ""),
                "notes": (v or {}).get("notes", ""),
            })
        if all(v["status"] == "unknown" for v in visas) and prev_site.get("visa_by_country"):
            visas = prev_site["visa_by_country"]
        statuses = {v["status"] for v in visas if v["status"] != "unknown"}
        visa_summary = statuses.pop() if len(statuses) == 1 else ("mixed" if statuses else "unknown")

        official_editions = [lang for lang in ("en", "zh", "fr", "es", "ru", "ar")
                             if site.get("description", {}).get(lang)]
        sitelinks = w.get("sitelinks", {})
        info_languages = {
            "zh": bool(site.get("description", {}).get("zh") or sitelinks.get("zh")),
            "en": bool(site.get("description", {}).get("en") or sitelinks.get("en")),
            "ja": bool(sitelinks.get("ja")),
            "ko": bool(sitelinks.get("ko")),
            "local": bool(local_lang and (intro_local or name_local)),
            "local_lang": local_lang,
            "local_lang_name": local_lang_name,
            "official_unesco": official_editions,
            "wikipedia_editions": len(sitelinks),
        }
        if not sitelinks and prev_site.get("info_languages"):
            info_languages = prev_site["info_languages"]

        cat = site.get("category", "")
        sub_iso = (sub.get("iso") or "").upper()
        # Transnational sites can resolve to a subdivision in the partner
        # country; only keep a code that belongs to the primary country,
        # otherwise the country -> subdivision cascade would leak.
        sub_ok = bool(sub_iso) and sub_iso.startswith(f"{primary.upper()}-")
        images = world_images(
            {**site, "country_en": country_en}, {**rec, "country_en": country_en},
            tier, RAW / "world_images" / f"{sid}_{tier}.json",
        ) or prev_site.get("images", [])

        out.append({
            "id": f"wh-{sid}",
            "unesco_id": sid,
            "dataset": "unesco",
            "tier": tier,
            "popularity_rank": rank_rec.get("rank") or prev_site.get("popularity_rank"),
            "popularity_score": rank_rec.get("score") or prev_site.get("popularity_score"),
            "country": primary.upper(),
            "country_zh": country_zh,
            "country_en": country_en,
            "countries": [
                {"iso2": c.upper(),
                 "zh": countries.get(c.upper(), {}).get("zh") or countries.get(c.upper(), {}).get("en", c.upper()),
                 "en": countries.get(c.upper(), {}).get("en", c.upper())}
                for c in iso
            ],
            "region": strip_html(site.get("location", "")),
            "subdivision_iso": sub_iso if sub_ok else "",
            "subdivision_zh": (sub.get("name_zh") or "") if sub_ok else "",
            "subdivision_en": (sub.get("name_en") or "") if sub_ok else "",
            "subdivision_source": (sub.get("source") or "") if sub_ok else "",
            "name_zh": name_zh or "",
            "name_zh_source": name_zh_source,
            "name_en": name_en,
            "name_local": name_local or "",
            "local_lang": local_lang,
            "local_lang_name": local_lang_name,
            "slug": f"{sid}-{'_'.join((name_en or sid).lower().split())[:40]}",
            "lat": lat,
            "lon": lon,
            "coord_accuracy": coord_accuracy,
            "category": cat,
            "category_zh": CATEGORY_ZH.get(cat, cat),
            "category_en": CATEGORY_EN.get(cat, cat),
            "criteria": site.get("criteria", ""),
            "year": site.get("year", ""),
            "danger": site.get("danger", False),
            "transnational": site.get("transnational", False),
            "intro_zh": intro_zh[:1400],
            "intro_zh_source": intro_zh_source,
            "intro_en": intro_en[:1400],
            "intro_en_source": intro_en_source,
            "intro_local": (intro_local or "")[:1400],
            "intro_local_source": local_source,
            "images": images,
            "unesco_url": site.get("http_url", ""),
            "transport": {
                "airports": airports,
                "nearest_airport_km": airports[0]["distance_km"] if airports else None,
                "distance_beijing_km": distance_km,
                "ferry_terminals": ferry,
                "railway_stations": stations,
            },
            "hotels": hotels,
            "visa": visas[0] if visas else {"status": "unknown"},
            "visa_by_country": visas,
            "visa_summary": visa_summary,
            "info_languages": info_languages,
            "sources": [
                {"name": "UNESCO World Heritage Centre", "url": site.get("http_url", "")},
                {"name": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(w.get('sitelinks', {}).get('en', ''))}"} if sitelinks.get("en") else {"name": "Wikidata", "url": f"https://www.wikidata.org/wiki/{w.get('item')}"},
                {"name": "OpenStreetMap", "url": "https://www.openstreetmap.org/"},
                {"name": "OurAirports", "url": "https://ourairports.com/data/"},
            ],
            "updated_at": now_iso(),
        })
        if i % 100 == 0:
            print(f"World build {i}/{len(sites)}")

    save_json(DATA / "world.json", {
        "generated_at": now_iso(),
        "count": len(out),
        "full_tier": sum(1 for x in out if x["tier"] == "full"),
        "sources": ["UNESCO WHC XML (en/zh/fr/es/ru/ar)", "Wikidata", "Wikipedia",
                    "Wikimedia Commons", "OpenStreetMap", "OurAirports", "Wikipedia visa table"],
        "sites": out,
    })
    print(f"saved {len(out)} overseas sites ({sum(1 for x in out if x['tier']=='full')} full tier)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
