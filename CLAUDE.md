# S&Poké 500 — project state & handoff

The **S&Poké 500** is a price-weighted index of the 500 most valuable English,
raw/ungraded Pokémon card **singles** — a "Google Finance for the Pokémon card
market." Static site on GitHub Pages, fed by a daily GitHub Action. Domain:
**poké500.com** (punycode `xn--pok500-dva.com`; ASCII alias `poke500.com`
owned, redirect pending — see below).

Repo: `ninjahawk/s-and-poke-500`. Work happens on **`main`** (Pages serves from
`main` `/docs`). Solo hobby project by the owner (on mobile, often away — you
manage end to end). **Multiple Claude sessions sometimes run in parallel**;
before assuming a fact is current, check whether another branch is ahead of
you (see `archive/BRANCHES.md`).

## Current state (as of 2026-07-16 ~18:00 UTC)

- **LIVE** at https://xn--pok500-dva.com/ since 2026-07-16 ~00:00 UTC. Pages
  `/docs`, DNS, Enforce-HTTPS all verified. Index **1,251.65** (−0.07%),
  286 history points (weekly to 2026-01-08, daily after).
- **Reddit soft launch is LIVE**: r/PokeInvesting, rev-3 "horse race" framing,
  approved after mod delay. ~12:30 UTC: 1.6k views, 7 shares; GoatCounter
  day-0: 5k post views → 87 visits (~1.7% CTR, normal). Runbook + decision
  rules: `REDDIT_POST.md`. Next waves per `LAUNCH.md` sequencing.
- **Newsletter (weekly, Buttondown `poke500`)**: pipeline fully built, merged,
  live on the site; DORMANT until the owner adds the `BUTTONDOWN_API_KEY`
  secret. Buttondown account pending human review. Details below.
- **poke500.com (ASCII) purchased** (Spaceship, 2026-07-16 ~15:00 UTC) after
  positive Reddit reception. Redirect records (301 unmasked, `@` + `www` →
  `https://xn--pok500-dva.com/`) still NOT live as of ~17:40 UTC — apex still
  serves Spaceship parking. poké500.com stays canonical; use the ASCII form in
  typed/spoken links.
- **Monetization plan**: `MONETIZE.md` (affiliates first — owner liked it).

## Repo map — active vs archive

**Active root docs** (keep current): `README.md` (public face), `CLAUDE.md`
(this file — current state + durable reference), `LAUNCH.md` (launch playbook,
still being executed), `REDDIT_POST.md` (live post runbook), `VIRALITY.md`
(research backing the post framing; source of the "never claim first/only
index" rule), `MONETIZE.md` (revenue plan).

**Archive** (`archive/` — historical, do not act on): session-by-session build
log (`HISTORY.md`), the resolved launch handoff, the retired-branch ledger
(`BRANCHES.md`), rejected logo variant. Convention: superseded material moves
there instead of being deleted.

**Branches**: `main` + this session's designated branch are the only active
ones; two parallel-session branches from 2026-07-16 are open (their durable
facts are already folded into this file); everything else is dead and listed
in `archive/BRANCHES.md` for the owner to delete in the GitHub UI. Remote
sessions cannot delete branches or push tags — don't try, document instead.
NOTE: `claude/reddit-post-metrics-du0hya` contains a daily-close email
pipeline (`send_daily_email.py`) that is **superseded** by the merged weekly
one — do NOT merge that branch.

## Owner to-do (the only human steps outstanding)

1. **Buttondown approval** (email to owner's Gmail, expected within ~a day of
   2026-07-16): then copy the API key (Buttondown Settings → API) and add repo
   Actions secret **`BUTTONDOWN_API_KEY`**. The next ~20:23 UTC build sends
   issue #1 automatically.
2. **poke500.com redirects** (Spaceship): add URL-Redirect records, 301
   unmasked, `@` and `www` → `https://xn--pok500-dva.com/`; a session should
   verify the chain once saved.
3. Ongoing launch execution per `LAUNCH.md` (next Reddit waves, Show HN).
   Blocked-on-owner: X/Bluesky/Discord accounts (social auto-post), Google
   account (Search Console), affiliate accounts (MONETIZE.md step 1).

## Session next steps

- Spot-check tonight's ~20:23 UTC build (first with genuinely fresh prices
  post-densify): same-day refresh of the 07-16 point, sane movers/breadth.
- Verify poke500.com redirect chain once the owner saves the records.
- When Buttondown approves + key added: watch the first newsletter send in the
  Action log.

## Data pipeline (`scripts/`)

- `tcg_common.py` — shared source of truth. TCGCSV category 3 = English Pokémon.
  Universe = **singles only** (must have a card `Number`); **excludes** sealed +
  oddities (jumbo/oversized box toppers, staff promos — bracket variants
  `[staff`/`error]` — "miscellaneous", and JP-only promos: collector numbers
  ending `-P`). Representative price = **max TCGplayer market price across
  regular printings; 1st Edition rows are EXCLUDED** (fallback: used only if a
  product has no non-1st-Ed market price). Why (2026-07-15, owner-approved):
  trophy 1st Eds trade off-TCGplayer, so their market prices are broken —
  Shadowless 1st Ed Charizard showed $250 vs ~$20k+ real. No mid/listing
  fallback ever. **Forward-fills** last-known price across gap days (STALE cap
  70d) — critical: without it, thin-trading days fake a crash. Keys are
  **string** productIds everywhere.
- **Glitch guard + movers gate** (protects against TCGplayer printing broken
  prices): a price far outside a card's own recent window is held at its
  recent median until later snapshots confirm it. Per-card daily change exists
  only between two guard-confirmed prints (`trusted`/`prevTrusted` flags);
  unconfirmed ⇒ `changePct: null` ⇒ "—" in the UI, excluded from movers +
  breadth. The index level itself uses every effective price. `latest.json`
  carries `guardWindows` for ranks 501–1000 so below-cutoff cards can't enter
  the basket at an unconfirmed spike.
- `backfill_history.py` — one-time. Weekly reconstruction from the TCGCSV price
  **archive** (`/archive/tcgplayer/prices-YYYY-MM-DD.ppmd.7z`, needs `py7zr`),
  daily for the most recent `DENSE_DAYS = 183`. Dynamic top-500 membership per
  date; S&P-style divisor chaining. Writes `docs/data/{latest,history}.json`.
  Run: `pip install py7zr && python3 scripts/backfill_history.py` (~8 min).
  Regenerating CHANGES THE INDEX LEVEL (divisor path) — expected, but never do
  it casually post-publicity.
- `build_index.py` — the Action's job (stdlib only, no py7zr, no key). Runs
  **hourly** (cron :23) but exits in seconds unless TCGCSV's
  `last-updated.txt` stamp differs from `latest.json`'s stored `sourceStamp`
  (TCGCSV drops once daily ~20:05 UTC, so real builds happen ~20:23). Fetches
  live prices, continues the series from committed `latest.json`, appends a
  history point. Daily change is measured vs the previous *day* (same-day
  re-runs keep the prior baseline). Frontend polls the JSON every 5 min +
  on tab focus.
- `send_newsletter.py` — weekly Buttondown recap; see Newsletter section.
- `make_sample.py` — legacy offline sample generator; unused.

**Gotchas learned the hard way:**
- TCGCSV "live" prices == the latest daily archive (same snapshot). The
  backfill compares the **two most recent distinct archive days** for the
  final 1-day change — don't compare live vs same-day archive (all-zero moves).
- Only ~40–50 of 500 cards move on a given day (vintage prices are sticky);
  breadth/movers reflecting that is correct, not a bug.
- Early-UTC hourly runs can append a point built from *yesterday's* snapshot
  (e.g. after anything resets `sourceStamp`); the point self-corrects at the
  next ~20:23 same-day refresh.

**CNAME lesson (IMPORTANT — do not repeat):** Pages reads `CNAME` from the
*publish folder*. A session deleted the root `CNAME` as "redundant", which
**deregistered the domain** from GitHub's edge. **Keep root `CNAME` AND
`docs/CNAME`, same value** (`xn--pok500-dva.com`) — one covers source=root,
the other source=/docs. GitHub Pages accepts IDNs in punycode form.

**Marketing claim rule (from VIRALITY.md):** competitor **PokéViews 100**
exists (equal-weighted monthly top-100) — **never claim "first/only index"**;
differentiate on real index mechanics (500 cards, divisor chaining, daily
membership), transparency, free/no-signup.

## Newsletter (Buttondown)

Created by the owner 2026-07-16, handle **poke500** (dashboard at
buttondown.com; account is the owner's Gmail). Buttondown's automated vetting
flagged the new account for **human review** — the owner submitted the vetting
form and the account shows "disabled" while review is pending (the
top-of-dashboard banner is the real status; approval by email, usually hours,
up to a day; if >1 day, email support@buttondown.com).
**IMPORTANT — do not draft Buttondown vetting/review answers**: their form
explicitly says "don't use an LLM"; they hand-read responses and AI-written
answers slow or sink the review. Give the owner facts, let them phrase it.

**Pipeline is BUILT and merged, dormant until the key exists. Cadence is
WEEKLY (owner decision — daily risks unsubscribes/spam flags):**
- **Subscribe form** on the homepage (`#subscribe`, above the footer; linked
  from the footer row; heading "Weekly market updates to your inbox") posts to
  Buttondown's embed endpoint for `poke500` (hidden `embed=1` input required).
  Works as soon as the account is enabled; verified rendering in both themes.
- **`scripts/send_newsletter.py`** (stdlib-only) composes a weekly recap —
  index close, change since last issue, week's range, top-3 **week-over-week**
  confirmed gainers/decliners — and POSTs it via the Buttondown API
  (`status: about_to_send`). Runs as the last step of `update-index.yml`.
  Weekly movers baseline: after each send the script writes
  `docs/data/newsletter_state.json` (per-card price+trusted snapshot) and the
  workflow commits it. The FIRST issue has no movers ("sets the baseline")
  and goes out on the first fresh build after the key is added, whatever
  weekday; issues then lock to Fridays (catch-up if ≥8 days pass). Gates,
  each exit-0: (a) no `BUTTONDOWN_API_KEY` secret, (b) `latest.json`
  `sourceStamp` date != today UTC (only the ~20:23 UTC build after TCGCSV's
  drop is "the close"), (c) not an issue day, (d) subject
  `week ending <asOfDate>` already sent. All paths unit-tested with a mocked
  API.
- **Plan/pricing facts (verified 2026-07-16 against Buttondown's own pages)**:
  free plan = up to **100 subscribers**, unlimited sends; the API is
  **"available on all plans, including free"**. The paid-feature banner
  applies to *scheduling* via the API (`status: scheduled` + `publish_date`)
  — we never schedule; OUR cron is the GitHub Action and we POST
  `about_to_send`. So $0 until >100 subscribers.
- **API quirks handled in the script (don't remove)**: requests pin
  `X-API-Version: 2026-04-01`; POSTs carry `X-Buttondown-Live-Dangerously:
  true` because that API version rejects a key's FIRST `about_to_send` with
  400 `sending_requires_confirmation` without it.
- A parallel session built a DAILY variant (`send_daily_email.py` on branch
  `claude/reddit-post-metrics-du0hya`) — superseded, never merge it.

## Analytics

GoatCounter (free, cookieless, not consent-gated): dashboard at
**https://poke500.goatcounter.com**. Account is under one of the owner's
personal Gmail addresses — this repo is PUBLIC, so never write emails or
credentials into it. Owner has confirmed working login (2026-07-16). Snippet
is the last script tag in `docs/index.html`. Day-0 baseline: 5k Reddit post
views → 87 visits (~1.7% CTR); ~78% of referrers show "(unknown)" = Reddit
iOS in-app browser.

## Frontend (`docs/`)

`index.html` + `styles.css` + `app.js` (vanilla, no deps). Reads
`data/latest.json` + `data/history.json`. Card images from TCGplayer CDN
(`tcgplayer-cdn.tcgplayer.com`) with a header on/off switch (off = no CDN
requests at all). Theme toggle, chart scrubber, sortable/search table,
subscribe section, about page (`/about`).

## Legal posture

Independent fan project. Nominative use of "Pokémon" + card names/thumbnails to
identify what's priced; parody of "S&P 500". Footer disclaims affiliation with
Nintendo / Creatures / GAME FREAK / The Pokémon Company / TCGplayer / S&P Global.
Prices are factual (not copyrightable); card **images** are the only real (small)
copyright surface — comparable trackers do the same. Footer currently says
"non-commercial" — MUST be updated when monetization starts (see MONETIZE.md
caveats). Not legal advice; owner told this.

## Dev notes

- Screenshots: global Playwright at `/opt/node22/lib/node_modules` (symlink
  `node_modules` in scratchpad); Chromium at `/opt/pw-browsers/chromium`; use
  `waitUntil: 'domcontentloaded'` (500 CDN images never let networkidle fire).
- Serve locally: `cd docs && python3 -m http.server`.
- reddit.com is NOT fetchable from the remote env — owner pastes post metrics
  and comment text; draft replies for them.
- Remote sessions: pushes work only to the session's designated branch; PRs
  are created/merged via the GitHub MCP tools. Branch deletion and tag pushes
  are blocked (403) — record in `archive/BRANCHES.md` instead.
