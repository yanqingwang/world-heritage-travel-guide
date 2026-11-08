(() => {
  "use strict";

  const I18N = {
    zh: {
      title: "世界遗产旅行指南",
      subtitle: "中国 5A 景区 · 海外 UNESCO 世界遗产",
      tabs: { china: "中国 5A", world: "海外世界遗产" },
      heroEyebrow: "公开数据 · 每周更新",
      heroTitle: "从 5A 景区到世界遗产，一次查清怎么去、住哪里、是否免签。",
      heroText: "官方名录、维基百科、OpenStreetMap 与 UNESCO 多语言文本合并为一份可检索的数据集。",
      search: "搜索景区、城市、国家…",
      allCountries: "全部国家",
      allProvinces: "全部省份",
      allSubdivisions: "全部省份 / 州",
      visitedOnly: "只看去过的",
      globe: "我的地球",
      globeTitle: "点亮你去过的世界",
      globeKicker: "我的足迹",
      globeHint: "拖动旋转 · 滚轮缩放 · 点击地区筛选",
      globeEmpty: "还没有标记。打开任意目的地，点「去过」即可点亮所在省份或国家。",
      globeSites: "目的地",
      globeCountries: "国家",
      globeProvinces: "省份",
      focusChina: "聚焦中国",
      spinOn: "暂停旋转",
      spinOff: "自动旋转",
      legendVisited: "去过",
      legendIdle: "未点亮",
      markVisited: "去过",
      markLike: "赞过",
      markBad: "不好",
      allCategories: "全部类型",
      allVisa: "全部签证状态",
      allTier: "全部资料等级",
      reset: "重置",
      loadMore: "加载更多",
      empty: "没有找到匹配的目的地。",
      emptyHint: "试试清空筛选条件，或换一个关键词。",
      footer: "数据来源：文化和旅游部、UNESCO、Wikipedia、Wikidata、OpenStreetMap、OurAirports。图片版权归原作者，详见条目内署名。",
      footerNote: "距离为直线距离；酒店/交通来自 OpenStreetMap，可能存在遗漏；签证政策会变化，出行前请以官方发布为准。",
      stats: { china: "中国 5A 景区", world: "海外世界遗产", full: "完整资料条目", langs: "官方语言版本" },
      result: (n, total) => `显示 ${n.toLocaleString("zh-CN")} / ${total.toLocaleString("zh-CN")} 条`,
      visa: {
        visa_free: "免签", visa_on_arrival: "落地签", evisa: "电子签",
        eta: "电子许可", visa_required: "需签证", restricted: "限制入境",
        mixed: "各国不同", unknown: "待核实", "n/a": "不适用",
      },
      tier: { full: "完整资料", basic: "基本资料" },
      cat: {
        natural: "自然风光", cultural: "人文古迹", historic: "历史遗址",
        mixed: "自然人文", theme: "主题乐园", resort: "度假休闲",
        museum: "博物馆", geology: "地质奇观", religious: "宗教文化",
        red: "红色旅游", folk: "民俗文化", wetland: "生态湿地",
        mountain: "山地风光", desert: "草原沙漠", coastal: "海滨度假",
        town: "古镇村落", garden: "皇家园林", grotto: "石窟艺术",
        water: "水利工程", "": "世界遗产",
      },
      sections: {
        intro: "简介", local: "本地语言介绍", transport: "交通", hotels: "附近酒店",
        visa: "签证（中国护照）", langs: "多语言信息", sources: "来源与图片署名",
        foreign: "境外游客", ranking: "热度",
      },
      labels: {
        airport: "机场", hsr: "高铁站", rail: "火车站", ferry: "码头",
        distance: "距离", fromBeijing: "距北京直线距离（至最近机场）", nearest: "最近",
        star: "星级", chain: "连锁", hotel: "酒店", noHotels: "暂未收录酒店数据；下次 OSM 刷新后补齐。",
        noTransport: "暂无交通设施数据。", coords: "坐标", map: "在 OpenStreetMap 查看",
        official: "官网", booking: "预约", unesco: "UNESCO 页面",
        criteria: "入选标准", year: "入选年份", danger: "濒危遗产",
        transnational: "跨境遗产", localLang: "本地语言", machine: "机器翻译",
        wikipedia: "维基百科", unescoOfficial: "UNESCO 官方文本", wikidata: "Wikidata",
        foreignOpen: "通常对境外游客开放", foreignUnknown: "需向官方核实",
        basicNote: "海外基本资料条目仍提供官方多语言介绍、机场与北京距离；酒店仅收录热门 150 条。",
        visaNote: "签证状态来自英文维基百科中国护照签证要求表，可能滞后；出行前请核实。",
        imageCredit: "图片",
      },
    },
    en: {
      title: "World Heritage Travel Guide",
      subtitle: "China 5A scenic areas · UNESCO World Heritage overseas",
      tabs: { china: "China 5A", world: "World Heritage" },
      heroEyebrow: "OPEN DATA · WEEKLY UPDATES",
      heroTitle: "From China's 5A scenic areas to World Heritage sites: how to get there, where to stay, and whether you need a visa.",
      heroText: "Official lists, Wikipedia, OpenStreetMap and UNESCO's multilingual texts merged into one searchable dataset.",
      search: "Search site, city or country…",
      allCountries: "All countries",
      allProvinces: "All provinces",
      allSubdivisions: "All provinces / states",
      visitedOnly: "Visited only",
      globe: "My globe",
      globeTitle: "Light up the world you have seen",
      globeKicker: "MY FOOTPRINT",
      globeHint: "Drag to rotate · scroll to zoom · click a region to filter",
      globeEmpty: "Nothing marked yet. Open any destination and press “Visited” to light up its province or country.",
      globeSites: "Destinations",
      globeCountries: "Countries",
      globeProvinces: "Provinces",
      focusChina: "Focus China",
      spinOn: "Pause spin",
      spinOff: "Auto-spin",
      legendVisited: "Visited",
      legendIdle: "Not lit",
      markVisited: "Visited",
      markLike: "Liked",
      markBad: "Not for me",
      allCategories: "All categories",
      allVisa: "All visa statuses",
      allTier: "All record tiers",
      reset: "Reset",
      loadMore: "Load more",
      empty: "No matching destination found.",
      emptyHint: "Try clearing filters or using a different keyword.",
      footer: "Sources: Ministry of Culture and Tourism, UNESCO, Wikipedia, Wikidata, OpenStreetMap, OurAirports. Image credits appear in each entry.",
      footerNote: "Distances are great-circle distances. Hotels/transport come from OpenStreetMap and may be incomplete. Visa rules change; verify with official sources before travelling.",
      stats: { china: "China 5A sites", world: "Overseas World Heritage", full: "Full records", langs: "Official-language editions" },
      result: (n, total) => `Showing ${n.toLocaleString("en-US")} / ${total.toLocaleString("en-US")}`,
      visa: {
        visa_free: "Visa-free", visa_on_arrival: "Visa on arrival", evisa: "eVisa",
        eta: "ETA", visa_required: "Visa required", restricted: "Restricted",
        mixed: "Varies by country", unknown: "Verify", "n/a": "Not applicable",
      },
      tier: { full: "Full record", basic: "Basic record" },
      cat: {
        natural: "Natural scenery", cultural: "Cultural heritage", historic: "Historic site",
        mixed: "Natural & cultural", theme: "Theme park", resort: "Resort & leisure",
        museum: "Museum", geology: "Geological wonder", religious: "Religious culture",
        red: "Red tourism", folk: "Folk culture", wetland: "Wetland ecology",
        mountain: "Mountain scenery", desert: "Grassland & desert", coastal: "Coastal resort",
        town: "Ancient town", garden: "Royal garden", grotto: "Grotto art",
        water: "Water conservancy", "": "World Heritage",
      },
      sections: {
        intro: "Introduction", local: "In the local language", transport: "Transport",
        hotels: "Nearby hotels", visa: "Visa (Chinese passport)", langs: "Language availability",
        sources: "Sources & image credits", foreign: "International visitors", ranking: "Popularity",
      },
      labels: {
        airport: "Airport", hsr: "High-speed rail", rail: "Railway station", ferry: "Ferry terminal",
        distance: "Distance", fromBeijing: "Great-circle distance from Beijing (nearest airport)", nearest: "Nearest",
        star: "Star-rated", chain: "Chain", hotel: "Hotel", noHotels: "Hotel data not collected yet; the next OSM refresh will fill it.",
        noTransport: "No transport data available.", coords: "Coordinates", map: "View on OpenStreetMap",
        official: "Official site", booking: "Booking", unesco: "UNESCO page",
        criteria: "Criteria", year: "Inscribed", danger: "In danger",
        transnational: "Transnational", localLang: "Local language", machine: "machine translation",
        wikipedia: "Wikipedia", unescoOfficial: "UNESCO official text", wikidata: "Wikidata",
        foreignOpen: "Generally open to international visitors", foreignUnknown: "Verify with official source",
        basicNote: "Basic overseas records still include official multilingual text, airports and Beijing distance; hotels are only included for the top 150.",
        visaNote: "Visa status comes from Wikipedia's visa requirements table for Chinese passports and may lag. Verify before travelling.",
        imageCredit: "Image",
      },
    },
  };

  const state = {
    tab: "china",
    lang: localStorage.getItem("whtg-lang") || "zh",
    query: "",
    country: "",
    subdivision: "",
    category: "",
    visa: "",
    tier: "",
    visitedOnly: false,
    limit: 60,
    data: { china: null, world: null },
    details: {},
    loading: {},
    marks: {},
    pending: null,
  };

  // Personal marks live in localStorage only: { [siteId]: { v, r, c, p, n } }
  // v = visited flag, r = "like" | "bad", c/p = country / ISO 3166-2 captured
  // at mark time so the globe does not need to download both datasets.
  try {
    state.marks = JSON.parse(localStorage.getItem("whtg-marks") || "{}") || {};
  } catch (_) {
    state.marks = {};
  }
  const saveMarks = () => {
    try { localStorage.setItem("whtg-marks", JSON.stringify(state.marks)); } catch (_) {}
  };

  const $ = (sel) => document.querySelector(sel);
  const t = () => I18N[state.lang];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
  const fmtKm = (v) => {
    if (v == null) return "—";
    const n = Number(v);
    const digits = n < 10 ? 1 : 0;
    return `${n.toLocaleString(state.lang === "zh" ? "zh-CN" : "en-US", {
      minimumFractionDigits: digits, maximumFractionDigits: digits,
    })} km`;
  };

  function localizedName(site) {
    if (state.lang === "zh") return site.name_zh || site.name_en || site.name_local || "";
    return site.name_en || site.name_zh || site.name_local || "";
  }
  function secondaryName(site) {
    const primary = localizedName(site);
    for (const v of [site.name_zh, site.name_en, site.name_local]) {
      if (v && v !== primary) return v;
    }
    return "";
  }
  function locationLine(site) {
    if (site.dataset === "china_5a") {
      return state.lang === "zh"
        ? [site.province_zh, site.city_zh].filter(Boolean).join(" · ")
        : [site.province_en, site.city_en].filter(Boolean).join(" · ");
    }
    const place = state.lang === "zh" ? site.country_zh : site.country_en;
    return [place, site.region].filter(Boolean).join(" · ");
  }
  function categoryLabel(site) {
    if (site.dataset === "china_5a") return state.lang === "zh" ? site.category_zh : site.category_en;
    return state.lang === "zh" ? site.category_zh : site.category_en;
  }
  function visaLabel(status) {
    return t().visa[status] || status || t().visa.unknown;
  }

  function setLang(lang) {
    state.lang = lang;
    localStorage.setItem("whtg-lang", lang);
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    $("#lang-toggle").textContent = lang === "zh" ? "EN" : "中文";
    $("#site-title").textContent = t().title;
    $("#site-subtitle").textContent = t().subtitle;
    $("#hero-eyebrow").textContent = t().heroEyebrow;
    $("#hero-title").textContent = t().heroTitle;
    $("#hero-text").textContent = t().heroText;
    $("#search").placeholder = t().search;
    $("#reset").textContent = t().reset;
    $("#load-more").textContent = t().loadMore;
    syncVisitedToggle();
    updateGlobeButton();
    if (globe.open) {
      updateGlobeLabels();
      updateGlobeStats();
      globe.dirty = true;
    }
    $("#empty").querySelector("p").textContent = t().empty;
    $("#empty").querySelector(".muted").textContent = t().emptyHint;
    $("#footer-line").textContent = t().footer;
    updateFooter();
    document.querySelectorAll(".tab").forEach((el) => {
      el.textContent = t().tabs[el.dataset.tab];
    });
    buildFilters();
    renderStats();
    render();
    if ($("#detail").open) {
      const id = $("#detail").dataset.siteId;
      if (id) openDetail(id, true);
    }
  }

  function buildFilters() {
    const country = $("#country-filter");
    const subdivision = $("#subdivision-filter");
    const category = $("#category-filter");
    const visa = $("#visa-filter");
    const tier = $("#tier-filter");
    const data = state.data[state.tab];
    if (data) {
      if (state.tab === "china") {
        // Same two-level logic as the overseas tab: country first, then the
        // ISO 3166-2 province.  China only has one country, but keeping the
        // control identical avoids a second mental model.
        country.innerHTML = `<option value="CN">${esc(state.lang === "zh" ? "中国" : "China")}</option>`;
        country.disabled = true;
        const provinces = [...new Map(data.sites.map((s) => [s.province_iso || s.province_zh, {
          value: s.province_iso || s.province_zh,
          zh: s.province_zh, en: s.province_en,
        }])).values()].sort((a, b) => (a.zh || "").localeCompare(b.zh || "", "zh"));
        subdivision.innerHTML = `<option value="">${esc(t().allSubdivisions)}</option>` +
          provinces.map((p) => `<option value="${esc(p.value)}">${esc(state.lang === "zh" ? p.zh : p.en)}</option>`).join("");
        subdivision.disabled = false;
        visa.disabled = true;
        tier.disabled = true;
      } else {
        // Countries with the most full-tier records first, then alphabetical.
        const fullCount = new Map();
        for (const s of data.sites) {
          if (s.tier === "full") fullCount.set(s.country, (fullCount.get(s.country) || 0) + 1);
        }
        const countries = [...new Map(data.sites.map((s) => [s.country, {
          value: s.country, zh: s.country_zh, en: s.country_en,
        }])).values()].sort((a, b) =>
          (fullCount.get(b.value) || 0) - (fullCount.get(a.value) || 0) ||
          (a.en || "").localeCompare(b.en || ""));
        country.innerHTML = `<option value="">${esc(t().allCountries)}</option>` +
          countries.map((p) => {
            const name = state.lang === "zh" ? (p.zh || p.en) : p.en;
            const n = fullCount.get(p.value) || 0;
            return `<option value="${esc(p.value)}">${esc(n ? `${name} (${n})` : name)}</option>`;
          }).join("");
        country.disabled = false;
        visa.disabled = false;
        tier.disabled = false;
        buildSubdivisionOptions();
      }
      const cats = [...new Set(data.sites.map((s) => s.category).filter(Boolean))];
      category.innerHTML = `<option value="">${esc(t().allCategories)}</option>` +
        cats.map((c) => `<option value="${esc(c)}">${esc(t().cat[c] || c)}</option>`).join("");
      category.disabled = false;
    }
    visa.innerHTML = `<option value="">${esc(t().allVisa)}</option>` +
      Object.entries(t().visa).map(([k, v]) => `<option value="${esc(k)}">${esc(v)}</option>`).join("");
    tier.innerHTML = `<option value="">${esc(t().allTier)}</option>` +
      Object.entries(t().tier).map(([k, v]) => `<option value="${esc(k)}">${esc(v)}</option>`).join("");
    // Language switches rebuild the options, so restore the active filters.
    country.value = state.country || (state.tab === "china" ? "CN" : "");
    if (state.tab === "world") buildSubdivisionOptions();
    subdivision.value = state.subdivision;
    category.value = state.category;
    visa.value = state.visa;
    tier.value = state.tier;
  }

  // ISO 3166-2 subdivisions of the selected country that actually have sites.
  function buildSubdivisionOptions() {
    const subdivision = $("#subdivision-filter");
    const data = state.data.world;
    if (!data) { subdivision.innerHTML = ""; subdivision.disabled = true; return; }
    const country = state.country;
    const rows = country
      ? data.sites.filter((s) => s.country === country && s.subdivision_iso &&
        s.subdivision_iso.startsWith(`${country}-`))
      : [];
    const unique = [...new Map(rows.map((s) => [s.subdivision_iso, {
      value: s.subdivision_iso,
      zh: s.subdivision_zh || s.subdivision_en || s.subdivision_iso,
      en: s.subdivision_en || s.subdivision_zh || s.subdivision_iso,
    }])).values()].sort((a, b) => (state.lang === "zh"
      ? (a.zh || "").localeCompare(b.zh || "", "zh")
      : (a.en || "").localeCompare(b.en || "")));
    subdivision.innerHTML = `<option value="">${esc(t().allSubdivisions)}</option>` +
      unique.map((p) => `<option value="${esc(p.value)}">${esc(state.lang === "zh" ? p.zh : p.en)}</option>`).join("");
    subdivision.disabled = unique.length === 0;
    if (!unique.some((p) => p.value === state.subdivision)) state.subdivision = "";
    subdivision.value = state.subdivision;
  }

  function syncVisitedToggle() {
    const el = $("#visited-filter");
    if (!el) return;
    el.classList.toggle("active", state.visitedOnly);
    el.setAttribute("aria-pressed", String(state.visitedOnly));
    el.textContent = `✓ ${t().visitedOnly}`;
  }

  function updateGlobeButton() {
    const { sites } = visitedSets();
    $("#globe-open").textContent = `🌍 ${t().globe}${sites ? ` · ${sites}` : ""}`;
  }

  function updateFooter() {
    const updated = state.data[state.tab]?.generated_at?.slice(0, 10);
    $("#footer-note").textContent = t().footerNote +
      (updated ? ` · ${state.lang === "zh" ? "数据更新" : "Data updated"} ${updated}` : "");
  }

  function renderStats() {
    const stats = $("#stats");
    const china = state.data.china;
    const world = state.data.world;
    const langCount = world ? (world.unesco_lang_count || 6) : 6;
    const locale = state.lang === "zh" ? "zh-CN" : "en-US";
    const fmtN = (n) => (typeof n === "number" ? n.toLocaleString(locale) : n);
    const items = [
      [china ? china.count : "359", t().stats.china],
      [world ? world.count : "1,213", t().stats.world],
      [world ? world.full_tier : "150", t().stats.full],
      [langCount, t().stats.langs],
    ];
    stats.innerHTML = items.map(([n, label]) =>
      `<div class="stat"><b>${esc(fmtN(n))}</b><span>${esc(label)}</span></div>`).join("");
  }

  function loadTab(tab) {
    state.tab = tab;
    document.querySelectorAll(".tab").forEach((el) => {
      const on = el.dataset.tab === tab;
      el.classList.toggle("active", on);
      el.setAttribute("aria-selected", String(on));
    });
    state.country = tab === "china" ? "CN" : "";
    state.subdivision = state.category = state.visa = state.tier = "";
    state.query = $("#search").value = "";
    state.limit = 60;
    $("#country-filter").value = state.country;
    $("#subdivision-filter").value = "";
    $("#category-filter").value = "";
    $("#visa-filter").value = "";
    $("#tier-filter").value = "";
    if (state.pending) {
      state.country = state.pending.country || state.country;
      state.subdivision = state.pending.subdivision || "";
      state.visitedOnly = !!state.pending.visitedOnly;
      state.pending = null;
    }
    syncVisitedToggle();
    if (state.data[tab]) {
      buildFilters();
      updateFooter();
      render();
      return;
    }
    if (state.loading[tab]) return;
    state.loading[tab] = true;
    $("#cards").innerHTML = `<p class="muted" style="grid-column:1/-1;padding:24px 0">Loading…</p>`;
    // The list only needs the compact index; full records load per site.
    fetch(`./data/${tab}-index.json`, { cache: "no-cache" })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((json) => {
        state.data[tab] = json;
        buildFilters();
        renderStats();
        updateFooter();
        render();
      })
      .catch((err) => {
        $("#cards").innerHTML = `<p class="muted" style="grid-column:1/-1;padding:24px 0">Failed to load data: ${esc(err.message)}</p>`;
      })
      .finally(() => { state.loading[tab] = false; });
  }

  function filtered() {
    const data = state.data[state.tab];
    if (!data) return [];
    const q = state.query.trim().toLowerCase();
    let list = data.sites.filter((s) => {
      if (q) {
        const hay = [
          s.name_zh, s.name_en, s.name_local, s.province_zh, s.province_en,
          s.city_zh, s.city_en, s.country_zh, s.country_en, s.region,
          s.category_zh, s.category_en,
        ].filter(Boolean).join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      if (state.country && s.country !== state.country) return false;
      if (state.subdivision) {
        const sub = state.tab === "china" ? (s.province_iso || s.province_zh) : s.subdivision_iso;
        if (sub !== state.subdivision) return false;
      }
      if (state.visitedOnly && !(state.marks[s.id] || {}).v) return false;
      if (state.category && s.category !== state.category) return false;
      if (state.tab === "world") {
        if (state.visa && s.visa_summary !== state.visa) return false;
        if (state.tier && s.tier !== state.tier) return false;
      }
      return true;
    });
    if (state.tab === "china") {
      list.sort((a, b) => (a.province_zh || "").localeCompare(b.province_zh || "", "zh") ||
        (a.name_zh || "").localeCompare(b.name_zh || "", "zh"));
    } else {
      list.sort((a, b) => (a.popularity_rank ?? 9999) - (b.popularity_rank ?? 9999));
    }
    return list;
  }

  function markRowHTML(site) {
    const m = state.marks[site.id] || {};
    const btn = (kind, cls, label) =>
      `<button type="button" class="mark-btn ${cls}" data-mark="${kind}" data-id="${esc(site.id)}" aria-pressed="${cls.includes("on")}">${label}</button>`;
    return `<div class="mark-row">
      ${btn("v", m.v ? "on" : "", `✓ ${esc(t().markVisited)}`)}
      ${btn("like", m.r === "like" ? "on like" : "", `👍 ${esc(t().markLike)}`)}
      ${btn("bad", m.r === "bad" ? "on bad" : "", `👎 ${esc(t().markBad)}`)}
    </div>`;
  }

  function cardHTML(site) {
    const name = localizedName(site);
    const sec = secondaryName(site);
    const img = (site.images || [])[0];
    const badges = [];
    if (site.dataset === "china_5a") {
      badges.push(`<span class="badge">${esc(categoryLabel(site))}</span>`);
    } else {
      badges.push(`<span class="badge">${esc(categoryLabel(site))}</span>`);
      if (site.tier === "full") badges.push(`<span class="badge gold">TOP ${esc(site.popularity_rank || "")}</span>`);
      badges.push(`<span class="badge ${site.visa_summary === "visa_free" ? "" : "clay"}">${esc(visaLabel(site.visa_summary))}</span>`);
    }
    if ((state.marks[site.id] || {}).v) {
      badges.unshift(`<span class="badge visited">✓ ${esc(t().markVisited)}</span>`);
    }
    const media = img
      ? `<img loading="lazy" src="${esc(img.url)}" alt="${esc(name)}" onerror="this.style.display='none';this.parentElement.querySelector('.fallback').style.display='grid'">`
      : "";
    const meta = [];
    if (site.dataset === "china_5a") {
      const hsr = (site.transport?.high_speed_stations || [])[0];
      if (hsr) meta.push(`🚄 ${esc(hsr.name)} · ${fmtKm(hsr.distance_km)}`);
      else {
        const ap = (site.transport?.airports || [])[0];
        if (ap) meta.push(`✈ ${esc(ap.iata || ap.name)} · ${fmtKm(ap.distance_km)}`);
      }
    } else {
      if (site.transport?.distance_beijing_km != null) meta.push(`✈ ${fmtKm(site.transport.distance_beijing_km)} → ${state.lang === "zh" ? "北京" : "Beijing"}`);
      if (site.year) meta.push(`${state.lang === "zh" ? "入选" : "Inscribed"} ${esc(site.year)}`);
    }
    return `<article class="card" data-id="${esc(site.id)}" tabindex="0" role="button" aria-label="${esc(name)}">
      <div class="card-media">
        ${media}
        <div class="fallback" style="display:${img ? "none" : "grid"}">${esc((name || "·").slice(0, 2))}</div>
        <div class="card-badges">${badges.join("")}</div>
      </div>
      <div class="card-body">
        <h3>${esc(name)}</h3>
        ${sec ? `<p class="local-name">${esc(sec)}</p>` : ""}
        <p class="where">${esc(locationLine(site))}</p>
        <div class="meta-line">${meta.map((m) => `<span>${m}</span>`).join("")}</div>
        ${markRowHTML(site)}
      </div>
    </article>`;
  }

  function render() {
    const list = filtered();
    const total = state.data[state.tab]?.count || list.length;
    $("#result-count").textContent = t().result(Math.min(state.limit, list.length), total);
    $("#result-note").textContent = state.tab === "world"
      ? (state.lang === "zh" ? "按中英文维基热度排序；TOP 150 为完整资料。" : "Ranked by Chinese/English Wikipedia interest; top 150 have full records.")
      : "";
    const shown = list.slice(0, state.limit);
    $("#cards").innerHTML = shown.map(cardHTML).join("");
    $("#empty").hidden = list.length > 0;
    $("#load-more").hidden = list.length <= state.limit;
    document.querySelectorAll(".card").forEach((el) => {
      el.addEventListener("click", (e) => {
        if (e.target.closest(".mark-btn")) return;
        openDetail(el.dataset.id);
      });
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openDetail(el.dataset.id); }
      });
    });
  }

  function sectionHTML(title, body) {
    return `<section class="section"><h3>${esc(title)}</h3>${body}</section>`;
  }

  function listHTML(items, renderItem) {
    if (!items || !items.length) return "";
    return `<ul class="list">${items.map(renderItem).join("")}</ul>`;
  }

  function openDetail(id, keep) {
    const data = state.data[state.tab];
    const summary = data?.sites.find((s) => s.id === id);
    if (!summary) return;
    const d = $("#detail");
    d.dataset.siteId = id;
    if (!keep && !d.open) d.showModal();
    const cached = state.details[id];
    if (cached) { renderDetail(cached); return; }
    // Paint the list-level header immediately, then swap in the full record.
    $("#detail-kicker").textContent = locationLine(summary);
    $("#detail-title").textContent = localizedName(summary);
    $("#detail-sub").textContent = secondaryName(summary);
    $("#detail-body").innerHTML = `<p class="note">${state.lang === "zh" ? "加载详情…" : "Loading details…"}</p>`;
    fetch(`./data/${state.tab}/${id}.json`, { cache: "no-cache" })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((site) => {
        state.details[id] = site;
        if (d.dataset.siteId === id) renderDetail(site);
      })
      .catch((err) => {
        $("#detail-body").innerHTML =
          `<p class="note">${state.lang === "zh" ? "详情加载失败" : "Failed to load details"}: ${esc(err.message)}</p>`;
      });
  }

  function renderDetail(site) {
    const d = $("#detail");
    d.dataset.siteId = site.id;
    const name = localizedName(site);
    const sec = secondaryName(site);
    $("#detail-kicker").textContent = site.dataset === "china_5a"
      ? `${locationLine(site)} · ${categoryLabel(site)}`
      : `${state.lang === "zh" ? (site.country_zh || site.country_en) : (site.country_en || site.country_zh)} ${site.region ? "· " + site.region : ""} · ${categoryLabel(site)}`;
    $("#detail-title").textContent = name;
    $("#detail-sub").textContent = sec || "";
    const body = [];
    const imgs = site.images || [];
    body.push(`<div class="gallery">${imgs.length ? imgs.map((img) =>
      `<figure><img loading="lazy" src="${esc(img.url)}" alt="${esc(name)}" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'no-image',textContent:'🏛️'}))"><figcaption>${esc([img.title, img.author, img.license].filter(Boolean).join(" · "))}</figcaption></figure>`
    ).join("") : `<div class="no-image">🏛️</div>`}</div>`);

    const chips = [];
    if (site.dataset === "china_5a") {
      chips.push(`<span class="chip green">${esc(categoryLabel(site))}</span>`);
      chips.push(`<span class="chip">${esc((state.lang === "zh" ? site.address_zh : site.address_en) || site.address_zh || "")}</span>`);
    } else {
      chips.push(`<span class="chip green">${esc(categoryLabel(site))}</span>`);
      if (site.year) chips.push(`<span class="chip">${t().labels.year} ${esc(site.year)}</span>`);
      if (site.criteria) chips.push(`<span class="chip">${t().labels.criteria} ${esc(site.criteria)}</span>`);
      if (site.tier === "full") chips.push(`<span class="chip clay">TOP ${esc(site.popularity_rank || "")}</span>`);
      if (site.danger) chips.push(`<span class="chip clay">${t().labels.danger}</span>`);
      if (site.transnational) chips.push(`<span class="chip">${t().labels.transnational}</span>`);
    }
    body.push(`<div class="chips">${chips.join("")}</div>`);
    body.push(markRowHTML(site));

    const intro = state.lang === "zh" ? site.intro_zh : site.intro_en;
    const introSource = state.lang === "zh" ? site.intro_zh_source : site.intro_en_source;
    body.push(sectionHTML(t().sections.intro,
      `<p class="prose">${esc(intro || "—")}</p>` +
      (introSource === "machine_translation" ? `<p class="note">${t().labels.machine}</p>` : "")));

    if (site.intro_local) {
      const langName = site.local_lang_name || site.local_lang || "";
      body.push(sectionHTML(`${t().sections.local}${langName ? " · " + esc(langName) : ""}`,
        `<blockquote class="local-block"><div class="local-label">${esc(langName)}</div>` +
        `<p class="prose">${esc(site.name_local || "")}</p>` +
        `<p class="prose secondary">${esc(site.intro_local)}</p>` +
        (site.intro_local_source === "machine_translation" ? `<p class="note">${t().labels.machine}</p>` : "") +
        `</blockquote>`));
    }

    const tr = site.transport || {};
    const airports = tr.airports || [];
    const hs = tr.high_speed_stations || [];
    const rails = tr.railway_stations || [];
    const ferries = tr.ferry_terminals || [];
    const transportBlocks = [];
    if (airports.length) transportBlocks.push(`<div class="panel"><h4>${t().labels.airport}</h4>${listHTML(airports, (a) =>
      `<li><div class="name">${esc(a.name)} <small>${esc(a.iata || "")} ${esc(a.city || "")}</small></div><div class="dist">${fmtKm(a.distance_km)}</div></li>`)}</div>`);
    if (hs.length) transportBlocks.push(`<div class="panel"><h4>${t().labels.hsr}</h4>${listHTML(hs, (a) =>
      `<li><div class="name">${esc(a.name)} <small>${esc(a.name_en || "")}</small></div><div class="dist">${fmtKm(a.distance_km)}</div></li>`)}</div>`);
    if (rails.length) transportBlocks.push(`<div class="panel"><h4>${t().labels.rail}</h4>${listHTML(rails, (a) =>
      `<li><div class="name">${esc(a.name)} <small>${esc(a.name_en || "")}</small></div><div class="dist">${fmtKm(a.distance_km)}</div></li>`)}</div>`);
    if (ferries.length) transportBlocks.push(`<div class="panel"><h4>${t().labels.ferry}</h4>${listHTML(ferries, (a) =>
      `<li><div class="name">${esc(a.name)} <small>${esc(a.name_en || "")}</small></div><div class="dist">${fmtKm(a.distance_km)}</div></li>`)}</div>`);
    if (site.dataset === "china_5a" && tr.nearest_airport_km != null) {
      transportBlocks.push(`<p class="note">${t().labels.nearest}: ${fmtKm(tr.nearest_airport_km)}</p>`);
    }
    if (site.dataset === "china_5a" || site.dataset === "unesco") {
      const extras = [];
      if (site.dataset !== "china_5a" && tr.distance_beijing_km != null) {
        extras.push(`<p class="note">${t().labels.fromBeijing}: ${fmtKm(tr.distance_beijing_km)}</p>`);
      }
      if (site.dataset === "unesco" && tr.nearest_airport_km > 400) {
        extras.push(`<p class="note">${state.lang === "zh" ? "该遗产地偏远，所列机场为最近的可定期通航机场，仅作门户参考。" : "The property is remote; the listed airport is the nearest scheduled gateway and is shown for reference only."}</p>`);
      }
      if (site.dataset !== "china_5a" && site.tier !== "full") {
        extras.push(`<p class="note">${state.lang === "zh" ? "基本资料条目仅提供机场信息；码头/火车站/酒店仅完整资料收录。" : "Basic records include airports only; ferry terminals, railway stations and hotels are in full records."}</p>`);
      }
      body.push(sectionHTML(t().sections.transport,
        (transportBlocks.length ? `<div class="grid-2">${transportBlocks.join("")}</div>` : `<p class="note">${t().labels.noTransport}</p>`) +
        extras.join("")));
    }

    if (site.dataset === "china_5a") {
      const f = site.foreign_visitors || {};
      body.push(sectionHTML(t().sections.foreign,
        `<p class="prose">${esc(state.lang === "zh" ? f.note_zh : f.note_en)}</p>` +
        `<p class="note">${state.lang === "zh" ? (f.status === "likely_open" ? t().labels.foreignOpen : t().labels.foreignUnknown) : (f.status === "likely_open" ? t().labels.foreignOpen : t().labels.foreignUnknown)}</p>`));
    }

    const hotels = site.hotels || [];
    if (site.dataset === "china_5a" || site.tier === "full") {
      body.push(sectionHTML(t().sections.hotels,
        hotels.length ? `${listHTML(hotels, (h) =>
          `<li><div class="name">${esc(h.name)} <small>${esc([h.name_en, h.stars ? h.stars + "★" : "", h.brand].filter(Boolean).join(" · "))}</small></div><div class="dist">${fmtKm(h.distance_km)} · ${esc(t().labels[h.kind] || h.kind)}</div></li>`)}` +
          `<p class="note">${state.lang === "zh" ? "来自 OpenStreetMap；星级/连锁信息可能不完整。" : "From OpenStreetMap; star/chain data may be incomplete."}</p>`
        : `<p class="note">${t().labels.noHotels}</p>`));
    } else {
      body.push(sectionHTML(t().sections.hotels, `<p class="note">${t().labels.basicNote}</p>`));
    }

    if (site.dataset !== "china_5a") {
      const visa = site.visa || {};
      let visaHTML = `<p class="prose"><strong>${esc(visaLabel(site.visa_summary))}</strong>` +
        (visa.days ? ` · ${esc(visa.days)} ${state.lang === "zh" ? "天" : "days"}` : "") + `</p>` +
        `<p class="note">${esc(state.lang === "zh" ? visa.notes : visa.requirement || visa.notes || "")}</p>`;
      if ((site.visa_by_country || []).length > 1) {
        visaHTML += listHTML(site.visa_by_country, (v) =>
          `<li><div class="name">${esc(state.lang === "zh" ? v.country_zh : v.country_en)}</div><div class="dist">${esc(visaLabel(v.status))}</div></li>`);
      }
      body.push(sectionHTML(t().sections.visa, visaHTML + `<p class="note">${t().labels.visaNote}</p>`));
    }

    const il = site.info_languages || {};
    const langNames = {
      zh: "中文", en: "English", ja: "日本語", ko: "한국어",
      local: il.local_lang_name || il.local_lang || (state.lang === "zh" ? "本地语言" : "Local"),
    };
    const langKeys = site.dataset === "china_5a" ? ["zh", "en", "ja", "ko"] : ["zh", "en", "ja", "ko", "local"];
    const langBadges = langKeys.map((k) =>
      `<span class="lang-badge ${il[k] ? "on" : "off"}">${esc(langNames[k])}</span>`).join("");
    const editions = (il.official_unesco || []).join(" · ");
    body.push(sectionHTML(t().sections.langs,
      `<div class="lang-badges">${langBadges}</div>` +
      (editions ? `<p class="note">UNESCO: ${esc(editions)}</p>` : "") +
      (il.wikipedia_editions ? `<p class="note">Wikipedia: ${esc(il.wikipedia_editions)} ${state.lang === "zh" ? "个语言版本" : "language editions"}</p>` : "")));

    const sources = site.sources || [];
    const links = [];
    if (site.web) links.push(`<a href="${esc(site.web)}" target="_blank" rel="noopener">${t().labels.official}</a>`);
    if (site.booking) links.push(`<a href="${esc(site.booking)}" target="_blank" rel="noopener">${t().labels.booking}</a>`);
    if (site.unesco_url) links.push(`<a href="${esc(site.unesco_url)}" target="_blank" rel="noopener">${t().labels.unesco}</a>`);
    if (site.lat != null && site.lon != null) {
      links.push(`<a href="https://www.openstreetmap.org/?mlat=${site.lat}&mlon=${site.lon}#map=13/${site.lat}/${site.lon}" target="_blank" rel="noopener">${t().labels.map}</a>`);
    }
    for (const s of sources) {
      if (s.url && !links.some((l) => l.includes(s.url))) {
        links.push(`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a>`);
      }
    }
    body.push(sectionHTML(t().sections.sources, `<div class="sources">${links.join("")}</div>` +
      (imgs.length ? `<p class="credit">${imgs.map((im) => `${t().labels.imageCredit}: ${esc(im.author || "—")} · ${esc(im.license || "—")} · ${esc(im.title || "")}`).join("<br>")}</p>` : "")));

    $("#detail-body").innerHTML = body.join("");
  }

  // ---------------------------------------------------------------------
  // Personal marks (visited / liked / not for me)
  // ---------------------------------------------------------------------
  function findSite(id) {
    for (const tab of ["china", "world"]) {
      const site = state.data[tab]?.sites.find((s) => s.id === id);
      if (site) return site;
    }
    return null;
  }

  function toggleMark(id, kind) {
    const site = findSite(id);
    if (!site) return;
    const m = { ...(state.marks[id] || {}) };
    if (kind === "v") m.v = m.v ? 0 : 1;
    else m.r = m.r === kind ? null : kind;
    if (m.v || m.r) {
      m.c = site.country || "";
      // Only Chinese records light up a province; overseas ones light the country.
      m.p = site.dataset === "china_5a" ? (site.province_iso || "") : "";
      m.n = localizedName(site);
      state.marks[id] = m;
    } else {
      delete state.marks[id];
    }
    saveMarks();
    refreshMarkUI(id);
    updateGlobeButton();
    if (globe.open) { globe.dirty = true; updateGlobeStats(); }
    if (state.visitedOnly) render();
  }

  function refreshMarkUI(id) {
    const m = state.marks[id] || {};
    document.querySelectorAll(`.mark-btn[data-id="${id}"]`).forEach((btn) => {
      const kind = btn.dataset.mark;
      const on = kind === "v" ? !!m.v : m.r === kind;
      btn.classList.toggle("on", on);
      btn.classList.toggle("like", kind === "like" && m.r === "like");
      btn.classList.toggle("bad", kind === "bad" && m.r === "bad");
      btn.setAttribute("aria-pressed", String(on));
    });
    const badges = document.querySelector(`.card[data-id="${id}"] .card-badges`);
    if (badges) {
      const existing = badges.querySelector(".badge.visited");
      if (m.v && !existing) {
        badges.insertAdjacentHTML("afterbegin",
          `<span class="badge visited">✓ ${esc(t().markVisited)}</span>`);
      } else if (!m.v && existing) {
        existing.remove();
      }
    }
  }

  // ---------------------------------------------------------------------
  // Globe: visited provinces (China) and countries (overseas) lit up
  // ---------------------------------------------------------------------
  const globe = {
    open: false, loaded: false, loading: false,
    world: null, provinces: null,
    rotation: [-104, -22], zoom: 1,
    spinning: true, dragging: false, moved: false, dirty: true,
    hover: null, raf: null, pointer: { x: 0, y: 0 },
    anim: null,
  };

  function visitedSets() {
    const countries = new Set();
    const provinces = new Set();
    let sites = 0;
    for (const m of Object.values(state.marks)) {
      if (!m.v) continue;
      sites += 1;
      if (m.p) provinces.add(m.p);
      if (m.c && m.c !== "CN") countries.add(m.c);
    }
    return { countries, provinces, sites };
  }

  async function ensureGeo() {
    if (globe.loaded || globe.loading) return;
    globe.loading = true;
    try {
      const [world, provinces] = await Promise.all([
        fetch("./assets/geo/world-110m.json").then((r) => r.json()),
        fetch("./assets/geo/china-provinces.json").then((r) => r.json()),
      ]);
      globe.world = world.features;
      globe.provinces = provinces.features;
      globe.loaded = true;
      globe.dirty = true;
    } catch (err) {
      $("#globe-canvas").replaceWith(Object.assign(document.createElement("p"), {
        className: "note", textContent: `Failed to load globe data: ${err.message}`,
      }));
    } finally {
      globe.loading = false;
    }
  }

  function globeSize() {
    const canvas = $("#globe-canvas");
    const rect = canvas.getBoundingClientRect();
    return { canvas, w: Math.max(rect.width, 240), h: Math.max(rect.height, 240) };
  }

  function projectionFor(w, h) {
    const radius = Math.min(w, h) / 2 - 10;
    return d3.geoOrthographic()
      .translate([w / 2, h / 2])
      .scale(radius * globe.zoom)
      .rotate([globe.rotation[0], globe.rotation[1], 0])
      .clipAngle(90);
  }

  function featureAt(px, py) {
    const { w, h } = globeSize();
    const projection = projectionFor(w, h);
    const lonlat = projection.invert([px, py]);
    if (!lonlat || !isFinite(lonlat[0]) || !isFinite(lonlat[1])) return null;
    for (const f of globe.provinces || []) {
      if (d3.geoContains(f, lonlat)) return { kind: "province", feature: f };
    }
    for (const f of globe.world || []) {
      if (d3.geoContains(f, lonlat)) return { kind: "country", feature: f };
    }
    return null;
  }

  function drawGlobe() {
    if (!globe.loaded) return;
    const { canvas, w, h } = globeSize();
    const dpr = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    const projection = projectionFor(w, h);
    const path = d3.geoPath(projection, ctx);
    const { countries, provinces } = visitedSets();

    // Ocean sphere with a soft directional light.
    const r = projection.scale();
    const cx = w / 2, cy = h / 2;
    const grad = ctx.createRadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.1, cx, cy, r);
    grad.addColorStop(0, "#20404c");
    grad.addColorStop(0.65, "#122a35");
    grad.addColorStop(1, "#0a1a22");
    ctx.beginPath();
    path({ type: "Sphere" });
    ctx.fillStyle = grad;
    ctx.fill();

    // Graticule
    ctx.beginPath();
    path(d3.geoGraticule10());
    ctx.strokeStyle = "rgba(150, 200, 210, .10)";
    ctx.lineWidth = 0.6;
    ctx.stroke();

    // Base countries
    for (const f of globe.world) {
      ctx.beginPath();
      path(f);
      ctx.fillStyle = "#243743";
      ctx.fill();
      ctx.strokeStyle = "rgba(160, 200, 210, .18)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Chinese provinces (drawn over China's country fill)
    for (const f of globe.provinces) {
      ctx.beginPath();
      path(f);
      const lit = provinces.has(f.properties.iso);
      if (lit) {
        ctx.save();
        ctx.shadowColor = "rgba(224, 161, 60, .85)";
        ctx.shadowBlur = 12;
        ctx.fillStyle = "#e0a13c";
        ctx.fill();
        ctx.restore();
      } else {
        ctx.fillStyle = "#2b414d";
        ctx.fill();
      }
      ctx.strokeStyle = lit ? "rgba(255, 214, 140, .85)" : "rgba(170, 210, 220, .22)";
      ctx.lineWidth = 0.6;
      ctx.stroke();
    }

    // Lit overseas countries
    for (const f of globe.world) {
      if (!countries.has(f.properties.iso2)) continue;
      if (f.properties.iso2 === "CN") continue; // provinces already cover it
      ctx.beginPath();
      path(f);
      ctx.save();
      ctx.shadowColor = "rgba(224, 161, 60, .85)";
      ctx.shadowBlur = 14;
      ctx.fillStyle = "#e0a13c";
      ctx.fill();
      ctx.restore();
      ctx.strokeStyle = "rgba(255, 219, 150, .9)";
      ctx.lineWidth = 0.8;
      ctx.stroke();
    }

    // Hover highlight
    if (globe.hover) {
      ctx.beginPath();
      path(globe.hover.feature);
      ctx.strokeStyle = "rgba(255, 250, 235, .95)";
      ctx.lineWidth = 1.6;
      ctx.stroke();
    }

    // Sphere rim
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(196, 154, 74, .5)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Compass hint: mark Beijing so the viewer can orient themselves.
    const beijing = projection([116.4, 39.9]);
    if (beijing && projection.invert(beijing)) {
      ctx.beginPath();
      ctx.arc(beijing[0], beijing[1], 2.6, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(240, 226, 200, .9)";
      ctx.fill();
    }
  }

  function updateGlobeStats() {
    const { countries, provinces, sites } = visitedSets();
    const items = [
      [sites, t().globeSites],
      [countries.size, t().globeCountries],
      [provinces.size, t().globeProvinces],
    ];
    $("#globe-stats").innerHTML = items.map(([n, label]) =>
      `<div class="globe-stat"><b>${n}</b><span>${esc(label)}</span></div>`).join("");
    $("#globe-empty").hidden = sites > 0;
    $("#globe-empty").textContent = t().globeEmpty;
  }

  function tick() {
    if (!globe.open) return;
    if (globe.spinning && !globe.dragging && !globe.anim) {
      globe.rotation[0] += 0.16;
      globe.dirty = true;
    }
    if (globe.dirty) {
      drawGlobe();
      globe.dirty = false;
    }
    globe.raf = requestAnimationFrame(tick);
  }

  function animateTo(rotation, zoom) {
    const start = { r: [...globe.rotation], z: globe.zoom, t: performance.now() };
    const target = { r: rotation, z: zoom };
    const duration = 700;
    const ease = (x) => 1 - Math.pow(1 - x, 3);
    const step = (now) => {
      const p = Math.min(1, (now - start.t) / duration);
      const k = ease(p);
      globe.rotation = [
        start.r[0] + (target.r[0] - start.r[0]) * k,
        start.r[1] + (target.r[1] - start.r[1]) * k,
      ];
      globe.zoom = start.z + (target.z - start.z) * k;
      globe.dirty = true;
      if (p < 1) globe.anim = requestAnimationFrame(step);
      else globe.anim = null;
    };
    if (globe.anim) cancelAnimationFrame(globe.anim);
    globe.anim = requestAnimationFrame(step);
  }

  function updateGlobeLabels() {
    $("#globe-kicker").textContent = t().globeKicker;
    $("#globe-title").textContent = t().globeTitle;
    $("#globe-hint").textContent = t().globeHint;
    $("#globe-close").setAttribute("aria-label", t().reset);
    $("#globe-china").textContent = t().focusChina;
    $("#globe-spin").textContent = globe.spinning ? t().spinOn : t().spinOff;
    $("#globe-legend").innerHTML =
      `<span><i class="dot lit"></i>${esc(t().legendVisited)}</span>` +
      `<span><i class="dot idle"></i>${esc(t().legendIdle)}</span>`;
  }

  function openGlobe() {
    const d = $("#globe");
    globe.open = true;
    if (!d.open) d.showModal();
    updateGlobeLabels();
    updateGlobeStats();
    ensureGeo().then(() => { globe.dirty = true; drawGlobe(); });
    if (!globe.raf) globe.raf = requestAnimationFrame(tick);
  }

  function closeGlobe() {
    globe.open = false;
    if (globe.raf) cancelAnimationFrame(globe.raf);
    globe.raf = null;
    const d = $("#globe");
    if (d.open) d.close();
  }

  function applyLocation(tab, country, subdivision) {
    closeGlobe();
    state.pending = { country, subdivision: subdivision || "" };
    if (state.tab !== tab) {
      loadTab(tab);
    } else {
      state.pending = null;
      state.country = country;
      state.subdivision = subdivision || "";
      buildFilters();
      render();
    }
  }

  function globeSelect(hit) {
    if (!hit) return;
    if (hit.kind === "province") {
      applyLocation("china", "CN", hit.feature.properties.iso);
    } else {
      const iso2 = hit.feature.properties.iso2;
      if (iso2 === "CN") applyLocation("china", "CN", "");
      else applyLocation("world", iso2, "");
    }
  }

  // Globe interaction
  $("#globe-open").addEventListener("click", openGlobe);
  $("#globe-close").addEventListener("click", closeGlobe);
  $("#globe").addEventListener("click", (e) => { if (e.target === $("#globe")) closeGlobe(); });
  $("#globe-china").addEventListener("click", () => animateTo([-104, -30], 2.1));
  $("#globe-spin").addEventListener("click", () => {
    globe.spinning = !globe.spinning;
    $("#globe-spin").textContent = globe.spinning ? t().spinOn : t().spinOff;
  });

  (() => {
    const canvas = $("#globe-canvas");
    const tip = $("#globe-tip");
    // offsetX is unreliable for synthetic events, so derive it from the rect.
    const localPoint = (e) => {
      const rect = canvas.getBoundingClientRect();
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    let down = null;
    canvas.addEventListener("pointerdown", (e) => {
      canvas.setPointerCapture(e.pointerId);
      globe.dragging = true;
      globe.moved = false;
      down = { x: e.clientX, y: e.clientY };
      globe.pointer = localPoint(e);
    });
    canvas.addEventListener("pointermove", (e) => {
      globe.pointer = localPoint(e);
      if (globe.dragging && down) {
        const dx = e.clientX - down.x;
        const dy = e.clientY - down.y;
        if (Math.abs(dx) + Math.abs(dy) > 3) globe.moved = true;
        globe.rotation[0] += dx * 0.3;
        globe.rotation[1] = Math.max(-85, Math.min(85, globe.rotation[1] - dy * 0.3));
        down = { x: e.clientX, y: e.clientY };
        globe.dirty = true;
        tip.hidden = true;
        return;
      }
      if (!globe.loaded) return;
      const hit = featureAt(globe.pointer.x, globe.pointer.y);
      globe.hover = hit;
      globe.dirty = true;
      if (hit) {
        const p = hit.feature.properties;
        const name = hit.kind === "province"
          ? (state.lang === "zh" ? p.name_zh : p.name_en)
          : (state.lang === "zh" ? (p.name_zh || p.name) : p.name);
        tip.textContent = name || p.iso || p.iso2 || "";
        tip.style.left = `${globe.pointer.x + 14}px`;
        tip.style.top = `${globe.pointer.y + 14}px`;
        tip.hidden = false;
      } else {
        tip.hidden = true;
      }
    });
    canvas.addEventListener("pointerup", () => {
      globe.dragging = false;
      if (!globe.moved && globe.loaded) globeSelect(featureAt(globe.pointer.x, globe.pointer.y));
      down = null;
    });
    canvas.addEventListener("pointerleave", () => {
      globe.dragging = false;
      globe.hover = null;
      tip.hidden = true;
      globe.dirty = true;
    });
    canvas.addEventListener("wheel", (e) => {
      e.preventDefault();
      const factor = Math.exp(-e.deltaY * 0.0012);
      globe.zoom = Math.max(0.75, Math.min(3.2, globe.zoom * factor));
      globe.dirty = true;
    }, { passive: false });
    window.addEventListener("resize", () => { globe.dirty = true; });
  })();

  // Events
  document.querySelectorAll(".tab").forEach((el) => el.addEventListener("click", () => loadTab(el.dataset.tab)));
  $("#lang-toggle").addEventListener("click", () => setLang(state.lang === "zh" ? "en" : "zh"));
  $("#search").addEventListener("input", (e) => { state.query = e.target.value; state.limit = 60; render(); });
  $("#country-filter").addEventListener("change", (e) => {
    state.country = e.target.value;
    state.subdivision = "";
    state.limit = 60;
    if (state.tab === "world") buildSubdivisionOptions();
    render();
  });
  $("#subdivision-filter").addEventListener("change", (e) => {
    state.subdivision = e.target.value;
    state.limit = 60;
    render();
  });
  $("#visited-filter").addEventListener("click", () => {
    state.visitedOnly = !state.visitedOnly;
    state.limit = 60;
    syncVisitedToggle();
    render();
  });
  $("#category-filter").addEventListener("change", (e) => { state.category = e.target.value; state.limit = 60; render(); });
  $("#visa-filter").addEventListener("change", (e) => { state.visa = e.target.value; state.limit = 60; render(); });
  $("#tier-filter").addEventListener("change", (e) => { state.tier = e.target.value; state.limit = 60; render(); });
  $("#reset").addEventListener("click", () => {
    state.query = state.subdivision = state.category = state.visa = state.tier = "";
    state.country = state.tab === "china" ? "CN" : "";
    state.visitedOnly = false;
    state.limit = 60;
    $("#search").value = "";
    $("#country-filter").value = state.country;
    $("#subdivision-filter").value = "";
    $("#category-filter").value = "";
    $("#visa-filter").value = "";
    $("#tier-filter").value = "";
    syncVisitedToggle();
    render();
  });
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".mark-btn");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    toggleMark(btn.dataset.id, btn.dataset.mark);
  });
  $("#load-more").addEventListener("click", () => { state.limit += 60; render(); });
  $("#detail-close").addEventListener("click", () => $("#detail").close());
  $("#detail").addEventListener("click", (e) => { if (e.target === $("#detail")) $("#detail").close(); });

  // Deep link: ?site=<id>&tab=world
  const params = new URLSearchParams(location.search);
  const initialTab = params.get("tab") === "world" ? "world" : "china";
  setLang(state.lang);
  loadTab(initialTab);
  const deepSite = params.get("site");
  if (deepSite) {
    const check = setInterval(() => {
      const data = state.data[state.tab];
      if (data) {
        clearInterval(check);
        if (data.sites.some((s) => s.id === deepSite)) openDetail(deepSite);
      }
    }, 200);
    setTimeout(() => clearInterval(check), 5000);
  }
})();
