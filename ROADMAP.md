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
killer feature per MONETIZE.md; needs card search UX + per-card history
(we currently keep only index-level history — would need to start
accumulating per-card daily prices, so the sooner it starts recording,
the longer the history when the feature ships).

## 5. Social auto-post ("market close" bot)

Daily close posted to X/Bluesky/Discord from the Action (LAUNCH.md
flywheel item 1). Blocked on owner creating the accounts.
