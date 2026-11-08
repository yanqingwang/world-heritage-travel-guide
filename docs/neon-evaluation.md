# Neon / PostgreSQL 可行性评估

结论：**当前公开站点不需要 Neon**。静态 JSON + 浏览器端筛选在 1,572 条记录规模下已经足够快；引入 Neon 反而会增加网络往返、冷启动和密钥暴露风险。只有将来做“多用户写回 / 收藏 / 评论 / 外部 API”时才值得增加一个只读或读写 API 层。

> 2026-11-09 更新：站点已改为「列表索引 + 单条详情」按需加载——列表只需约 1.3 MB（gzip 后 ~230 KB）的 `world-index.json`，点开条目时再取单条 JSON。这进一步拉开了与数据库方案的差距：首屏数据比整包 world.json 小 6 倍，慢网络下也能先看到列表。

## 实测数据（本机，2026-11-08）

| 指标 | 实测 |
|---|---:|
| `data/world.json` 原始大小 | 6.12 MB |
| gzip 后传输大小（CDN 常态） | ~1.62 MB |
| `site/data/world-index.json`（列表索引） | 1.3 MB raw / ~0.23 MB gzip |
| 浏览器解析 1,213 条 JSON | 73 ms |
| 浏览器内按国家筛选（JP） | 0.4 ms |
| `data/china.json` | 2.52 MB / 359 条 |

浏览器端筛选在内存数组上执行，复杂度 O(n)，1,572 条记录下低于 1 ms；搜索、国家、类型、签证、资料等级组合筛选同样是毫秒级。

## 对比 Neon

| 维度 | 静态 JSON（当前） | Neon Postgres |
|---|---|---|
| 查询延迟 | 解析一次后 < 1 ms | 每次 20–100 ms 网络往返 + 连接/冷启动 |
| 部署 | GitHub Pages / 任意静态托管 | 需要 API 网关或 Serverless Function |
| 密钥 | 无 | 需要把连接串放进服务端；静态前端不能直连（会暴露） |
| 离线/缓存 | CDN 可缓存，离线可用 | 每次都要联网；CDN 缓存无效 |
| 数据更新 | Actions 重建 JSON 并提交 | 需要 migration / upsert 管线 |
| 成本 | 0 | 免费额度够用，但增加运维面 |
| 适用规模 | 十万条以内浏览器筛选都可行 | 百万级、复杂 SQL、多表关联、并发写入 |

## 什么情况下再引入 Neon

1. 需要跨设备保存用户数据（收藏、行程、笔记）；
2. 需要对外开放带分页/全文检索的 API；
3. 数据量增长到浏览器内存/解析不可接受（例如 > 5–10 万条完整记录）；
4. 需要多人协作编辑与审计。

届时建议：Neon 只存“用户数据 + 可检索索引”，公开只读数据仍由 JSON/CDN 提供；前端通过一个最小 API（Vercel/Cloudflare Worker）访问 Neon，不暴露连接串。

## 可选：一键导入 SQL（未启用）

如果外部研究者需要 SQL 版本，可用下面的最小 schema 把两份 JSON 导入本地 Postgres/Neon；本项目默认不维护在线库。

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE sites (
  id            text PRIMARY KEY,
  dataset       text NOT NULL,          -- china_5a | unesco
  tier          text,                   -- full | basic
  country       text,                   -- ISO2; 中国条目为 CN
  province_zh   text,
  city_zh       text,
  name_zh       text,
  name_en       text,
  name_local    text,
  local_lang    text,
  lat           double precision,
  lon           double precision,
  category      text,
  intro_zh      text,
  intro_en      text,
  intro_local   text,
  unesco_id     text,
  year          text,
  criteria      text,
  visa_summary  text,
  popularity_rank integer,
  payload       jsonb NOT NULL,         -- 完整记录
  updated_at    timestamptz
);
CREATE INDEX sites_country_idx ON sites (country);
CREATE INDEX sites_dataset_tier_idx ON sites (dataset, tier);
CREATE INDEX sites_name_trgm_idx ON sites USING gin (name_en gin_trgm_ops);
```
