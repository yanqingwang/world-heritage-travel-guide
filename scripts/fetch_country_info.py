#!/usr/bin/env python3
"""Build data/raw/country_info.json — practical per-country facts for travellers.

Sources:
  * mledoze/countries (MIT/OAT): currency, timezones, driving side, IDD prefix,
    UN membership region info.
  * World plug-type mapping (curated static table; plug types are stable facts
    that no free API covers reliably).

Output keys per ISO2: {currency_code, currency_name, currency_symbol,
timezones, timezone_utc, drives_side, idd, plug_types, voltage_hz}
"""
from __future__ import annotations

import json
import sys

from common import RAW, http_get, save_json

SOURCE_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"

# Plug types / voltage by ISO2, from the standard IEC world plug map.
# "A/B" etc.; voltage string like "220V/50Hz".
PLUGS = {
    "AD": ("C,F", "230V/50Hz"), "AE": ("C,D,G", "220V/50Hz"), "AF": ("C,F", "220V/50Hz"),
    "AG": ("A,B", "230V/60Hz"), "AL": ("C,F", "230V/50Hz"), "AM": ("C,F", "230V/50Hz"),
    "AO": ("C,F", "220V/50Hz"), "AR": ("C,I", "220V/50Hz"), "AT": ("C,F", "230V/50Hz"),
    "AU": ("I", "230V/50Hz"), "AZ": ("C,F", "220V/50Hz"), "BA": ("C,F", "230V/50Hz"),
    "BB": ("A,B", "115V/50Hz"), "BD": ("C,D,G,K", "220V/50Hz"), "BE": ("C,F", "230V/50Hz"),
    "BF": ("C,E", "220V/50Hz"), "BG": ("C,F", "230V/50Hz"), "BH": ("C,D,G", "230V/50Hz"),
    "BJ": ("C,E", "220V/50Hz"), "BO": ("A,C", "230V/50Hz"), "BR": ("C,N", "127/220V/60Hz"),
    "BW": ("D,G,M", "231V/50Hz"), "BY": ("C,F", "230V/50Hz"), "BZ": ("A,B,G", "110/220V/60Hz"),
    "CA": ("A,B", "120V/60Hz"), "CD": ("C,E", "220V/50Hz"), "CF": ("C,E", "220V/50Hz"),
    "CG": ("C,E", "230V/50Hz"), "CH": ("C,J", "230V/50Hz"), "CI": ("C,E", "220V/50Hz"),
    "CL": ("C,L", "220V/50Hz"), "CM": ("C,E", "220V/50Hz"), "CN": ("A,C,I", "220V/50Hz"),
    "CO": ("A,B", "110V/60Hz"), "CR": ("A,B", "120V/60Hz"), "CU": ("A,B,C,L", "110/220V/60Hz"),
    "CV": ("C,F", "230V/50Hz"), "CY": ("G", "230V/50Hz"), "CZ": ("C,F", "230V/50Hz"),
    "DE": ("C,F", "230V/50Hz"), "DK": ("C,E,K", "230V/50Hz"), "DM": ("D,G", "230V/50Hz"),
    "DO": ("A,B", "110V/60Hz"), "DZ": ("C,E", "230V/50Hz"), "EC": ("A,B", "120V/60Hz"),
    "EE": ("C,F", "230V/50Hz"), "EG": ("C,F", "220V/50Hz"), "ER": ("C,F", "230V/50Hz"),
    "ES": ("C,F", "230V/50Hz"), "ET": ("C,F", "220V/50Hz"), "FI": ("C,F", "230V/50Hz"),
    "FJ": ("I", "240V/50Hz"), "FM": ("A,B", "120V/60Hz"), "FR": ("C,E", "230V/50Hz"),
    "GA": ("C", "220V/50Hz"), "GB": ("G", "230V/50Hz"), "GE": ("C,F", "220V/50Hz"),
    "GH": ("D,G", "230V/50Hz"), "GM": ("G", "230V/50Hz"), "GR": ("C,F", "230V/50Hz"),
    "GT": ("A,B", "120V/60Hz"), "GW": ("C,F", "220V/50Hz"), "HN": ("A,B", "110V/60Hz"),
    "HR": ("C,F", "230V/50Hz"), "HT": ("A,B", "110V/60Hz"), "HU": ("C,F", "230V/50Hz"),
    "ID": ("C,F", "230V/50Hz"), "IE": ("G", "230V/50Hz"), "IL": ("C,H", "230V/50Hz"),
    "IN": ("C,D,M", "230V/50Hz"), "IQ": ("C,D,G", "230V/50Hz"), "IR": ("C,F", "230V/50Hz"),
    "IS": ("C,F", "230V/50Hz"), "IT": ("C,F,L", "230V/50Hz"), "JM": ("A,B", "110V/50Hz"),
    "JO": ("C,D,G", "230V/50Hz"), "JP": ("A,B", "100V/50-60Hz"), "KE": ("G", "240V/50Hz"),
    "KG": ("C,F", "220V/50Hz"), "KH": ("A,C,G", "230V/50Hz"), "KI": ("I", "240V/50Hz"),
    "KM": ("C,E", "220V/50Hz"), "KN": ("D,G", "230V/60Hz"), "KP": ("C,F", "220V/50Hz"),
    "KR": ("C,F", "220V/60Hz"), "KZ": ("C,F", "220V/50Hz"), "LA": ("A,B,C,E,F", "230V/50Hz"),
    "LB": ("C,D,G", "220V/50Hz"), "LC": ("D,G", "240V/50Hz"), "LK": ("D,G", "230V/50Hz"),
    "LS": ("M", "220V/50Hz"), "LT": ("C,F", "230V/50Hz"), "LU": ("C,F", "230V/50Hz"),
    "LV": ("C,F", "230V/50Hz"), "LY": ("C,F", "127/230V/50Hz"), "MA": ("C,E", "220V/50Hz"),
    "ME": ("C,F", "230V/50Hz"), "MG": ("C,E", "220V/50Hz"), "MH": ("A,B", "120V/60Hz"),
    "ML": ("C,E", "220V/50Hz"), "MM": ("C,D,F,G", "230V/50Hz"), "MN": ("C,F", "230V/50Hz"),
    "MR": ("C", "220V/50Hz"), "MT": ("G", "230V/50Hz"), "MU": ("C,G", "230V/50Hz"),
    "MW": ("G", "230V/50Hz"), "MX": ("A,B", "127V/60Hz"), "MY": ("G", "240V/50Hz"),
    "MZ": ("C,F", "220V/50Hz"), "NA": ("D,M", "220V/50Hz"), "NE": ("C,D,E", "220V/50Hz"),
    "NG": ("D,G", "230V/50Hz"), "NI": ("A,B", "120V/60Hz"), "NL": ("C,F", "230V/50Hz"),
    "NO": ("C,F", "230V/50Hz"), "NP": ("C,D,M", "230V/50Hz"), "NZ": ("I", "230V/50Hz"),
    "OM": ("C,G", "240V/50Hz"), "PA": ("A,B", "120V/60Hz"), "PE": ("A,C", "220V/60Hz"),
    "PG": ("I", "240V/50Hz"), "PH": ("A,B,C", "220V/60Hz"), "PK": ("C,D,G", "230V/50Hz"),
    "PL": ("C,F", "230V/50Hz"), "PS": ("C,H", "230V/50Hz"), "PT": ("C,F", "230V/50Hz"),
    "PW": ("A,B", "120V/60Hz"), "PY": ("C", "220V/50Hz"), "QA": ("D,G", "240V/50Hz"),
    "RO": ("C,F", "230V/50Hz"), "RS": ("C,F", "230V/50Hz"), "RU": ("C,F", "220V/50Hz"),
    "RW": ("C,J", "230V/50Hz"), "SA": ("G", "230V/60Hz"), "SB": ("I,G", "230V/50Hz"),
    "SC": ("G", "240V/50Hz"), "SD": ("C,D", "230V/50Hz"), "SE": ("C,F", "230V/50Hz"),
    "SG": ("G", "230V/50Hz"), "SI": ("C,F", "230V/50Hz"), "SK": ("C,F", "230V/50Hz"),
    "SL": ("D,G", "230V/50Hz"), "SM": ("C,F", "230V/50Hz"), "SN": ("C,D,E,K", "230V/50Hz"),
    "SR": ("A,C,F", "127/220V/60Hz"), "SS": ("C,D", "230V/50Hz"), "ST": ("C,F", "230V/50Hz"),
    "SV": ("A,B", "120V/60Hz"), "SY": ("C,E", "220V/50Hz"), "TD": ("C,E", "220V/50Hz"),
    "TH": ("A,B,C", "220V/50Hz"), "TJ": ("C,F", "220V/50Hz"), "TM": ("C,F", "220V/50Hz"),
    "TN": ("C,E", "230V/50Hz"), "TR": ("C,F", "230V/50Hz"), "TZ": ("D,G", "230V/50Hz"),
    "UA": ("C,F", "230V/50Hz"), "UG": ("G", "240V/50Hz"), "US": ("A,B", "120V/60Hz"),
    "UY": ("C,F", "220V/50Hz"), "UZ": ("C,F", "220V/50Hz"), "VA": ("C,F", "230V/50Hz"),
    "VE": ("A,B", "120V/60Hz"), "VN": ("A,C", "220V/50Hz"), "VU": ("I", "230V/50Hz"),
    "XJ": ("C,F", "230V/50Hz"), "YE": ("D,G", "230V/50Hz"), "ZA": ("M,N", "230V/50Hz"),
    "ZM": ("C,D,G", "230V/50Hz"), "ZW": ("D,G", "230V/50Hz"),
}

# Left/right-hand traffic by ISO2 ("left" = drive on the left).
DRIVE_SIDE = {
    "AG": "left", "AU": "left", "BB": "left", "BD": "left", "BN": "left",
    "BW": "left", "BZ": "right", "CA": "right", "CD": "right", "CF": "right",
    "CG": "right", "CH": "right", "CN": "right", "CM": "right", "CY": "left",
    "DM": "left", "FJ": "left", "GB": "left", "GD": "left", "GH": "left",
    "GM": "left", "GR": "right", "GY": "left", "HK": "left", "ID": "left",
    "IE": "left", "IN": "left", "JM": "left", "JP": "left", "KE": "left",
    "KI": "left", "KN": "left", "KR": "right", "LK": "left", "LS": "left",
    "MO": "left", "MT": "left", "MU": "left", "MV": "left", "MW": "left",
    "MY": "left", "MZ": "left", "NA": "left", "NP": "left", "NZ": "left",
    "PG": "left", "PK": "left", "SB": "left", "SC": "left", "SG": "left",
    "SL": "right", "SR": "left", "SZ": "left", "TH": "left", "TZ": "left",
    "UG": "left", "US": "right", "VA": "right", "VU": "left", "ZA": "left",
    "ZM": "left", "ZW": "left",
}

# Main UTC offset per ISO2 (largest population centre; IANA-derived).
TIMEZONE_MAIN = {
    "AD": "UTC+01:00",
    "AE": "UTC+04:00",
    "AF": "UTC+04:30",
    "AG": "UTC-04:00",
    "AL": "UTC+01:00",
    "AM": "UTC+04:00",
    "AO": "UTC+01:00",
    "AR": "UTC-03:00",
    "AT": "UTC+01:00",
    "AU": "UTC+10:00",
    "AZ": "UTC+04:00",
    "BA": "UTC+01:00",
    "BB": "UTC-04:00",
    "BD": "UTC+06:00",
    "BE": "UTC+01:00",
    "BF": "UTC+00:00",
    "BG": "UTC+02:00",
    "BH": "UTC+03:00",
    "BJ": "UTC+01:00",
    "BO": "UTC-04:00",
    "BR": "UTC-03:00",
    "BW": "UTC+02:00",
    "BY": "UTC+03:00",
    "BZ": "UTC-06:00",
    "CA": "UTC-05:00",
    "CD": "UTC+02:00",
    "CF": "UTC+01:00",
    "CG": "UTC+01:00",
    "CH": "UTC+01:00",
    "CI": "UTC+00:00",
    "CL": "UTC-04:00",
    "CM": "UTC+01:00",
    "CN": "UTC+08:00",
    "CO": "UTC-05:00",
    "CR": "UTC-06:00",
    "CU": "UTC-05:00",
    "CV": "UTC-01:00",
    "CY": "UTC+02:00",
    "CZ": "UTC+01:00",
    "DE": "UTC+01:00",
    "DK": "UTC+01:00",
    "DM": "UTC-04:00",
    "DO": "UTC-04:00",
    "DZ": "UTC+01:00",
    "EC": "UTC-05:00",
    "EE": "UTC+02:00",
    "EG": "UTC+02:00",
    "ER": "UTC+03:00",
    "ES": "UTC+01:00",
    "ET": "UTC+03:00",
    "FI": "UTC+02:00",
    "FJ": "UTC+12:00",
    "FM": "UTC+11:00",
    "FR": "UTC+01:00",
    "GA": "UTC+01:00",
    "GB": "UTC+00:00",
    "GE": "UTC+04:00",
    "GH": "UTC+00:00",
    "GM": "UTC+00:00",
    "GR": "UTC+02:00",
    "GT": "UTC-06:00",
    "GW": "UTC+00:00",
    "HN": "UTC-06:00",
    "HR": "UTC+01:00",
    "HT": "UTC-05:00",
    "HU": "UTC+01:00",
    "ID": "UTC+07:00",
    "IE": "UTC+00:00",
    "IL": "UTC+02:00",
    "IN": "UTC+05:30",
    "IQ": "UTC+03:00",
    "IR": "UTC+03:30",
    "IS": "UTC+00:00",
    "IT": "UTC+01:00",
    "JM": "UTC-05:00",
    "JO": "UTC+03:00",
    "JP": "UTC+09:00",
    "KE": "UTC+03:00",
    "KG": "UTC+06:00",
    "KH": "UTC+07:00",
    "KI": "UTC+12:00",
    "KM": "UTC+03:00",
    "KN": "UTC-04:00",
    "KP": "UTC+09:00",
    "KR": "UTC+09:00",
    "KZ": "UTC+06:00",
    "LA": "UTC+07:00",
    "LB": "UTC+02:00",
    "LC": "UTC-04:00",
    "LK": "UTC+05:30",
    "LS": "UTC+02:00",
    "LT": "UTC+02:00",
    "LU": "UTC+01:00",
    "LV": "UTC+02:00",
    "LY": "UTC+02:00",
    "MA": "UTC+01:00",
    "ME": "UTC+01:00",
    "MG": "UTC+03:00",
    "MH": "UTC+12:00",
    "ML": "UTC+00:00",
    "MM": "UTC+06:30",
    "MN": "UTC+08:00",
    "MR": "UTC+00:00",
    "MT": "UTC+01:00",
    "MU": "UTC+04:00",
    "MW": "UTC+02:00",
    "MX": "UTC-06:00",
    "MY": "UTC+08:00",
    "MZ": "UTC+02:00",
    "NA": "UTC+02:00",
    "NE": "UTC+01:00",
    "NG": "UTC+01:00",
    "NI": "UTC-06:00",
    "NL": "UTC+01:00",
    "NO": "UTC+01:00",
    "NP": "UTC+05:45",
    "NZ": "UTC+12:00",
    "OM": "UTC+04:00",
    "PA": "UTC-05:00",
    "PE": "UTC-05:00",
    "PG": "UTC+10:00",
    "PH": "UTC+08:00",
    "PK": "UTC+05:00",
    "PL": "UTC+01:00",
    "PS": "UTC+02:00",
    "PT": "UTC+00:00",
    "PW": "UTC+09:00",
    "PY": "UTC-04:00",
    "QA": "UTC+03:00",
    "RO": "UTC+02:00",
    "RS": "UTC+01:00",
    "RU": "UTC+03:00",
    "RW": "UTC+02:00",
    "SA": "UTC+03:00",
    "SB": "UTC+11:00",
    "SC": "UTC+04:00",
    "SD": "UTC+02:00",
    "SE": "UTC+01:00",
    "SG": "UTC+08:00",
    "SI": "UTC+01:00",
    "SK": "UTC+01:00",
    "SL": "UTC+00:00",
    "SM": "UTC+01:00",
    "SN": "UTC+00:00",
    "SR": "UTC-03:00",
    "SS": "UTC+02:00",
    "ST": "UTC+00:00",
    "SV": "UTC-06:00",
    "SY": "UTC+03:00",
    "TD": "UTC+01:00",
    "TH": "UTC+07:00",
    "TJ": "UTC+05:00",
    "TM": "UTC+05:00",
    "TN": "UTC+01:00",
    "TR": "UTC+03:00",
    "TZ": "UTC+03:00",
    "UA": "UTC+02:00",
    "UG": "UTC+03:00",
    "US": "UTC-05:00",
    "UY": "UTC-03:00",
    "UZ": "UTC+05:00",
    "VA": "UTC+01:00",
    "VE": "UTC-04:00",
    "VN": "UTC+07:00",
    "VU": "UTC+11:00",
    "XJ": "UTC+02:00",
    "YE": "UTC+03:00",
    "ZA": "UTC+02:00",
    "ZM": "UTC+02:00",
    "ZW": "UTC+02:00",
}

CURRENCY_ZH = {
    "USD": ("美元", "$"), "EUR": ("欧元", "€"), "JPY": ("日元", "¥"), "GBP": ("英镑", "£"),
    "CNY": ("人民币", "¥"), "KRW": ("韩元", "₩"), "THB": ("泰铢", "฿"), "INR": ("印度卢比", "₹"),
    "RUB": ("卢布", "₽"), "TRY": ("土耳其里拉", "₺"), "CHF": ("瑞士法郎", "CHF"),
    "CAD": ("加拿大元", "C$"), "AUD": ("澳大利亚元", "A$"), "NZD": ("新西兰元", "NZ$"),
    "BRL": ("雷亚尔", "R$"), "MXN": ("墨西哥比索", "$"), "ARS": ("阿根廷比索", "$"),
    "EGP": ("埃及镑", "£"), "ZAR": ("兰特", "R"), "SAR": ("沙特里亚尔", "﷼"),
    "AED": ("迪拉姆", "د.إ"), "QAR": ("卡塔尔里亚尔", "﷼"), "IDR": ("印尼盾", "Rp"),
    "MYR": ("林吉特", "RM"), "PHP": ("菲律宾比索", "₱"), "VND": ("越南盾", "₫"),
    "SGD": ("新加坡元", "S$"), "ILS": ("谢克尔", "₪"), "SEK": ("瑞典克朗", "kr"),
    "NOK": ("挪威克朗", "kr"), "DKK": ("丹麦克朗", "kr"), "PLN": ("兹罗提", "zł"),
    "CZK": ("捷克克朗", "Kč"), "HUF": ("福林", "Ft"), "RON": ("列伊", "lei"),
    "CLP": ("智利比索", "$"), "COP": ("哥伦比亚比索", "$"), "PEN": ("索尔", "S/"),
}


def fetch_countries() -> list[dict] | None:
    r = http_get(SOURCE_URL, timeout=120, retries=3)
    if r is None or r.status_code != 200:
        doc = RAW / "mledoze_countries.json"
        if doc.exists():
            return json.loads(doc.read_text(encoding="utf-8"))
        return None
    RAW.joinpath("mledoze_countries.json").write_bytes(r.content)
    return json.loads(r.content.decode("utf-8"))


def main() -> int:
    rows = fetch_countries()
    if not rows:
        print("mledoze/countries unavailable; keeping previous output", file=sys.stderr)
        return 1

    # The GitHub snapshot dropped `timezones`/`car` fields; use curated tables
    # embedded in this file (no extra fetch, no repo-side JSON dependency).
    tz_map = TIMEZONE_MAIN
    drive_map = DRIVE_SIDE

    out: dict[str, dict] = {}
    for row in rows:
        iso2 = (row.get("cca2") or "").upper()
        if not iso2:
            continue
        currencies = row.get("currencies") or {}
        code, meta = next(iter(currencies.items()), ("", None))
        if isinstance(meta, dict):
            name, symbol = meta.get("name", ""), meta.get("symbol", "")
        else:  # legacy shape: {code: "Name"}
            name, symbol = (meta or ""), ""
        languages = row.get("languages") or {}
        # Store readable names ("Japanese", "Swiss German") instead of ISO 639-3
        # codes — the UI lists them as traveller-facing facts.
        lang_names = sorted(v if isinstance(v, str) and v else k
                            for k, v in languages.items())
        plug, volt = PLUGS.get(iso2, ("", ""))
        zh, _ = CURRENCY_ZH.get(code, ("", symbol))
        out[iso2] = {
            "currency_code": code,
            "currency_en": name,
            "currency_zh": zh or name,
            "currency_symbol": symbol,
            "timezone_main": tz_map.get(iso2, ""),
            "drives_side": drive_map.get(iso2, ""),
            "idd_prefix": ((row.get("idd") or {}).get("root") or "") +
                          ((row.get("idd") or {}).get("suffixes") or [""])[0],
            "languages": lang_names,
            "plug_types": plug,
            "voltage": volt,
        }

    save_json(RAW / "country_info.json", {
        "source": "https://github.com/mledoze/countries (MIT) + curated IEC plug/timezone/drive tables",
        "count": len(out),
        "items": out,
    })
    print(f"saved country info for {len(out)} countries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
