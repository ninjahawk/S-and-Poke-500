/* The S&Poké 500 — frontend logic (vanilla JS, no dependencies).
   Reads data/latest.json + data/history.json and renders the dashboard, including
   an S&P-style interactive chart with a hover/drag scrubber. */

(() => {
  "use strict";

  const state = {
    latest: null,
    history: [], // [{date, index, ...}]
    range: "all",
    sort: { key: "rank", dir: "asc" },
    search: "",
    filtered: [],
  };

  const $ = (sel) => document.querySelector(sel);

  // ---- formatting helpers ------------------------------------------------ //
  const fmtIndex = (n) =>
    n == null ? "—" : n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const fmtPrice = (n) => {
    if (n == null) return "—";
    const opts = n >= 1000 ? { maximumFractionDigits: 0 } : { minimumFractionDigits: 2, maximumFractionDigits: 2 };
    return "$" + n.toLocaleString("en-US", opts);
  };
  const fmtPct = (n) => (n == null ? "—" : (n >= 0 ? "+" : "") + n.toFixed(2) + "%");
  const fmtDate = (iso) =>
    new Date(iso + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  const dirClass = (n) => (n > 0 ? "up" : n < 0 ? "down" : "flat");

  // ---- data load --------------------------------------------------------- //
  async function load() {
    try {
      const [latest, history] = await Promise.all([
        fetch("data/latest.json", { cache: "no-store" }).then((r) => r.json()),
        fetch("data/history.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : { points: [] })),
      ]);
      state.latest = latest;
      state.history = (history && history.points) || [];
      renderAll();
    } catch (err) {
      console.error(err);
      $("#hero-index").textContent = "—";
      $("#chart-caption").textContent = "Couldn't load market data. It may not have been generated yet.";
      document.getElementById("app").setAttribute("aria-busy", "false");
    }
  }

  function renderAll() {
    const d = state.latest;
    const sample = !!d.sample;
    const banner = $("#sample-banner");
    banner.hidden = !sample;
    if (d.asOfDate) $("#as-of").textContent = "As of " + fmtDate(d.asOfDate) + (sample ? " · sample" : "");

    renderHero(d);
    renderStats(d);
    renderMovers(d);
    setupTable(d);
    setupChart();
    document.getElementById("app").setAttribute("aria-busy", "false");
  }

  // ---- hero -------------------------------------------------------------- //
  function renderHero(d) {
    $("#hero-index").textContent = fmtIndex(d.index);
    const el = $("#hero-change");
    if (d.changePct == null) {
      el.textContent = "Baseline day — change tracked from tomorrow";
      el.className = "hero-change flat";
    } else {
      const cls = dirClass(d.changePct);
      const arrow = cls === "up" ? "▲" : cls === "down" ? "▼" : "•";
      el.className = "hero-change " + cls;
      el.textContent = `${arrow} ${fmtIndex(Math.abs(d.change))} (${fmtPct(d.changePct)}) today`;
    }
  }

  // ---- stats ------------------------------------------------------------- //
  function renderStats(d) {
    $("#stat-total").textContent = fmtPrice(d.totalValue);
    const b = d.breadth || { advancing: 0, declining: 0 };
    $("#stat-breadth").innerHTML =
      `<span class="up-ink">${b.advancing}</span> / <span class="down-ink">${b.declining}</span>`;
    $("#stat-count").textContent = d.constituentCount;
    const net = (b.advancing || 0) - (b.declining || 0);
    const ratio = b.declining ? b.advancing / b.declining : b.advancing;
    let mood = "Balanced";
    if (net > 0 && ratio >= 2) mood = "Bullish";
    else if (net > 0) mood = "Firm";
    else if (net < 0 && ratio <= 0.5) mood = "Bearish";
    else if (net < 0) mood = "Soft";
    const mEl = $("#stat-mood");
    mEl.textContent = mood;
    mEl.className = "stat-value " + (net > 0 ? "up-ink" : net < 0 ? "down-ink" : "");
  }

  // ---- movers ------------------------------------------------------------ //
  function moverItem(c, up) {
    const li = document.createElement("li");
    li.className = "mover-item";
    const thumb = c.image
      ? `<img class="mover-thumb" src="${c.image}" alt="" loading="lazy" />`
      : `<span class="mover-thumb thumb-ph">CARD</span>`;
    li.innerHTML = `
      ${thumb}
      <div class="mover-body">
        <div class="mover-name">${esc(c.name)}</div>
        <div class="mover-set">${esc(c.setName || "")}</div>
      </div>
      <div class="mover-meta">
        <div class="mover-price">${fmtPrice(c.price)}</div>
        <div class="mover-pct ${up ? "up-ink" : "down-ink"}">${fmtPct(c.changePct)}</div>
      </div>`;
    return li;
  }
  function renderMovers(d) {
    const g = $("#gainers"), l = $("#losers");
    g.innerHTML = ""; l.innerHTML = "";
    const gainers = d.gainers || [], losers = d.losers || [];
    if (!gainers.length && !losers.length) {
      const note = "<li class='mover-set'>Day-over-day moves appear after the first update.</li>";
      g.innerHTML = note; l.innerHTML = note; return;
    }
    gainers.forEach((c) => g.appendChild(moverItem(c, true)));
    losers.forEach((c) => l.appendChild(moverItem(c, false)));
  }

  // ---- table ------------------------------------------------------------- //
  function setupTable(d) {
    state.constituents = d.constituents || [];
    $("#search").addEventListener("input", (e) => {
      state.search = e.target.value.trim().toLowerCase();
      renderTable();
    });
    document.querySelectorAll("th.sortable").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.sort;
        if (state.sort.key === key) state.sort.dir = state.sort.dir === "asc" ? "desc" : "asc";
        else state.sort = { key, dir: key === "rank" ? "asc" : "desc" };
        renderTable();
      });
    });
    renderTable();
  }

  function renderTable() {
    const q = state.search;
    let rows = state.constituents.filter(
      (c) => !q || c.name.toLowerCase().includes(q) || (c.setName || "").toLowerCase().includes(q)
    );
    const { key, dir } = state.sort;
    const mul = dir === "asc" ? 1 : -1;
    rows.sort((a, b) => {
      const av = a[key] ?? -Infinity, bv = b[key] ?? -Infinity;
      return av < bv ? -1 * mul : av > bv ? 1 * mul : 0;
    });

    const body = $("#table-body");
    const frag = document.createDocumentFragment();
    for (const c of rows) {
      const tr = document.createElement("tr");
      const thumb = c.image
        ? `<img class="td-thumb" src="${c.image}" alt="" loading="lazy" />`
        : `<span class="td-thumb thumb-ph">—</span>`;
      const changeCell =
        c.changePct == null
          ? `<span class="badge-new">NEW</span>`
          : `<span class="${c.changePct >= 0 ? "up-ink" : "down-ink"}">${fmtPct(c.changePct)}</span>`;
      tr.innerHTML = `
        <td class="td-rank">${c.rank}</td>
        <td><div class="td-card">${thumb}<div><span class="td-name">${esc(c.name)}</span> <span class="td-num">#${esc(c.number || "")}</span></div></div></td>
        <td class="td-set col-set">${esc(c.setName || "")}</td>
        <td class="td-price">${fmtPrice(c.price)}</td>
        <td class="td-change">${changeCell}</td>`;
      frag.appendChild(tr);
    }
    body.innerHTML = "";
    body.appendChild(frag);
    $("#table-count").textContent = `${rows.length} of ${state.constituents.length} cards`;

    document.querySelectorAll("th.sortable").forEach((th) => {
      th.classList.remove("sorted-asc", "sorted-desc");
      if (th.dataset.sort === key) th.classList.add(dir === "asc" ? "sorted-asc" : "sorted-desc");
    });
  }

  // ---- chart ------------------------------------------------------------- //
  const SVGNS = "http://www.w3.org/2000/svg";
  let chart = { geo: null };

  function visiblePoints() {
    const pts = state.history;
    if (state.range === "all") return pts;
    const days = parseInt(state.range, 10);
    if (pts.length <= 2) return pts;
    const cutoff = new Date(pts[pts.length - 1].date + "T00:00:00");
    cutoff.setDate(cutoff.getDate() - days);
    const sliced = pts.filter((p) => new Date(p.date + "T00:00:00") >= cutoff);
    return sliced.length >= 2 ? sliced : pts.slice(-2);
  }

  function setupChart() {
    // Enable/disable range buttons based on available history span.
    const pts = state.history;
    const spanDays = pts.length >= 2
      ? (new Date(pts[pts.length - 1].date) - new Date(pts[0].date)) / 86400000
      : 0;
    document.querySelectorAll(".range-btn").forEach((btn) => {
      const r = btn.dataset.range;
      btn.disabled = r !== "all" && (pts.length < 2 || spanDays < parseInt(r, 10) * 0.5);
      btn.classList.toggle("is-active", r === state.range);
      btn.onclick = () => {
        if (btn.disabled) return;
        state.range = r;
        document.querySelectorAll(".range-btn").forEach((b) => b.classList.toggle("is-active", b === btn));
        drawChart();
      };
    });

    const fig = $("#chart");
    fig.addEventListener("pointermove", onScrub);
    fig.addEventListener("pointerdown", onScrub);
    fig.addEventListener("pointerleave", hideScrub);
    if (!chart.ro) {
      chart.ro = new ResizeObserver(() => drawChart());
      chart.ro.observe($("#chart"));
    }
    drawChart();
  }

  function drawChart() {
    const svg = $("#chart-svg");
    const pts = visiblePoints();
    const empty = $("#chart-empty");
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    hideScrub();

    if (!pts || pts.length < 2) {
      empty.hidden = false;
      $("#chart-caption").textContent = "";
      chart.geo = null;
      return;
    }
    empty.hidden = true;

    const W = svg.clientWidth || 1000;
    const H = svg.clientHeight || 340;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    const padL = 52, padR = 14, padT = 14, padB = 26;
    const plotW = W - padL - padR, plotH = H - padT - padB;

    const values = pts.map((p) => p.index);
    let min = Math.min(...values), max = Math.max(...values);
    const pad = (max - min) * 0.12 || max * 0.02 || 1;
    min -= pad; max += pad;

    const x = (i) => padL + (pts.length === 1 ? plotW / 2 : (i / (pts.length - 1)) * plotW);
    const y = (v) => padT + plotH - ((v - min) / (max - min)) * plotH;
    chart.geo = { pts, x, y, padL, padR, padT, padB, plotW, plotH, W, H };

    const up = values[values.length - 1] >= values[0];
    const color = up ? getCss("--up") : getCss("--down");
    const gid = "spk-grad";

    // gradient
    const defs = mk("defs");
    const grad = mk("linearGradient", { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 });
    grad.appendChild(mk("stop", { offset: "0%", "stop-color": color, "stop-opacity": "0.28" }));
    grad.appendChild(mk("stop", { offset: "100%", "stop-color": color, "stop-opacity": "0" }));
    defs.appendChild(grad);
    svg.appendChild(defs);

    // horizontal gridlines + y labels
    const ticks = 4;
    for (let t = 0; t <= ticks; t++) {
      const v = min + ((max - min) * t) / ticks;
      const yy = y(v);
      svg.appendChild(mk("line", { x1: padL, x2: W - padR, y1: yy, y2: yy,
        stroke: getCss("--grid"), "stroke-width": 1 }));
      const lbl = mk("text", { x: padL - 8, y: yy + 4, "text-anchor": "end",
        fill: getCss("--muted"), "font-size": 11, "font-family": "system-ui, sans-serif" });
      lbl.textContent = Math.round(v).toLocaleString("en-US");
      svg.appendChild(lbl);
    }

    // x labels (start, mid, end)
    [0, Math.floor((pts.length - 1) / 2), pts.length - 1].forEach((i, k) => {
      const t = mk("text", { x: x(i), y: H - 8,
        "text-anchor": k === 0 ? "start" : k === 2 ? "end" : "middle",
        fill: getCss("--muted"), "font-size": 11, "font-family": "system-ui, sans-serif" });
      t.textContent = shortDate(pts[i].date);
      svg.appendChild(t);
    });

    // area + line
    let line = "", area = "";
    pts.forEach((p, i) => {
      const px = x(i), py = y(p.index);
      line += (i ? "L" : "M") + px.toFixed(1) + "," + py.toFixed(1) + " ";
    });
    area = line + `L${x(pts.length - 1).toFixed(1)},${(padT + plotH).toFixed(1)} L${x(0).toFixed(1)},${(padT + plotH).toFixed(1)} Z`;
    svg.appendChild(mk("path", { d: area, fill: `url(#${gid})` }));
    svg.appendChild(mk("path", { d: line, fill: "none", stroke: color,
      "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));

    // scrubber elements (hidden until hover)
    chart.crossLine = mk("line", { class: "cross", stroke: getCss("--axis"),
      "stroke-width": 1, "stroke-dasharray": "3 3", y1: padT, y2: padT + plotH, opacity: 0 });
    chart.dot = mk("circle", { r: 4.5, fill: color, stroke: getCss("--surface"),
      "stroke-width": 2, opacity: 0 });
    svg.appendChild(chart.crossLine);
    svg.appendChild(chart.dot);
    chart.color = color;

    const first = pts[0].index, last = pts[pts.length - 1].index;
    const chg = ((last / first - 1) * 100);
    const label = { 7: "past week", 30: "past month", 90: "past 3 months", 365: "past year" }[state.range] || "since launch";
    $("#chart-caption").innerHTML =
      `<span class="${chg >= 0 ? "up-ink" : "down-ink"}">${fmtPct(chg)}</span> ${label} · ${pts.length} day${pts.length === 1 ? "" : "s"} of history` +
      (state.latest.sample ? " · sample data" : "");
  }

  function onScrub(e) {
    const geo = chart.geo;
    if (!geo) return;
    const svg = $("#chart-svg");
    const rect = svg.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * geo.W;
    // nearest data index
    let i = Math.round(((relX - geo.padL) / geo.plotW) * (geo.pts.length - 1));
    i = Math.max(0, Math.min(geo.pts.length - 1, i));
    const p = geo.pts[i];
    const px = geo.x(i), py = geo.y(p.index);
    chart.crossLine.setAttribute("x1", px);
    chart.crossLine.setAttribute("x2", px);
    chart.crossLine.setAttribute("opacity", 1);
    chart.dot.setAttribute("cx", px);
    chart.dot.setAttribute("cy", py);
    chart.dot.setAttribute("opacity", 1);

    const tip = $("#chart-tooltip");
    const chg = ((p.index / geo.pts[0].index - 1) * 100);
    tip.innerHTML =
      `<div class="tt-value">${fmtIndex(p.index)}</div>` +
      `<div class="tt-date">${fmtDate(p.date)}</div>` +
      `<div class="tt-delta ${chg >= 0 ? "up-ink" : "down-ink"}">${fmtPct(chg)} <span style="color:var(--muted)">vs. start</span></div>`;
    tip.hidden = false;
    const figRect = $("#chart").getBoundingClientRect();
    const tipX = (px / geo.W) * rect.width; // px within svg
    let left = tipX;
    const half = tip.offsetWidth / 2;
    left = Math.max(half + 2, Math.min(rect.width - half - 2, left));
    tip.style.left = left + "px";
    tip.style.top = Math.max(0, (py / geo.H) * rect.height - 12) + "px";
  }
  function hideScrub() {
    if (chart.crossLine) chart.crossLine.setAttribute("opacity", 0);
    if (chart.dot) chart.dot.setAttribute("opacity", 0);
    const tip = $("#chart-tooltip");
    if (tip) tip.hidden = true;
  }

  // ---- small utils ------------------------------------------------------- //
  function mk(tag, attrs) {
    const el = document.createElementNS(SVGNS, tag);
    if (attrs) for (const k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function getCss(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }
  function shortDate(iso) {
    return new Date(iso + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---- theme toggle ------------------------------------------------------ //
  function initTheme() {
    const saved = localStorage.getItem("spk-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
    $("#theme-toggle").addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const isDark = cur ? cur === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = isDark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("spk-theme", next);
      if (state.latest) drawChart(); // recolor for new theme
    });
  }

  initTheme();
  load();
})();
