# 世界遗产旅行指南 · World Heritage Travel Guide

A bilingual, source-backed travel dataset covering **359 Chinese 5A scenic areas** and **1,213 UNESCO World Heritage sites outside China** (150 of them with full records). Every record is available in Chinese and English, with the country's official language added whenever an official UNESCO edition or a Wikipedia edition exists.

**[Open the site →](https://yanqingwang.github.io/world-heritage-travel-guide/)**

---

## 中文

### 这个仓库提供什么

| 数据集 | 条目 | 内容 |
|---|---:|---|
| 中国 5A 景区 | 359 | 名称、省市、详细地址、坐标、特色分类、中英文简介、最多 5 张图片、最近高铁站/机场、30 km 内星级/连锁酒店（最多 5 家）、中英日韩信息可得性、境外游客提示 |
| 海外 UNESCO 世界遗产 | 1,213 | 官方中/英/法/西/俄/阿文本、所在国官方语言版本、入选年份/标准、机场与距北京直线距离、签证（中国护照）、多语言信息可得性 |
| 海外「完整资料」条目 | 150 | 在上一行基础上增加 50 km 内酒店、码头/火车站、最多 5 张图片与热度排名 |

### 主要特点

- **中英双语界面**，详情内可直接查看所在国官方语言（日语、韩语、法语、西班牙语、德语、意大利语等，取决于是否有官方/维基文本）。
- **按国家/省份、类型、签证状态、资料等级筛选**，支持名称/城市/国家搜索。
- **数据可机读**：`data/china.json`、`data/world.json`；每个条目另有 Markdown 版本在 `entries/`。
- **来源可追溯**：每条记录保留官方页面、维基条目、OpenStreetMap、图片署名与更新时间。
- **每周自动更新**：GitHub Actions 抓取文旅部 5A 名录、UNESCO 多语言 XML、维基百科签证表，滚动刷新 OSM 设施，重建站点并记录 `CHANGELOG.md`。

### 数据字段（节选）

```jsonc
{
  "id": "cn-1283",
  "dataset": "china_5a",
  "name_zh": "故宫博物院",
  "name_en": "Palace Museum",
  "province_zh": "北京市",
  "city_zh": "东城区",
  "lat": 39.924091,
  "lon": 116.403414,
  "category_zh": "历史遗址",
  "intro_zh": "……",
  "intro_en": "……",
  "images": [{ "url": "…", "author": "…", "license": "CC BY-SA 4.0", "source": "…" }],
  "transport": {
    "airports": [{ "name": "Beijing Capital International Airport", "iata": "PEK", "distance_km": 25.6 }],
    "high_speed_stations": [{ "name": "北京南", "high_speed": true, "distance_km": 6.2 }]
  },
  "hotels": [{ "name": "…", "stars": 5, "distance_km": 1.4, "kind": "star" }],
  "info_languages": { "zh": true, "en": true, "ja": false, "ko": false }
}
```

海外条目额外包含 `visa` / `visa_by_country` / `transport.distance_beijing_km` / `tier` / `popularity_rank`，以及 `name_local` 与 `intro_local`。

### 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 核心源 + 构建（最快）
python scripts/update_all.py --quick

# 完整刷新（会访问维基百科、OSM、Google 翻译回退）
python scripts/update_all.py --budget 80

# 预览
python -m http.server 8000 --directory site
# http://localhost:8000
```

环境变量（均可选）：

| 变量 | 用途 |
|---|---|
| `FIRECRAWL_API_KEY` | 绕过 UNESCO 官网 Cloudflare，抓取六种官方语言 XML；未设置时尝试直连，失败则使用仓库内快照 |
| `TRANSLATE_PROXY` | 本地运行 Google 翻译回退时的代理，例如 `socks5://127.0.0.1:1080` |
| `ALL_PROXY` | 本地访问 Overpass 的代理（GitHub Actions 不需要） |
| `REFRESH_WIKI=1` | 强制重新抓取维基百科多语言文本/图片 |

### 每周自动更新

`.github/workflows/update.yml` 每周一 03:17 UTC 运行：

1. 抓取文旅部 5A 名录、UNESCO 六语 XML、维基百科签证要求表；
2. 滚动刷新约 80 个目的地的 OSM 酒店/车站/码头；
3. 重建 `data/*.json`、`site/`、`entries/`；
4. 写入 `CHANGELOG.md` 与 `data/changelog/YYYY-MM-DD.json`；
5. 有变更则自动 commit，并部署 GitHub Pages。

首次启用完整 UNESCO 更新时，建议在仓库 Secrets 中添加 `FIRECRAWL_API_KEY`。没有该 secret 时，直连失败会保留上一版快照，不会破坏构建。

### 数据质量与边界

- **距离是直线距离（great-circle）**，不是实际飞行/驾车里程。
- **酒店/车站/码头来自 OpenStreetMap**，中国境内星级标签较少；没有星级时按连锁品牌/名称推断，并在 `kind` 中标注。
- **高铁站**用 423 个站名清单匹配 OSM 车站，未覆盖的站会退回到普通火车站；站点名称与线路以 OSM 为准。
- **英文名称优先用维基百科；没有时用拼音 + 英文后缀**，并标注 `name_en_source`。
- **简介优先官方/维基文本；缺失时用机器翻译**，并在 `intro_*_source` 标注 `machine_translation`。
- **签证状态来自英文维基百科「Visa requirements for Chinese citizens」**，可能滞后；出行前请以中国领事服务网/目的国官方为准。
- **境外游客开放状态**为中国 5A 的总体提示，不代表每个景区都已逐条核实；预约与护照要求请查官网。
- **UNESCO 图片/文本版权归 UNESCO**，本站仅引用短简介与缩略图并链接原页面；图片优先使用 Wikimedia Commons，署名见条目。
- **发布前结构校验**：`scripts/validate_data.py` 检查双语字段、坐标范围、图片/酒店数量与距离上限，硬错误会阻断每周发布。
- **为什么不用数据库**：1,572 条记录在浏览器内筛选 <1 ms，静态 JSON + CDN 比 Neon 往返更快、更便宜；实测与取舍见 [`docs/neon-evaluation.md`](docs/neon-evaluation.md)。

### 许可

- 代码：MIT（见 `LICENSE`）。
- 数据来源与再分发条款：见 `NOTICE.md`。OpenStreetMap 数据遵循 ODbL；维基百科文本遵循 CC BY-SA 4.0；UNESCO 文本/图片版权归 UNESCO。

---

## English

### What this repository contains

| Dataset | Records | Fields |
|---|---:|---|
| China 5A scenic areas | 359 | Names, province/city, address, coordinates, category, Chinese/English intros, up to 5 images, nearest high-speed rail station/airport, up to 5 star/chain hotels within 30 km, zh/en/ja/ko information availability, international-visitor note |
| Overseas UNESCO sites | 1,213 | Official UNESCO text in zh/en/fr/es/ru/ar, the country's official language where available, inscription year/criteria, airports and great-circle distance from Beijing, visa rules for Chinese passports, language availability |
| Overseas "full" records | 150 | Adds hotels within 50 km, ferry terminals/railway stations, up to 5 images and a popularity rank |

### Highlights

- **Bilingual UI** (Chinese/English) with a third block in the destination's official language when an official UNESCO or Wikipedia edition exists.
- **Filters** by country/province, category, visa status and record tier; free-text search.
- **Machine-readable** `data/china.json` and `data/world.json`; every record also has a Markdown mirror in `entries/`.
- **Traceable sources**: official pages, Wikipedia/Wikidata, OpenStreetMap, image credits and `updated_at` on every record.
- **Weekly automation**: GitHub Actions refreshes the MCT 5A list, UNESCO's six-language XML and the Wikipedia visa table, rotates OSM facility refreshes, rebuilds the site and appends `CHANGELOG.md`.

### Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/update_all.py --quick
python -m http.server 8000 --directory site
```

Optional environment variables: `FIRECRAWL_API_KEY` (UNESCO Cloudflare bypass), `TRANSLATE_PROXY` (local Google Translate fallback proxy), `ALL_PROXY` (local Overpass proxy), `REFRESH_WIKI=1`.

### Caveats

- Distances are **great-circle distances**, not flight or driving distances.
- Hotels/stations/ferries come from **OpenStreetMap** and may be incomplete; star ratings are sparse in China and are supplemented by chain-brand inference (`kind` marks the basis).
- **High-speed rail** matching uses a 423-station name list; uncovered stations fall back to the nearest ordinary railway station.
- English names use Wikipedia first, then **pinyin + English suffix**; machine-translated introductions are explicitly labelled.
- Visa rules are a **Wikipedia-sourced snapshot** and can lag; verify with official sources.
- UNESCO text and images remain © UNESCO; images prefer Wikimedia Commons with attribution in each record.
- **Structure validation** runs before publishing (`scripts/validate_data.py`): bilingual fields, coordinate ranges, image/hotel caps and distance limits. Hard errors block the weekly deploy.
- **Why no database**: filtering 1,572 records in the browser takes <1 ms; static JSON over a CDN beats a Neon round-trip on latency and cost. See [`docs/neon-evaluation.md`](docs/neon-evaluation.md).

### License

Code: MIT. Data attribution and redistribution terms: see `NOTICE.md`.
