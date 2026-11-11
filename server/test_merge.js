// 前端合并逻辑单测：node server/test_merge.js
// 从 account.js 抽出 mergeMarks 的等价实现验证（与浏览器端保持同一算法）
const assert = require('assert');

function mergeMarks(local, remote) {
  const out = { ...(remote || {}) };
  let changed = false;
  for (const [id, lm] of Object.entries(local || {})) {
    const rm = out[id];
    if (!rm) { out[id] = lm; changed = true; continue; }
    const lt = Number(lm.t || 0);
    const rt = Number(rm.t || 0);
    if (lt > rt) { out[id] = lm; changed = true; }
    if (lt > rt && !lm.v && !lm.r) delete out[id];
  }
  return { merged: out, changed };
}

// 1) 本地新增推送
let r = mergeMarks({ a: { v: 1, t: 10 } }, {});
assert.deepStrictEqual(r.merged, { a: { v: 1, t: 10 } });
assert.ok(r.changed);

// 2) 本地较新覆盖远端（本地缺 r = 用户取消了 like，整条以较新者为准）
r = mergeMarks({ a: { v: 1, t: 20 } }, { a: { v: 1, r: 'like', t: 10 } });
assert.deepStrictEqual(r.merged.a, { v: 1, t: 20 });

// 3) 远端较新保留远端
r = mergeMarks({ a: { v: 1, t: 10 } }, { a: { v: 1, r: 'like', t: 30 } });
assert.deepStrictEqual(r.merged.a, { v: 1, r: 'like', t: 30 });
assert.strictEqual(r.changed, false);

// 4) 本地较新的墓碑（取消标记）应删除
r = mergeMarks({ a: { t: 50 } }, { a: { v: 1, t: 10 } });
assert.strictEqual(r.merged.a, undefined);
assert.ok(r.changed);

// 5) 远端较新的标记不被旧墓碑删掉
r = mergeMarks({ a: { t: 5 } }, { a: { v: 1, t: 10 } });
assert.strictEqual(r.merged.a.v, 1);

// 6) 两端各有独有条目 → 并集
r = mergeMarks({ a: { v: 1, t: 1 } }, { b: { v: 1, t: 2 } });
assert.deepStrictEqual(Object.keys(r.merged).sort(), ['a', 'b']);
assert.strictEqual(r.changed, true);

// 7) 空输入
assert.deepStrictEqual(mergeMarks({}, {}).merged, {});
assert.deepStrictEqual(mergeMarks(null, null).merged, {});

console.log('mergeMarks: 9 assertions OK');
