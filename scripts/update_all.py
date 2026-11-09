#!/usr/bin/env python3
"""Orchestrate the weekly data refresh and build.

Design goals:
  * a failure in one upstream source never blocks the rest of the build;
  * heavy Wikipedia/OSM work is cached and rotated;
  * the weekly job is safe to run unattended on GitHub Actions.

Usage:
    python scripts/update_all.py --budget 80
    python scripts/update_all.py --quick          # core sources + build only
    python scripts/update_all.py --refresh-wiki   # force Wikipedia re-enrichment
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def run(script: str, *args: str, env: dict | None = None, required: bool = False) -> bool:
    cmd = [PY, os.path.join(ROOT, "scripts", script), *args]
    print(f"\n$ {' '.join(cmd)}", flush=True)
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(cmd, cwd=ROOT, env=merged)
    ok = proc.returncode == 0
    if not ok and required:
        raise SystemExit(f"required step failed: {script}")
    if not ok:
        print(f"warning: {script} failed (exit {proc.returncode}); continuing", flush=True)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=80)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--refresh-wiki", action="store_true")
    args = ap.parse_args()

    first_week = datetime.now(timezone.utc).day <= 7

    # fetch_china returns non-zero when the MCT API is down; the build reuses
    # the committed snapshot, so a transient outage should not stop the run.
    run("fetch_china.py")
    run("fetch_unesco.py")
    run("fetch_countries.py")
    run("fetch_country_names.py")
    run("fetch_country_info.py")
    run("fetch_visa.py")
    run("fetch_airports.py")
    run("fetch_airport_names.py")
    run("fetch_wikidata.py")
    run("geocode_unesco.py")
    # ISO 3166-2 subdivisions are cached per site; only missing records trigger
    # an API call, so running both resolvers weekly stays inside rate limits.
    run("fetch_subdivisions.py")
    if not args.quick:
        run("fetch_subdivisions_nominatim.py")

    if not args.quick:
        wiki_env = {"REFRESH_WIKI": "1"} if (args.refresh_wiki or first_week) else {}
        run("enrich_wiki.py", env=wiki_env)
        if first_week:
            run("check_websites.py")
        run("rank_unesco.py")
        run("enrich_osm.py", "--budget", str(args.budget))

    run("build_china.py", required=True)
    run("build_world.py", required=True)
    run("validate_data.py", required=True)
    run("build_site.py", required=True)
    run("changelog.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
