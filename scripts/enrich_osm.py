#!/usr/bin/env python3
"""Enrich sites with nearby hotels, railway stations and ferry terminals from
OpenStreetMap via Overpass.

China 5A sites: hotels within 30 km, railway stations within 60 km.
Overseas "full" tier (top 300): hotels within 50 km, stations and ferry
terminals within 50 km.  Overseas "basic" tier intentionally skips hotels.

Caching / rotation:
  * One cache file per site, so a failure never blocks the build.
  * --budget N refreshes at most N stale sites per run (default 80).  The
    weekly job therefore refreshes the whole catalogue on a rolling basis
    without hammering the public Overpass endpoint.

Usage:
    python scripts/enrich_osm.py --budget 5
    python scripts/enrich_osm.py --force --only china
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone

from common import (
    CACHE, RAW, element_point, haversine_km, load_json, now_iso, overpass,
    save_json,
)

OSM_CACHE = RAW / "osm"
OSM_CACHE.mkdir(parents=True, exist_ok=True)
STATE_FILE = RAW / "osm_state.json"

CHAIN_RE = (
    "全季|汉庭|如家|亚朵|桔子|维也纳|锦江|格林豪泰|速8|7天|宜必思|莫泰|"
    "希尔顿|万豪|洲际|温德姆|凯悦|喜来登|香格里拉|丽思卡尔顿|假日|皇冠|"
    "开元|银泰|保利|碧桂园|华住|携程|途家|凯宾斯基|康莱德|四季|朗廷|"
    "Hilton|Marriott|InterContinental|Hyatt|Sheraton|Shangri|Ritz|"
    "Holiday Inn|Crowne Plaza|Wyndham|Kempinski|Ibis|Novotel|Radisson|"
    "Accor|Mercure|Best Western|Holiday Inn Express|Four Seasons|"
    "Fairmont|Le Méridien|Westin|Sofitel|Novotel|Pullman|Renaissance|"
    "DoubleTree|Hampton|Holiday|Mövenpick|St. Regis|Mandarin Oriental"
)
LUX_RE = (
    "五星|四星|五星级|四星级|皇冠假日|希尔顿|万豪|洲际|香格里拉|凯悦|喜来登|"
    "丽思卡尔顿|半岛|四季|柏悦|威斯汀|索菲特|凯宾斯基|康莱德|朗廷|瑞吉|"
    "宝格丽|阿玛尼|文华东方|安缦|悦榕庄|W酒店|"
    "Hilton|Marriott|InterContinental|Hyatt|Sheraton|Shangri|Ritz|"
    "Four Seasons|Peninsula|Kempinski|Conrad|Mandarin Oriental|St. Regis|"
    "Bulgari|Armani|Aman|Banyan|Westin|Sofitel|Fairmont|W Hotel"
)


def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def is_chain(name: str, brand: str) -> bool:
    return bool(re.search(CHAIN_RE, f"{name} {brand}", re.I))


def is_star_name(name: str) -> bool:
    return bool(re.search(LUX_RE, name, re.I))


def query_nearby(lat: float, lon: float, *, hotel_km: int, station_km: int,
                 ferries: bool) -> dict:
    """One Overpass round-trip per site: hotels, stations and (optionally) ferries.

    The old implementation issued up to four sequential requests per site, which
    made a full 500-site refresh take hours.  A single union query is both far
    faster and easier on the public endpoint.
    """
    parts = [
        f"nwr(around:{hotel_km * 1000},{lat},{lon})[tourism=hotel];",
        f"node(around:{station_km * 1000},{lat},{lon})[railway=station];",
    ]
    if ferries:
        parts.append(f"nwr(around:{hotel_km * 1000},{lat},{lon})[amenity=ferry_terminal];")
        parts.append(f"nwr(around:{hotel_km * 1000},{lat},{lon})[harbour=yes];")
    data = overpass("[out:json][timeout:90];(" + "".join(parts) + ");out center tags;")
    hotels, stations, ferry = [], [], []
    if not data:
        # Signal failure so the caller does not cache an empty result.
        return None
    for e in data.get("elements", []):
        tags = e.get("tags") or {}
        pt = element_point(e)
        if not pt:
            continue
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue
        lat2, lon2 = pt
        dist = round(haversine_km(lat, lon, lat2, lon2), 1)
        if tags.get("tourism") == "hotel":
            hotels.append({
                "name": name,
                "name_en": tags.get("name:en"),
                "stars": _int(tags.get("stars")),
                "brand": tags.get("brand") or tags.get("brand:en"),
                "lat": lat2,
                "lon": lon2,
                "distance_km": dist,
                "kind": "star" if tags.get("stars") else (
                    "chain" if is_chain(name, tags.get("brand") or "") else "hotel"),
                "source": "OpenStreetMap",
            })
        elif tags.get("railway") == "station":
            if tags.get("station") == "subway" or tags.get("subway") == "yes":
                continue
            stations.append({
                "name": name, "name_en": tags.get("name:en"),
                "lat": lat2, "lon": lon2, "distance_km": dist,
                "operator": tags.get("operator"),
            })
        elif tags.get("amenity") == "ferry_terminal" or tags.get("harbour") == "yes":
            ferry.append({
                "name": name, "name_en": tags.get("name:en"),
                "lat": lat2, "lon": lon2, "distance_km": dist,
                "operator": tags.get("operator"),
            })

    def dedupe(items):
        out, seen = [], set()
        for x in sorted(items, key=lambda z: z["distance_km"]):
            key = x["name"].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(x)
        return out

    hotels = dedupe(hotels)
    selected = sorted(
        hotels,
        key=lambda h: (0 if h["kind"] == "star" else 1 if h["kind"] == "chain" else 2,
                       -(h["stars"] or 0), h["distance_km"]),
    )[:5]
    return {
        "hotels": selected,
        "hotel_count": len(hotels),
        "stations": dedupe(stations)[:8],
        "ferry_terminals": dedupe(ferry)[:5],
    }


def attach_hsr(stations: list[dict], hsr_names: set[str]) -> list[dict]:
    for st in stations:
        base = re.sub("站$", "", st["name"]).strip()
        st["high_speed"] = base in hsr_names
    return sorted(stations, key=lambda x: (0 if x.get("high_speed") else 1, x["distance_km"]))


def enrich_one(kind: str, site: dict, hsr_names: set[str], force: bool) -> str:
    cache_file = OSM_CACHE / f"{kind}_{site['id']}.json"
    if cache_file.exists() and not force:
        return "cached"
    lat, lon = float(site["lat"]), float(site["lon"])
    if kind == "china":
        nearby = query_nearby(lat, lon, hotel_km=30, station_km=60, ferries=False)
        if nearby is None:
            return "failed"
        result = {
            "hotels": nearby["hotels"], "hotels_nearby_30km": nearby["hotel_count"],
            "stations": attach_hsr(nearby["stations"], hsr_names),
            "ferry_terminals": [],
            "fetched_at": now_iso(),
        }
    else:
        nearby = query_nearby(lat, lon, hotel_km=50, station_km=50, ferries=True)
        if nearby is None:
            return "failed"
        result = {
            "hotels": nearby["hotels"], "hotels_nearby_50km": nearby["hotel_count"],
            "stations": nearby["stations"],
            "ferry_terminals": nearby["ferry_terminals"],
            "fetched_at": now_iso(),
        }
    save_json(cache_file, result)
    return "fetched"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=80, help="max stale sites to refresh (0 = all)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", choices=["china", "world"], default=None)
    args = ap.parse_args()

    hsr = load_json(RAW / "hsr_stations.json", []) or []
    hsr_names = {re.sub("站$", "", h.get("name", "")).strip() for h in hsr if h.get("name")}
    state = load_json(STATE_FILE, {}) or {}

    tasks: list[tuple[str, dict]] = []
    china = load_json(RAW / "china_official.json", {}) or {}
    if args.only in (None, "china"):
        for site in china.get("sites", []):
            tasks.append(("china", site))
    if args.only in (None, "world"):
        unesco = load_json(RAW / "unesco_sites.json", {}) or {}
        rank = (load_json(RAW / "unesco_rank.json", {}) or {}).get("items", {})
        wiki = (load_json(RAW / "unesco_wikidata.json", {}) or {}).get("items", {})
        for site in unesco.get("sites", []):
            if (site.get("iso") or []) and set(site["iso"]) <= {"cn"}:
                continue
            rec = rank.get(site["id"]) or {}
            if rec.get("tier") != "full":
                continue
            wd = wiki.get(site["id"]) or {}
            if wd.get("lat") is None:
                continue
            site = {**site, "lat": wd["lat"], "lon": wd["lon"]}
            tasks.append(("world", site))

    # Refresh least-recently-checked first.
    tasks.sort(key=lambda t: state.get(f"{t[0]}:{t[1]['id']}", ""))
    if not args.force and args.budget:
        tasks = tasks[:args.budget]

    fetched = failures = 0
    import concurrent.futures as futures

    refresh = args.force or args.budget > 0

    def work(kind: str, site: dict) -> tuple[str, str, str]:
        status = enrich_one(kind, site, hsr_names, refresh)
        return kind, site["id"], status

    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        future_map = {pool.submit(work, kind, site): (kind, site) for kind, site in tasks}
        done = 0
        for fut in futures.as_completed(future_map):
            kind, site = future_map[fut]
            done += 1
            try:
                _, sid, status = fut.result()
                if status == "failed":
                    # Leave the old state timestamp so failed sites are retried
                    # before sites that were refreshed successfully.
                    failures += 1
                else:
                    state[f"{kind}:{sid}"] = now_iso()
                    if status == "fetched":
                        fetched += 1
                print(f"[{done}/{len(tasks)}] {kind} {site.get('name') or site.get('name', {}).get('en', '')}: {status}", flush=True)
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"[{done}/{len(tasks)}] FAIL {site.get('id')}: {exc}", flush=True)
            if done % 10 == 0:
                save_json(STATE_FILE, state)
    save_json(STATE_FILE, state)
    print(f"done: {fetched} fetched, {failures} failures, {len(tasks)} considered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
