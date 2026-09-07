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

### Any-card catalog — PUBLISHED SINCE 2026-09-07

The other data half: a portfolio is useless if you can only add cards that
happen to sit in the top 500. `scripts/publish_catalog.py` publishes the
**whole English singles universe** — every set, every card, today's price —
as static JSON under `docs/data/catalog/`, live at
`https://xn--pok500-dva.com/data/catalog/…`.

- **Costs nothing extra to produce.** `build_index.py` already downloads all
  ~220 TCGplayer category-3 groups' products and prices every day and throws
  ~26,000 of them away. It now side-writes that fetched universe to
  `.cache/tcg_snapshot.json` (gitignored, never committed) as a pure
  additive write inside its own `try/except`; `publish_catalog.py` consumes
  the cache. Zero extra requests, and if the side-write ever fails the index
  build does not notice.
- **Same isolation contract as the per-card history**: its own
  `continue-on-error: true` workflow step AFTER the index commit, whole body
  in `try/except`, always exits 0. On an hourly no-op run there is no cache,
  so it publishes nothing and fetches nothing. `--fetch` re-downloads with
  the normal throttling (used for the first publish and as a manual repair);
  `--size` reports the published bytes.
- **Same universe and price rule as the index**, because both come from
  `tcg_common`: singles only, no sealed/jumbo/oversized/box-topper, no
  "miscellaneous", no `[staff]`/`(staff)`, no miscut/misprint/error, no
  JP-only `-P` promos; price = highest TCGplayer **market** price across a
  product's regular printings with 1st Edition rows excluded, `null` when
  there is no market price that day.
- **Prices here are RAW.** The index's glitch guard (rolling-median hold)
  needs a per-card history this catalog does not keep, so it is not applied.
  Every set file says so in a `note` field at the top — do not quietly drop
  that note, an unguarded price can print a wild outlier on a thin card.
- **Files** (`docs/data/catalog/`):
  - `sets.json` — `{generated, asOfDate, sets:[{id, name, abbr, count,
    priced, published}]}`, newest set first (undated sets last). `abbr` and
    `published` come from TCGCSV's group `abbreviation`/`publishedOn`.
  - `sets/<setId>.json` — `{note, setId, setName, asOfDate, cards:[{id, name,
    number, rarity, printing, image, price, prevPrice, pricedAsOf}]}`, cards
    sorted by collector number (numerically — "9/181" before "170/181") then
    name.
  - `search.json` — `{asOfDate, cards:[[id, name, setId, number], …]}`.
    Array-of-arrays on purpose: the app downloads this whole file once at
    launch, and objects would roughly double it. Budget is 2 MB; if it is
    ever exceeded the script drops cards with no market price and records
    that in a `note` field.
- **`prevPrice`** is read from the previously *committed* copy of the same
  set file before it is overwritten: yesterday's `price` when that file's
  `asOfDate` is older than today's, `null` on the first run or when the card
  was absent. A same-day republish (workflow retry, manual re-run) keeps the
  existing `prevPrice` rather than collapsing every change to zero — the same
  baseline rule `build_index.py` uses for the index's daily change.
- **Size at first publish (2026-09-07)**: **211 sets, 26,633 cards, 26,248
  priced**; 213 files, **7.17 MB** total; largest single file 411 KB
  (`sets/2282.json`); `search.json` **1.25 MB**, under budget, so no cards
  were dropped. GitHub Pages' limits are 1 GB per site and a 100 MB soft cap
  per file — the whole catalog is under 1% of the site budget. It is
  republished in full each day, which does grow repo history; if that ever
  becomes a problem the fix is to commit only changed set files.
- **Tests**: `tests/test_publish_catalog.py` (40) — the universe filters, the
  price rule (including 1st-Edition-only fallback), `prevPrice` carry-over
  and the same-day rule, the cache handshake, file shapes, number sorting,
  the over-budget `search.json` trim, and subprocess tests proving the
  entrypoint exits 0 with nothing available. All fetches mocked.

Still to build: card search UX, holdings entry/storage, and the
portfolio-vs-index comparison itself (the catalog above supplies the data
for search; graded holdings need a separate price source — research lives
outside this repo).

## 5. Social auto-post ("market close" bot)

Daily close posted to X/Bluesky/Discord from the Action (LAUNCH.md
flywheel item 1). Blocked on owner creating the accounts.
