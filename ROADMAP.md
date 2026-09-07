# Roadmap — planned product work

Committed intentions, roughly ordered. Revenue-specific items live in
`MONETIZE.md`; this is the product side. Move items to `archive/HISTORY.md`
when shipped.

## 1. PWA — installable web app (owner decision 2026-07-16: we're doing this)

Make "Add to Home Screen" produce a real app: its own icon, standalone
window (no browser chrome), instant loads. The site is already a perfect
candidate (static, self-contained, data via two JSON fetches).

- `manifest.json`: name "S&Poké 500", short_name "Poké 500", standalone
  display, theme/background colors per scheme, start_url `/`, icons
  (192/512 PNG + maskable — generate from `docs/logo.png`).
- `<link rel="manifest">` + `apple-touch-icon` (iOS ignores manifest icons).
- Service worker: cache-first for the app shell (HTML/CSS/JS/logo),
  network-first for `data/*.json` so prices stay live; enables offline
  "last close" viewing as a bonus. Keep it minimal — bad SW caching is the
  classic way to serve stale sites; version the cache and skipWaiting on
  deploy.
- The settings menu (header gear) is where an "Install app" affordance can
  live later if we want to prompt.

## 2. Sub-indices (era/segment views)

"Vintage 100" / "Modern 100" style index tabs off the same daily data —
directly requested by Reddit commenters on launch day (era-balanced view).
Divisor-chained like the main index. Also the answer to "top 500 skews
vintage" critiques: show the segments side by side.

## 3. Price-move alerts + watchlist (pairs with MONETIZE.md premium tier)

Per-card watchlists (localStorage first, accounts later if ever) and
"index/card moved >X% this week" email alerts — the newsletter
infrastructure already sends mail; alerts are a filter + template away.

## 4. Portfolio tracker ("did my collection beat the index?")

Enter your cards, see total value + performance vs the S&Poké 500. The
killer feature per MONETIZE.md; needs card search UX + per-card history.

### Per-card daily history — RECORDING SINCE 2026-09-06

The data half of this item is done: the pipeline now accumulates a per-card
daily series so the history is already long when the feature (and the app's
per-card sparkline) ships.

- **File**: `docs/data/cards_history.json`, public at
  `https://xn--pok500-dva.com/data/cards_history.json`.
  Shape, chosen for size and a one-line Swift `Codable` decode:
  `{"generated": iso, "dates": ["2026-07-15", …],
  "cards": {"<productId>": [price_or_null, … aligned to dates …]}}`.
  Every series has exactly `dates.count` entries, so `cards[id][i]` pairs
  with `dates[i]`. Prices are floats at 2 dp; ids are the same string
  TCGplayer productIds used everywhere else. Written compactly (no indent).
- **A null is a real answer, not a gap to interpolate.** A price is written
  only when that card's print was `trusted` that day; guard-held, carried-
  forward and stale prints are null, as is any day the card was not a
  constituent. Recording an unconfirmed price would bake in exactly the fake
  spikes the glitch guard exists to suppress. Consumers should skip nulls,
  never zero-fill them. Only `constituents` are recorded — `guardWindows`
  (ranks 501–1000) is ignored.
- **Script**: `scripts/record_card_history.py` (stdlib only, no network). It
  reads the already-built `latest.json` and writes one column per `asOfDate`,
  idempotently — re-running a date replaces that column, never duplicates it.
- **It cannot break the daily build.** It is its own workflow step, placed
  AFTER the index commit and BEFORE the newsletter step, with
  `continue-on-error: true`; the script wraps everything in try/except and
  always exits 0. Its commit step uses the same guarded add/diff/commit
  pattern as `latest.json` and resets the index afterwards so it can never
  leave staged changes for the newsletter's chart commit.
- **Backfill (one-off, already run)**: `python3 scripts/record_card_history.py
  --backfill` reconstructs the current 500 constituents' series from this
  repo's own git history of `docs/data/latest.json` — `git log --format=%H`,
  `git show <sha>:docs/data/latest.json`, each commit's own `asOfDate`, newest
  commit per date wins, all-untrusted columns skipped. No TCGCSV archive
  download. It skips dates already recorded, so it is safe to re-run. Seeded
  **51 dates, 2026-07-15 → 2026-09-06, 487 of the 500 cards** (the other 13
  had no trusted print in that window; they join the file the first day they
  print one). 2026-07-14 exists in git but predates the `trusted` flag, so it
  would have been an all-null column and was dropped.
- **Size**: 169 KB at 51 dates ≈ 3.3 KB/date → **~1.16 MB at one year** of
  daily data, comfortably under the ~2.5 MB ceiling, so the simple aligned-
  array scheme stands. If churn ever pushes it over, the fallback is per-card
  `{"first": dateIndex, "prices": […]}` runs, which drops the leading-null
  padding for cards that joined late. Revisit if it passes ~2 MB.
- **Tests**: `tests/test_record_card_history.py` (42) — append, idempotent
  replace, null-when-untrusted, basket churn, `guardWindows` exclusion, file
  format, corrupt-input tolerance, backfill date-precedence, and a subprocess
  test proving the entrypoint exits 0 with no data and outside a git repo.
  Run `python3 -m unittest discover tests`.

Still to build: card search UX, holdings entry/storage, and the
portfolio-vs-index comparison itself.

## 5. Social auto-post ("market close" bot)

Daily close posted to X/Bluesky/Discord from the Action (LAUNCH.md
flywheel item 1). Blocked on owner creating the accounts.
