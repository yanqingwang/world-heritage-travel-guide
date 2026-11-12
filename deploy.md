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

个人标记（去过/赞过/不好）始终先写入浏览器 localStorage。跨设备恢复有两条路径，二者都不需要把管理员凭据放进前端。

Marks (visited/liked/not-for-me) always go to localStorage first. Two paths exist for cross-device restore; neither embeds an admin credential in the frontend.

### 1. 推荐：账号服务 · Recommended: account server

`server/app.py` 提供「用户名 + 密码 + 恢复码」注册/登录和 `/api/marks` 同步；登录后标记按单条时间戳合并，换浏览器登录即可恢复，未登录完全不联网。前端通过 `GET /api/health` 探测 `{"service":"whg"}`：静态 GitHub Pages 镜像没有后端，会显示「此站点为纯静态镜像」，并保留 localStorage 与导出/导入 JSON；账号服务器部署（含 Pages 用 `?api=` 指向后端的跨源场景）才显示登录表单。部署细节见下方「账号服务部署」。

`server/app.py` provides username/password sign-up (with a one-time recovery code) and `/api/marks` sync. Signed-in marks merge per record by timestamp; signed-out visitors make no network calls. The frontend probes `GET /api/health` for `{"service":"whg"}`: a static GitHub Pages build shows "Static mirror only" and keeps localStorage + JSON export/import, while the account-server build (or Pages pointed at it with `?api=`) shows the sign-in form. See "Account server" below for deployment.

### 2. 可选：GitHub Contents API · Optional: GitHub Contents API

站点内「☁ 云同步」可选地用访客自己的 Fine-grained PAT 把 `marks-<device>.json` 写到本仓库 `sync/`；令牌只留在访客浏览器。保存令牌时前端会依次判断 `GET /user`（令牌是否有效）与 `GET /repos/{owner}/{repo}` 的 `permissions.push`（是否有写权限），并区分 401 / 403 / 404 / 409 给出可读提示。

**判断结论**：这条路径**不适用于任意公众访客**。Fine-grained PAT 只能授予「令牌持有者本来就有权限」的仓库；普通访客无法用自己生成的 PAT 给自己授权写入 `yanqingwang/world-heritage-travel-guide`，只有仓库所有者/协作者能成功推送。纯静态 GitHub Pages 也无法完成 GitHub OAuth 登录：Web application flow 的 `client_secret` 不能放在浏览器里，Device flow 同样需要服务端交换 token。因此面向公众的自助登录必须用上面的账号服务（或未来增加 GitHub App / serverless 后端）；普通访客请继续使用「导出/导入 JSON」，或把备份目标改成自己的 fork。

The in-site "☁ Cloud sync" can optionally write `marks-<device>.json` under `sync/` using the visitor's own Fine-grained PAT; the token stays in their browser. On save, the frontend checks `GET /user` (valid token?) and `permissions.push` from `GET /repos/{owner}/{repo}` (may this token commit here?), and maps 401 / 403 / 404 / 409 to readable messages.

**Verdict**: this path does **not** work for arbitrary public visitors. A fine-grained PAT can only grant access the token holder already has; a visitor cannot mint a PAT that writes to someone else's `yanqingwang/world-heritage-travel-guide` — only the owner/collaborators can push. A static GitHub Pages page also cannot do GitHub OAuth sign-in by itself: the web application flow's `client_secret` cannot live in browser code, and the device flow likewise needs a server-side token exchange. Public self-service login therefore requires the account server above (or a future GitHub App / serverless backend); ordinary visitors should keep using Export / Import JSON, or point the backup at their own fork.


---

## 账号服务部署 · Account server (Aliyun)

站点默认是纯静态（GitHub Pages）。带账号登录与云同步的版本多一个轻后端
`server/app.py`（Flask + SQLite，同时托管 `site/` 静态文件），单进程即可运行。

### 本地运行

```bash
pip install flask
python server/app.py                 # http://127.0.0.1:8123
python server/test_app.py            # 28 项接口断言
node server/test_merge.js            # 前端合并算法 9 项断言
```

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `WHG_DB` | `data/accounts.db` | SQLite 路径（账号 + 会话 + 标记） |
| `WHG_HOST` / `WHG_PORT` | `127.0.0.1` / `8123` | 监听地址/端口（生产用 `0.0.0.0:8123` 或用 gunicorn） |
| `WHG_TOKEN_TTL_DAYS` | `30` | 登录会话有效期 |

### 阿里云 ECS / 轻量应用服务器（推荐：一键脚本）

仓库内 `scripts/deploy_server.sh` 覆盖「拉代码 → venv → 装 flask+gunicorn →
初始化账号库 → 跑自测 → systemd 常驻 → 健康检查 → 可选 nginx」：

```bash
# 在服务器上执行（先 clone 或让脚本自动 clone）
WHG_DOMAIN=whg.example.com bash scripts/deploy_server.sh
# 不带域名（仅 IP + 端口访问）： bash scripts/deploy_server.sh

# 安全组需放行 8123（或 80/443，如用 nginx）
# 备份： cp /srv/whg/data/accounts.db ~/whg-backup-$(date +%F).db
```

手动方式（不使用脚本时）：

```bash
# 1) 上传代码（任选 git clone 或 rsync）
git clone https://github.com/yanqingwang/world-heritage-travel-guide.git /srv/whg
cd /srv/whg && python3 -m venv .venv && .venv/bin/pip install flask

# 2) 生产进程（gunicorn 4 worker，SQLite 单文件足够）
.venv/bin/pip install gunicorn
.venv/bin/gunicorn -w 4 -b 0.0.0.0:8123 server.app:app

# 3) systemd 常驻（/etc/systemd/system/whg.service）
[Unit]
Description=World Heritage Guide (account + site)
After=network.target
[Service]
WorkingDirectory=/srv/whg
Environment=WHG_HOST=0.0.0.0 WHG_PORT=8123
ExecStart=/srv/whg/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8123 server.app:app
Restart=always
[Install]
WantedBy=multi-user.target

# 4) Nginx 反代 + HTTPS（可选，域名需备案）
server {
  server_name whg.example.com;
  location / { proxy_pass http://127.0.0.1:8123; proxy_set_header Host $host; }
}
```

### 阿里云函数计算 FC（备选）

Flask 应用可按「Web 函数」方式部署：入口 `server.app:app`，运行时 Python 3.11+，
环境变量 `WHG_DB=/mnt/accounts.db`（挂载 NAS，SQLite 单写者，建议实例数 1 或换 RDS）。
静态资源随代码打包即可。

### 数据与备份

- 账号/会话/标记都在 `WHG_DB` 指向的 SQLite 文件，定期 `cp` 备份即可
- 密码与恢复码均为 werkzeug 哈希；会话 token 30 天过期
- 单用户标记上限 512KB（约 1 万条）
