#!/usr/bin/env python3
"""Shared helpers for the world-heritage-travel-guide data pipeline.

All network calls are best-effort: the weekly job must keep the previous
snapshot when an upstream source is unavailable instead of failing the build.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import socket
import threading

try:
    # This network has no working IPv6 route; urllib3 otherwise hangs in
    # SYN-SENT for every Wikipedia/Wikidata request.
    from urllib3.util import connection
    connection.allowed_gai_family = lambda: socket.AF_INET
except Exception:
    pass

import requests
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = ROOT / "cache"
SITE = ROOT / "site"
ENTRIES = ROOT / "entries"
for _p in (DATA, RAW, CACHE, SITE, ENTRIES):
    _p.mkdir(parents=True, exist_ok=True)

UA = "world-heritage-travel-guide/1.0 (+https://github.com/yanqingwang/world-heritage-travel-guide)"
PROXY = (
    os.environ.get("HTTPS_PROXY")
    or os.environ.get("https_proxy")
    or os.environ.get("ALL_PROXY")
    or os.environ.get("all_proxy")
    or ""
)
TRANSLATE_PROXY = os.environ.get("TRANSLATE_PROXY") or PROXY
if PROXY.startswith("socks5h://"):
    PROXY = "socks5://" + PROXY[len("socks5h://") :]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "lxml")
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def pinyin_slug(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = re.sub(r"[（）()·、，,。.\s\-—/]", "", value)
    value = re.sub("(旅游景区|旅游度假区|文化旅游区|旅游区|风景区|景区)$", "", value)
    ascii_slug = re.sub(r"[^A-Za-z0-9]+", "-", "".join(lazy_pinyin(value))).strip("-").lower()
    return ascii_slug or hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def unique_slug(base: str, used: set[str], suffix: str = "") -> str:
    slug = base or "site"
    if suffix:
        slug = f"{slug}-{suffix}"
    original = slug
    n = 2
    while slug in used:
        slug = f"{original}-{n}"
        n += 1
    used.add(slug)
    return slug


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _proxies(proxy: str | None = None) -> dict[str, str] | None:
    p = PROXY if proxy is None else proxy
    if not p:
        return None
    return {"http": p, "https": p}


def http_get(url: str, *, params: dict | None = None, timeout: int = 40,
             retries: int = 4, headers: dict | None = None, use_proxy: bool | None = None) -> requests.Response | None:
    """GET with exponential backoff. Returns None after all retries."""
    hdr = {"User-Agent": UA}
    if headers:
        hdr.update(headers)
    delay = 1.5
    proxies = _proxies() if (use_proxy is None and PROXY) or use_proxy else None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=hdr, timeout=timeout, proxies=proxies)
            if r.status_code == 200:
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 25)
                continue
            return r
        except requests.RequestException:
            time.sleep(delay)
            delay = min(delay * 2, 25)
    return None


def http_post(url: str, *, data: dict | None = None, json_body: dict | None = None,
              timeout: int = 60, retries: int = 4, headers: dict | None = None) -> requests.Response | None:
    hdr = {"User-Agent": UA}
    if headers:
        hdr.update(headers)
    delay = 1.5
    for _ in range(retries):
        try:
            r = requests.post(url, data=data, json=json_body, headers=hdr, timeout=timeout,
                              proxies=_proxies())
            if r.status_code == 200:
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 25)
                continue
            return r
        except requests.RequestException:
            time.sleep(delay)
            delay = min(delay * 2, 25)
    return None


def get_json(url: str, *, params: dict | None = None, timeout: int = 40,
             retries: int = 4, headers: dict | None = None) -> Any:
    r = http_get(url, params=params, timeout=timeout, retries=retries, headers=headers)
    if r is None or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Translation (Google Translate public endpoint, cached; used only as fallback
# when no official/Wikipedia text exists).  Outputs are explicitly labelled
# `machine_translation` in the data.
# ---------------------------------------------------------------------------
TRANSLATION_CACHE = RAW / "translations.json"
_translations: dict[str, str] | None = None
_TRANSLATION_LOCK = threading.Lock()


def _cache() -> dict[str, str]:
    global _translations
    if _translations is None:
        with _TRANSLATION_LOCK:
            if _translations is None:
                _translations = load_json(TRANSLATION_CACHE, {}) or {}
    return _translations


def _save_cache() -> None:
    with _TRANSLATION_LOCK:
        save_json(TRANSLATION_CACHE, _cache())


def translate(text: str, target: str, source: str = "auto", *, timeout: int = 30) -> str | None:
    text = (text or "").strip()
    if not text:
        return ""
    key = hashlib.sha1(f"{source}|{target}|{text}".encode("utf-8")).hexdigest()
    cached = _cache().get(key)
    if cached:
        return cached
    from curl_cffi import requests as cffi_requests

    params = {
        "client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text,
    }
    proxies = _proxies(TRANSLATE_PROXY)
    delay = 2.0
    for _ in range(4):
        try:
            r = cffi_requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params=params, impersonate="chrome", timeout=timeout, proxies=proxies,
            )
            if r.status_code == 200:
                payload = r.json()
                out = "".join(seg[0] for seg in payload[0] if seg and seg[0])
                if out:
                    cache = _cache()
                    with _TRANSLATION_LOCK:
                        cache[key] = out
                        if len(cache) % 20 == 0:
                            save_json(TRANSLATION_CACHE, cache)
                    return out
            time.sleep(delay)
            delay = min(delay * 2, 20)
        except Exception:
            time.sleep(delay)
            delay = min(delay * 2, 20)
    return None


def save_translations() -> None:
    _save_cache()


# ---------------------------------------------------------------------------
# Wikipedia
# ---------------------------------------------------------------------------
def wiki_api(lang: str, params: dict, *, timeout: int = 30) -> Any:
    params = {"format": "json", "formatversion": 2, **params}
    return get_json(f"https://{lang}.wikipedia.org/w/api.php", params=params, timeout=timeout, retries=5)


def wiki_search(lang: str, query: str, limit: int = 5) -> list[dict]:
    data = wiki_api(lang, {"action": "query", "list": "search", "srsearch": query, "srlimit": limit})
    return ((data or {}).get("query") or {}).get("search", []) or []


def wiki_page(lang: str, title: str, props: str = "extracts|pageprops|langlinks|pageimages",
              *, intro: bool = True) -> dict | None:
    data = wiki_api(lang, {
        "action": "query", "titles": title, "prop": props, "redirects": 1,
        "lllimit": "max", "exintro": 1 if intro else 0, "explaintext": 1,
        "exsectionformat": "plain", "piprop": "original|thumbnail", "pithumbsize": 1280,
    })
    pages = ((data or {}).get("query") or {}).get("pages", {})
    if isinstance(pages, dict):
        pages = list(pages.values())
    for page in pages or []:
        if page.get("missing") or page.get("invalid"):
            continue
        if page.get("title"):
            return page
    return None


def wiki_langlinks(lang: str, title: str) -> dict[str, str]:
    page = wiki_page(lang, title, props="langlinks")
    if not page:
        return {}
    out = {}
    for ll in page.get("langlinks", []) or []:
        out[ll.get("lang")] = ll.get("*")
    return out


# ---------------------------------------------------------------------------
# Wikimedia Commons
# ---------------------------------------------------------------------------
COMMONS_API = "https://commons.wikimedia.org/w/api.php"


def _commons_imageinfo(page: dict) -> dict | None:
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata") or {}
    url = info.get("thumburl") or info.get("url")
    if not url:
        return None
    title = page.get("title", "")
    artist = strip_html((meta.get("Artist") or {}).get("value", ""))
    license_name = strip_html((meta.get("LicenseShortName") or {}).get("value", ""))
    credit = strip_html((meta.get("Credit") or {}).get("value", ""))
    return {
        "url": url,
        "title": title.removeprefix("File:"),
        "author": artist[:120],
        "license": license_name[:60],
        "credit": credit[:160],
        "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(
            title.replace(" ", "_"), safe="/:"),
    }


def commons_search(query: str, limit: int = 6) -> list[dict]:
    data = get_json(COMMONS_API, params={
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1280,
    }, retries=4)
    pages = ((data or {}).get("query") or {}).get("pages", {})
    if isinstance(pages, dict):
        pages = list(pages.values())
    out = []
    for page in pages or []:
        item = _commons_imageinfo(page)
        if item:
            out.append(item)
    return out


def commons_category(category: str, limit: int = 8) -> list[dict]:
    data = get_json(COMMONS_API, params={
        "action": "query", "format": "json", "generator": "categorymembers",
        "gcmtitle": f"Category:{category}", "gcmtype": "file", "gcmlimit": limit,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1280,
    }, retries=4)
    pages = ((data or {}).get("query") or {}).get("pages", {})
    if isinstance(pages, dict):
        pages = list(pages.values())
    out = []
    for page in pages or []:
        item = _commons_imageinfo(page)
        if item:
            out.append(item)
    return out


def commons_file(filename: str) -> dict | None:
    # Wikidata P18 values are URL-encoded (`Longs%20Peak.jpg`); MediaWiki wants
    # the decoded title or the file page 404s.
    filename = urllib.parse.unquote(filename or "")
    title = filename if filename.startswith("File:") else f"File:{filename}"
    data = get_json(COMMONS_API, params={
        "action": "query", "format": "json", "titles": title,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1280,
    })
    pages = ((data or {}).get("query") or {}).get("pages", {})
    if isinstance(pages, dict):
        pages = list(pages.values())
    for page in pages or []:
        return _commons_imageinfo(page)
    return None


# ---------------------------------------------------------------------------
# Overpass
# ---------------------------------------------------------------------------
# The German and Kumi endpoints are frequently at capacity; the French mirror
# has been consistently available and accepts global queries.  Rotation still
# spreads load when a mirror starts failing.
OVERPASS_ENDPOINTS = [
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def overpass(query: str, *, timeout: int = 90, tries: int = 5) -> dict | None:
    """Run an Overpass query, rotating endpoints and backing off on 429/502."""
    delay = 3.0
    for attempt in range(tries):
        endpoint = OVERPASS_ENDPOINTS[attempt % len(OVERPASS_ENDPOINTS)]
        try:
            r = requests.post(endpoint, data={"data": query},
                              headers={"User-Agent": UA}, timeout=timeout, proxies=_proxies())
            if r.status_code == 200:
                try:
                    return r.json()
                except Exception:
                    pass
            elif r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 45)
                continue
        except requests.RequestException:
            time.sleep(delay)
            delay = min(delay * 2, 45)
    return None


def element_point(e: dict) -> tuple[float, float] | None:
    if "lat" in e and "lon" in e:
        return float(e["lat"]), float(e["lon"])
    center = e.get("center")
    if center:
        return float(center["lat"]), float(center["lon"])
    return None
