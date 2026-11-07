#!/usr/bin/env python3
"""Fetch visa requirements for mainland Chinese passport holders.

Source: English Wikipedia, "Visa requirements for Chinese citizens".  The
article is updated frequently and is used here as a readable, sourced proxy
for the underlying government notifications.  The generated record keeps the
raw requirement text and the retrieval date so readers can verify it.

Output: data/raw/visa.json
"""
from __future__ import annotations

import io
import re
import sys

import pandas as pd

from common import DATA, RAW, load_json, now_iso, save_json, strip_html, wiki_api

PAGE = "Visa requirements for Chinese citizens"
SOURCE_URL = "https://en.wikipedia.org/wiki/Visa_requirements_for_Chinese_citizens"

ALIASES = {
    "united states": "US", "united states of america": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "great britain": "GB",
    "russia": "RU", "russian federation": "RU",
    "south korea": "KR", "republic of korea": "KR", "korea, south": "KR",
    "north korea": "KP", "democratic people's republic of korea": "KP",
    "czech republic": "CZ", "czechia": "CZ",
    "turkey": "TR", "türkiye": "TR", "turkiye": "TR",
    "vietnam": "VN", "viet nam": "VN",
    "laos": "LA", "lao pdr": "LA",
    "syria": "SY", "syrian arab republic": "SY",
    "iran": "IR", "islamic republic of iran": "IR",
    "bolivia": "BO", "plurinational state of bolivia": "BO",
    "venezuela": "VE", "bolivarian republic of venezuela": "VE",
    "tanzania": "TZ", "united republic of tanzania": "TZ",
    "moldova": "MD", "republic of moldova": "MD",
    "micronesia": "FM", "federated states of micronesia": "FM",
    "bahamas": "BS", "the bahamas": "BS",
    "gambia": "GM", "the gambia": "GM",
    "cape verde": "CV", "cabo verde": "CV",
    "democratic republic of the congo": "CD", "dr congo": "CD",
    "republic of the congo": "CG", "congo": "CG",
    "ivory coast": "CI", "côte d'ivoire": "CI",
    "east timor": "TL", "timor-leste": "TL",
    "swaziland": "SZ", "eswatini": "SZ",
    "macedonia": "MK", "north macedonia": "MK",
    "burma": "MM", "myanmar": "MM",
    "holy see": "VA", "vatican city": "VA",
    "palestine": "PS", "state of palestine": "PS",
    "taiwan": "TW", "hong kong": "HK", "macau": "MO", "macao": "MO",
}


def norm(name: str) -> str:
    name = strip_html(name).lower()
    name = re.sub(r"\[[^\]]*\]", "", name)
    name = re.sub(r"[^a-z0-9' ]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def build_name_map() -> dict[str, str]:
    countries = load_json(RAW / "countries.json", {}) or {}
    mapping: dict[str, str] = {}
    for iso, rec in countries.items():
        for key in (rec.get("en"), rec.get("zh")):
            if key:
                mapping[norm(key)] = iso
    mapping.update(ALIASES)
    return mapping


def classify(text: str) -> tuple[str, int | None]:
    t = text.lower()
    days = None
    m = re.search(r"(\d+)\s*(day|days)", t)
    if m:
        days = int(m.group(1))
    else:
        m = re.search(r"(\d+)\s*(month|months)", t)
        if m:
            days = int(m.group(1)) * 30
    if "not admitted" in t or "entry refused" in t or "prohibited" in t:
        return "restricted", days
    if "visa not required" in t or "visa-free" in t or "visa free" in t or "no visa" in t:
        return "visa_free", days
    if "visa on arrival" in t or "on-arrival" in t:
        return "visa_on_arrival", days
    if "evisa" in t or "e-visa" in t or "electronic visa" in t:
        return "evisa", days
    if "entry permit" in t or "eta" in t or "electronic travel authorization" in t:
        return "eta", days
    if "visa required" in t or "visa is required" in t:
        return "visa_required", days
    if "visa" in t:
        return "visa_required", days
    return "unknown", days


def main() -> int:
    data = wiki_api("en", {
        "action": "parse", "page": PAGE, "prop": "text", "formatversion": 2,
    }, timeout=50)
    if not data or "parse" not in data:
        print("visa source unavailable; keeping previous snapshot", file=sys.stderr)
        return 1
    html = data["parse"]["text"]
    tables = pd.read_html(io.StringIO(html))
    target = None
    for table in tables:
        cols = [str(c) for c in table.columns]
        if any("Visa requirement" in c for c in cols) and any("Country" in c for c in cols):
            target = table
            break
    if target is None:
        print("visa table not found; keeping previous snapshot", file=sys.stderr)
        return 1

    name_map = build_name_map()
    records = {}
    for _, row in target.iterrows():
        country = strip_html(str(row.iloc[0]))
        if not country or country.lower() == "nan":
            continue
        requirement = strip_html(str(row.get("Visa requirement", "")))
        allowed = strip_html(str(row.get("Allowed stay", "")))
        notes = strip_html(str(row.get("Notes (excluding departure fees)", "")))
        iso = name_map.get(norm(country))
        if not iso:
            continue
        status, days = classify(requirement + " " + allowed)
        records[iso] = {
            "iso2": iso,
            "country": country,
            "status": status,
            "days": days,
            "requirement": requirement[:120],
            "allowed_stay": allowed[:80],
            "notes": notes[:300],
            "source": SOURCE_URL,
            "fetched_at": now_iso(),
        }

    save_json(RAW / "visa.json", {
        "source": SOURCE_URL,
        "source_name": "Wikipedia: Visa requirements for Chinese citizens",
        "fetched_at": now_iso(),
        "count": len(records),
        "countries": records,
    })
    print(f"saved visa policy for {len(records)} countries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
