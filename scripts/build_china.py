#!/usr/bin/env python3
"""Merge the China 5A dataset into the public JSON model.

Output: data/china.json
"""
from __future__ import annotations

import re
import sys

from common import (
    CACHE, DATA, RAW, haversine_km, load_json, now_iso, pinyin_slug, save_json,
    translate, unique_slug,
)
from transport import nearest

PROVINCE_EN = {
    "北京": "Beijing", "天津": "Tianjin", "河北": "Hebei", "山西": "Shanxi",
    "内蒙古": "Inner Mongolia", "辽宁": "Liaoning", "吉林": "Jilin",
    "黑龙江": "Heilongjiang", "上海": "Shanghai", "江苏": "Jiangsu",
    "浙江": "Zhejiang", "安徽": "Anhui", "福建": "Fujian", "江西": "Jiangxi",
    "山东": "Shandong", "河南": "Henan", "湖北": "Hubei", "湖南": "Hunan",
    "广东": "Guangdong", "广西": "Guangxi", "海南": "Hainan", "重庆": "Chongqing",
    "四川": "Sichuan", "贵州": "Guizhou", "云南": "Yunnan", "西藏": "Tibet",
    "陕西": "Shaanxi", "甘肃": "Gansu", "青海": "Qinghai", "宁夏": "Ningxia",
    "新疆": "Xinjiang",
}

# ISO 3166-2:CN.  Keeping the code on every record lets the site use one
# country -> province/state cascade for both datasets.
PROVINCE_ISO = {
    "北京": "CN-BJ", "天津": "CN-TJ", "河北": "CN-HE", "山西": "CN-SX",
    "内蒙古": "CN-NM", "辽宁": "CN-LN", "吉林": "CN-JL", "黑龙江": "CN-HL",
    "上海": "CN-SH", "江苏": "CN-JS", "浙江": "CN-ZJ", "安徽": "CN-AH",
    "福建": "CN-FJ", "江西": "CN-JX", "山东": "CN-SD", "河南": "CN-HA",
    "湖北": "CN-HB", "湖南": "CN-HN", "广东": "CN-GD", "广西": "CN-GX",
    "海南": "CN-HI", "重庆": "CN-CQ", "四川": "CN-SC", "贵州": "CN-GZ",
    "云南": "CN-YN", "西藏": "CN-XZ", "陕西": "CN-SN", "甘肃": "CN-GS",
    "青海": "CN-QH", "宁夏": "CN-NX", "新疆": "CN-XJ",
    "台湾": "CN-TW", "香港": "CN-HK", "澳门": "CN-MO",
}

CITY_EN = {    "北京市": "Beijing", "上海市": "Shanghai", "天津市": "Tianjin", "重庆市": "Chongqing",
    "杭州市": "Hangzhou", "苏州市": "Suzhou", "南京市": "Nanjing", "无锡市": "Wuxi",
    "扬州市": "Yangzhou", "常州市": "Changzhou", "镇江市": "Zhenjiang", "徐州市": "Xuzhou",
    "淮安市": "Huai'an", "盐城市": "Yancheng", "连云港市": "Lianyungang",
    "西安市": "Xi'an", "咸阳市": "Xianyang", "延安市": "Yan'an", "渭南市": "Weinan",
    "宝鸡市": "Baoji", "汉中市": "Hanzhong", "榆林市": "Yulin", "商洛市": "Shangluo",
    "成都市": "Chengdu", "乐山市": "Leshan", "阿坝藏族羌族自治州": "Aba Tibetan and Qiang Autonomous Prefecture",
    "甘孜藏族自治州": "Ganzi Tibetan Autonomous Prefecture",
    "凉山彝族自治州": "Liangshan Yi Autonomous Prefecture",
    "绵阳市": "Mianyang", "雅安市": "Ya'an", "广元市": "Guangyuan", "南充市": "Nanchang",
    "昆明市": "Kunming", "大理白族自治州": "Dali Bai Autonomous Prefecture",
    "丽江市": "Lijiang", "迪庆藏族自治州": "Diqing Tibetan Autonomous Prefecture",
    "西双版纳傣族自治州": "Xishuangbanna Dai Autonomous Prefecture",
    "保山市": "Baoshan", "文山壮族苗族自治州": "Wenshan Zhuang and Miao Autonomous Prefecture",
    "红河哈尼族彝族自治州": "Honghe Hani and Yi Autonomous Prefecture",
    "武汉市": "Wuhan", "宜昌市": "Yichang", "十堰市": "Shiyan", "恩施土家族苗族自治州": "Enshi Tujia and Miao Autonomous Prefecture",
    "长沙市": "Changsha", "张家界市": "Zhangjiajie", "湘西土家族苗族自治州": "Xiangxi Tujia and Miao Autonomous Prefecture",
    "广州市": "Guangzhou", "深圳市": "Shenzhen", "珠海市": "Zhuhai", "佛山市": "Foshan",
    "惠州市": "Huizhou", "韶关市": "Shaoguan", "清远市": "Qingyuan", "梅州市": "Meizhou",
    "南宁市": "Nanning", "桂林市": "Guilin", "柳州市": "Liuzhou", "北海市": "Beihai",
    "海口市": "Haikou", "三亚市": "Sanya", "儋州市": "Danzhou",
    "福州市": "Fuzhou", "厦门市": "Xiamen", "泉州市": "Quanzhou", "南平市": "Nanping",
    "龙岩市": "Longyan", "三明市": "Sanming", "宁德市": "Ningde", "莆田市": "Putian",
    "南昌市": "Nanchang", "九江市": "Jiujiang", "上饶市": "Shangrao", "景德镇市": "Jingdezhen",
    "赣州市": "Ganzhou", "吉安市": "Ji'an", "抚州市": "Fuzhou", "宜春市": "Yichun",
    "济南市": "Jinan", "青岛市": "Qingdao", "烟台市": "Yantai", "威海市": "Weihai",
    "泰安市": "Tai'an", "济宁市": "Jining", "临沂市": "Linyi", "潍坊市": "Weifang",
    "淄博市": "Zibo", "枣庄市": "Zaozhuang", "东营市": "Dongying",
    "郑州市": "Zhengzhou", "洛阳市": "Luoyang", "开封市": "Kaifeng", "安阳市": "Anyang",
    "焦作市": "Jiaozuo", "新乡市": "Xinxiang", "南阳市": "Nanyang", "信阳市": "Xinyang",
    "合肥市": "Hefei", "黄山市": "Huangshan", "池州市": "Chizhou", "安庆市": "Anqing",
    "六安市": "Lu'an", "宣城市": "Xuancheng", "芜湖市": "Wuhu",
    "太原市": "Taiyuan", "大同市": "Datong", "晋中市": "Jinzhong", "临汾市": "Linfen",
    "运城市": "Yuncheng", "忻州市": "Xinzhou", "长治市": "Changzhi", "晋城市": "Jincheng",
    "石家庄市": "Shijiazhuang", "保定市": "Baoding", "承德市": "Chengde", "秦皇岛市": "Qinhuangdao",
    "唐山市": "Tangshan", "邯郸市": "Handan", "邢台市": "Xingtai", "张家口市": "Zhangjiakou",
    "哈尔滨市": "Harbin", "沈阳市": "Shenyang", "大连市": "Dalian", "长春市": "Changchun",
    "吉林市": "Jilin", "延边朝鲜族自治州": "Yanbian Korean Autonomous Prefecture",
    "呼和浩特市": "Hohhot", "鄂尔多斯市": "Ordos", "呼伦贝尔市": "Hulunbuir",
    "银川市": "Yinchuan", "中卫市": "Zhongwei", "西宁市": "Xining",
    "海北藏族自治州": "Haibei Tibetan Autonomous Prefecture",
    "海南藏族自治州": "Hainan Tibetan Autonomous Prefecture",
    "乌鲁木齐市": "Urumqi", "吐鲁番市": "Turpan", "喀什地区": "Kashgar Prefecture",
    "阿克苏地区": "Aksu Prefecture", "伊犁哈萨克自治州": "Ili Kazakh Autonomous Prefecture",
    "阿勒泰地区": "Altay Prefecture", "昌吉回族自治州": "Changji Hui Autonomous Prefecture",
    "博尔塔拉蒙古自治州": "Bortala Mongol Autonomous Prefecture",
    "拉萨市": "Lhasa", "日喀则市": "Shigatse", "林芝市": "Nyingchi", "山南市": "Shannan",
}

SUFFIX_EN = [
    ("旅游度假区", "Tourist Resort"), ("文化旅游区", "Cultural Tourism Area"),
    ("风景名胜区", "Scenic and Historic Area"), ("旅游景区", "Scenic Area"),
    ("旅游区", "Tourist Area"), ("景区", "Scenic Area"),
    ("古镇", "Ancient Town"), ("古城", "Ancient City"), ("古村", "Ancient Village"),
    ("国家公园", "National Park"), ("湿地公园", "Wetland Park"),
    ("森林公园", "Forest Park"), ("地质公园", "Geopark"),
    ("博物馆", "Museum"), ("博物院", "Museum"), ("纪念馆", "Memorial Hall"),
    ("石窟", "Grottoes"), ("大峡谷", "Grand Canyon"), ("瀑布", "Waterfall"),
    ("山", "Mountain"), ("湖", "Lake"), ("寺", "Temple"), ("宫", "Palace"),
]

CATEGORIES = {
    "natural": ("自然风光", "Natural scenery"),
    "cultural": ("人文古迹", "Cultural heritage"),
    "historic": ("历史遗址", "Historic site"),
    "mixed": ("自然人文", "Natural & cultural"),
    "theme": ("主题乐园", "Theme park"),
    "resort": ("度假休闲", "Resort & leisure"),
    "museum": ("博物馆", "Museum"),
    "geology": ("地质奇观", "Geological wonder"),
    "religious": ("宗教文化", "Religious culture"),
    "red": ("红色旅游", "Red tourism"),
    "folk": ("民俗文化", "Folk culture"),
    "wetland": ("生态湿地", "Wetland ecology"),
    "mountain": ("山地风光", "Mountain scenery"),
    "desert": ("草原沙漠", "Grassland & desert"),
    "coastal": ("海滨度假", "Coastal resort"),
    "town": ("古镇村落", "Ancient town"),
    "garden": ("皇家园林", "Royal garden"),
    "grotto": ("石窟艺术", "Grotto art"),
    "water": ("水利工程", "Water conservancy"),
}


def classify(name: str, intro: str) -> str:
    text = f"{name} {intro}"
    if re.search("主题|乐园|方特|欢乐谷|迪士尼|海洋公园|动物园|植物园", text):
        return "theme"
    if re.search("温泉|滑雪|度假", text):
        return "resort"
    if re.search("革命|红色|长征|战役|会议旧址|抗战", text):
        return "red"
    if re.search("石窟|摩崖|壁画", text):
        return "grotto"
    if re.search("古镇|古城|古村|水乡|村落", text):
        return "town"
    if re.search("园林|皇家园林|避暑山庄", text):
        return "garden"
    if re.search("故宫|皇宫|皇陵|长城|关城|城墙|遗址|陵|墓|战场|会址|故居|旧址", text):
        return "historic"
    if re.search("湿地", text):
        return "wetland"
    if re.search("草原|沙漠|戈壁", text):
        return "desert"
    if re.search("海滨|海岛|海滩|海湾|海岸", text):
        return "coastal"
    # A temple mentioned in a mountain's introduction should not turn the whole
    # scenic area into "religious culture".  Only an explicit religious name
    # wins over the natural feature in the name.
    if re.search("寺|庙|宫|观|庵|祠|佛|禅|文殊|普陀|五台|峨眉|九华|武当|青城|"
                 "布达拉|大昭|塔尔|三清|梵净|鸡足", name):
        return "religious"
    if re.search("山|峰|雪山|峡谷|瀑布|森林|湖|河|江|泉|洞|冰川|保护区|自然", text):
        if re.search("峡谷|溶洞|喀斯特|丹霞|雅丹|冰川|地质", text):
            return "geology"
        if re.search("山|峰|雪山", text):
            return "mountain"
        return "natural"
    if re.search("寺|庙|宫|观|教堂|塔|坛|祠", text):
        return "religious"
    if re.search("水利|大坝|工程|都江堰|三峡", text):
        return "water"
    if re.search("民俗|文化|非遗|民族", text):
        return "folk"
    if re.search("博物馆|博物院|纪念馆|展览馆|美术馆", text):
        return "museum"
    return "mixed"


def english_name(site: dict, wiki: dict) -> tuple[str, str]:
    if wiki.get("en_title"):
        return wiki["en_title"], "wikipedia"
    base = site["name"]
    suffix_en = ""
    for zh, en in SUFFIX_EN:
        if base.endswith(zh) and len(base) > len(zh):
            base = base[: -len(zh)]
            suffix_en = en
            break
    if wiki.get("zh_title") and len(wiki["zh_title"]) < len(base):
        base = wiki["zh_title"]
    pinyin = "".join(__import__("pypinyin").lazy_pinyin(base)).strip()
    pinyin = pinyin[:1].upper() + pinyin[1:] if pinyin else base
    return f"{pinyin} {suffix_en}".strip(), "pinyin"


def city_en(city: str) -> str:
    if city in CITY_EN:
        return CITY_EN[city]
    suffix = ""
    base = city
    for zh, en in (("自治州", "Autonomous Prefecture"), ("地区", "Prefecture"),
                   ("新区", "New Area"), ("市", "City"), ("区", "District"),
                   ("县", "County"), ("盟", "League"), ("旗", "Banner")):
        if city.endswith(zh) and len(city) > len(zh):
            base, suffix = city[: -len(zh)], en
            break
    pinyin = "".join(__import__("pypinyin").lazy_pinyin(base)).strip()
    pinyin = pinyin[:1].upper() + pinyin[1:] if pinyin else base
    return f"{pinyin} {suffix}".strip()


def info_languages(wiki: dict, website_langs: dict) -> dict:
    wiki_langs = set(wiki.get("langs") or [])
    out = {
        "zh": True,
        "en": bool(wiki.get("en_title") or website_langs.get("en")),
        "ja": "ja" in wiki_langs or bool(website_langs.get("ja")),
        "ko": "ko" in wiki_langs or bool(website_langs.get("ko")),
        "source": [],
    }
    if wiki_langs:
        out["source"].append("Wikipedia language editions")
    if website_langs:
        out["source"].append("official website language switcher")
    return out


def main() -> int:
    official = load_json(RAW / "china_official.json", {}) or load_json(DATA / "official.json", {}) or {}
    sites = official.get("sites", [])
    wiki = (load_json(RAW / "china_wiki.json", {}) or {}).get("items", {})
    website_langs = load_json(RAW / "website_langs.json", {}) or {}
    previous = {s["id"]: s for s in (load_json(DATA / "china.json", {}) or {}).get("sites", [])}

    # Machine-translate the official intro and address once per unique string.
    # These calls used to run sequentially; eight workers cut the build from
    # tens of minutes to a few.
    texts = sorted({s.get("intro") for s in sites if s.get("intro")} |
                   {s.get("address") for s in sites if s.get("address")})
    translated: dict[str, str] = {}
    if texts:
        import concurrent.futures as futures

        def _translate(text: str) -> tuple[str, str | None]:
            return text, translate(text, "en")

        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            for text, value in pool.map(_translate, texts):
                if value:
                    translated[text] = value
    used: set[str] = set()
    out = []
    for i, site in enumerate(sites, 1):
        sid = site["id"]
        prev_site = previous.get(f"cn-{sid}", {})
        w = wiki.get(sid, {})
        name_en, name_en_source = english_name(site, w)
        intro_zh = site.get("intro") or ""
        intro_en = w.get("intro_en")
        intro_en_source = "wikipedia" if intro_en else None
        if not intro_en and intro_zh:
            intro_en = translated.get(intro_zh)
            intro_en_source = "machine_translation" if intro_en else None
        if not intro_en and prev_site.get("intro_en"):
            intro_en = prev_site["intro_en"]
            intro_en_source = prev_site.get("intro_en_source")
        address = site.get("address") or ""
        address_en = translated.get(address) if address else None
        address_en_source = "machine_translation" if address_en else None
        if not address_en and prev_site.get("address_en"):
            address_en = prev_site["address_en"]
            address_en_source = prev_site.get("address_en_source")

        osm = load_json(RAW / "osm" / f"china_{sid}.json", {}) or {}
        stations = osm.get("stations") or []
        high_speed = [s for s in stations if s.get("high_speed")][:3]
        rail = [s for s in stations if not s.get("high_speed")][:3]
        if not stations:
            high_speed = (prev_site.get("transport") or {}).get("high_speed_stations", [])
            rail = (prev_site.get("transport") or {}).get("railway_stations", [])
        airports = nearest(site["lat"], site["lon"], limit=3, max_km=250) or \
            (prev_site.get("transport") or {}).get("airports", [])
        cat = classify(site["name"], intro_zh)
        cat_zh, cat_en = CATEGORIES[cat]
        langs = info_languages(w, website_langs.get(sid, {}) or {})
        likely_open = bool(langs.get("en"))

        slug = unique_slug(site.get("slug") or pinyin_slug(site["name"]), used, sid)

        out.append({
            "id": f"cn-{sid}",
            "dataset": "china_5a",
            "country": "CN",
            "country_zh": "中国",
            "country_en": "China",
            "province_zh": site.get("province_full") or site.get("province"),
            "province_en": PROVINCE_EN.get(site.get("province"), site.get("province")),
            "province_iso": PROVINCE_ISO.get(site.get("province") or "", ""),
            "city_zh": site.get("city"),
            "city_en": city_en(site.get("city") or ""),
            "name_zh": site["name"],
            "name_en": name_en,
            "name_en_source": name_en_source,
            "slug": slug,
            "lat": site["lat"],
            "lon": site["lon"],
            "address_zh": address,
            "address_en": address_en,
            "address_en_source": address_en_source,
            "category": cat,
            "category_zh": cat_zh,
            "category_en": cat_en,
            "intro_zh": intro_zh,
            "intro_en": (intro_en or "")[:1200],
            "intro_en_source": intro_en_source,
            "images": (w.get("images") or prev_site.get("images") or [])[:5],
            "web": site.get("web") or "",
            "booking": site.get("booking") or "",
            "transport": {
                "airports": airports,
                "nearest_airport_km": airports[0]["distance_km"] if airports else None,
                "high_speed_stations": high_speed,
                "railway_stations": rail,
            },
            "hotels": (osm.get("hotels") or prev_site.get("hotels") or [])[:5],
            "hotels_nearby_30km": osm.get("hotels_nearby_30km", prev_site.get("hotels_nearby_30km", 0)),
            "info_languages": langs,
            "foreign_visitors": {
                "status": "likely_open" if likely_open else "unknown",
                "note_zh": "中国 5A 景区通常对境外游客开放；部分景区需护照实名预约，出行前请以官网为准。",
                "note_en": "Most 5A sites admit international visitors; passport-based reservations may be required. Check the official site before travelling.",
            },
            "sources": [
                {"name": "文化和旅游部 5A 景区名录", "url": "https://lyfw.mct.gov.cn/site/special/home"},
                *([{"name": "Wikipedia", "url": f"https://zh.wikipedia.org/wiki/{w['zh_title']}"}] if w.get("zh_title") else []),
                {"name": "OpenStreetMap", "url": "https://www.openstreetmap.org/"},
            ],
            "updated_at": now_iso(),
        })
        if i % 50 == 0:
            print(f"China build {i}/{len(sites)}")

    save_json(DATA / "china.json", {
        "generated_at": now_iso(),
        "count": len(out),
        "sources": ["MCT 5A list", "Wikipedia", "Wikimedia Commons", "OpenStreetMap", "OurAirports"],
        "sites": out,
    })
    print(f"saved {len(out)} China sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
