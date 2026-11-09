#!/usr/bin/env python3
"""Map China 5A sites and UNESCO sites to Wikipedia/Wikidata, then collect
multilingual text and Commons images.

China output:  data/raw/china_wiki.json
UNESCO output: data/raw/unesco_wiki.json

The script deliberately distinguishes official text, Wikipedia text and machine
translation.  Machine translation is only used when neither an official nor a
Wikipedia version exists, and is labelled in the output.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
from collections import defaultdict

from common import (
    CACHE, COMMONS_API, DATA, RAW, commons_file, commons_search, curl_json,
    get_json, load_json, now_iso, pinyin_slug, save_json, strip_html,
    translate, wiki_api, wiki_page, wiki_search, wiki_summary,
)

WIKI_CACHE = CACHE / "wiki"
WIKI_CACHE.mkdir(parents=True, exist_ok=True)


def cache_path(name: str):
    return WIKI_CACHE / name


def title_clean(title: str) -> str:
    return urllib.parse.unquote(title.replace("_", " "))


def similarity(query: str, title: str) -> float:
    q = re.sub(r"[^\w一-鿿]+", "", query)
    t = re.sub(r"[^\w一-鿿]+", "", title)
    if not q or not t:
        return 0.0
    if q == t:
        return 1.0
    if q in t or t in q:
        return 0.9
    # Scenic-area names carry qualifiers the article title drops ("齐齐哈尔市
    # 扎龙生态" vs "黑龙江扎龙国家级自然保护区").  Fall back to the longest
    # common contiguous CJK run so a distinctive core ("扎龙") still matches.
    best = 0
    for i in range(len(q)):
        for j in range(len(t)):
            if q[i] == t[j]:
                k = 0
                while i + k < len(q) and j + k < len(t) and q[i + k] == t[j + k]:
                    k += 1
                best = max(best, k)
    # A distinctive >=2-char CJK run ("扎龙", "双龙") outweighs fuzzy overlap:
    # score it relative to the *shorter* side so long titles don't dilute it.
    core = best / max(min(len(q), len(t), 4), 1) if best >= 2 else 0.0
    qs = {q[i:i + 2] for i in range(len(q) - 1)}
    ts = {t[i:i + 2] for i in range(len(t) - 1)}
    jaccard = len(qs & ts) / len(qs | ts) if qs and ts else 0.0
    return max(jaccard, core * 0.85 if best >= 2 else 0.0)


def is_generic_place(title: str) -> bool:
    # Pure administrative names ("金华市", "冶力关镇"). Scenic-area titles like
    # "双龙风景旅游区" end in 区 too — strip scenic suffixes before testing so
    # they are not mistaken for a city/county article.
    t = re.sub("(旅游景区|旅游度假区|文化旅游区|旅游区|风景区|景区|自然保护区)$", "", title)
    return bool(re.search(r"(市|县|区|省|自治州|地区|镇|乡|盟|州)$", t))


def choose_zh_title(site: dict, candidates: list[str]) -> str | None:
    name = re.sub("(旅游景区|旅游度假区|文化旅游区|旅游区|风景区|景区)$", "", site["name"])
    # 5A names lead with the administrative prefix ("新乡市宝泉", "甘南州冶力关");
    # the article is titled with the feature alone. Score both the full name and
    # the stripped name and take the better match per candidate, so "新乡市"
    # (a substring of the full name, 0.9) cannot beat "宝泉水库"/"河南宝泉
    # 旅游区" (a weak 0.42 against the full name but 0.9 against "宝泉").
    stripped = re.sub(r"^[一-鿿]{1,3}(市|州|县|区|盟)", "", name)
    def score(title: str) -> float:
        s = max(similarity(name, title), similarity(stripped, title))
        # A candidate that is exactly the query's administrative prefix
        # ("新乡市" in "新乡市宝泉") is the parent city, not the place — cap it
        # below the 0.62 bar so a real feature article always wins. When the
        # city is the only candidate it is still accepted by the fallback
        # (threshold 0.55) for its intro text; images handle it separately.
        if is_generic_place(title) and name.startswith(title):
            s = min(s, 0.55)  # below the 0.62 accept bar
        return s
    scored = sorted((((s, not is_generic_place(t)), t) for s, t in
                     ((score(t), t) for t in candidates)), reverse=True)
    for (score_, _non_generic), title in scored:
        if score_ >= 0.62 and not (is_generic_place(title) and not is_generic_place(name)):
            return title
    # Fallback for weak matches: prefer the best non-generic candidate even
    # below the 0.62 bar ("黑龙江扎龙国家级自然保护区" scores 0.42 against
    # "齐齐哈尔市扎龙生态"); only settle for a bare administrative name
    # ("新乡市") when nothing else is on offer — its text is still useful,
    # and image sourcing treats it separately.
    best_non_generic = next((s for s, ng, _t in
                             ((s_, ng, t_) for (s_, ng), t_ in scored if ng)), None)
    for (score_, non_generic), title in scored:
        if non_generic or is_generic_place(name):
            if score_ >= 0.4:
                return title
        elif best_non_generic is None and score_ >= 0.55:
            return title
    return None


def geosearch_titles(lat: float, lon: float) -> list[str]:
    data = wiki_api("zh", {
        "action": "query", "list": "geosearch", "gscoord": f"{lat}|{lon}",
        "gsradius": 10000, "gslimit": 12,
    })
    return [x["title"] for x in ((data or {}).get("query") or {}).get("geosearch", []) or []]


def zh_page_via_rest(title: str) -> dict | None:
    """zh Wikipedia page facts via the api.wikimedia.org REST gateway.

    The action API (*.wikipedia.org) is unreachable from some networks this
    runs on; REST gives us the qid (through the page HTML? no — through the
    /bare endpoint), langlinks and thumbnail — everything enrich needs.
    """
    key = urllib.parse.quote(title.replace(" ", "_"), safe="")
    bare = curl_json(f"https://api.wikimedia.org/core/v1/wikipedia/zh/page/{key}/bare", timeout=25)
    if not bare or bare.get("key") is None:
        return None
    langs: dict[str, str] = {}
    ll = curl_json(f"https://api.wikimedia.org/core/v1/wikipedia/zh/page/{key}/links/language",
                   timeout=25) or []
    for item in ll:
        code = item.get("lang")
        if code:
            langs[code] = item.get("title") or ""
    qid = None
    # /bare does not carry the wikidata id; pull it from the entity lookup API,
    # which is hosted on wikidata.org and usually reachable when REST is.
    wb = get_json("https://www.wikidata.org/w/api.php", params={
        "action": "wbgetentities", "sites": "zhwiki", "titles": title,
        "props": "info", "format": "json", "formatversion": 2,
    }, timeout=20, retries=1)
    try:
        qid = next(iter((wb or {}).get("entities", {})), None)
    except Exception:
        qid = None
    thumbnail = None
    summ = curl_json(f"https://api.wikimedia.org/core/v1/wikipedia/zh/page/{key}/summary",
                     timeout=25) or {}
    thumb = ((summ or {}).get("thumbnail") or {}).get("source")
    if thumb:
        thumbnail = {"source": thumb}
    return {
        "title": bare.get("title") or title,
        "pageprops": {"wikibase_item": qid} if qid else {},
        "langlinks": [{"lang": k, "*": v} for k, v in langs.items()],
        "thumbnail": thumbnail,
        "original": thumbnail,
    }


def china_site(site: dict) -> dict:
    cached = load_json(cache_path(f"cn_{site['id']}.json"))
    if cached:
        return cached

    name = site["name"]
    query = re.sub("(旅游景区|旅游度假区|文化旅游区|旅游区|风景区|景区)$", "", name)
    hits = [h["title"] for h in wiki_search("zh", query, 6)] or []
    title = choose_zh_title(site, hits)
    if not title or similarity(query, title) < 0.55:
        # Strip the administrative prefix ("甘南州", "黄冈市" …): the article is
        # usually titled with the feature alone, and REST search ranks the
        # full unprefixed name lower.
        stripped = re.sub(r"^[一-鿿]{1,3}(市|州|县|区|盟)", "", query)
        if stripped != query:
            more = [h["title"] for h in wiki_search("zh", stripped, 6)]
            title = choose_zh_title(site, hits + more) or title
    if not title or similarity(query, title) < 0.55:
        geo = geosearch_titles(site["lat"], site["lon"])
        title = choose_zh_title(site, geo) or title

    page = None
    if title:
        # REST gateway first: reliable where the action API is blocked.
        page = zh_page_via_rest(title)
        if page is None:
            page = wiki_page("zh", title, props="pageprops|langlinks|pageimages", intro=False)
    if not page:
        result = {"matched": False, "zh_title": None, "en_title": None, "langs": [],
                  "wikidata_id": None, "intro_en": None, "en_source": None, "images": []}
        save_json(cache_path(f"cn_{site['id']}.json"), result)
        return result

    langs = {ll["lang"]: (ll.get("title") or ll.get("*")) for ll in page.get("langlinks", []) or []}
    en_title = langs.get("en")
    en_page = wiki_page("en", en_title, props="extracts|pageimages") if en_title else None
    intro_en = strip_html(en_page.get("extract", "")) if en_page else None
    if not intro_en and en_title:
        # en Wikipedia action API may also be blocked; REST summary fallback.
        summ = wiki_summary("en", en_title)
        intro_en = strip_html((summ or {}).get("extract", "")) or None
    images = []
    qid = page.get("pageprops", {}).get("wikibase_item")
    if qid:
        ent = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json", retries=3)
        try:
            claims = ent["entities"][qid]["claims"]
            for c in claims.get("P18", [])[:3]:
                fn = c["mainsnak"]["datavalue"]["value"]
                img = commons_file(fn)
                if img:
                    images.append(img)
        except Exception:
            pass

    # Image search terms: the stripped scenic name beats the full official
    # name. Querying "黄山市皖南古村落-西递宏村 安徽省" pools every file tagged
    # Huangshan/Anhui (the same generic images then fill 黄山/宏村/古徽州 alike);
    # "西递宏村" hits the village photos. When the wiki match is a parent city
    # article, skip its title too — it would repeat the same city images.
    core = re.sub(r"^[一-鿿]{1,3}(市|州|县|区|盟)", "", name) or name
    matched_is_city = is_generic_place(page.get("title") or "")
    search_terms = [f"{core} {site['province_full']}", core]
    if not matched_is_city:
        if en_title:
            search_terms.append(en_title)
    seen_terms = set()
    for term in search_terms:
        if not term.strip() or term in seen_terms:
            continue
        seen_terms.add(term)
        for img in commons_search(term, 6):
            # Gazette PDFs and other non-photo files rank high on Chinese
            # government-title queries; keep images only.
            fname = img.get("title") or ""
            if fname.lower().endswith((".pdf", ".djvu", ".tif", ".tiff")):
                continue
            if img not in images:
                images.append(img)
    # Deduplicate by URL and keep at most five.
    seen, kept = set(), []
    for img in images:
        if img.get("url") and img["url"] not in seen:
            seen.add(img["url"])
            kept.append(img)
    result = {
        "matched": True,
        "zh_title": page.get("title"),
        "en_title": en_title,
        "langs": sorted(langs.keys()),
        "wikidata_id": qid,
        "intro_en": intro_en[:1200] if intro_en else None,
        "en_source": "wikipedia" if intro_en else None,
        "images": kept[:5],
    }
    save_json(cache_path(f"cn_{site['id']}.json"), result)
    return result


def fetch_sitelinks(items: list[str]) -> dict[str, dict]:
    """Fetch labels and all sitelinks for Wikidata items, 50 at a time."""
    out: dict[str, dict] = {}
    for i in range(0, len(items), 50):
        chunk = items[i:i + 50]
        data = get_json("https://www.wikidata.org/w/api.php", params={
            "action": "wbgetentities", "format": "json", "ids": "|".join(chunk),
            "props": "sitelinks|labels", "languages": "en|zh|ja|ko|fr|es|de|it|pt|ru|ar|th|tr|vi|id",
        }, retries=4)
        for qid, ent in ((data or {}).get("entities") or {}).items():
            if not ent or ent.get("missing"):
                continue
            out[qid] = {
                "labels": {k: v.get("value") for k, v in (ent.get("labels") or {}).items()},
                # Wikidata keys are `enwiki`, `zhwiki`, ...; store the language
                # code (`en`, `zh`) because every consumer looks up codes.
                "sitelinks": {k[:-4]: v.get("title")
                              for k, v in (ent.get("sitelinks") or {}).items()
                              if k.endswith("wiki")},
            }
        time.sleep(0.4)
    return out


# For multilingual countries, Wikidata's P37 list is not ordered by everyday
# usage.  These overrides keep the "local language" meaningful.
LOCAL_LANG_OVERRIDE = {
    "US": None, "GB": None, "AU": None, "NZ": None, "IE": None, "ZA": None,
    "SG": None, "CA": "fr", "IN": "hi", "PH": "fil", "MY": "ms",
    "CH": "de", "BE": "fr", "LU": "fr", "MT": "mt", "CY": "el",
    "FJ": None, "PG": None, "NA": None, "BW": None, "ZW": None, "KE": None,
}

LANG_TO_WIKI = {
    "zh": "zh", "en": "en", "ja": "ja", "ko": "ko", "fr": "fr", "es": "es",
    "de": "de", "it": "it", "pt": "pt", "ru": "ru", "ar": "ar", "th": "th",
    "tr": "tr", "vi": "vi", "id": "id", "nl": "nl", "pl": "pl", "sv": "sv",
    "da": "da", "no": "no", "fi": "fi", "cs": "cs", "hu": "hu", "ro": "ro",
    "el": "el", "he": "he", "fa": "fa", "uk": "uk", "sr": "sr", "hr": "hr",
    "bg": "bg", "sk": "sk", "sl": "sl", "lt": "lt", "lv": "lv", "et": "et",
    "ms": "ms", "tl": "tl", "sw": "sw", "af": "af", "am": "am", "ka": "ka",
    "hy": "hy", "az": "az", "kk": "kk", "uz": "uz", "mn": "mn", "ne": "ne",
    "si": "si", "km": "km", "lo": "lo", "my": "my", "bn": "bn", "ur": "ur",
}


def fetch_extracts(lang: str, titles: list[str]) -> dict[str, str]:
    """Batch-fetch intro extracts for up to 20 titles per request."""
    out: dict[str, str] = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i:i + 20]
        data = wiki_api(lang, {
            "action": "query", "titles": "|".join(chunk), "prop": "extracts",
            "exintro": 1, "explaintext": 1, "redirects": 1, "exsectionformat": "plain",
        })
        pages = ((data or {}).get("query") or {}).get("pages", {})
        if isinstance(pages, dict):
            pages = list(pages.values())
        for page in pages or []:
            title = title_clean(page.get("title", ""))
            text = strip_html(page.get("extract", ""))
            if title and text:
                out[title] = text[:1500]
        time.sleep(0.25)
    return out


def unesco_sites(force: bool = False) -> dict:
    unesco = load_json(RAW / "unesco_sites.json", {}) or {}
    wikidata = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
    countries = load_json(RAW / "countries.json", {}) or {}
    cache_file = RAW / "unesco_wiki.json"
    cached = load_json(cache_file, {}) or {}
    if not force and cached.get("fetched_at") and cached.get("items"):
        return cached

    items = {sid: rec["item"] for sid, rec in wikidata.items() if rec.get("item")}
    entities = fetch_sitelinks(list(items.values()))

    chosen: dict[str, dict] = {}
    local_titles: dict[str, list[tuple[str, str]]] = defaultdict(list)
    zh_titles: list[str] = []
    for site in unesco.get("sites", []):
        sid = site["id"]
        wd = wikidata.get(sid) or {}
        ent = entities.get(wd.get("item", ""), {})
        sitelinks = ent.get("sitelinks", {})
        labels = ent.get("labels", {})
        primary = (site.get("iso") or [""])[0].upper()
        country = countries.get(primary, {})
        official = [l.get("code") for l in country.get("langs", []) if l.get("code")]
        # Keep the country's official language only when it is not the base
        # English/Chinese edition and a Wikipedia/UNESCO text exists.
        local = None
        if primary in LOCAL_LANG_OVERRIDE:
            override = LOCAL_LANG_OVERRIDE[primary]
            if override and (override in site.get("description", {}) or sitelinks.get(override)):
                local = override
        else:
            non_base = [c for c in official if c not in ("en", "zh")]
            if len(non_base) == 1:
                if non_base[0] in site.get("description", {}) or sitelinks.get(non_base[0]):
                    local = non_base[0]
            else:
                for code in non_base:
                    if code in site.get("description", {}) or sitelinks.get(code):
                        local = code
                        break
        chosen[sid] = {
            "item": wd.get("item"),
            "sitelinks": sitelinks,
            "labels": labels,
            "local_lang": local,
            "country": primary,
        }
        if local and sitelinks.get(local):
            local_titles[local].append((sid, title_clean(sitelinks[local])))
        if not site.get("description", {}).get("zh") and sitelinks.get("zh"):
            zh_titles.append((sid, title_clean(sitelinks["zh"])))

    # English extracts only needed for sites lacking an official English description.
    en_titles = [(s["id"], title_clean(chosen[s["id"]]["sitelinks"]["en"]))
                 for s in unesco.get("sites", [])
                 if not s.get("description", {}).get("en") and chosen[s["id"]]["sitelinks"].get("en")]
    extracts_en = fetch_extracts("en", [t for _, t in en_titles]) if en_titles else {}
    extracts_zh = fetch_extracts("zh", [t for _, t in zh_titles]) if zh_titles else {}
    extracts_local: dict[str, dict[str, str]] = {}
    for lang, pairs in local_titles.items():
        if lang in LANG_TO_WIKI:
            extracts_local[lang] = fetch_extracts(LANG_TO_WIKI[lang], [t for _, t in pairs])

    out_items: dict[str, dict] = {}
    missing_zh: list[tuple[str, str]] = []
    for site in unesco.get("sites", []):
        sid = site["id"]
        rec = chosen[sid]
        local = rec["local_lang"]
        local_name = None
        local_intro = None
        local_source = None
        if local:
            official_edition = site.get("name", {}).get(local)
            if official_edition:
                local_name = official_edition
                local_intro = site.get("description", {}).get(local)
                local_source = "unesco_official" if local_intro else None
            if not local_intro and rec["sitelinks"].get(local):
                title = title_clean(rec["sitelinks"][local])
                local_intro = extracts_local.get(local, {}).get(title)
                local_source = "wikipedia" if local_intro else None
            if not local_name and local_intro:
                local_name = rec["sitelinks"].get(local)
        zh_name = site.get("name", {}).get("zh")
        zh_intro = site.get("description", {}).get("zh")
        zh_source = "unesco_official" if zh_intro else None
        if not zh_intro and rec["sitelinks"].get("zh"):
            title = title_clean(rec["sitelinks"]["zh"])
            zh_intro = extracts_zh.get(title)
            zh_source = "wikipedia" if zh_intro else None
        if not zh_intro:
            missing_zh.append((sid, site.get("description", {}).get("en", "")))
        en_intro = site.get("description", {}).get("en")
        if not en_intro and rec["sitelinks"].get("en"):
            en_intro = extracts_en.get(title_clean(rec["sitelinks"]["en"]))
        out_items[sid] = {
            "sitelinks": rec["sitelinks"],
            "labels": rec["labels"],
            "local_lang": local,
            "name_local": local_name,
            "intro_local": local_intro,
            "local_source": local_source,
            "name_zh": zh_name,
            "intro_zh": zh_intro,
            "zh_source": zh_source,
            "intro_en": en_intro,
        }

    # Fill Chinese descriptions with machine translation only when both the
    # official Chinese edition and Chinese Wikipedia are missing.  These calls
    # are independent, so run them concurrently; the public endpoint is slow.
    import concurrent.futures as futures

    def translate_one(item: tuple[str, str]) -> tuple[str, str | None]:
        sid, text = item
        return sid, translate(text, "zh") if text else None

    pending = [(sid, text) for sid, text in missing_zh if text]
    if pending:
        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            for sid, mt in pool.map(translate_one, pending):
                if mt:
                    out_items[sid]["intro_zh"] = mt
                    out_items[sid]["zh_source"] = "machine_translation"

    out = {"fetched_at": now_iso(), "count": len(out_items), "items": out_items}
    save_json(cache_file, out)
    return out


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="limit China sites (debug)")
    ap.add_argument("--skip-unesco", action="store_true")
    args = ap.parse_args()

    china = load_json(RAW / "china_official.json", {}) or {}
    sites = china.get("sites", [])
    if args.limit:
        sites = sites[: args.limit]
    if sites:
        import concurrent.futures as futures

        existing = (load_json(RAW / "china_wiki.json", {}) or {}).get("items", {}) if not args.limit else {}
        out = dict(existing)
        done = 0
        with futures.ThreadPoolExecutor(max_workers=10) as pool:
            future_map = {pool.submit(china_site, site): site for site in sites}
            for fut in futures.as_completed(future_map):
                site = future_map[fut]
                try:
                    out[site["id"]] = fut.result()
                except Exception as exc:  # noqa: BLE001
                    print(f"China wiki failed for {site['id']}: {exc}")
                done += 1
                if done % 20 == 0:
                    print(f"China wiki {done}/{len(sites)}", flush=True)
                    save_json(RAW / "china_wiki.json", {
                        "fetched_at": now_iso(), "count": len(out), "items": out,
                    })
        save_json(RAW / "china_wiki.json", {
            "fetched_at": now_iso(), "count": len(out), "items": out,
        })

    if not args.skip_unesco:
        unesco = unesco_sites(force=os.environ.get("REFRESH_WIKI") == "1")
        print(f"UNESCO wiki: {unesco.get('count')} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
