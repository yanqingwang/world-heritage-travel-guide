/* account.js — 账号登录与个人标记云同步（本地优先）
 *
 * 口径（2026-11-11 用户要求）：
 * - 登录：用户名 + 密码；注册时下发一次性恢复码，忘记密码用
 *   「用户名 + 恢复码 + 新密码」重置（不依赖邮件服务）
 * - 登录后：{siteId: {v,r,c,p,n,t}} 标记与服务器同步，换浏览器可恢复
 * - 未登录：只写 localStorage，不发任何网络请求（与 GitHub 本地优先一致）
 *
 * 服务器 API（server/app.py）：
 *   POST /api/auth/register {username,password} → {token,user,recoveryCode}
 *   POST /api/auth/login    {username,password} → {token,user}
 *   POST /api/auth/reset-password {username,recoveryCode,newPassword}
 *   GET  /api/marks  (Bearer) → {marks, updatedAt}
 *   PUT  /api/marks  (Bearer) {marks} → {updatedAt, count}
 *
 * 合并：每个 site 的标记带 t（毫秒时间戳），冲突按单条取较新；本地有云端无的推送上去。
 */
(() => {
  "use strict";

  const TOKEN_KEY = "whtg-token";
  const USER_KEY = "whtg-user";
  const LAST_SYNC_KEY = "whtg-sync-last";
  const STATE_KEY = "whtg-account-open";
  const API = ""; // 同源部署；本地联调可用 ?api=http://127.0.0.1:8123 覆盖

  const apiBase = () => {
    const q = new URLSearchParams(location.search).get("api");
    return q || API;
  };

  const S = {
    get token() { return localStorage.getItem(TOKEN_KEY) || ""; },
    set token(v) { v ? localStorage.setItem(TOKEN_KEY, v) : localStorage.removeItem(TOKEN_KEY); },
    get user() { try { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); } catch (_) { return null; } },
    set user(v) { v ? localStorage.setItem(USER_KEY, JSON.stringify(v)) : localStorage.removeItem(USER_KEY); },
    get lastSync() { return localStorage.getItem(LAST_SYNC_KEY) || ""; },
    set lastSync(v) { localStorage.setItem(LAST_SYNC_KEY, v || ""); },
  };

  const req = async (path, { method = "GET", body, auth = true } = {}) => {
    const headers = { "Content-Type": "application/json" };
    if (auth && S.token) headers.Authorization = "Bearer " + S.token;
    const r = await fetch(apiBase() + path, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
    });
    let data = null;
    try { data = await r.json(); } catch (_) { /* empty */ }
    if (!r.ok) throw new Error((data && data.error) || `请求失败 ${r.status}`);
    return data;
  };

  const listeners = { merge: [], status: [] };
  const on = (evt, fn) => { (listeners[evt] || (listeners[evt] = [])).push(fn); };
  const emit = (evt, ...args) => (listeners[evt] || []).forEach((fn) => {
    try { fn(...args); } catch (e) { console.warn("account listener", e); }
  });

  // ---------- 合并 ----------
  // local / remote: {siteId: {v,r,c,p,n,t}}；return {merged, changed}
  function mergeMarks(local, remote) {
    const out = { ...(remote || {}) };
    let changed = false;
    for (const [id, lm] of Object.entries(local || {})) {
      const rm = out[id];
      if (!rm) { out[id] = lm; changed = true; continue; }
      const lt = Number(lm.t || 0);
      const rt = Number(rm.t || 0);
      if (lt > rt) { out[id] = lm; changed = true; }
      // 较新的本地被标记删除（值为 {t} 且既无 v 也无 r）时，保留删除语义：
      if (lt > rt && !lm.v && !lm.r) delete out[id];
    }
    return { merged: out, changed };
  }

  let pushTimer = null;
  let pushing = false;

  async function push(local, { silent = true } = {}) {
    if (!S.token) return null;
    if (pushing) return null;
    pushing = true;
    try {
      const r = await req("/api/marks", { method: "PUT", body: { marks: local } });
      S.lastSync = r.updatedAt || new Date().toISOString();
      emit("status", { ok: true, at: S.lastSync, count: r.count });
      return r;
    } catch (e) {
      if (!silent) throw e;
      emit("status", { ok: false, error: e.message });
      return null;
    } finally { pushing = false; }
  }

  /** 标记变更后调用：本地立即保存（由 app.js 负责），这里只做防抖上云。 */
  function syncSoon(getMarks) {
    if (!S.token) return;                  // 未登录：完全不联网
    clearTimeout(pushTimer);
    pushTimer = setTimeout(() => push(getMarks()), 1200);
  }

  /** 登录 / 页面加载时：拉云端 + 合并 + 回写本地 + 推送合并结果。 */
  async function pullAndMerge(getMarks, setMarks) {
    if (!S.token) return null;
    const remote = await req("/api/marks");
    const local = getMarks() || {};
    const { merged, changed } = mergeMarks(local, remote.marks || {});
    setMarks(merged);
    if (changed || !remote.updatedAt) await push(merged);
    S.lastSync = remote.updatedAt || S.lastSync;
    emit("merge", merged, { changed, updatedAt: remote.updatedAt });
    return merged;
  }

  // ---------- UI ----------
  const I18N = {
    zh: {
      title: "账号与同步", kicker: "个人标记", sub: "登录后「去过 / 赞过 / 不好」在服务器保存一份，换浏览器也能恢复；不登录则只存本机。",
      login: "登录", register: "注册", logout: "退出登录", forgot: "忘记密码？",
      username: "用户名", password: "密码", password2: "确认密码",
      doLogin: "登录", doRegister: "创建账号", doReset: "重置密码",
      resetTitle: "用恢复码重置密码", recovery: "恢复码（注册时给你的 XXXX-XXXX-XXXX）",
      newPassword: "新密码", backToLogin: "返回登录",
      loggedIn: (u) => `已登录：${u}`, notLoggedIn: "未登录 · 只保存在本机浏览器",
      lastSync: (t) => `上次同步：${t}`, never: "尚未同步",
      syncNow: "立即同步", syncing: "同步中…",
      registered: "账号已创建，请抄下恢复码并妥善保存（只显示这一次）。",
      resetOk: "密码已重置，请用新密码登录；旧恢复码已失效，新恢复码已生成。",
      copy: "复制", copied: "已复制",
      err: (m) => `操作失败：${m}`,
      pwMismatch: "两次输入的密码不一致",
      needRecovery: "请输入恢复码",
      tip: "未登录时标记只保存在本机（localStorage），不会上传服务器。",
    },
    en: {
      title: "Account & sync", kicker: "Personal marks", sub: "Sign in to keep your visited / liked / not-for-me marks on the server and restore them in another browser. Without signing in, everything stays local.",
      login: "Sign in", register: "Register", logout: "Sign out", forgot: "Forgot password?",
      username: "Username", password: "Password", password2: "Confirm password",
      doLogin: "Sign in", doRegister: "Create account", doReset: "Reset password",
      resetTitle: "Reset with recovery code", recovery: "Recovery code (XXXX-XXXX-XXXX from sign-up)",
      newPassword: "New password", backToLogin: "Back to sign in",
      loggedIn: (u) => `Signed in as ${u}`, notLoggedIn: "Not signed in · stored in this browser only",
      lastSync: (t) => `Last sync: ${t}`, never: "Never synced",
      syncNow: "Sync now", syncing: "Syncing…",
      registered: "Account created. Copy the recovery code now — it is shown only once.",
      resetOk: "Password reset. Sign in with the new password; the old recovery code no longer works — a new one was issued.",
      copy: "Copy", copied: "Copied",
      err: (m) => `Failed: ${m}`,
      pwMismatch: "Passwords do not match",
      needRecovery: "Recovery code required",
      tip: "When not signed in, marks stay in this browser (localStorage) and are never uploaded.",
    },
  };
  const lang = () => (document.documentElement.lang || "zh").startsWith("en") ? "en" : "zh";
  const t = (k, ...a) => {
    const v = I18N[lang()][k];
    return typeof v === "function" ? v(...a) : (v || k);
  };

  let panel = null;
  let mode = "login";   // login | register | reset

  function ensurePanel() {
    if (panel) return panel;
    panel = document.createElement("section");
    panel.id = "account-panel";
    panel.className = "account-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "false");
    panel.hidden = true;
    document.body.appendChild(panel);
    panel.addEventListener("click", (e) => {
      if (e.target === panel) close();
    });
    return panel;
  }

  function render() {
    const p = ensurePanel();
    const user = S.user;
    const sync = S.lastSync;
    let body;
    if (user) {
      body = `
        <div class="acc-status">${t("loggedIn", user.displayName || user.username)}</div>
        <div class="acc-meta">${sync ? t("lastSync", new Date(sync).toLocaleString()) : t("never")}</div>
        <div class="acc-actions">
          <button class="acc-btn" data-act="sync">${t("syncNow")}</button>
          <button class="acc-btn ghost" data-act="logout">${t("logout")}</button>
        </div>`;
    } else if (mode === "reset") {
      body = `
        <h2>${t("resetTitle")}</h2>
        <label>${t("username")}<input id="acc-u" autocomplete="username"></label>
        <label>${t("recovery")}<input id="acc-r" placeholder="XXXX-XXXX-XXXX" autocomplete="off"></label>
        <label>${t("newPassword")}<input id="acc-p" type="password" autocomplete="new-password"></label>
        <div class="acc-actions">
          <button class="acc-btn" data-act="do-reset">${t("doReset")}</button>
          <button class="acc-btn ghost" data-act="mode-login">${t("backToLogin")}</button>
        </div>`;
    } else {
      const reg = mode === "register";
      body = `
        <div class="acc-tabs">
          <button class="acc-tab ${reg ? "" : "on"}" data-act="mode-login">${t("login")}</button>
          <button class="acc-tab ${reg ? "on" : ""}" data-act="mode-register">${t("register")}</button>
        </div>
        <label>${t("username")}<input id="acc-u" autocomplete="username"></label>
        <label>${t("password")}<input id="acc-p" type="password" autocomplete="${reg ? "new-password" : "current-password"}"></label>
        ${reg ? `<label>${t("password2")}<input id="acc-p2" type="password" autocomplete="new-password"></label>` : ""}
        <div class="acc-actions">
          <button class="acc-btn" data-act="${reg ? "do-register" : "do-login"}">${reg ? t("doRegister") : t("doLogin")}</button>
          ${reg ? "" : `<button class="acc-btn ghost" data-act="mode-reset">${t("forgot")}</button>`}
        </div>
        ${reg ? `<p class="acc-tip">${t("tip")}</p>` : ""}`;
    }
    p.innerHTML = `
      <div class="acc-sheet">
        <div class="acc-head">
          <div>
            <div class="acc-kicker">${t("kicker")}</div>
            <h1>${t("title")}</h1>
          </div>
          <button class="acc-close" data-act="close" aria-label="close">×</button>
        </div>
        <p class="acc-sub">${t("sub")}</p>
        ${body}
        <div class="acc-msg" id="acc-msg"></div>
      </div>`;
    p.querySelector(".acc-sub") && S.token === "" &&
      p.querySelector(".acc-sub").insertAdjacentHTML("afterend",
        `<div class="acc-badge">${t("notLoggedIn")}</div>`);
  }

  const msg = (text, kind = "info") => {
    const box = document.querySelector("#acc-msg");
    if (!box) return;
    box.textContent = text;
    box.className = "acc-msg " + kind;
    if (kind === "ok") {
      // 恢复码需要方便抄走
      box.innerHTML = `<div>${escapeHtml(text)}</div>`;
    }
  };

  const escapeHtml = (v) => String(v).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);

  const val = (id) => (document.getElementById(id)?.value || "").trim();

  async function handle(act) {
    try {
      if (act === "close") return close();
      if (act === "mode-login" || act === "mode-register" || act === "mode-reset") {
        mode = act.replace("mode-", "");
        return render();
      }
      if (act === "do-register") {
        const p1 = val("acc-p"); const p2 = val("acc-p2");
        if (p1 !== p2) return msg(t("pwMismatch"), "err");
        const r = await req("/api/auth/register",
          { method: "POST", body: { username: val("acc-u"), password: p1 }, auth: false });
        S.token = r.token; S.user = r.user; mode = "login";
        render();
        const box = document.querySelector("#acc-msg");
        box.className = "acc-msg ok";
        box.innerHTML = `<div>${t("registered")}</div>
          <div class="acc-code">${escapeHtml(r.recoveryCode)}</div>
          <button class="acc-btn small" data-act="copy">${t("copy")}</button>`;
        emit("login", r.user);
        return;
      }
      if (act === "do-login") {
        const r = await req("/api/auth/login",
          { method: "POST", body: { username: val("acc-u"), password: val("acc-p") }, auth: false });
        S.token = r.token; S.user = r.user;
        render();
        msg(t("loggedIn", r.user.displayName || r.user.username), "ok");
        startSync();
        emit("login", r.user);
        return;
      }
      if (act === "do-reset") {
        if (!val("acc-r")) return msg(t("needRecovery"), "err");
        const r = await req("/api/auth/reset-password", {
          method: "POST", auth: false,
          body: { username: val("acc-u"), recoveryCode: val("acc-r"),
                  newPassword: val("acc-p") },
        });
        mode = "login";
        render();
        const box = document.querySelector("#acc-msg");
        box.className = "acc-msg ok";
        box.innerHTML = `<div>${t("resetOk")}</div>
          <div class="acc-code">${escapeHtml(r.recoveryCode)}</div>
          <button class="acc-btn small" data-act="copy">${t("copy")}</button>`;
        return;
      }
      if (act === "logout") {
        try { await req("/api/auth/logout", { method: "POST" }); } catch (_) { /* 忽略 */ }
        S.token = ""; S.user = ""; S.lastSync = "";
        render();
        emit("logout");
        return;
      }
      if (act === "sync") {
        msg(t("syncing"));
        await startSync();
        render();
        return;
      }
      if (act === "copy") {
        const code = document.querySelector(".acc-code")?.textContent || "";
        if (code) {
          try {
            await navigator.clipboard.writeText(code);
            const b = document.querySelector('[data-act="copy"]');
            if (b) b.textContent = t("copied");
          } catch (_) { /* 无剪贴板权限：用户手动选择 */ }
        }
      }
    } catch (e) {
      msg(t("err", e.message), "err");
    }
  }

  let startSync = async () => null;   // 由 app.js 注入（需要读写 state.marks）

  function open() {
    render();
    ensurePanel().hidden = false;
    document.body.classList.add("acc-open");
    sessionStorage.setItem(STATE_KEY, "1");
  }
  function close() {
    if (panel) panel.hidden = true;
    document.body.classList.remove("acc-open");
    sessionStorage.removeItem(STATE_KEY);
  }

  function mount({ getMarks, setMarks, button = null }) {
    ensurePanel().addEventListener("click", (e) => {
      const act = e.target.closest("[data-act]")?.dataset.act;
      if (act) handle(act);
    });
    startSync = async () => {
      try {
        const merged = await pullAndMerge(getMarks, setMarks);
        if (merged) msg(t("lastSync", new Date(S.lastSync).toLocaleString()), "ok");
        return merged;
      } catch (e) {
        msg(t("err", e.message), "err");
        return null;
      }
    };
    const btn = button || document.querySelector("[data-account-open]");
    if (btn) btn.addEventListener("click", open);
    if (S.token) startSync();      // 已登录：打开页面即合并一次
    if (sessionStorage.getItem(STATE_KEY)) open();
    return { open, close, on, syncSoon, startSync, state: S };
  }

  window.WHGAccount = { mount, open, close, on, syncSoon, mergeMarks, state: S, t };
})();
