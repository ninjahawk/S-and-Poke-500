# Session-by-session build log (archive)

Chronological record of what each working session did, moved out of CLAUDE.md
2026-07-16 during consolidation. Durable rules/lessons were kept in CLAUDE.md;
this is the full history for archaeology.

## Pre-launch (through 2026-07-14)

- Google Finance–style UI (`docs/`). Refined off the "candy pill" look → plain
  colored text + small triangles (▲▼). Legal/trademark footer, OG/Twitter meta,
  `docs/og-image.png` social card, light+dark themes.
- **Data pipeline rebuilt on TCGCSV** (free daily TCGplayer mirror; no API key).
  Real history reconstructed back to **2024-02-08** (~2.5 yrs, 129 weekly
  points), index rebased to **1,000** at that date.
- Range selector: 1W/1M/6M/1Y/**MAX** (MAX shows the full series however long it
  grows; it was "5Y" pre-launch, which overstated the ~2.5y of data).
- `docs/CNAME` = `xn--pok500-dva.com`; canonical/OG URLs use it too.

## 2026-07-15 — launch-readiness pass

- **Pages enabled** (owner, ~14:50 UTC): Deploy from a branch, `main` /
  `/ (root)` at first; owner later flipped to `/docs`. No API/MCP tool exists
  for Pages settings.
- **Daily Action verified end-to-end**: workflow_dispatch run succeeded and
  committed `chore: update S&Poke 500 index (2026-07-15)` to `main`. A 0.00%
  day right after a same-day refresh is expected (TCGCSV live == latest archive).
- **CNAME incident**: a session deleted the root `CNAME` as "redundant"
  (`ba68d3a`), which deregistered the domain from GitHub's edge. Restoring it
  (PR #3) re-registered within seconds. Lesson kept in CLAUDE.md.
- Added: `docs/404.html`, `docs/robots.txt`, `docs/sitemap.xml`, JSON-LD
  WebSite schema in `index.html`.

## 2026-07-15 — pricing-accuracy audit (branch `claude/pricing-accuracy-sources-wafpwg`)

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
  never released in English). Now excluded: collector number ending `-P`.
- **Bug fixed — no staleness cap in daily builder**: `build_index.py` forward-
  filled prices forever (backfill had 70d cap). Now shared `tc.STALE_DAYS = 70`,
  per-card `pricedAsOf` tracked; carried prices age out.
- **Transparency added**: per-card `printing` (96/500 are priced by Reverse
  Holofoil — a top confusion source!) + `pricedAsOf` in latest.json; † stale
  markers; card modal shows printing/price-date/stale notice + compare links;
  "How these prices work" methodology section; README updated (removed false
  "lines up with PriceCharting" claim).
- **Data regenerated** with the fixed universe: 36 bogus cards out, divisor
  rebalanced 235.66→227.68, index continuous (1082.17, +0.73%).

## 2026-07-15 late — glitch guard + movers gate (branch `claude/continue-6bvev4`)

- **Movers decision resolved**: per-card daily change exists only between two
  guard-confirmed prints. `guard_prices` reports held prints;
  `trusted`/`prevTrusted` flags per constituent; unconfirmed endpoints ⇒
  `changePct: null` ⇒ card shows "—" and sits out of movers + breadth. Index
  level itself uses every effective price. Killed the fake +240%/+5,137%
  movers AND the late-release jumps (Shuckle).
- **Guard hole fixed**: windows were persisted only for the 500 constituents;
  `latest.json` now carries a `guardWindows` watch zone (ranks 501–1000) so
  below-cutoff cards can't enter the basket at an unconfirmed spike price.
- **Frontend**: null `changePct` no longer renders as "New" (uses `isNew`);
  gated cards show "—" + tooltip; methodology + movers-panel notes.
- **Data regenerated with the guard**: 129 points, base 1,000 @ 2024-02-08 →
  1,355.70 (divisor 180.3037). Worst surviving mover +28%.

## 2026-07-16 ~00:00 UTC — LAUNCH

Owner completed all three manual steps, verified by session probes:
0. Pages folder switched to `/docs` — app is the homepage; `404.html`,
   `robots.txt`, `sitemap.xml` all serve 200 from `/`.
1. Registrar DNS: apex resolves to the four GitHub Pages A records; `www`
   resolves via CNAME (v4+v6). Parking IPs gone.
2. HTTPS: cert issued and Enforce HTTPS on — `http://` 301s to
   `https://xn--pok500-dva.com/`, apex serves 200, `www` 301s to apex.
- At the time the owner was sticking with poké500.com only — SUPERSEDED
  later on 2026-07-16: owner bought ASCII `poke500.com` after positive
  Reddit reception.
- Note: `ninjahawk.github.io/s-and-poke-500/` redirects into the owner's
  user-site domain (`nathanlangley.dev/s-and-poke-500/`, 404) — that's the
  user-site redirect, not a bug; the project serves on its custom domain.

## 2026-07-16 early — densify + polish (branch `claude/continue-previous-gwpi5f`)

- **History densified to daily for the recent 6 months** (`backfill_history.py`
  `DENSE_DAYS = 183`): 285 points (101 weekly to 2026-01-08, then daily from
  2026-01-14) vs 129 weekly. Verified: the 100 overlapping weekly points
  reproduce the old series EXACTLY, all 18 invariants pass, max step 5.25%.
- **Index level changed: 1,355.70 → 1,252.47 (+0.86% 1D).** Expected: daily
  (vs weekly) rebalancing takes a different divisor path. Happened BEFORE any
  publicity. LAUNCH.md's "up 36%" claims were updated to ~25%.
- **Card-image on/off switch** in the header (persisted like the theme);
  images off = no TCGplayer CDN requests at all.
- **About & legal page** `docs/about.html` (serves at `/about`).

## 2026-07-16 midday — Reddit soft launch + metrics (branches `claude/reddit-post-soft-launch-2lo8tx`, `claude/reddit-post-metrics-du0hya`, parallel sessions)

- **Reddit post went LIVE** on r/PokeInvesting (~03:00 UTC posted, approved
  after mod delay). Rev-3 "horse race" framing (see REDDIT_POST.md). Metrics
  ~12:30 UTC: 1.6k views, 7 shares, 1 upvote, 1 comment (shares = the healthy
  signal). GoatCounter day-0: 5k post views → 87 site visits (~1.7% CTR,
  normal), ~90% of traffic Reddit.
- **Virality research** (VIRALITY.md): verified vs-S&P numbers, case studies,
  competitor check — PokéViews 100 exists (equal-weighted monthly top-100), so
  NEVER claim "first/only index". LAUNCH.md differentiators updated.
- **Owner bought ASCII `poke500.com`** (~15:00 UTC, Spaceship). Plan:
  registrar-level 301 (unmasked) redirect `@` + `www` →
  `https://xn--pok500-dva.com/`; poké500.com stays canonical. Redirect records
  still not live as of ~17:40 UTC (apex still parks).
- That session also built `send_daily_email.py` (daily-close Buttondown
  pipeline) — **superseded** the same day by the owner's explicit weekly
  decision and the merged weekly `send_newsletter.py`. Never merged.
- GoatCounter access confirmed solved (owner logged in ~15:30 UTC).

## 2026-07-16 — newsletter session (branch `claude/newsletter-creation-gbl2t4`, PRs #13–16)

- **First post-densify daily build verified clean**: hourly Action ran at
  03:43 UTC (densify had reset `sourceStamp`) and appended 2026-07-16 =
  1,251.65 (−0.07%), 286 points, 500 constituents, guardWindows intact
  (`b169913`).
- **Buttondown account created by owner** (handle `poke500`); flagged for
  human review; owner submitted the vetting form themselves.
- **Weekly newsletter pipeline built and merged**: homepage subscribe form
  ("Weekly market updates to your inbox", hidden `embed=1` input),
  `send_newsletter.py` weekly recap with week-over-week movers via
  `newsletter_state.json` baseline, workflow integration, all gates
  unit-tested with a mocked API. Verified live on the site.
- **Buttondown API research**: free plan = 100 subscribers; API on all plans;
  "scheduling" is the paid feature (we don't use it — GitHub cron drives the
  schedule, sends are immediate `about_to_send`). Found + fixed: API
  v2026-04-01 rejects a key's first `about_to_send` without
  `X-Buttondown-Live-Dangerously: true`.
- **MONETIZE.md written** (affiliates → sponsorship → premium tier).
- **Consolidation**: this archive/ folder created; HANDOFF.md and the session
  log moved here; branch ledger written (BRANCHES.md).
