# Soft-launch Reddit post — LIVE STATUS & runbook

**Status (2026-07-16 ~03:00 UTC):** POSTED to r/PokeInvesting by the owner,
**awaiting moderator approval**. Link:
https://www.reddit.com/r/PokeInvesting/s/AlfDGheWPI
(reddit.com is not fetchable from the dev environment — owner reports status.)

**Metrics log (owner-reported → GoatCounter visits):**
- ~12:30 UTC: 1.6k views, 7 shares → 87 visits (~1.7% CTR)
- ~19:00 UTC: 18k views, 43 shares, 13 upvotes, 33 comments → 293 visits
  (~1.6% CTR). Shares are the viral vector; upvote count lags because most
  traffic arrives via share links (viewers can't/don't vote).

The posted version is **rev 3, the "horse race" framing** (below) — chosen
after the virality research in `VIRALITY.md`. A modmail asking for approval
was suggested to the owner (unknown if sent).

## Decision rules (agreed with owner)

- **Approved within ~2–3h of posting** → owner immediately posts the prepared
  FIRST COMMENT (below), then replies to every comment for ~2 hours.
  Prepared answers: `LAUNCH.md` §Prepared answers + `VIRALITY.md`
  §Competitive reality (the "PokéViews already exists" answer).
- **Still pending next morning** → DELETE and repost fresh between
  **8–11am ET** (same title/body/image). Reddit ranks on upvotes-vs-age; a
  post approved hours late is born buried. Fresh clock > pending post.
- **No crossposting** anywhere until this wave settles. Next waves:
  r/PokemonTCG Day 1–2 (video-led, casual tone), Show HN Day 3–7 (add the
  vs-S&P table to the architecture first-comment).
- Scoreboard: https://poke500.goatcounter.com (reddit.com shows as referrer;
  soft-post success bar 500–2k visits).

## What was posted (rev 3 — title)

Over the last 12 months, the 500 most valuable English Pokémon cards returned
+19.7%. The S&P 500 returned +20.9%. I built a free live index so you can
watch the race (poké500.com)

## Body (chart screenshot embedded at top)

Everyone's throwing around numbers right now — "average cards up 46%!", the
$16M Logan Paul Pikachu, "even Buffett should rethink." I wanted the real
number, so I built one: the **S&Poké 500**, a live index of the 500 most
valuable English raw singles, calculated like an actual market index (divisor
chaining, daily membership rebalancing) from TCGplayer market prices, with
history back to Feb 2024.

The race so far:

| | Top 500 Pokémon cards | S&P 500 |
|---|---|---|
| Last 12 months | **+19.7%** | +20.9% |
| 2026 so far | +7.9% | +10.6% |
| Since Feb 2024 | +35.6% | +51.5% |

Before anyone yells — yes: no dividends, you'd lose ~15% selling on
TCGplayer, and this is raw ungraded singles only. Stocks are still winning.
But the top of the card market keeping pace with the hottest stock market in
memory, with a max drawdown of 5.9%, is wilder than I expected when I started.

Other things the data shows: it takes **$215 just to crack the top 500**
(card #500 is — of course — a Charizard). #1 isn't Base Set Zard, it's
Charizard Star Delta Species at $4,000. Moonbreon is #6 at $2,396. And ~90%
of the top 500 don't move on a given day — the "market" is basically 50 cards
doing all the work.

Site: [poké500.com](https://xn--pok500-dva.com/) — free, no signup, no ads,
updates daily ~4pm ET. Every card links out to TCGplayer/PriceCharting/eBay
so you can check me, and the methodology (including the ugly parts) is public
on the site.

**Search your biggest card and tell me its rank.** And if you think a price
is wrong, say so — "why does card X show $Y" always has an interesting answer.

## FIRST COMMENT (owner posts immediately on approval)

Methodology for anyone who wants to poke holes: prices are TCGplayer market
price (not listings), one representative printing per card, 1st Editions
excluded because their TCGplayer prices are broken ($250 "market price" on a
$20k card), obviously-glitched prints get filtered by a rolling-median guard,
and a card only shows a daily % between two confirmed prices. Index math is
S&P-style divisor chaining so the level stays continuous when membership
changes. All of it's documented on the site — happy to answer anything about
the math. And to be extra clear: this is data, not investment advice.

## Assets

- **Chart screenshot** (MAX range hero) — sent to owner in chat; regenerate:
  serve `docs/` locally, Playwright at 1100px, click MAX, clip top 640px.
- **Demo video** `poke500-demo.mp4` — 33s, 720×1280, silent; in repo root on
  this branch (TEMPORARY delivery copy, delete before merge) and sent in
  chat. Earmarked to LEAD the r/PokemonTCG wave, not r/PokeInvesting.
  Recording pipeline: see prior session — staged copy of docs/ with card
  images localized (CDN unreachable by headless Chromium; curl works via
  proxy), Playwright recordVideo + scripted choreography, imageio-ffmpeg
  webm→mp4. Full shot list below (hand-shot fallback).

## Video — DONE (2026-07-16)

A finished 33s demo mp4 (`poke500-demo.mp4`, 720×1280, silent, ~4.5 MB) was
produced with a scripted Playwright recording against a local copy of the
live site (card images localized so they render instantly) and sent to the
owner in chat. Shot order: cold open on 1,355.70 → 1Y→MAX zoom-out → tooltip
scrub across the chart → movers → top-10 crawl → Moonbreon modal → return to
hero. The hand-shot notes below are the fallback if a reshoot is ever needed.

## Video shoot — director's notes (35s silent vertical, one take)

Pre-flight: DND on; open poké500.com in the browser (URL bar visible =
branding); scroll the full page once to warm the image cache, back to top;
set range to **1M** (opening position); dark mode optional; record.

Move at half natural speed. Shot list:

| Time | Shot | Direction |
|---|---|---|
| 0–4s | Cold open | Hold on **1,355.70**, no touching |
| 4–10s | The zoom-out ⭐ | Tap **1Y**, beat, tap **MAX** — the money shot |
| 10–16s | The scrub | Press-drag to Feb 2024 (~1,000), hold, drag to today |
| 16–22s | Movers | Slow scroll through Today's movers |
| 22–29s | The rich list | Crawl ranks 1–6 ($4,000 Zard Star → Moonbreon) |
| 29–35s | Moonbreon close-up | Tap Umbreon VMAX row → modal ($2,396, #6 of 500), hold 2s, cut |

## Superseded drafts

- Rev 1 (feature-list "I built a thing") — rejected by owner as boring.
- Rev 2 (data-drop, no S&P comparison) — superseded by rev 3 after the
  virality research; rev 2's bullets were folded into rev 3's body.
