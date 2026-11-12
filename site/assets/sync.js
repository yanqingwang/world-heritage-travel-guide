/* Cloud sync for personal marks (visited/liked/bad).
 *
 * localStorage ("whtg-marks") stays the primary store.  This module adds an
 * optional cloud copy: one JSON file per device pair under sync/ in the repo,
 * written through the GitHub Contents API.  The visitor supplies their own
 * fine-grained PAT (Contents: Read & Write on this one repository) — the site
 * never embeds or proxies credentials.  The token lives in localStorage on the
 * visitor's machine only.
 *
 *   GET  /repos/{owner}/{repo}/contents/sync/<file>   read  (works anonymously)
 *   PUT  /repos/{owner}/{repo}/contents/sync/<file>   write (needs the PAT)
 *
 * Anonymous visitors can still move marks between devices with the JSON
 * export/import buttons.
 */
(() => {
  "use strict";

  const OWNER = "yanqingwang";
  const REPO = "world-heritage-travel-guide";
  const BRANCH = "main";
  const DIR = "sync";
  const TOKEN_KEY = "whtg-sync-token";
  const NAME_KEY = "whtg-sync-name";
  const LAST_KEY = "whtg-sync-last";

  const api = (path, opts = {}) => {
    const headers = { Accept: "application/vnd.github+json" };
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) headers.Authorization = `Bearer ${token}`;
    return fetch(`https://api.github.com${path}`, { ...opts, headers })
      .then(async (r) => {
        if (!r.ok) {
          let msg = `GitHub API ${r.status}`;
          try { msg = (await r.json()).message || msg; } catch (_) {}
          const err = new Error(msg);
          err.status = r.status;
          throw err;
        }
        return r.status === 204 ? null : r.json();
      });
  };

  // A visitor's own PAT cannot grant itself write access to someone else's
  // repository.  Check /user first (token valid?) and then permissions.push
  // on the target repo (can this token actually commit here?) before showing
  // a confusing "Resource not accessible by integration" on every push.
  async function checkAccess() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return { ok: false, reason: "no_token" };
    let user;
    try {
      const r = await fetch("https://api.github.com/user", {
        headers: { Accept: "application/vnd.github+json", Authorization: `Bearer ${token}` },
      });
      if (r.status === 401) return { ok: false, reason: "bad_token" };
      if (r.status === 403) return { ok: false, reason: "rate_limit" };
      if (!r.ok) return { ok: false, reason: `http_${r.status}` };
      user = await r.json();
    } catch (_) {
      return { ok: false, reason: "network" };
    }
    try {
      const r = await fetch(`https://api.github.com/repos/${OWNER}/${REPO}`, {
        headers: { Accept: "application/vnd.github+json", Authorization: `Bearer ${token}` },
      });
      if (r.status === 401) return { ok: false, reason: "bad_token" };
      if (r.status === 403) return { ok: false, reason: "rate_limit" };
      if (!r.ok) return { ok: false, reason: `http_${r.status}` };
      const repo = await r.json();
      if (!repo.permissions || !repo.permissions.push) {
        return { ok: false, reason: "no_push" };
      }
      return { ok: true, login: user.login };
    } catch (_) {
      return { ok: false, reason: "network" };
    }
  }

  function explain(err) {
    if (err && err.status === 401) return "bad_token";
    if (err && err.status === 403) return "rate_limit";
    if (err && err.status === 409) return "conflict";
    if (err && err.status === 404) return "not_found";
    return "network";
  }

  const fileName = () => {
    let name = localStorage.getItem(NAME_KEY);
    if (!name) {
      name = `device-${Math.random().toString(36).slice(2, 8)}`;
      localStorage.setItem(NAME_KEY, name);
    }
    return `${DIR}/marks-${name}.json`;
  };

  // Encode/decode UTF-8 content the way the Contents API expects.
  const enc = (obj) => btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(obj))));
  const dec = (b64) => JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))));

  const state = {
    get token() { return localStorage.getItem(TOKEN_KEY) || ""; },
    get device() { return fileName().replace(`${DIR}/marks-`, "").replace(".json", ""); },
    get last() { try { return JSON.parse(localStorage.getItem(LAST_KEY)) || null; } catch (_) { return null; } },
  };

  async function push(marks) {
    const path = fileName();
    let sha = null;
    try {
      const cur = await api(`/repos/${OWNER}/${REPO}/contents/${path}?ref=${BRANCH}`);
      sha = cur.sha;
    } catch (_) { /* 404 → create new file */ }
    const doc = {
      version: 1,
      device: state.device,
      updated_at: new Date().toISOString(),
      marks,
    };
    await api(`/repos/${OWNER}/${REPO}/contents/${path}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `sync: marks backup from ${state.device}`,
        content: enc(doc),
        branch: BRANCH,
        ...(sha ? { sha } : {}),
      }),
    });
    const stamp = { at: doc.updated_at, device: state.device, count: Object.keys(marks).length };
    localStorage.setItem(LAST_KEY, JSON.stringify(stamp));
    return stamp;
  }

  async function pull() {
    const path = fileName();
    const cur = await api(`/repos/${OWNER}/${REPO}/contents/${path}?ref=${BRANCH}`);
    const doc = dec(cur.content || "");
    return { marks: doc.marks || {}, updated_at: doc.updated_at || "", device: doc.device || "" };
  }

  // Merge cloud marks into local: cloud wins on newer non-empty records only
  // when the local record is absent; explicit local records always win so a
  // pull never erases what the visitor just marked.  Returns merged map.
  function merge(localMarks, cloudMarks) {
    const merged = { ...localMarks };
    for (const [id, m] of Object.entries(cloudMarks || {})) {
      const l = merged[id];
      if (!l) merged[id] = m;
      else {
        // union of flags; cloud "r" wins only when local has none
        merged[id] = {
          ...l,
          v: Math.max(l.v || 0, m.v || 0) || undefined,
          r: l.r || m.r || null,
          c: l.c || m.c || "",
          p: l.p || m.p || "",
          n: l.n || m.n || "",
        };
        if (!merged[id].v && !merged[id].r) delete merged[id];
      }
    }
    return merged;
  }

  async function listDevices() {
    const dir = await api(`/repos/${OWNER}/${REPO}/contents/${DIR}?ref=${BRANCH}`);
    return (Array.isArray(dir) ? dir : [])
      .filter((f) => f.type === "file" && f.name.startsWith("marks-") && f.name.endsWith(".json"))
      .map((f) => ({ name: f.name.replace(/^marks-/, "").replace(/\.json$/, ""), sha: f.sha, path: f.path }));
  }

  async function readDevice(name) {
    const cur = await api(`/repos/${OWNER}/${REPO}/contents/${DIR}/marks-${name}.json?ref=${BRANCH}`);
    const doc = dec(cur.content || "");
    return { marks: doc.marks || {}, updated_at: doc.updated_at || "" };
  }

  window.WHTG_SYNC = {
    state, push, pull, merge, listDevices, readDevice, checkAccess, explain,
    saveToken: (t) => t ? localStorage.setItem(TOKEN_KEY, t.trim()) : localStorage.removeItem(TOKEN_KEY),
    saveName: (n) => n ? localStorage.setItem(NAME_KEY, n.trim().replace(/[^a-zA-Z0-9_-]/g, "-").slice(0, 32)) : localStorage.removeItem(NAME_KEY),
    clearLast: () => localStorage.removeItem(LAST_KEY),
  };
})();
