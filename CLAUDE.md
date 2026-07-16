# S&Poké 500 — project state & handoff

The **S&Poké 500** is a price-weighted index of the 500 most valuable English,
raw/ungraded Pokémon card **singles** — a "Google Finance for the Pokémon card
market." Static site on GitHub Pages, fed by a daily GitHub Action. Target
domain: **poké500.com** (punycode `xn--pok500-dva.com`).

Repo: `ninjahawk/s-and-poke-500`. Work happens on **`main`** (Pages serves from
`main` `/docs`). This is a solo hobby/launch project by the owner (on mobile,
often away — you manage end to end).

## Status (as of 2026-07-15)

> **✅ LAUNCHED (2026-07-16 ~00:00 UTC).** The site is fully live at
> **https://xn--pok500-dva.com/** (poké500.com): the glitch-guard work was
> merged to `main` (fast-forward, `4676db7`), Pages deployed it, and the owner
> completed all three manual steps — Pages folder is now **`/docs`** (app
> serves at `/`), registrar DNS points at GitHub Pages (apex A + www CNAME
> verified), and **Enforce HTTPS is on** (HTTP 301s to HTTPS, cert valid).
> Live index **1,252.47** (see the 2026-07-16 densify entry below for why the
> level changed from launch's 1,355.70). `HANDOFF.md` is a resolution record.

**Done & pushed to `main`:**
- Google Finance–style UI (`docs/`). Refined off the "candy pill" look → plain
  colored text + small triangles (▲▼). Legal/trademark footer, OG/Twitter meta,
  `docs/og-image.png` social card, light+dark themes.
- **Data pipeline rebuilt on TCGCSV** (free daily TCGplayer mirror; no API key).
  See `scripts/`. Real history reconstructed back to **2024-02-08** (~2.5 yrs,
  129 weekly points), index rebased to **1,000** at that date.
- Range selector: 1W/1M/6M/1Y/**MAX** (MAX shows the full series however long it
  grows; it was "5Y" pre-launch, which overstated the ~2.5y of data).
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

**Done 2026-07-15, late session (glitch guard activated + movers gate, branch
`claude/continue-6bvev4` — needs merge to `main`):**
- **Movers decision resolved** (the HANDOFF.md open item): per-card daily
  change exists **only between two guard-confirmed prints**. `guard_prices`
  reports held prints; `trusted`/`prevTrusted` flags per constituent;
  unconfirmed endpoints ⇒ `changePct: null` ⇒ card shows "—" and sits out of
  movers + breadth. Index level itself uses every effective price (honest).
  Kills the fake +240%/+5,137% movers AND the late-release jumps (Shuckle).
- **New guard hole fixed**: windows were persisted only for the 500
  constituents, so any card below the cutoff was trusted unconditionally by
  the daily build — a one-day spike could enter the basket at a fake price.
  Now `latest.json` carries a `guardWindows` watch zone (ranks 501–1000).
- **Frontend**: null `changePct` no longer renders as "New" (uses `isNew`);
  gated cards show "—" + tooltip; modal says "no confirmed daily change";
  methodology + movers-panel note explain the confirmed-print rule.
- **Data regenerated with the guard** (backfill + daily build, all invariants
  verified): 129 points, base 1,000 @ 2024-02-08 → **1,355.70** (divisor
  180.3037). Worst surviving mover +28%. The public index number changed
  materially from 1,082 (old buggy series) — expected and correct.

**Owner launch steps — ALL DONE (verified 2026-07-16 ~00:00 UTC):**
0. ✅ Pages folder switched to `/docs` — app is the homepage; `404.html`,
   `robots.txt`, `sitemap.xml` all serve 200 from `/`.
1. ✅ Registrar DNS: apex resolves to the four GitHub Pages A records; `www`
   resolves via CNAME (v4+v6). Parking IPs gone.
2. ✅ HTTPS: cert issued and **Enforce HTTPS on** — `http://` 301s to
   `https://xn--pok500-dva.com/`, apex serves 200, `www` 301s to apex.
- Owner is sticking with **poké500.com only** (not buying ASCII `poke500.com`).
  Accept it; don't re-litigate. SEO/discovery will lean on the "Poké" term + the
  in-page "S&Poké 500" name + Reddit/reference links.
- Note: `ninjahawk.github.io/s-and-poke-500/` redirects into the owner's
  user-site domain (`nathanlangley.dev/s-and-poke-500/`, 404) — that's the
  user-site redirect, not a bug here; the project serves on its custom domain.

**Done 2026-07-16, early session (branch `claude/continue-previous-gwpi5f` —
the three remaining optional items):**
- **History densified to daily for the recent 6 months** (`backfill_history.py`
  `DENSE_DAYS = 183`): 285 points now (101 weekly to 2026-01-08, then daily
  from 2026-01-14) vs 129 weekly. The 1W/1M/6M chart ranges now have daily
  resolution, matching the cadence the live builder appends at. Verified: the
  100 overlapping weekly points reproduce the old series EXACTLY (deterministic
  chain), all 18 invariants pass (sum/divisor/breadth/gating/guardWindows/
  cadence), max step 5.25%, worst mover +28.09%.
- **The index level changed: 1,355.70 → 1,252.47 (+0.86% 1D).** Expected, not
  a bug: with daily (vs weekly) rebalancing over the recent stretch the divisor
  chain takes a different path, and the 1D baseline basket differs. The daily
  path is the more correct one (it's how the index behaves going forward), and
  this happened BEFORE any publicity (Day-0 post not yet made). LAUNCH.md's
  "up 36%" claims were updated to ~25%.
- **Card-image on/off switch** in the header (persisted like the theme).
  Images off = thumbnails/modal image are *not rendered at all* (no TCGplayer
  CDN requests), for extra copyright caution; modal image box collapses.
- **About & legal page** `docs/about.html` (serves at `/about` — GH Pages
  resolves extensionless): index summary, universe rules, legal/trademark/
  privacy posture, GitHub link (repo is public). Linked from footer + sitemap.

**Done 2026-07-16, midday session (branch `claude/reddit-post-metrics-du0hya`):**
- **Day-0 build gate largely verified.** The Action committed a real build at
  03:43 UTC (`b169913`) — triggered early because the densify rewrote
  `sourceStamp` to the archive stamp, so the next hourly run saw a mismatch.
  It appended cleanly to the densified series: 285→286 points, 2026-07-16 =
  **1,251.65** (−0.07% vs 1,252.47), 500 constituents, guardWindows intact,
  live site serves it. All per-card confirmed changes are 0.00% — expected
  (TCGCSV live == the 07-15 archive snapshot at that hour); the −0.07% is
  divisor/membership rebalance + non-gated fills. Tonight's ~20:23 UTC run
  (after the real ~20:05 drop) will same-day-refresh the 07-16 point with
  genuinely new prices — that's the last bit to spot-check.
- **Reddit soft launch is LIVE** (r/PokeInvesting per LAUNCH.md). Metrics
  reported by owner ~12:30 UTC: post approved, **1.6k views, 7 shares,
  1 upvote, 1 comment**. Shares are the healthy signal; 1 upvote at 1.6k
  views is normal for the first hours after a mod-approval delay. Playbook:
  reply to every comment fast; hold r/PokemonTCG until Day 1.
  NOTE: reddit.com (www + old) is **blocked from the remote env** — comment
  text must be pasted in by the owner; draft replies for them.

**Possible next steps / not yet done:**
- Spot-check tonight's ~20:23 UTC build (first with genuinely fresh prices
  post-densify): same-day refresh of the 07-16 point, sane movers/breadth.
- Flywheel item 1 (daily "market close" auto-post) — blocked on the owner
  creating the X/Bluesky/Discord account. Search Console — needs owner's
  Google account.

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

## Analytics
GoatCounter (free, cookieless, not consent-gated): dashboard at
**https://poke500.goatcounter.com** — account is the owner's email; login is in
the owner's password manager/chat history (created 2026-07-16; verification
email sent to their Gmail). Snippet is the last script tag in
`docs/index.html`. Adblock impact is minimal vs GA. The dashboard can be made
public in its settings if the owner wants stats as part of the transparency
story.

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
