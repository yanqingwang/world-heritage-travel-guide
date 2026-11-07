#!/usr/bin/env python3
"""Fetch the OurAirports dataset and keep only scheduled commercial airports.

OpenFlights' airports.dat is convenient but still lists airports that closed
years ago (for example Beijing Nanyuan, NAY).  OurAirports carries a
`scheduled_service` flag and an airport status, so the nearest-airport result
is a real, currently served airport.

Input:  data/raw/airports.csv  (full public-domain dataset, cached locally)
Output: data/raw/airports.json (filtered, committed)
"""
from __future__ import annotations

import csv
import sys

from common import RAW, http_get, now_iso, save_json

CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
KEEP_TYPES = {"large_airport", "medium_airport", "small_airport"}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="download the full CSV even when a local cache exists")
    args = ap.parse_args()

    csv_file = RAW / "airports.csv"
    text = ""
    if csv_file.exists() and not args.refresh:
        text = csv_file.read_text(encoding="utf-8")
    else:
        r = http_get(CSV_URL, timeout=180, retries=3)
        if r is not None and r.status_code == 200:
            r.encoding = "utf-8"
            text = r.text
            csv_file.write_text(text, encoding="utf-8")
        elif csv_file.exists():
            text = csv_file.read_text(encoding="utf-8")
            print("airports.csv download failed; using the local cache")
    if not text:
        print("airports.csv unavailable; keeping the previous filtered snapshot")
        return 0

    rows = list(csv.DictReader(text.splitlines()))
    airports = []
    for row in rows:
        if row.get("type") not in KEEP_TYPES:
            continue
        if row.get("scheduled_service") != "yes" or not row.get("iata_code"):
            continue
        try:
            lat, lon = float(row["latitude_deg"]), float(row["longitude_deg"])
        except (TypeError, ValueError):
            continue
        airports.append({
            "name": row.get("name", ""),
            "iata": row["iata_code"],
            "city": row.get("municipality", ""),
            "country": row.get("iso_country", ""),
            "lat": lat,
            "lon": lon,
            "type": row["type"],
        })

    save_json(RAW / "airports.json", {
        "fetched_at": now_iso(),
        "source": "OurAirports (public domain)",
        "count": len(airports),
        "airports": airports,
    })
    print(f"airports: {len(airports)} scheduled commercial airports from {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
