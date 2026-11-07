#!/usr/bin/env python3
"""Fetch and normalize the UNESCO World Heritage list.

The official whc.unesco.org XML endpoint is behind a Cloudflare challenge.
The weekly job therefore tries, in order:

1. Firecrawl API (set FIRECRAWL_API_KEY) - reliable Cloudflare bypass.
2. Direct HTTP with curl_cffi browser impersonation.
3. The committed snapshot in data/raw/unesco*.xml (keeps the site buildable).

Six official language editions are stored: en, zh, fr, es, ru, ar.  Names and
short descriptions from those editions are reused as the authoritative
multilingual text; Wikipedia is only a fallback.

Output: data/raw/unesco_sites.json
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

from common import RAW, http_post, now_iso, save_json, strip_html

LANGS = ["en", "zh", "fr", "es", "ru", "ar"]
URLS = {lang: f"https://whc.unesco.org/{lang}/list/xml/" for lang in LANGS}


def snapshot_path(lang: str):
    return RAW / ("unesco.xml" if lang == "en" else f"unesco_{lang}.xml")


def _firecrawl(lang: str, key: str) -> str | None:
    payload = {"url": URLS[lang], "formats": ["rawHtml"], "onlyMainContent": False}
    r = http_post(
        "https://api.firecrawl.dev/v1/scrape",
        json_body=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        timeout=90,
        retries=2,
    )
    if not r or r.status_code != 200:
        return None
    try:
        return (r.json().get("data") or {}).get("rawHtml")
    except Exception:
        return None


def _direct(lang: str) -> str | None:
    try:
        from curl_cffi import requests as cffi
        from common import _proxies

        r = cffi.get(URLS[lang], impersonate="chrome", timeout=60, proxies=_proxies())
        if r.status_code == 200 and r.text.lstrip().startswith("<?xml"):
            return r.text
    except Exception:
        pass
    return None


def refresh(lang: str) -> tuple[str, str]:
    """Return (xml_text, status). Status is firecrawl|direct|cached|missing."""
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if key:
        text = _firecrawl(lang, key)
        if text and text.lstrip().startswith("<?xml"):
            snapshot_path(lang).write_text(text, encoding="utf-8")
            return text, "firecrawl"
    text = _direct(lang)
    if text:
        snapshot_path(lang).write_text(text, encoding="utf-8")
        return text, "direct"
    path = snapshot_path(lang)
    if path.exists():
        return path.read_text(encoding="utf-8"), "cached"
    return "", "missing"


def parse_language(xml_text: str) -> dict[str, dict]:
    """Return {id: {name, description}} for one language edition."""
    root = ET.fromstring(xml_text)
    out: dict[str, dict] = {}
    for row in root.findall("row"):
        sid = (row.findtext("id_number") or "").strip()
        if not sid:
            continue
        out[sid] = {
            "name": (row.findtext("site") or "").strip(),
            "description": strip_html(row.findtext("short_description") or ""),
        }
    return out


def parse_meta(xml_text: str) -> dict[str, dict]:
    """Return English-edition metadata for every site."""
    root = ET.fromstring(xml_text)
    out: dict[str, dict] = {}
    for row in root.findall("row"):
        sid = (row.findtext("id_number") or "").strip()
        if not sid:
            continue
        out[sid] = {
            "id": sid,
            "dossier": (row.findtext("dossier") or "").strip(),
            "unique_number": (row.findtext("unique_number") or "").strip(),
            "http_url": (row.findtext("http_url") or "").strip(),
            "image_url": (row.findtext("image_url") or "").strip(),
            "iso": [x.strip().lower() for x in (row.findtext("iso_code") or "").split(",") if x.strip()],
            "states": [x.strip() for x in (row.findtext("states") or "").split(",") if x.strip()],
            "location": (row.findtext("location") or "").strip(),
            "region": (row.findtext("regions") or "").strip(),
            "category": (row.findtext("category") or "").strip(),
            "criteria": (row.findtext("criteria_txt") or "").strip(),
            "year": (row.findtext("date_inscribed") or "").strip(),
            "danger": (row.findtext("danger") or "0").strip() == "1",
            "transnational": (row.findtext("transnational") or "0").strip() == "1",
        }
    return out


def main() -> int:
    texts: dict[str, str] = {}
    statuses: dict[str, str] = {}
    for lang in LANGS:
        text, status = refresh(lang)
        statuses[lang] = status
        if text:
            texts[lang] = text
        print(f"UNESCO {lang}: {status}")

    if "en" not in texts:
        print("No English UNESCO snapshot; aborting", file=sys.stderr)
        return 1

    meta = parse_meta(texts["en"])
    merged: dict[str, dict] = {}
    for sid, rec in meta.items():
        merged[sid] = {**rec, "name": {}, "description": {}}

    for lang, text in texts.items():
        for sid, rec in parse_language(text).items():
            if sid not in merged:
                continue
            if rec["name"]:
                merged[sid]["name"][lang] = rec["name"]
            if rec["description"]:
                merged[sid]["description"][lang] = rec["description"]

    sites = sorted(merged.values(), key=lambda x: int(x["id"]) if x["id"].isdigit() else 0)
    out = {
        "source": "https://whc.unesco.org/en/list/",
        "source_name": "UNESCO World Heritage Centre",
        "fetched_at": now_iso(),
        "status": statuses,
        "count": len(sites),
        "sites": sites,
    }
    save_json(RAW / "unesco_sites.json", out)
    print(f"saved {len(sites)} UNESCO sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
