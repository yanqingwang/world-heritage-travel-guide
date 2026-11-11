#!/usr/bin/env bash
# 一键部署世界遗产指南（静态站 + 账号/同步 API）到阿里云 ECS / 轻量应用服务器
#
# 在【服务器上】执行（Ubuntu/Debian 或 Alibaba Cloud Linux/CentOS 均可）：
#   bash scripts/deploy_server.sh
#
# 可选环境变量：
#   WHG_DIR=/srv/whg           安装目录
#   WHG_PORT=8123              监听端口
#   WHG_DOMAIN=whg.example.com 绑定域名（留空则仅 IP 访问；填了会生成 nginx 站点）
#   WHG_REPO=...               仓库地址（默认官方 GitHub）
#
# 前置：仓库已 clone 到 WHG_DIR（或本脚本会自动 clone）。
set -euo pipefail

WHG_DIR="${WHG_DIR:-/srv/whg}"
WHG_PORT="${WHG_PORT:-8123}"
WHG_DOMAIN="${WHG_DOMAIN:-}"
WHG_REPO="${WHG_REPO:-https://github.com/yanqingwang/world-heritage-travel-guide.git}"

say() { printf '\n\033[1;36m== %s\033[0m\n' "$*"; }

say "1/6 准备代码目录 $WHG_DIR"
if [ ! -d "$WHG_DIR/.git" ]; then
  mkdir -p "$(dirname "$WHG_DIR")"
  git clone --depth 1 "$WHG_REPO" "$WHG_DIR"
else
  git -C "$WHG_DIR" fetch --depth 1 origin && git -C "$WHG_DIR" reset --hard origin/main
fi

say "2/6 Python 虚拟环境与依赖"
cd "$WHG_DIR"
command -v python3 >/dev/null || { echo "缺少 python3"; exit 1; }
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q flask gunicorn

say "3/6 数据目录与初始化（账号库在 $WHG_DIR/data/accounts.db）"
mkdir -p data
WHG_DB="$WHG_DIR/data/accounts.db" .venv/bin/python - <<'PY'
import os, sys
sys.path.insert(0, "server")
import app
app.init_db()
print("账号库就绪：", os.environ["WHG_DB"])
PY

say "4/6 自测（接口 28 项 + 合并逻辑 9 项）"
.venv/bin/python server/test_app.py | tail -1
command -v node >/dev/null && node server/test_merge.js || echo "（未安装 node，跳过前端合并单测）"

say "5/6 systemd 常驻服务"
UNIT=/etc/systemd/system/whg.service
sudo tee "$UNIT" >/dev/null <<EOF
[Unit]
Description=World Heritage Guide (site + account API)
After=network.target

[Service]
WorkingDirectory=$WHG_DIR
Environment=WHG_HOST=0.0.0.0 WHG_PORT=$WHG_PORT WHG_DB=$WHG_DIR/data/accounts.db
ExecStart=$WHG_DIR/.venv/bin/gunicorn -w 4 -b 0.0.0.0:$WHG_PORT --access-logfile - server.app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now whg
sudo systemctl --no-pager --lines=0 status whg | head -3

say "6/6 健康检查"
for i in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:$WHG_PORT/api/health" >/dev/null 2>&1; then
    echo "✅ 服务已就绪：http://127.0.0.1:$WHG_PORT"
    curl -s "http://127.0.0.1:$WHG_PORT/api/health"; echo
    break
  fi
  sleep 1
  [ "$i" = 20 ] && { echo "❌ 健康检查失败，查看：journalctl -u whg -n 100"; exit 1; }
done

if [ -n "$WHG_DOMAIN" ]; then
  say "Nginx + HTTPS（域名 $WHG_DOMAIN）"
  if command -v nginx >/dev/null; then
    sudo tee "/etc/nginx/conf.d/whg.conf" >/dev/null <<EOF
server {
  listen 80;
  server_name $WHG_DOMAIN;
  client_max_body_size 2m;
  location / {
    proxy_pass http://127.0.0.1:$WHG_PORT;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }
}
EOF
    sudo nginx -t && sudo systemctl reload nginx
    echo "Nginx 已配置。HTTPS 可执行： sudo certbot --nginx -d $WHG_DOMAIN"
  else
    echo "未安装 nginx；如需域名访问： apt install -y nginx 后重跑本脚本（带 WHG_DOMAIN）"
  fi
fi

cat <<EOF

部署完成 🎉
  站点：      http://<服务器IP>:$WHG_PORT/
  健康检查：  http://<服务器IP>:$WHG_PORT/api/health
  备份：      cp $WHG_DIR/data/accounts.db ~/whg-backup-\$(date +%F).db
  日志：      journalctl -u whg -f
  安全组：    记得在阿里云安全组放行 $WHG_PORT 端口（或 80/443 走 nginx）
EOF