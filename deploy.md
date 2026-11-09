# 部署与运维 · Deployment & Operations

面向仓库管理员的数据管线、本地运行、环境变量与每周自动更新说明。普通访客只需 [README](README.md) 与[在线站点](https://yanqingwang.github.io/world-heritage-travel-guide/)。

Operations guide for repository maintainers: running the data pipeline locally, environment variables, and the weekly automation. Visitors only need the [README](README.md) and the [live site](https://yanqingwang.github.io/world-heritage-travel-guide/).

---

## 本地运行 · Local development

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

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/update_all.py --quick
python -m http.server 8000 --directory site
```

## 环境变量 · Environment variables

均可选（不设置时管线走内置回退）：

| 变量 | 用途 |
|---|---|
| `FIRECRAWL_API_KEY` | 绕过 UNESCO 官网 Cloudflare，抓取六种官方语言 XML；未设置时尝试直连，失败则使用仓库内快照 |
| `TRANSLATE_PROXY` | 本地运行 Google 翻译回退时的代理，例如 `socks5://127.0.0.1:1080` |
| `ALL_PROXY` | 本地访问 Overpass 的代理（GitHub Actions 不需要） |
| `REFRESH_WIKI=1` | 强制重新抓取维基百科多语言文本/图片 |

All optional — the pipeline falls back gracefully:

| Variable | Purpose |
|---|---|
| `FIRECRAWL_API_KEY` | Bypasses UNESCO's Cloudflare to fetch the six official-language XML files; without it the fetcher tries direct access and falls back to the in-repo snapshot |
| `TRANSLATE_PROXY` | Proxy for the local Google Translate fallback, e.g. `socks5://127.0.0.1:1080` |
| `ALL_PROXY` | Local proxy for Overpass (not needed on GitHub Actions) |
| `REFRESH_WIKI=1` | Force re-fetching Wikipedia multilingual text/images |

## 每周自动更新 · Weekly automation

`.github/workflows/update.yml` 每周一 03:17 UTC 运行：

1. 抓取文旅部 5A 名录、UNESCO 六语 XML、维基百科签证要求表；
2. 滚动刷新约 80 个目的地的 OSM 酒店/车站/码头；
3. 重建 `data/*.json`、`site/`、`entries/`；
4. 写入 `CHANGELOG.md` 与 `data/changelog/YYYY-MM-DD.json`；
5. 有变更则自动提交，并部署 GitHub Pages。

首次启用完整 UNESCO 更新时，建议在仓库 Secrets 中添加 `FIRECRAWL_API_KEY`。没有该 secret 时，直连失败会保留上一版快照，不会破坏构建。

`.github/workflows/update.yml` runs every Monday at 03:17 UTC:

1. Fetches the MCT 5A list, UNESCO's six-language XML and the Wikipedia visa table;
2. Rotates OSM hotel/station/ferry refreshes for ~80 destinations;
3. Rebuilds `data/*.json`, `site/` and `entries/`;
4. Appends `CHANGELOG.md` and writes `data/changelog/YYYY-MM-DD.json`;
5. Auto-commits when anything changed and deploys GitHub Pages.

For the full UNESCO refresh add `FIRECRAWL_API_KEY` to the repository Secrets. Without the secret, a failed direct fetch keeps the previous snapshot and the build still succeeds.

## 站点部署 · Site deploy

`.github/workflows/pages.yml` 在 `site/**` 或 workflow 文件本身有推送时自动运行（也可手动触发 workflow_dispatch），把 `site/` 发布到 GitHub Pages。数据更新由 `update.yml` 内部触发同一部署。

`.github/workflows/pages.yml` deploys `site/` to GitHub Pages automatically on pushes touching `site/**` or the workflow file (also triggerable via workflow_dispatch). The weekly data job deploys through the same workflow.

## 个人标记云同步 · Marks cloud sync

访客的个人标记（去过/赞过/不好）以浏览器 localStorage 为主存储；可选地在仓库 `sync/` 目录按设备保存 `marks-<device>.json`（一人一份），通过 GitHub Contents API 读写。访客需自备仅限本仓库 Contents 读写权限的 Fine-grained PAT；令牌只存在访客自己的浏览器里，站点不收集凭据。匿名访客可用「导出/导入 JSON」在设备间手动搬运标记。

Visitor marks (visited/liked/not-for-me) live in localStorage first; optionally one `marks-<device>.json` per person is kept under `sync/` in this repo, read and written through the GitHub Contents API. Visitors supply their own Fine-grained PAT scoped to Contents: Read & Write on this repository only; the token stays in their browser. Anonymous visitors can move marks between devices with the JSON export/import buttons.
