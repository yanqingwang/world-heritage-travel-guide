# -*- coding: utf-8 -*-
"""世界遗产旅行指南 · 账号与个人标记同步服务

设计口径（2026-11-11 用户要求）：
- 登录：用户名 + 密码（注册时生成一次性恢复码，忘记密码用「用户名 + 恢复码」重置，
  不依赖邮件服务）
- 个人标记（去过 / 赞过 / 不好）：登录后与服务器同步，换浏览器可恢复
- 未登录：前端纯 localStorage，不发任何请求（与 GitHub 的本地优先一致）

运行：  python server/app.py            # 默认 127.0.0.1:8123
        FDE 风格的 env：WHG_DB / WHG_PORT / WHG_HOST
托管：  Flask 同时以静态站点方式返回 site/，单进程即可部署（阿里云 ECS/轻量应用服务器）。
"""
from __future__ import annotations

import json
import logging
import os
import secrets
import sqlite3
import string
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent.parent
SITE_DIR = BASE / "site"
DB_PATH = Path(os.environ.get("WHG_DB", BASE / "data" / "accounts.db"))
TOKEN_TTL_DAYS = int(os.environ.get("WHG_TOKEN_TTL_DAYS", "30"))
MAX_MARKS_BYTES = 512 * 1024          # 单人标记上限 512KB（约 1 万条）
RECOVERY_ALPHABET = string.ascii_uppercase + string.digits

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
log = logging.getLogger("whg")


# ---------------------------------------------------------------- 存储

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db() -> None:
    with conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            TEXT PRIMARY KEY,
                username      TEXT NOT NULL UNIQUE,   -- 小写去空格后的登录名
                display_name  TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                recovery_hash TEXT NOT NULL,          -- 恢复码只存哈希
                created_at    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_marks (
                user_id    TEXT PRIMARY KEY,
                payload    TEXT NOT NULL,             -- {"marks": {...}, "updatedAt": "..."}
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
            """
        )


def _norm_username(name: str) -> str:
    return (name or "").strip().lower()


def _new_recovery_code() -> str:
    """XXXX-XXXX-XXXX 形式的恢复码（无易混字符）。"""
    raw = "".join(secrets.choice(RECOVERY_ALPHABET) for _ in range(12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"


def _norm_recovery(code: str) -> str:
    return "".join(ch for ch in (code or "").upper() if ch.isalnum())


def _valid_username(name: str) -> bool:
    return 3 <= len(name) <= 32 and all(
        ch.isalnum() or ch in "_-." for ch in name)


def _public_user(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "username": row["username"],
            "displayName": row["display_name"], "createdAt": row["created_at"]}


def _issue_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    with conn() as c:
        c.execute("INSERT INTO sessions VALUES (?,?,?,?)",
                  (token, user_id, now.isoformat(timespec="seconds"),
                   (now + timedelta(days=TOKEN_TTL_DAYS)).isoformat(timespec="seconds")))
    return token


def _current_user():
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    if not token:
        return None
    with conn() as c:
        row = c.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token = ? AND s.expires_at > ?",
            (token, _now())).fetchone()
    return row


def auth_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = _current_user()
        if not user:
            return jsonify({"ok": False, "error": "请先登录"}), 401
        request.user = user  # type: ignore[attr-defined]
        return fn(*a, **kw)
    return wrapper


# ---------------------------------------------------------------- 账号 API

@app.post("/api/auth/register")
def register():
    body = request.get_json(silent=True) or {}
    username = _norm_username(body.get("username") or "")
    display = (body.get("displayName") or body.get("username") or "").strip()
    password = str(body.get("password") or "")
    if not _valid_username(username):
        return jsonify({"ok": False,
                        "error": "用户名需 3-32 位，仅字母/数字/下划线/短横线/点"}), 400
    if len(password) < 8:
        return jsonify({"ok": False, "error": "密码至少 8 位"}), 400
    recovery = _new_recovery_code()
    uid = secrets.token_hex(12)
    try:
        with conn() as c:
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?)",
                      (uid, username, display or username,
                       generate_password_hash(password),
                       generate_password_hash(_norm_recovery(recovery)), _now()))
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "error": "用户名已被占用"}), 409
    token = _issue_token(uid)
    log.info("注册 %s", username)
    return jsonify({
        "ok": True, "token": token,
        "user": {"id": uid, "username": username, "displayName": display or username},
        # 恢复码只在注册时返回一次，前端要求用户抄走
        "recoveryCode": recovery,
    }), 201


@app.post("/api/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    username = _norm_username(body.get("username") or "")
    password = str(body.get("password") or "")
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False, "error": "用户名或密码不正确"}), 401
    return jsonify({"ok": True, "token": _issue_token(row["id"]),
                    "user": _public_user(row)})


@app.post("/api/auth/logout")
@auth_required
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip()
    with conn() as c:
        c.execute("DELETE FROM sessions WHERE token = ?", (token,))
    return jsonify({"ok": True})


@app.get("/api/auth/me")
@auth_required
def me():
    return jsonify({"ok": True, "user": _public_user(request.user)})


@app.post("/api/auth/reset-password")
def reset_password():
    """忘记密码：用户名 + 恢复码 + 新密码。成功后旧会话全部失效，签发新恢复码。"""
    body = request.get_json(silent=True) or {}
    username = _norm_username(body.get("username") or "")
    code = _norm_recovery(body.get("recoveryCode") or "")
    new_password = str(body.get("newPassword") or "")
    if len(new_password) < 8:
        return jsonify({"ok": False, "error": "新密码至少 8 位"}), 400
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not row or not code or not check_password_hash(row["recovery_hash"], code):
            # 统一文案，不区分「用户不存在」与「恢复码错误」
            return jsonify({"ok": False, "error": "用户名或恢复码不正确"}), 401
        new_recovery = _new_recovery_code()
        c.execute("UPDATE users SET password_hash = ?, recovery_hash = ? WHERE id = ?",
                  (generate_password_hash(new_password),
                   generate_password_hash(_norm_recovery(new_recovery)), row["id"]))
        c.execute("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
    log.info("重置密码 %s", username)
    return jsonify({"ok": True, "recoveryCode": new_recovery,
                    "hint": "旧恢复码已失效，请保存新的恢复码"})


# ---------------------------------------------------------------- 标记同步 API

@app.get("/api/marks")
@auth_required
def get_marks():
    with conn() as c:
        row = c.execute("SELECT payload, updated_at FROM user_marks WHERE user_id = ?",
                        (request.user["id"],)).fetchone()
    if not row:
        return jsonify({"ok": True, "marks": {}, "updatedAt": None})
    data = json.loads(row["payload"] or "{}")
    return jsonify({"ok": True, "marks": data.get("marks") or {},
                    "updatedAt": data.get("updatedAt") or row["updated_at"]})


@app.put("/api/marks")
@auth_required
def put_marks():
    body = request.get_json(silent=True) or {}
    marks = body.get("marks")
    if not isinstance(marks, dict):
        return jsonify({"ok": False, "error": "marks 必须是对象"}), 400
    payload = json.dumps({"marks": marks, "updatedAt": _now()}, ensure_ascii=False)
    if len(payload.encode()) > MAX_MARKS_BYTES:
        return jsonify({"ok": False, "error": "标记数据过大（上限 512KB）"}), 413
    now = _now()
    with conn() as c:
        c.execute(
            "INSERT INTO user_marks(user_id, payload, updated_at) VALUES (?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload, "
            "updated_at=excluded.updated_at",
            (request.user["id"], payload, now))
        row = c.execute("SELECT payload FROM user_marks WHERE user_id = ?",
                        (request.user["id"],)).fetchone()
    saved = json.loads(row["payload"])
    return jsonify({"ok": True, "updatedAt": saved["updatedAt"],
                    "count": len(marks)})


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "whg", "time": _now()})


# ---------------------------------------------------------------- 静态站点

@app.get("/")
def index():
    return send_from_directory(SITE_DIR, "index.html")


@app.get("/<path:path>")
def static_files(path: str):
    target = SITE_DIR / path
    if target.is_file():
        return send_from_directory(SITE_DIR, path)
    # 站点是 hash 路由式单页（index.html#…），未知路径回落到首页
    return send_from_directory(SITE_DIR, "index.html")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    init_db()
    app.run(host=os.environ.get("WHG_HOST", "127.0.0.1"),
            port=int(os.environ.get("WHG_PORT", "8123")), debug=False)