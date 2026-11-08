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
    category: "",
    visa: "",
    tier: "",
    limit: 60,
    data: { china: null, world: null },
    loading: {},
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
    const category = $("#category-filter");
    const visa = $("#visa-filter");
    const tier = $("#tier-filter");
    const data = state.data[state.tab];
    if (data) {
      if (state.tab === "china") {
        const provinces = [...new Map(data.sites.map((s) => [s.province_zh, {
          value: s.province_zh, zh: s.province_zh, en: s.province_en,
        }])).values()].sort((a, b) => a.zh.localeCompare(b.zh, "zh"));
        country.innerHTML = `<option value="">${esc(t().allProvinces)}</option>` +
          provinces.map((p) => `<option value="${esc(p.value)}">${esc(state.lang === "zh" ? p.zh : p.en)}</option>`).join("");
        country.disabled = false;
        visa.disabled = true;
        tier.disabled = true;
      } else {
        const countries = [...new Map(data.sites.map((s) => [s.country, {
          value: s.country, zh: s.country_zh, en: s.country_en,
        }])).values()].sort((a, b) => (a.en || "").localeCompare(b.en || ""));
        country.innerHTML = `<option value="">${esc(t().allCountries)}</option>` +
          countries.map((p) => `<option value="${esc(p.value)}">${esc(state.lang === "zh" ? (p.zh || p.en) : p.en)}</option>`).join("");
        country.disabled = false;
        visa.disabled = false;
        tier.disabled = false;
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
    country.value = state.country;
    category.value = state.category;
    visa.value = state.visa;
    tier.value = state.tier;
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
    const langCount = world
      ? new Set(world.sites.flatMap((s) => s.info_languages?.official_unesco || [])).size
      : 6;
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
    state.country = state.category = state.visa = state.tier = "";
    state.query = $("#search").value = "";
    state.limit = 60;
    $("#country-filter").value = "";
    $("#category-filter").value = "";
    $("#visa-filter").value = "";
    $("#tier-filter").value = "";
    if (state.data[tab]) {
      buildFilters();
      updateFooter();
      render();
      return;
    }
    if (state.loading[tab]) return;
    state.loading[tab] = true;
    $("#cards").innerHTML = `<p class="muted" style="grid-column:1/-1;padding:24px 0">Loading…</p>`;
    fetch(`./data/${tab}.json`)
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
      if (state.country) {
        if (state.tab === "china" && s.province_zh !== state.country) return false;
        if (state.tab === "world" && s.country !== state.country) return false;
      }
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
      el.addEventListener("click", () => openDetail(el.dataset.id));
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
    const site = data?.sites.find((s) => s.id === id);
    if (!site) return;
    const d = $("#detail");
    d.dataset.siteId = id;
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
    if (!keep) d.showModal();
    d.dataset.siteId = id;
  }

  // Events
  document.querySelectorAll(".tab").forEach((el) => el.addEventListener("click", () => loadTab(el.dataset.tab)));
  $("#lang-toggle").addEventListener("click", () => setLang(state.lang === "zh" ? "en" : "zh"));
  $("#search").addEventListener("input", (e) => { state.query = e.target.value; state.limit = 60; render(); });
  $("#country-filter").addEventListener("change", (e) => { state.country = e.target.value; state.limit = 60; render(); });
  $("#category-filter").addEventListener("change", (e) => { state.category = e.target.value; state.limit = 60; render(); });
  $("#visa-filter").addEventListener("change", (e) => { state.visa = e.target.value; state.limit = 60; render(); });
  $("#tier-filter").addEventListener("change", (e) => { state.tier = e.target.value; state.limit = 60; render(); });
  $("#reset").addEventListener("click", () => {
    state.query = state.country = state.category = state.visa = state.tier = "";
    state.limit = 60;
    $("#search").value = "";
    $("#country-filter").value = "";
    $("#category-filter").value = "";
    $("#visa-filter").value = "";
    $("#tier-filter").value = "";
    render();
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
