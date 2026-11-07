#!/usr/bin/env python3
"""Record meaningful changes between weekly builds.

The state file stores a per-record fingerprint of the fields that travellers
care about (names, introductions, category, visa summary, transport facilities
and hotel names).  A changelog file and a human-readable CHANGELOG.md entry are
written only when something actually changed.

Outputs:
  data/state.json
  data/changelog/YYYY-MM-DD.json
  CHANGELOG.md
"""
from __future__ import annotations

import sys

from common import DATA, ROOT, load_json, now_iso, save_json, stable_hash, today

STATE = DATA / "state.json"
CHANGELOG_DIR = DATA / "changelog"

WATCH_FIELDS = [
    "name_zh", "name_en", "category", "tier", "visa_summary",
    "intro_zh", "intro_en", "intro_local", "hotels", "transport",
    "danger", "year", "criteria", "images",
]


def fingerprint(site: dict) -> str:
    payload = {k: site.get(k) for k in WATCH_FIELDS}
    # Hotels and transport are lists of dicts; keep only the stable, user-visible parts.
    if isinstance(payload.get("hotels"), list):
        payload["hotels"] = [
            (h.get("name"), h.get("distance_km"), h.get("kind")) for h in payload["hotels"]
        ]
    if isinstance(payload.get("transport"), dict):
        t = payload["transport"]
        payload["transport"] = {
            "airports": [(a.get("name"), a.get("distance_km")) for a in t.get("airports", [])],
            "hsr": [(a.get("name"), a.get("distance_km")) for a in t.get("high_speed_stations", [])],
            "ferry": [(a.get("name"), a.get("distance_km")) for a in t.get("ferry_terminals", [])],
            "distance_beijing_km": t.get("distance_beijing_km"),
        }
    if isinstance(payload.get("images"), list):
        payload["images"] = [i.get("url") for i in payload["images"]]
    return stable_hash(payload)


def field_diffs(old_site: dict, new_site: dict) -> list[str]:
    changed = []
    for field in WATCH_FIELDS:
        if field in ("hotels", "transport", "images"):
            continue
        if old_site.get(field) != new_site.get(field):
            changed.append(field)
    if [h.get("name") for h in old_site.get("hotels", [])] != [h.get("name") for h in new_site.get("hotels", [])]:
        changed.append("hotels")
    old_t = old_site.get("transport") or {}
    new_t = new_site.get("transport") or {}
    for key in ("airports", "high_speed_stations", "ferry_terminals"):
        if [x.get("name") for x in old_t.get(key, [])] != [x.get("name") for x in new_t.get(key, [])]:
            changed.append(f"transport.{key}")
    if old_t.get("distance_beijing_km") != new_t.get("distance_beijing_km"):
        changed.append("transport.distance_beijing_km")
    if [i.get("url") for i in old_site.get("images", [])] != [i.get("url") for i in new_site.get("images", [])]:
        changed.append("images")
    return sorted(set(changed))


def main() -> int:
    state = load_json(STATE, {}) or {}
    old_sites = state.get("sites", {})
    old_records = state.get("records", {})

    china = (load_json(DATA / "china.json", {}) or {}).get("sites", [])
    world = (load_json(DATA / "world.json", {}) or {}).get("sites", [])
    current = {s["id"]: s for s in china + world}

    added, removed, changed = [], [], []
    for sid, site in current.items():
        if sid not in old_sites:
            added.append({"id": sid, "name": site.get("name_zh") or site.get("name_en")})
        else:
            old = old_records.get(sid, {})
            fields = field_diffs(old, site)
            if fields:
                changed.append({"id": sid, "name": site.get("name_zh") or site.get("name_en"), "fields": fields})
    for sid in old_sites:
        if sid not in current:
            removed.append({"id": sid, "name": (old_records.get(sid) or {}).get("name_zh")
                            or (old_records.get(sid) or {}).get("name_en") or ""})

    first_run = not old_sites
    new_state = {
        "generated_at": now_iso(),
        "counts": {"china": len(china), "world": len(world)},
        "sites": {sid: fingerprint(site) for sid, site in current.items()},
        "records": {
            sid: {
                "name_zh": site.get("name_zh"), "name_en": site.get("name_en"),
                **{k: site.get(k) for k in WATCH_FIELDS if k not in ("hotels", "transport", "images")},
                "hotels": site.get("hotels", []),
                "transport": site.get("transport", {}),
                "images": site.get("images", []),
            }
            for sid, site in current.items()
        },
    }
    save_json(STATE, new_state)

    if first_run:
        path = ROOT / "CHANGELOG.md"
        if not path.exists():
            path.write_text(
                "# 变更记录 / Changelog\n\n"
                f"## {today()} — initial dataset\n\n"
                f"- 中国 5A：{len(china):,} 条；海外世界遗产：{len(world):,} 条。\n"
                "- 首次构建，作为后续每周变更对比的基线。\n",
                encoding="utf-8",
            )
        print("first run: state initialized and baseline changelog written")
        return 0
    if not (added or removed or changed):
        print("no changes")
        return 0

    CHANGELOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": today(),
        "generated_at": now_iso(),
        "counts": new_state["counts"],
        "added": added,
        "removed": removed,
        "changed": changed,
    }
    save_json(CHANGELOG_DIR / f"{today()}.json", entry)

    lines = [f"\n## {today()}", "",
             f"- 中国 5A：{len(china):,} 条；海外世界遗产：{len(world):,} 条。",
             f"- 新增 {len(added)} 条，移除 {len(removed)} 条，更新 {len(changed)} 条。"]
    if added:
        lines.append("- 新增：" + "、".join(x["name"] or x["id"] for x in added[:20]) +
                     (" …" if len(added) > 20 else ""))
    if removed:
        lines.append("- 移除：" + "、".join(x["name"] or x["id"] for x in removed[:20]))
    if changed:
        field_counts: dict[str, int] = {}
        for x in changed:
            for f in x["fields"]:
                field_counts[f] = field_counts.get(f, 0) + 1
        summary = "、".join(f"{k} × {v}" for k, v in sorted(field_counts.items(), key=lambda kv: -kv[1])[:8])
        lines.append(f"- 变更字段：{summary}")
    path = ROOT / "CHANGELOG.md"
    if not path.exists():
        path.write_text("# 变更记录 / Changelog\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"changelog: +{len(added)} -{len(removed)} ~{len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
