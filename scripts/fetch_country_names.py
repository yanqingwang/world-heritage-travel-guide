#!/usr/bin/env python3
"""Fill Chinese country and language names using Wikipedia langlinks.

Wikidata Query Service is occasionally unavailable; Wikipedia's API is a
reliable fallback for country names.  The script preserves all existing data.

Output: data/raw/countries.json (in place)
"""
from __future__ import annotations

import sys
import time

from common import RAW, load_json, save_json, wiki_api

# Wikipedia's zh langlinks sometimes return Taiwan / Hong Kong variants.  For a
# mainland-Chinese-facing dataset, normalise the names that would otherwise look
# inconsistent in the country filter.
COUNTRY_ZH_FIX = {
    "AM": "亚美尼亚", "AW": "阿鲁巴", "BF": "布基纳法索", "BI": "布隆迪",
    "BO": "玻利维亚", "BW": "博茨瓦纳", "CF": "中非共和国", "DO": "多米尼加",
    "FJ": "斐济", "GE": "格鲁吉亚", "GW": "几内亚比绍", "IE": "爱尔兰",
    "KM": "科摩罗", "KN": "圣基茨和尼维斯", "LI": "列支敦士登",
    "LK": "斯里兰卡", "LV": "拉脱维亚", "ME": "黑山", "MH": "马绍尔群岛",
    "MK": "北马其顿", "NG": "尼日利亚", "NR": "瑙鲁", "NU": "纽埃",
    "PS": "巴勒斯坦", "PW": "帕劳", "RO": "罗马尼亚", "SR": "苏里南",
    "SS": "南苏丹", "SX": "荷属圣马丁", "SZ": "埃斯瓦蒂尼", "TN": "突尼斯",
    "TO": "汤加", "TT": "特立尼达和多巴哥", "TV": "图瓦卢", "VE": "委内瑞拉",
    "ZW": "津巴布韦",
}

LANG_ZH = {
    "fr": "法语", "es": "西班牙语", "de": "德语", "it": "意大利语",
    "pt": "葡萄牙语", "ru": "俄语", "ar": "阿拉伯语", "ja": "日语",
    "ko": "韩语", "th": "泰语", "tr": "土耳其语", "vi": "越南语",
    "id": "印度尼西亚语", "nl": "荷兰语", "pl": "波兰语", "sv": "瑞典语",
    "da": "丹麦语", "no": "挪威语", "fi": "芬兰语", "cs": "捷克语",
    "hu": "匈牙利语", "ro": "罗马尼亚语", "el": "希腊语", "he": "希伯来语",
    "fa": "波斯语", "uk": "乌克兰语", "sr": "塞尔维亚语", "hr": "克罗地亚语",
    "bg": "保加利亚语", "sk": "斯洛伐克语", "sl": "斯洛文尼亚语",
    "lt": "立陶宛语", "lv": "拉脱维亚语", "et": "爱沙尼亚语",
    "ms": "马来语", "tl": "他加禄语", "sw": "斯瓦希里语", "af": "南非荷兰语",
    "am": "阿姆哈拉语", "ka": "格鲁吉亚语", "hy": "亚美尼亚语",
    "az": "阿塞拜疆语", "kk": "哈萨克语", "uz": "乌兹别克语",
    "mn": "蒙古语", "ne": "尼泊尔语", "si": "僧伽罗语", "km": "高棉语",
    "lo": "老挝语", "my": "缅甸语", "bn": "孟加拉语", "ur": "乌尔都语",
    "hi": "印地语", "fil": "菲律宾语", "mt": "马耳他语", "cy": "威尔士语",
    "ga": "爱尔兰语", "en": "英语", "zh": "中文",
}


def main() -> int:
    data = load_json(RAW / "countries.json", {}) or {}
    todo = [(iso, rec["en"]) for iso, rec in data.items() if not rec.get("zh") and rec.get("en")]
    print(f"{len(todo)} countries need Chinese names")
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        payload = wiki_api("en", {
            "action": "query", "titles": "|".join(t for _, t in chunk),
            "prop": "langlinks", "lllang": "zh", "redirects": 1,
        })
        pages = ((payload or {}).get("query") or {}).get("pages", {})
        if isinstance(pages, dict):
            pages = list(pages.values())
        titles = {t for _, t in chunk}
        by_title = {p.get("title"): p for p in pages or []}
        for iso, title in chunk:
            page = by_title.get(title)
            if page and page.get("langlinks"):
                data[iso]["zh"] = page["langlinks"][0].get("title") or page["langlinks"][0].get("*", "")
        time.sleep(0.3)

    # Fallback for titles that did not resolve in the batch query (territories,
    # renamed states, redirects).
    from common import wiki_page, wiki_search

    missing = [(iso, rec["en"]) for iso, rec in data.items() if not rec.get("zh") and rec.get("en")]
    for i, (iso, name) in enumerate(missing, 1):
        hits = wiki_search("en", name, 1)
        if not hits:
            continue
        page = wiki_page("en", hits[0]["title"], props="langlinks")
        for ll in (page or {}).get("langlinks", []) or []:
            if ll.get("lang") == "zh":
                data[iso]["zh"] = ll.get("title") or ll.get("*", "")
                break
        if i % 20 == 0:
            print(f"fallback {i}/{len(missing)}")
        time.sleep(0.25)

    for iso, zh in COUNTRY_ZH_FIX.items():
        if iso in data:
            data[iso]["zh"] = zh

    for rec in data.values():
        for lang in rec.get("langs", []):
            code = lang.get("code", "")
            if not lang.get("zh") and code in LANG_ZH:
                lang["zh"] = LANG_ZH[code]

    save_json(RAW / "countries.json", data)
    print(f"filled Chinese names: {sum(1 for v in data.values() if v.get('zh'))}/{len(data)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
