# Reddit launch posts — LIVE STATUS & runbooks

═══════════════════════════════════════════════════════════════════

# WAVE 2 — r/PokemonTCG: ❌ DEAD END (owner rules-check 2026-07-17)

**Verdict: do NOT post to r/PokemonTCG.** Owner screenshotted the sub
rules (~14:50 UTC): Rule 3 restricts pricing/buying/selling content,
Rule 5 bans "market research for products or services," Rule 7 gates
video posts behind an undisclosed comment-karma threshold, Rule 6 flags
AI-made content as spam, Rule 10 covers promotion generally. A market-
index video post from an account with no karma in that sub trips several
at once — removal is near-certain and would burn the domain with those
mods. The draft below is KEPT as the template for any casual collector
sub that passes a rules check (vet with this exact failure pattern in
mind: pricing megathreads, promo bans, video karma gates).

**Re-routed plan (highest value first):**
1. **Today (Friday):** the original r/PokeInvesting thread IS the live
   channel — post the newsletter EDIT + the gold-star reply; first
   newsletter issue sends tonight.
2. **Show HN, Monday 2026-07-20, 9–11am ET** — the real wave 2.
   LAUNCH.md has title + architecture first-comment ready. ⚠️ Update the
   vs-S&P table to POST-densify numbers first (1yr +10.2% vs +20.9%;
   since Feb 2024 +25.4% vs +51.5% — the old +19.7% photo-finish framing
   is dead; lead with architecture/$0-stack instead, which is HN's angle
   anyway). No video on HN — screenshots + the live site.
3. **Weekly movers ritual on r/PokeInvesting starts NEXT Friday**
   (2026-07-24) — same-sub reposting one day after wave 1 is too soon.
4. Collector Discords + smaller collector subs: owner vets rules per
   venue; the drafted post below is the template. The new demo video
   (v2, current data) leads X/TikTok/Shorts whenever those accounts
   exist.

# WAVE 2b — r/dataisbeautiful (researched + asset built 2026-07-17, POST TODAY)

**Venue verdict: rule-compatible by design, not hope.** DIB's documented
rules — "[OC]" in the title, a comment stating data source + tool, plain
non-sensational titles — are exactly our format, and linking your own
site in the sourcing comment is standard OC practice there. Multi-million
member sub; the collectible-vs-stocks frame is the most proven viral
shape for this data (VIRALITY.md, LEGO study). Stocks winning HELPS here:
zero shill-smell, and both tribes argue in the comments.

**Asset**: `cards-vs-sp500.png` (sent to owner in chat 2026-07-17; both
lines indexed to 100 at 2024-02-08, through 2026-07-16: cards +25%,
S&P +51%). Regenerate: `racechart.py` pattern — S&Poké history.json +
FRED SP500 CSV (fredgraph.csv?id=SP500; stooq is bot-walled), palette
#2a78d6/#eb6834 (validated), matplotlib. Numbers verified against
VIRALITY.md's independently-checked closes.

**Title (plain, per DIB rules):**
[OC] The 500 most valuable Pokémon cards vs. the S&P 500, indexed to
Feb 2024

**Required sourcing comment (post immediately — DIB removes OC without it):**
> Data: the Pokémon line is the S&Poké 500, a price-weighted index of the
> 500 most valuable English raw (ungraded) Pokémon singles that I built —
> computed daily from TCGplayer market prices (via the free tcgcsv.com
> mirror) with S&P-style divisor chaining and daily membership
> rebalancing. Methodology and the live chart: poké500.com. S&P 500 daily
> closes via FRED. Tool: matplotlib.
>
> Caveats up front: raw ungraded singles only (graded cards are a
> different market), neither line includes dividends, and selling cards
> costs ~15% in fees/spread — so in practice the stock gap is even wider
> than it looks. The part that surprised me: on April 8, 2025, the S&P
> had round-tripped all the way back to its Feb-2024 level while the
> cards sat at +13.5% — for a few weeks last spring, cardboard was
> beating the stock market.

**No newsletter mention** (same reasoning as the wave-2 decision; the
site converts). Reply to "where's card X" comments with rank lookups —
same engagement engine as wave 1.

## Original wave-2 draft (kept as template — numbers current 2026-07-16 close)

**⚠️ NUMBERS CHANGED since wave 1 — never reuse rev-3's stats or the old
video.** The daily-densify rebuild (2026-07-16) changed the index's divisor
path: the level is now ~1,254 (video showed 1,355.70), 1-yr return is now
**+10.2%** (was +19.7%), Moonbreon is **#7** (was #6), card #500 is now a
**Rayquaza C Lv.X (~$219)** (was "a Charizard at $215"). A visitor
cross-checking the old numbers against the live site would see a ~8%
mismatch — instant credibility loss on a card sub. All numbers below are
from the 2026-07-16 close; **refresh them from latest.json if posting after
today's ~4:23pm ET update** (they'll drift slightly, not structurally).

**Audience shift from wave 1**: r/PokemonTCG is the big casual sub —
collectors and nostalgia, not investors. Per VIRALITY.md empirics: post a
*feeling* with data behind it; beauty travels; the horse-race/finance
framing stays OUT of the post (it's wave 1's angle and it now favors
stocks anyway). Video leads, text stays short, methodology lives in the
first comment (Show-HN style).

**Pre-post checklist (owner):**
1. Check r/PokemonTCG's rules/flair for self-promo (some subs have a
   showcase day or required flair; getting this wrong = removal).
2. Wave 1 must be settled (it is — posted ~36h ago, replies handled).
3. Best window 8–11am ET; Friday ~noon ET acceptable, weekend morning is
   strong for casual subs. One venue at a time still applies.

## Title (pick one; A recommended)

**A (surprise + invite):** The most valuable Pokémon card right now isn't
Base Set Charizard. I built a free live index of the 500 most valuable
cards — like a stock market for the whole hobby. Search your best card and
tell me its rank (poké500.com)

**B (threshold hook):** It takes about $219 just to crack the top 500 most
valuable Pokémon cards. I built a free "S&P 500 for Pokémon" so you can see
the whole market — and where your cards rank (poké500.com)

## Body (video attached at top — the NEW one, see Video section)

> I wanted one number that answers "is the Pokémon card market up or down
> today?" — the way a stock index does — so I built it: a live,
> price-weighted index of the 500 most valuable English raw singles,
> priced from TCGplayer market data, updated every day around 4pm ET.
> Free, no signup, no ads.
>
> Things the data surprised me with:
>
> - **#1 isn't Base Set Zard** — it's Charizard Star (Delta Species) from
>   Dragon Frontiers at **$4,000**, with Shining Charizard right behind at
>   $3,999. (It's still Charizards at the top, of course.)
> - **Moonbreon** (Umbreon VMAX alt art) sits at **#7, $2,396** — the
>   highest card printed in the last decade.
> - It takes **~$219** just to crack the top 500. Card #500 right now is a
>   Rayquaza C Lv.X.
> - On a typical day, **~90% of the top 500 don't move at all** — the
>   "market" is a few dozen cards doing all the work.
>
> **Search your best card and tell me its rank.** And if a price looks
> wrong, say so — "why does card X show $Y" always has an interesting
> answer (different trackers measure different markets; every card links
> to TCGplayer/PriceCharting/eBay so you can check me).

## First comment (owner posts immediately)

> How it works, for anyone who wants to poke holes: prices are TCGplayer
> *market* price (actual sales, not listings) via the free tcgcsv.com
> mirror, one representative regular printing per card (1st Editions
> excluded — their TCGplayer prices are broken, a $20k card shows $250),
> obviously-glitched prices get filtered against each card's own recent
> median, and a card only shows a daily % between two confirmed prices.
> The index math is S&P-style divisor chaining so the number stays
> continuous as cards enter and leave the top 500. History back to
> Feb 2024. All of it's documented on the site, and it's data, not
> investment advice.

## Email list in the post? NO (decided 2026-07-17, reasoning on record)

Do **not** mention the newsletter in the post or first comment:
1. r/PokemonTCG mods and voters punish self-promo smell hard; a
   newsletter plug converts a "cool project" post into a lead-gen post
   and risks removal under promo rules.
2. The funnel already works without it: the site's promo banner +
   subscribe dialog convert visitors on their own (~1 sub/60–100 visits
   on launch day) — the post's only job is traffic.
3. VIRALITY.md: marketing smell kills comment velocity, and comment
   velocity in hour one decides reach.

**If someone asks** "how do I follow this?" — reply with: "There's a
weekly Friday recap email on the site (or just check the number — it
updates daily ~4pm ET)." That's the only sanctioned mention.

## Video: RE-RECORD (old one is stale — do not reuse)

The wave-1 demo mp4 cold-opens on 1,355.70; live is ~1,254 and Moonbreon
moved to #7. Same 33s vertical format and shot list as before (hero →
1Y→MAX zoom-out → scrub → movers → top-6 crawl → Moonbreon modal), just
re-recorded against current data. Regeneration pipeline: staged copy of
docs/ with the visible card images localized (headless Chromium can't
reach the TCGplayer CDN; curl via proxy works), Playwright recordVideo +
scripted choreography, webm→mp4 via imageio-ffmpeg.

## Measuring

Same scoreboard: https://poke500.goatcounter.com (watch referrers).
Wave-1 baseline to beat: 18k views / 43 shares / ~300 visits (~1.6% CTR).
r/PokemonTCG is ~10x the sub — a comparable CTR is a good outcome; the
video's share rate is the number to watch.

═══════════════════════════════════════════════════════════════════

# WAVE 1 — r/PokeInvesting soft launch (LIVE)

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
