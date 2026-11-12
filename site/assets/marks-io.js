/* 个人标记（去过 / 赞过 / 不好）的本地备份辅助。
 *
 * 站点始终以 localStorage 为第一存储；这里的 merge() 只服务于
 * 「导出 JSON / 导入 JSON」的手动搬运，不联网、不涉及任何凭据。
 *
 * 跨浏览器自动同步请使用站内账号（account.js + 服务器 /api）。
 */
(() => {
  "use strict";

  // 合并两份标记：同一个地点取并集；标记时间较新的一方优先。
  function merge(localMarks, importedMarks) {
    const merged = { ...localMarks };
    for (const [id, m] of Object.entries(importedMarks || {})) {
      const l = merged[id];
      if (!l) {
        merged[id] = m;
        continue;
      }
      merged[id] = {
        ...l,
        v: Math.max(l.v || 0, m.v || 0) || undefined,
        r: l.r || m.r || null,
        c: l.c || m.c || "",
        p: l.p || m.p || "",
        n: l.n || m.n || "",
      };
      // 既没有「去过」也没有评价的条目视为已取消标记
      if (!merged[id].v && !merged[id].r) delete merged[id];
    }
    return merged;
  }

  window.WHTG_MARKS = { merge };
})();
