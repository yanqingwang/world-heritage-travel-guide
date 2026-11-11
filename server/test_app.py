# -*- coding: utf-8 -*-
"""账号与标记同步服务自测（不依赖 pytest）：python server/test_app.py"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

os.environ["WHG_DB"] = str(Path(tempfile.mkdtemp()) / "t.db")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as srv  # noqa: E402

PASS = 0


def ok(cond: bool, msg: str) -> None:
    global PASS
    if not cond:
        raise AssertionError("FAIL: " + msg)
    PASS += 1
    print("  ✅", msg)


def main() -> None:
    srv.init_db()
    c = srv.app.test_client()

    # 未登录访问标记接口 → 401
    ok(c.get("/api/marks").status_code == 401, "未登录读取标记 401")

    # 注册
    r = c.post("/api/auth/register", json={"username": "Alice_01", "password": "pw123456"})
    d = r.get_json()
    ok(r.status_code == 201 and d["ok"], "注册成功")
    ok("-" in d["recoveryCode"] and len(d["recoveryCode"]) == 14, "下发恢复码 XXXX-XXXX-XXXX")
    tok = d["token"]

    # 重名 / 弱密码 / 非法用户名
    ok(c.post("/api/auth/register", json={
        "username": "alice_01", "password": "pw123456"}).status_code == 409, "重名注册 409（大小写不敏感）")
    ok(c.post("/api/auth/register", json={
        "username": "bob", "password": "123"}).status_code == 400, "弱密码 400")
    ok(c.post("/api/auth/register", json={
        "username": "a b", "password": "pw123456"}).status_code == 400, "非法用户名 400")

    # 登录
    r = c.post("/api/auth/login", json={"username": "ALICE_01", "password": "pw123456"})
    ok(r.status_code == 200 and r.get_json()["ok"], "登录成功（用户名大小写不敏感）")
    tok2 = r.get_json()["token"]
    ok(c.post("/api/auth/login", json={
        "username": "alice_01", "password": "wrong"}).status_code == 401, "错误密码 401")

    # me
    h = {"Authorization": "Bearer " + tok2}
    ok(c.get("/api/auth/me", headers=h).get_json()["user"]["username"] == "alice_01", "me 返回当前用户")

    # 空标记
    d = c.get("/api/marks", headers=h).get_json()
    ok(d["ok"] and d["marks"] == {} and d["updatedAt"] is None, "初始无标记")

    # 写入 + 读取（跨 token：换浏览器）
    marks = {"cn-1": {"v": 1, "t": 1000}, "jp-2": {"r": "like", "t": 2000}}
    r = c.put("/api/marks", json={"marks": marks}, headers=h)
    ok(r.status_code == 200 and r.get_json()["count"] == 2, "写入 2 条标记")
    d = c.get("/api/marks", headers={"Authorization": "Bearer " + tok}).get_json()
    ok(d["marks"] == marks, "另一会话（新 token）读回同样的标记")

    # 覆盖更新
    c.put("/api/marks", json={"marks": {"cn-1": {"v": 1, "r": "like", "t": 3000}}}, headers=h)
    d = c.get("/api/marks", headers=h).get_json()
    ok(list(d["marks"]) == ["cn-1"], "整份覆盖（删除的条目不再出现）")

    # 参数校验
    ok(c.put("/api/marks", json={"marks": []}, headers=h).status_code == 400, "marks 非对象 400")
    big = {"x%d" % i: {"v": 1, "n": "x" * 200} for i in range(4000)}
    ok(c.put("/api/marks", json={"marks": big}, headers=h).status_code == 413, "超大标记 413")

    # 重置密码：错误恢复码
    ok(c.post("/api/auth/reset-password", json={
        "username": "alice_01", "recoveryCode": "AAAA-AAAA-AAAA",
        "newPassword": "newpw12345"}).status_code == 401, "错误恢复码 401")

    # 空恢复码 → 401
    r = c.post("/api/auth/reset-password", json={
        "username": "alice_01", "recoveryCode": "", "newPassword": "newpw12345"})
    ok(r.status_code == 401, "空恢复码 401")

    # 用真恢复码
    reg = c.post("/api/auth/register", json={
        "username": "carol", "password": "pw123456"}).get_json()
    r = c.post("/api/auth/reset-password", json={
        "username": "carol", "recoveryCode": reg["recoveryCode"],
        "newPassword": "brandnew123"})
    d = r.get_json()
    ok(r.status_code == 200 and d["ok"] and d["recoveryCode"] != reg["recoveryCode"],
       "恢复码重置成功且换发新恢复码")
    ok(c.get("/api/auth/me", headers={"Authorization": "Bearer " + reg["token"]}
             ).status_code == 401, "重置后旧会话失效")
    ok(c.post("/api/auth/login", json={
        "username": "carol", "password": "pw123456"}).status_code == 401, "旧密码失效")
    ok(c.post("/api/auth/login", json={
        "username": "carol", "password": "brandnew123"}).status_code == 200, "新密码可登录")
    ok(c.post("/api/auth/reset-password", json={
        "username": "carol", "recoveryCode": reg["recoveryCode"],
        "newPassword": "x" * 10}).status_code == 401, "旧恢复码失效")

    # 退出登录
    hc = {"Authorization": "Bearer " + c.post("/api/auth/login", json={
        "username": "carol", "password": "brandnew123"}).get_json()["token"]}
    ok(c.post("/api/auth/logout", headers=hc).status_code == 200, "退出登录")
    ok(c.get("/api/auth/me", headers=hc).status_code == 401, "退出后 token 失效")

    # 健康检查 + 静态站
    ok(c.get("/api/health").get_json()["ok"], "健康检查")
    ok(c.get("/").status_code == 200, "根路径返回站点首页")
    ok(c.get("/assets/account.js").status_code == 200, "静态资源可访问")
    ok(c.get("/some/spa/route").status_code == 200, "未知路径回落首页（hash 路由）")

    print(f"\n{PASS} 项断言全部通过")


if __name__ == "__main__":
    main()