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
  approved after mod delay. Latest (owner-reported ~19:00 UTC): **18k views,
  43 shares, 13 upvotes, 33 comments; 293 GoatCounter visits** (~1.6% CTR,
  consistent with day-0). Shares are the strong signal; low upvote count is
  normal for share-driven traffic. Runbook + decision rules: `REDDIT_POST.md`.
  Next waves per `LAUNCH.md` sequencing.
- **Newsletter (weekly, Buttondown `poke500`)**: **account APPROVED**
  (2026-07-16 ~19:00 UTC; owner subscribed themselves and verified the
  double-opt-in flow works). **First organic subscriber confirmed
  2026-07-16 ~23:30 UTC** (launch day; on-model at ~1 sub/60–100 visits).
  Site now has a promo banner + animated subscribe dialog (shipped PRs
  #23–#27, conversion-researched copy). Pipeline fully built, merged, live;
  still DORMANT until the owner adds the `BUTTONDOWN_API_KEY` Actions secret
  — the next hourly build after that sends issue #1 (today's close already
  ingested). Details below.
- **poke500.com (ASCII) is LIVE** (purchased on Spaceship 2026-07-16 ~15:00
  UTC; redirect verified ~18:45 UTC): all four combinations (http/https ×
  apex/www) 301 → `https://xn--pok500-dva.com/` and land 200. Spaceship URL
  redirect (301 unmasked, FreeSSL certs) + auto-renew ON, renews 2027-07-16.
  Gotcha for the record: Spaceship's parking page overrode the apex redirect
  until parking was disabled; www worked first. poké500.com stays canonical;
  use the ASCII form in typed/spoken links.
- **Monetization plan**: `MONETIZE.md` (affiliates first — owner liked it).
- **Day-0 mobile polish shipped** (from Reddit feedback, both live): empty
  movers section collapses to one state-aware line (says "snapshot lands
  ~4pm ET" before the daily drop), and the Top-500 table no longer clips the
  daily-change column on phones (fit verified at 390/360px; 77% of traffic
  is mobile). Day-1: card/subscribe modals use an iOS-safe scroll lock
  (body pinned at offset; owner-reported "black bars" bug fixed) and
  `html` carries the theme background.

## ⚠️ SUBSCRIBER RETENTION — INCREDIBLY HIGH PRIORITY (owner directive 2026-07-16)

Losing a newsletter subscriber is the worst self-inflicted failure this
project can have. **Retention beats every other consideration; never any
mistakes on the email path.** Concretely, for every session:

1. **Never send anything to the list manually** — no test emails, no manual
   workflow triggers to force a send, no API experiments against the real
   Buttondown account. The ONLY thing that sends is the tested weekly
   pipeline on its own schedule.
2. **Cadence is a retention decision**: weekly, locked. Never increase
   frequency or add new email types without the owner explicitly asking.
3. **The send gates in `send_newsletter.py` are retention armor** (key
   check, fresh-close check, Friday check, already-sent dedupe check).
   Never weaken or remove them. Any change to that script or the
   workflow's send step needs its unit tests passing AND extra-careful
   review; when in doubt, don't ship — ask the owner.
4. **Never risk a broken or duplicate issue.** A malformed email or a
   double-send burns trust and triggers unsubscribes; if a send's
   correctness is uncertain, not sending is always the right call (a late
   issue costs nothing; a bad one costs subscribers).
5. **The subscriber list lives only in Buttondown** — never export it,
   never write addresses into this (public) repo, never point the form at
   anything else.
6. **Deliverability protections stay**: double opt-in stays on, no spammy
   subject lines/copy, unsubscribe always works (Buttondown handles it —
   don't interfere). Spam-risk audit 2026-07-17: `DELIVERABILITY.md` —
   verdict low-risk; one queued fix (switch email links from the
   punycode domain to poke500.com, retention rules apply).

## Repo map — active vs archive

**Active root docs** (keep current): `README.md` (public face), `CLAUDE.md`
(this file — current state + durable reference), `LAUNCH.md` (launch playbook,
still being executed), `REDDIT_POST.md` (live post runbook), `VIRALITY.md`
(research backing the post framing; source of the "never claim first/only
index" rule), `MONETIZE.md` (revenue plan), `ROADMAP.md` (planned product
work — PWA/installable app is item 1, owner-committed), `VENUES.md`
(graded venue map, v2 rules-verified), `DELIVERABILITY.md` (email
spam-risk audit; punycode-link fix shipped in PR #43), `OUTREACH.md`
(earned-media/embed plan: press, creators, roundups, permanent
listings, barter menu).

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

1. **Add the Buttondown API key** (approval came through 2026-07-16): copy the
   key (Buttondown Settings → API) and add repo Actions secret
   **`BUTTONDOWN_API_KEY`**. The next ~20:23 UTC build sends issue #1
   automatically (baseline issue, no movers; then locks to Fridays).
2. Ongoing launch execution per `LAUNCH.md` (next Reddit waves, Show HN).
   Blocked-on-owner: X/Bluesky/Discord accounts (social auto-post), Google
   account (Search Console), affiliate accounts (MONETIZE.md step 1).

## Session next steps

- Spot-check tonight's ~20:23 UTC build (first with genuinely fresh prices
  post-densify): same-day refresh of the 07-16 point, sane movers/breadth.
- When the owner adds `BUTTONDOWN_API_KEY`: watch the first newsletter send in
  the Action log (subject `week ending <asOfDate>`; owner is subscriber #1 and
  should receive it).

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
buttondown.com; account is the owner's Gmail). Buttondown's human review
**APPROVED the account same day (~19:00 UTC)** — the account is enabled. The
owner subscribed their own email and confirmed the full double-opt-in signup
flow works end to end (multi-step = intent filter + deliverability protection;
owner is subscriber #1). Remaining step: add the `BUTTONDOWN_API_KEY` Actions
secret (see Owner to-do). Historical note kept for future accounts: new
Buttondown accounts get flagged for human vetting and show "disabled" until
approved; their form says "don't use an LLM" for the vetting answers — never
draft those.

**Pipeline is BUILT and merged, dormant until the key exists. Cadence is
WEEKLY (owner decision — daily risks unsubscribes/spam flags):**
- **Subscribe form** on the homepage (`#subscribe`, above the footer; linked
  from the footer row; heading "Weekly market updates to your inbox") posts to
  Buttondown's embed endpoint for `poke500` (hidden `embed=1` input required).
  Works as soon as the account is enabled; verified rendering in both themes.
- **`scripts/send_newsletter.py`** composes the weekly issue as a **rich
  Google-Finance-style HTML email** (owner-approved via inbox previews
  2026-07-17): headline close (Buttondown renders the subject as the H1 —
  subject pattern `Pokémon cards rose X.XX% this week — week ending
  <Mon D, YYYY>`; research-backed rewrite 2026-07-17, both compose paths
  share `issue_subject()`, anchor `issue_anchor()` kept for dedupe and the
  gate also matches the legacy ISO form), the week's chart (transparent
  matplotlib PNG → `docs/email/chart-<asOfDate>.png`, committed+pushed by
  the script, which then POLLS the Pages URL until live before sending),
  stat rows, and top-3 week-over-week mover rows with card thumbnails.
  **Fallback armor**: any rich-path failure sends the previous
  plain-markdown compose instead; chart work only starts after all four
  send gates pass. Tests: `tests/test_send_newsletter.py` (30, API fully
  mocked — run `python3 -m unittest discover tests` before touching).
  POSTs via the Buttondown API (`status: about_to_send`); runs as the last
  step of `update-index.yml` (which pip-installs matplotlib best-effort).
  **Preview channel**: due to due diligence around the retention directive,
  design iterations go to the owner ONLY, via Buttondown draft +
  `/send-draft` with `recipients: [owner email]` — drafts can't reach the
  list; preview subjects must NEVER contain "week ending".
  Weekly movers baseline: after each send the script writes
  `docs/data/newsletter_state.json` (per-card price+trusted snapshot) and the
  workflow commits it. The FIRST issue has no movers (reader-facing copy
  teases "Starting next Friday: the week's biggest gainers and losers,
  card by card" — never say "baseline"/"per-card" to readers, owner called
  that cringe) and goes out on the first fresh build after the key is
  added, whatever weekday; issues then lock to Fridays (catch-up if ≥8
  days pass). Gates, each exit-0: (a) no `BUTTONDOWN_API_KEY` secret,
  (b) `latest.json` `sourceStamp` date != today UTC (only the ~20:23 UTC
  build after TCGCSV's drop is "the close"), (c) not an issue day,
  (d) subject with this issue's anchor (or legacy `week ending
  <asOfDate>`) already sent. All paths unit-tested with a mocked API.
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
