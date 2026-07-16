/* S&Poké 500 — frontend logic (vanilla JS, no dependencies).
   Reads data/latest.json + data/history.json and renders a Google Finance–style
   quote page: hero number, gradient area chart with a dotted previous-close
   reference line and hover/drag scrubber, overview stats, movers, and the
   searchable table of all 500 cards. */

(() => {
  "use strict";

  const state = {
    latest: null,
    history: [], // [{date, index, ...}]
    range: "max", // non-numeric ⇒ visiblePoints shows the full series, however long it grows
    maxRange: "max",
    sort: { key: "rank", dir: "asc" },
    search: "",
    constituents: [],
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
    $("#sample-banner").hidden = !d.sample;
    renderHero(d);
    renderOverview(d);
    renderMovers(d);
    setupTable(d);
    setupChart();
    setupCardModal();
    document.getElementById("app").setAttribute("aria-busy", "false");
  }

  // ---- quote header ------------------------------------------------------ //
  function renderHero(d) {
    $("#hero-index").textContent = fmtIndex(d.index);
    const el = $("#hero-change");
    if (d.changePct == null) {
      el.className = "quote-change flat";
      el.textContent = "Baseline day — change tracked from tomorrow";
    } else {
      const up = d.changePct >= 0;
      el.className = "quote-change " + (up ? "up" : "down");
      el.innerHTML =
        `<span class="chg-ic" aria-hidden="true">${up ? "▲" : "▼"}</span>` +
        `<span class="chg-pct">${fmtPct(d.changePct)}</span>` +
        `<span class="chg-abs">(${(d.change >= 0 ? "+" : "") + fmtIndex(d.change)}) Today</span>`;
    }
    if (d.generated) {
      const t = new Date(d.generated);
      $("#as-of").innerHTML = esc(
        t.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) +
        ", " + t.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: "UTC" }) +
        " UTC" + (d.sample ? " · sample data" : "")
      ) + ' · <a class="asof-link" href="#methodology">How prices work</a>';
    }
  }

  // ---- overview ----------------------------------------------------------- //
  function renderOverview(d) {
    $("#ov-prev").textContent = fmtIndex(d.prevIndex);
    $("#ov-total").textContent = fmtPrice(d.totalValue);
    const pts = state.history;
    if (pts.length) {
      const values = pts.map((p) => p.index);
      $("#ov-high").textContent = fmtIndex(Math.max(...values));
      $("#ov-low").textContent = fmtIndex(Math.min(...values));
    }
    const b = d.breadth || { advancing: 0, declining: 0 };
    $("#ov-breadth").innerHTML =
      `<span class="up-ink">${b.advancing}</span> <span style="color:var(--muted)">/</span> <span class="down-ink">${b.declining}</span>`;
  }

  // ---- movers ------------------------------------------------------------ //
  function moverItem(c, up) {
    const li = document.createElement("li");
    li.className = "mover-item";
    li.dataset.id = c.id;
    const thumb = c.image && !imagesOff()
      ? `<img class="mover-thumb" src="${c.image}" alt="" loading="lazy" />`
      : `<span class="mover-thumb thumb-ph">CARD</span>`;
    li.innerHTML = `
      ${thumb}
      <div class="mover-body">
        <div class="mover-name">${esc(c.name)}</div>
        <div class="mover-set">${esc(c.setName || "")}</div>
      </div>
      <div class="mover-meta">
        <span class="mover-price">${fmtPrice(c.price)}</span>
        <span class="delta ${up ? "up" : "down"}"><span class="tri" aria-hidden="true">${up ? "▲" : "▼"}</span>${Math.abs(c.changePct).toFixed(2)}%</span>
      </div>`;
    return li;
  }
  function renderMovers(d) {
    const g = $("#gainers"), l = $("#losers");
    const cols = $("#mover-cols"), empty = $("#movers-empty"), note = $("#movers-note");
    g.innerHTML = ""; l.innerHTML = "";
    const gainers = d.gainers || [], losers = d.losers || [];
    if (!gainers.length && !losers.length) {
      // Collapse the whole section to one line. Distinguish "today's price
      // snapshot hasn't landed yet" (sourceStamp is from a previous day)
      // from a genuinely flat day.
      const stampDay = (d.sourceStamp || "").slice(0, 10);
      const waiting = d.asOfDate && stampDay && stampDay < d.asOfDate;
      empty.textContent = d.prevIndex == null
        ? "Day-over-day moves appear after the first update."
        : waiting
          ? "No movers yet — today's TCGplayer price snapshot lands around 4pm ET."
          : "No confirmed movers today — no card with confirmed prices on both days changed price.";
      cols.hidden = true; note.hidden = true; empty.hidden = false;
      return;
    }
    cols.hidden = false; note.hidden = false; empty.hidden = true;
    gainers.slice(0, 6).forEach((c) => g.appendChild(moverItem(c, true)));
    losers.slice(0, 6).forEach((c) => l.appendChild(moverItem(c, false)));
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
    const asOf = (state.latest && state.latest.asOfDate) || null;
    let anyStale = false;
    for (const c of rows) {
      const tr = document.createElement("tr");
      tr.dataset.id = c.id;
      const thumb = c.image && !imagesOff()
        ? `<img class="td-thumb" src="${c.image}" alt="" loading="lazy" />`
        : `<span class="td-thumb thumb-ph">—</span>`;
      const changeCell =
        c.changePct == null
          ? (c.isNew
              ? `<span class="badge-new">New</span>`
              : `<span class="delta flat" title="No confirmed day-over-day price for this card — see How these prices work">—</span>`)
          : `<span class="delta ${c.changePct >= 0 ? "up" : "down"}"><span class="tri" aria-hidden="true">${c.changePct >= 0 ? "▲" : "▼"}</span>${Math.abs(c.changePct).toFixed(2)}%</span>`;
      const stale = isStale(c, asOf);
      if (stale) anyStale = true;
      const staleMark = stale
        ? `<sup class="stale-mark" title="No recent TCGplayer sales data — price carried forward from ${fmtDate(c.pricedAsOf)}">†</sup>`
        : "";
      tr.innerHTML = `
        <td class="td-rank">${c.rank}</td>
        <td><div class="td-card">${thumb}<div><span class="td-name">${esc(c.name)}</span> <span class="td-num">#${esc(c.number || "")}</span></div></div></td>
        <td class="td-set col-set">${esc(c.setName || "")}</td>
        <td class="td-price">${fmtPrice(c.price)}${staleMark}</td>
        <td class="td-change">${changeCell}</td>`;
      frag.appendChild(tr);
    }
    body.innerHTML = "";
    body.appendChild(frag);
    $("#table-count").textContent = `${rows.length} of ${state.constituents.length} cards`;
    const staleNote = $("#stale-note");
    if (staleNote) staleNote.hidden = !anyStale;

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
    const days = parseInt(state.range, 10);
    if (!days || pts.length <= 2) return pts;
    const cutoff = new Date(pts[pts.length - 1].date + "T00:00:00");
    cutoff.setDate(cutoff.getDate() - days);
    const sliced = pts.filter((p) => new Date(p.date + "T00:00:00") >= cutoff);
    return sliced.length >= 2 ? sliced : pts.slice(-2);
  }

  function setupChart() {
    const pts = state.history;
    const spanDays = pts.length >= 2
      ? (new Date(pts[pts.length - 1].date) - new Date(pts[0].date)) / 86400000
      : 0;
    document.querySelectorAll(".range-btn").forEach((btn) => {
      const r = btn.dataset.range;
      // The MAX button always shows everything; narrower ones switch off
      // until enough history exists to fill roughly half their window.
      btn.disabled = r !== state.maxRange && (pts.length < 2 || spanDays < parseInt(r, 10) * 0.5);
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
      chart.geo = null;
      return;
    }
    empty.hidden = true;

    const W = svg.clientWidth || 1000;
    const H = svg.clientHeight || 340;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    const padL = 56, padR = 14, padT = 18, padB = 28;
    const plotW = W - padL - padR, plotH = H - padT - padB;

    const values = pts.map((p) => p.index);
    let min = Math.min(...values), max = Math.max(...values);
    const pad = (max - min) * 0.12 || max * 0.02 || 1;
    min -= pad; max += pad;

    // Position points by DATE, not array index: the series mixes weekly deep
    // history with daily recent points, so index-based spacing would compress
    // years and stretch months on the long ranges.
    const times = pts.map((p) => new Date(p.date + "T00:00:00").getTime());
    const t0 = times[0], t1 = times[times.length - 1];
    const x = (i) => padL + (t1 === t0 ? plotW / 2 : ((times[i] - t0) / (t1 - t0)) * plotW);
    const y = (v) => padT + plotH - ((v - min) / (max - min)) * plotH;
    chart.geo = { pts, times, t0, t1, x, y, padL, padR, padT, padB, plotW, plotH, W, H };

    const up = values[values.length - 1] >= values[0];
    const color = up ? getCss("--up") : getCss("--down");
    const gid = "spk-grad";

    // gradient fill
    const defs = mk("defs");
    const grad = mk("linearGradient", { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 });
    grad.appendChild(mk("stop", { offset: "0%", "stop-color": color, "stop-opacity": "0.22" }));
    grad.appendChild(mk("stop", { offset: "100%", "stop-color": color, "stop-opacity": "0" }));
    defs.appendChild(grad);
    svg.appendChild(defs);

    // vertical time gridlines + x labels (Google Finance style)
    const spanDays =
      (new Date(pts[pts.length - 1].date) - new Date(pts[0].date)) / 86400000;
    const xticks = pts.length > 6 ? 4 : 2;
    for (let t = 0; t <= xticks; t++) {
      const i = nearestIndex(times, t0 + ((t1 - t0) * t) / xticks);
      const px = x(i);
      if (t > 0 && t < xticks) {
        svg.appendChild(mk("line", { x1: px, x2: px, y1: padT, y2: padT + plotH,
          stroke: getCss("--hairline"), "stroke-width": 1 }));
      }
      const lbl = mk("text", { x: px, y: H - 8,
        "text-anchor": t === 0 ? "start" : t === xticks ? "end" : "middle",
        fill: getCss("--muted"), "font-size": 11.5, "font-family": "inherit" });
      lbl.textContent = axisDate(pts[i].date, spanDays);
      svg.appendChild(lbl);
    }

    // y-axis labels (no horizontal gridlines — clean, like the reference)
    const yticks = 4;
    for (let t = 0; t <= yticks; t++) {
      const v = min + ((max - min) * t) / yticks;
      const lbl = mk("text", { x: padL - 10, y: y(v) + 4, "text-anchor": "end",
        fill: getCss("--muted"), "font-size": 11.5, "font-family": "inherit" });
      lbl.textContent = Math.round(v).toLocaleString("en-US");
      svg.appendChild(lbl);
    }

    // dotted reference line at range-start value (Google's "prev close" line)
    const ref = values[0];
    const refY = y(ref);
    svg.appendChild(mk("line", { x1: padL, x2: W - padR, y1: refY, y2: refY,
      stroke: getCss("--faint"), "stroke-width": 1, "stroke-dasharray": "1.5 4",
      "stroke-linecap": "round" }));

    // area + line
    let line = "";
    pts.forEach((p, i) => {
      line += (i ? "L" : "M") + x(i).toFixed(1) + "," + y(p.index).toFixed(1) + " ";
    });
    const area = line + `L${x(pts.length - 1).toFixed(1)},${(padT + plotH).toFixed(1)} L${x(0).toFixed(1)},${(padT + plotH).toFixed(1)} Z`;
    svg.appendChild(mk("path", { d: area, fill: `url(#${gid})` }));
    svg.appendChild(mk("path", { d: line, fill: "none", stroke: color,
      "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));

    // latest-point dot (always visible, like Google's live dot)
    svg.appendChild(mk("circle", { cx: x(pts.length - 1), cy: y(values[values.length - 1]),
      r: 4, fill: color }));

    // scrubber elements (hidden until hover)
    chart.crossLine = mk("line", { stroke: getCss("--border"),
      "stroke-width": 1, y1: padT, y2: padT + plotH, opacity: 0 });
    chart.dot = mk("circle", { r: 4.5, fill: color, stroke: getCss("--bg"),
      "stroke-width": 2, opacity: 0 });
    svg.appendChild(chart.crossLine);
    svg.appendChild(chart.dot);

  }

  function onScrub(e) {
    const geo = chart.geo;
    if (!geo) return;
    const svg = $("#chart-svg");
    const rect = svg.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * geo.W;
    const frac = Math.max(0, Math.min(1, (relX - geo.padL) / geo.plotW));
    const i = nearestIndex(geo.times, geo.t0 + frac * (geo.t1 - geo.t0));
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
    let left = (px / geo.W) * rect.width;
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

  // ---- live refresh -------------------------------------------------------- //
  // The data files change once a day (when TCGCSV drops its snapshot and the
  // hourly Action commits). Poll cheaply so an open tab ticks over to the new
  // day on its own; also check immediately whenever the tab regains focus.
  const REFRESH_MS = 5 * 60 * 1000;
  async function checkForUpdate() {
    try {
      const r = await fetch("data/latest.json", { cache: "no-store" });
      if (!r.ok) return;
      const fresh = await r.json();
      if (state.latest && fresh.generated === state.latest.generated) return;
      const hist = await fetch("data/history.json", { cache: "no-store" })
        .then((h) => (h.ok ? h.json() : null))
        .catch(() => null);
      state.latest = fresh;
      if (hist && hist.points) state.history = hist.points;
      state.constituents = fresh.constituents || [];
      renderHero(fresh);
      renderOverview(fresh);
      renderMovers(fresh);
      renderTable();
      drawChart();
    } catch (err) {
      // transient network failure -- try again next tick
    }
  }
  setInterval(checkForUpdate, REFRESH_MS);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && state.latest) checkForUpdate();
  });

  // ---- card lightbox ------------------------------------------------------ //
  function setupCardModal() {
    if (setupCardModal.done) return;
    setupCardModal.done = true;
    const modal = $("#card-modal");
    const openFrom = (e) => {
      const hit = e.target.closest("[data-id]");
      if (hit) openCard(hit.dataset.id);
    };
    $("#table-body").addEventListener("click", openFrom);
    $("#gainers").addEventListener("click", openFrom);
    $("#losers").addEventListener("click", openFrom);
    modal.addEventListener("click", (e) => {
      if (e.target.closest("[data-close]")) closeCard();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.hidden) closeCard();
    });
  }

  function openCard(id) {
    const c = state.constituents.find((x) => x.id === id);
    if (!c) return;
    const modal = $("#card-modal");
    $("#cm-name").textContent = c.name + (c.number ? ` #${c.number}` : "");
    $("#cm-set").textContent = c.setName || "";
    $("#cm-price").textContent = fmtPrice(c.price);
    const delta = $("#cm-delta");
    if (c.changePct == null) {
      delta.className = "delta flat";
      delta.textContent = c.isNew ? "New entry" : "— no confirmed daily change";
    } else {
      const up = c.changePct >= 0;
      delta.className = "delta " + (up ? "up" : "down");
      delta.innerHTML = `<span class="tri" aria-hidden="true">${up ? "▲" : "▼"}</span>${Math.abs(c.changePct).toFixed(2)}% today`;
    }
    $("#cm-rank").textContent = "#" + c.rank + " of 500";
    $("#cm-rarity").textContent = c.rarity || "—";
    $("#cm-prev").textContent = fmtPrice(c.prevPrice);
    $("#cm-printing").textContent = c.printing || "—";
    $("#cm-asof").textContent = c.pricedAsOf ? fmtDate(c.pricedAsOf) : "—";

    // Flag carried-forward (stale) prices so nobody mistakes them for a live quote.
    const staleEl = $("#cm-stale");
    const asOf = (state.latest && state.latest.asOfDate) || null;
    if (isStale(c, asOf)) {
      staleEl.textContent =
        "† No recent TCGplayer sales data for this card — its most recent market price " +
        `(${fmtDate(c.pricedAsOf)}) is carried forward. Thinly traded cards like this are ` +
        "where price trackers disagree the most.";
      staleEl.hidden = false;
    } else {
      staleEl.hidden = true;
    }

    // Compare the same card across sources — different markets, different numbers.
    const q = `pokemon ${c.name} ${c.setName || ""}`.trim();
    $("#cm-link").href = "https://www.tcgplayer.com/product/" + encodeURIComponent(c.id);
    $("#cm-link-pc").href =
      "https://www.pricecharting.com/search-products?type=prices&q=" + encodeURIComponent(q);
    $("#cm-link-ebay").href =
      "https://www.ebay.com/sch/i.html?LH_Complete=1&LH_Sold=1&_nkw=" + encodeURIComponent(q);

    // Load the sharpest CDN rendition available, stepping down on error.
    // The image stays hidden behind a spinner until it has fully loaded, so
    // the modal never shows a half-rendered card.
    const img = $("#cm-img");
    const spinner = $("#cm-loading");
    const candidates = c.image && !imagesOff()
      ? [c.image.replace("_200w", "_in_1000x1000"), c.image.replace("_200w", "_400w"), c.image]
      : [];
    let attempt = 0;
    img.classList.remove("is-loaded");
    const reveal = () => {
      img.classList.add("is-loaded");
      spinner.hidden = true;
    };
    img.onload = reveal;
    img.onerror = () => {
      attempt += 1;
      if (attempt < candidates.length) img.src = candidates[attempt];
      else {
        img.removeAttribute("src");
        spinner.hidden = true;
      }
    };
    img.alt = c.name;
    if (candidates.length) {
      spinner.hidden = false;
      img.src = candidates[0];
      // Cached image: some browsers won't refire `load` for a same-URL src.
      if (img.complete && img.naturalWidth > 0) reveal();
    } else {
      img.removeAttribute("src");
      spinner.hidden = true;
    }

    modal.hidden = false;
    document.body.classList.add("modal-open");
    requestAnimationFrame(() => requestAnimationFrame(() => modal.classList.add("is-open")));
  }

  function closeCard() {
    const modal = $("#card-modal");
    modal.classList.remove("is-open");
    document.body.classList.remove("modal-open");
    setTimeout(() => { modal.hidden = true; }, 220);
  }

  // ---- small utils ------------------------------------------------------- //
  // Index of the timestamp in the sorted array `times` closest to `target`.
  function nearestIndex(times, target) {
    let lo = 0, hi = times.length - 1;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (times[mid] < target) lo = mid; else hi = mid;
    }
    return target - times[lo] <= times[hi] - target ? lo : hi;
  }
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
  // Axis tick label. On short ranges (<~10mo) the day matters and the year is
  // obvious, so show "Jul 15". On longer ranges the ticks fall in different
  // years, so a day-only label ("Feb 8") is ambiguous — show "Feb '24" instead.
  function axisDate(iso, spanDays) {
    const d = new Date(iso + "T00:00:00");
    if (spanDays > 300) {
      return d.toLocaleDateString("en-US", { month: "short" }) +
        " '" + String(d.getFullYear()).slice(-2);
    }
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  // A price is "stale" when it was carried forward from an earlier day because
  // TCGplayer had no fresh sales data for the card in the current snapshot.
  function isStale(c, asOfDate) {
    return Boolean(c.pricedAsOf && asOfDate && c.pricedAsOf < asOfDate);
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---- card-image switch --------------------------------------------------- //
  // Off = thumbnails and the modal image are never rendered (no CDN requests),
  // for anyone who prefers a text-only view. Persisted like the theme.
  function imagesOff() {
    return document.documentElement.getAttribute("data-images") === "off";
  }
  function initImages() {
    if (localStorage.getItem("spk-images") === "off") {
      document.documentElement.setAttribute("data-images", "off");
    }
    const btn = $("#img-toggle");
    const sync = () => {
      const off = imagesOff();
      btn.setAttribute("aria-pressed", String(!off));
      btn.setAttribute("aria-label", off ? "Show card images" : "Hide card images");
      btn.title = off ? "Show card images" : "Hide card images";
    };
    sync();
    btn.addEventListener("click", () => {
      const next = imagesOff() ? "on" : "off";
      if (next === "off") document.documentElement.setAttribute("data-images", "off");
      else document.documentElement.removeAttribute("data-images");
      localStorage.setItem("spk-images", next);
      sync();
      if (state.latest) {
        renderMovers(state.latest);
        renderTable();
      }
    });
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
  initImages();
  load();
})();
