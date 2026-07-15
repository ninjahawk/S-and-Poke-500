# S&Poké 500 — project state & handoff

The **S&Poké 500** is a price-weighted index of the 500 most valuable English,
raw/ungraded Pokémon card **singles** — a "Google Finance for the Pokémon card
market." Static site on GitHub Pages, fed by a daily GitHub Action. Target
domain: **poké500.com** (punycode `xn--pok500-dva.com`).

Repo: `ninjahawk/s-and-poke-500`. Work happens on **`main`** (Pages serves from
`main` `/docs`). This is a solo hobby/launch project by the owner (on mobile,
often away — you manage end to end).

## Status (as of 2026-07-15)

> **⚠️ ACTIVE HANDOFF — read `HANDOFF.md` first.** A price-glitch-guard effort is
> in progress and unfinished. Live site is fine (untouched); new guard code is
> committed but **not activated** (data not regenerated). One product decision is
> open (how to present daily Top-Movers, since TCGplayer thin-card data can't
> support reliable daily moves) plus one ~8-min backfill run to finish. Also
> shipped & live this session: modal layout-shift fix, chart x-axis year labels,
> and removal of the "Market mood" row. Full detail + exact finish steps in
> `HANDOFF.md`.

**Done & pushed to `main`:**
- Google Finance–style UI (`docs/`). Refined off the "candy pill" look → plain
  colored text + small triangles (▲▼). Legal/trademark footer, OG/Twitter meta,
  `docs/og-image.png` social card, light+dark themes.
- **Data pipeline rebuilt on TCGCSV** (free daily TCGplayer mirror; no API key).
  See `scripts/`. Real history reconstructed back to **2024-02-08** (~2.5 yrs,
  129 weekly points), index rebased to **1,000** at that date.
- Range selector capped at **5Y** (1W/1M/6M/1Y/5Y).
- `docs/CNAME` = `xn--pok500-dva.com`; canonical/OG URLs use it too.

**Done 2026-07-15 (launch-readiness pass):**
- **Pages is enabled** (owner did it, ~14:50 UTC): Deploy from a branch,
  `main` / **`/ (root)`** — NOT `/docs`. Verified by Host-header probe: the
  domain serves the Jekyll-rendered README at `/` and the app at `/docs/`.
  Owner must flip the folder to `/docs` (see pending list). There is no
  API/MCP tool for Pages settings, so this can't be done for them.
- **Daily Action verified end-to-end**: workflow_dispatch run succeeded and
  committed `chore: update S&Poke 500 index (2026-07-15)` to `main`. A 0.00%
  day right after a same-day refresh is expected (TCGCSV live == latest archive).
- **CNAME lesson (IMPORTANT — do not repeat):** Pages reads `CNAME` from the
  *publish folder* — with source = root, that's the **root** `CNAME`
  (`xn--pok500-dva.com`, created when the owner set the domain). A session
  deleted it as "redundant" (`ba68d3a`), which **deregistered the domain** from
  GitHub's edge (Host-header probe returned "Site not found"). Restoring it
  (PR #3, merged) re-registered the domain within seconds of deploy — verified
  edge now serves 200 for that Host. **Keep root `CNAME` AND `docs/CNAME`, same
  value** — one covers source=root, the other covers source=/docs.
  GitHub Pages accepts IDNs in punycode form (docs + the accepted UI entry).
- Added: `docs/404.html`, `docs/robots.txt`, `docs/sitemap.xml`, JSON-LD
  WebSite schema in `index.html`.

**Done 2026-07-15 (pricing-accuracy audit, branch `claude/pricing-accuracy-sources-wafpwg`):**
Prompted by user complaints that prices "look wrong / don't match other sites."
- **Verified pipeline vs source**: our numbers exactly mirror TCGplayer Market
  Price via TCGCSV (checked 9 products' raw rows). Cross-checked externally:
  Umbreon ex 161/131 within ~3% of PriceCharting; but thin vintage diverges
  hugely by *source definition* (Charizard Gold Star DF: $4,000 TCGplayer market
  vs ~$2,136 PriceCharting ungraded). PriceCharting = eBay solds (mixed
  condition/auctions); we = TCGplayer sales. Neither is "wrong" — now explained
  on-site.
- **Bug fixed — staff promos leaked in**: filter matched only `"(staff"`, but
  TCGplayer uses `[Staff]`; 31 staff promos (6% of basket!) were in the index.
  Now excluded (`[staff` + `error]` bracket variants added).
- **Bug fixed — Japanese-only promos in an "English" index**: 5 cards with JP
  promo numbers (`227/S-P`, `98/XY-P`, …; e.g. rank-15 Pikachu Stamp Box, $1.6k,
  never released in English — PriceCharting files it under *Japanese* Promo).
  Now excluded: collector number ending `-P`.
- **Bug fixed — no staleness cap in daily builder**: `build_index.py` forward-
  filled prices forever (backfill had 70d cap). Now shared `tc.STALE_DAYS = 70`,
  per-card `pricedAsOf` tracked; carried prices age out.
- **Transparency added**: per-card `printing` (96/500 are priced by Reverse
  Holofoil — a top confusion source!) + `pricedAsOf` in latest.json; † stale
  markers in table + legend; card modal shows printing/price-date/stale notice
  + compare links (TCGplayer, PriceCharting, eBay solds); "How these prices
  work" methodology section (#methodology) explaining source differences;
  README updated (removed false "lines up with PriceCharting" claim).
- **Data regenerated** with the fixed universe (2026-07-15 snapshot): 36 bogus
  cards out, divisor rebalanced 235.66→227.68, index continuous (1082.17,
  +0.73%). Old carried cards have `printing: null` until next live pricing —
  self-heals.

**Pending — OWNER must do (can't be done via tools):**
0. **Settings → Pages → Build and deployment → Folder: change `/ (root)` to
   `/docs`**, Save. Until then the domain serves the README at `/` and the app
   at `/docs/`; after the switch the app is the homepage and `docs/404.html`,
   `robots.txt`, `sitemap.xml` serve from `/`.
1. **DNS for poké500.com** at registrar (currently points at parking IPs):
   apex `A` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
   `185.199.111.153`; `www` `CNAME` → `ninjahawk.github.io`. Delete any
   registrar parking A/AAAA records.
2. **After DNS propagates**: Settings → Pages should show the custom domain
   with a green DNS check (re-enter `xn--pok500-dva.com` and Save if the field
   is empty); then enable **Enforce HTTPS** once the cert is issued (can take
   up to ~24h after DNS is correct).
- Owner is sticking with **poké500.com only** (not buying ASCII `poke500.com`).
  Accept it; don't re-litigate. SEO/discovery will lean on the "Poké" term + the
  in-page "S&Poké 500" name + Reddit/reference links.
- Note: `ninjahawk.github.io/s-and-poke-500/` redirects into the owner's
  user-site domain (`nathanlangley.dev/s-and-poke-500/`, 404) — that's the
  user-site redirect, not a bug here; the project serves on its custom domain.

**Possible next steps / not yet done:**
- Optional: densify recent history to daily (backfill is weekly); add an image
  on/off switch for extra copyright safety; a small About/legal page.

## Data pipeline (`scripts/`)

- `tcg_common.py` — shared source of truth. TCGCSV category 3 = English Pokémon.
  Universe = **singles only** (must have a card `Number`); **excludes** sealed +
  oddities (jumbo/oversized box toppers, staff promos, error cards,
  "miscellaneous"). Representative price = **max TCGplayer market price across
  regular printings; 1st Edition rows are EXCLUDED** (fallback: used only if a
  product has no non-1st-Ed market price). Why (2026-07-15, owner-approved):
  trophy 1st Eds trade off-TCGplayer, so their market prices are broken —
  Shadowless 1st Ed Charizard showed $250 vs ~$20k+ real; mixing printings made
  the top of the list incoherent (1st Ed Tyranitar #1 while 1st Ed Base Zard
  couldn't rank). No mid/listing fallback ever. **Forward-fills** last-known
  price across gap days (STALE cap 70d) — critical: without it, thin-trading
  days fake a crash. Keys are **string** productIds everywhere.
- `backfill_history.py` — one-time. Weekly reconstruction from the TCGCSV price
  **archive** (`/archive/tcgplayer/prices-YYYY-MM-DD.ppmd.7z`, needs `py7zr`).
  Dynamic top-500 membership per date; S&P-style divisor chaining. Writes
  `docs/data/{latest,history}.json`. Run: `pip install py7zr && python3
  scripts/backfill_history.py` (~8 min: ~127 archive downloads + catalog build).
- `build_index.py` — the Action's job (stdlib only, no py7zr, no key). Runs
  **hourly** (cron :23) but exits in seconds unless TCGCSV's
  `last-updated.txt` stamp differs from `latest.json`'s stored `sourceStamp`
  (TCGCSV drops once daily ~20:05 UTC, so real builds happen ~20:23). Fetches
  live prices, continues the series from committed `latest.json`, appends a
  history point. Daily change is measured vs the previous *day* (same-day
  re-runs keep the prior baseline). Frontend polls the JSON every 5 min +
  on tab focus, so open tabs update without reload.
- `make_sample.py` — legacy offline sample generator; unused now.

**Gotchas learned the hard way:**
- TCGCSV "live" prices == the latest daily archive (same snapshot). So the
  backfill compares the **two most recent distinct archive days** for the final
  1-day change — don't compare live vs same-day archive (gives all-zero moves).
- Only ~40–50 of 500 cards move on a given day (vintage prices are sticky);
  breadth/movers reflecting that is correct, not a bug.

## Frontend (`docs/`)
`index.html` + `styles.css` + `app.js` (vanilla, no deps). Reads
`data/latest.json` + `data/history.json`. Card images come from TCGplayer CDN
(`tcgplayer-cdn.tcgplayer.com`). Theme toggle, chart scrubber, sortable/search
table of the 500.

## Legal posture
Independent fan project. Nominative use of "Pokémon" + card names/thumbnails to
identify what's priced; parody of "S&P 500". Footer disclaims affiliation with
Nintendo / Creatures / GAME FREAK / The Pokémon Company / TCGplayer / S&P Global.
Prices are factual (not copyrightable); card **images** are the only real (small)
copyright surface — comparable trackers (PriceCharting, PokeData) do the same.
Not legal advice; owner told this.

## Dev notes
- Screenshots: global Playwright at `/opt/node22/lib/node_modules` (symlink
  `node_modules` in scratchpad); Chromium at `/opt/pw-browsers/chromium`; use
  `waitUntil: 'domcontentloaded'` (500 CDN images never let networkidle fire).
- Serve locally: `cd docs && python3 -m http.server`.
