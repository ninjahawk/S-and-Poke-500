# What actually makes this go viral — deep analysis (2026-07-16)

Researched against comparable projects that succeeded, current market discourse,
and r/PokeInvesting's actual engagement data. Verified numbers throughout.

## The verified numbers (compute date 2026-07-15)

| Window | S&Poké 500 | S&P 500 | Winner |
|---|---|---|---|
| 1 year (Jul '25 → Jul '26) | **+19.7%** (1,132.63 → 1,355.70) | **+20.9%** (6,263.70 → 7,572.40) | photo finish |
| YTD 2026 | +7.9% | +10.6% (6,845.50 →) | stocks |
| Since inception (Feb 8 '24) | +35.6% | +51.5% (4,997.91 →) | stocks |
| Max drawdown over period | **−5.9%** (May–Oct '24) | double-digit (spring '25) | cards (illiquidity caveat) |

S&P closes verified via search: 4,997.91 (2024-02-08), 6,263.70 (2025-07-15),
6,845.50 (2025-12-31), 7,572.40 (2026-07-15). Ours from history.json.

**This is the found treasure.** The discourse RIGHT NOW is full of mushy claims
("average cards +46% YoY", "Pokémon cards crush the S&P — even Buffett should
rethink" on Yahoo Finance, a LinkedIn counter-thread calling the comparison
misleading). Nobody in that argument has a rigorous number. We do, daily.

## Case studies — what actually worked and the transferable mechanic

**1. McBroken (2020).** Reverse-engineered McDonald's API, placed $18k of fake
orders per minute to map broken ice-cream machines. Went global in days;
McDonald's VP publicly responded. Mechanics: (a) universal shared frustration,
(b) ONE number/map, zero friction, (c) *comically unreasonable engineering
effort applied to something silly* — the gap between rigor and subject IS the
joke, (d) a brand response as accelerant. → Transfer: "real S&P divisor math,
2.5 years of reconstructed daily data, for cardboard Pikachus" is our version
of the unreasonable-effort flex. Say the effort out loud.

**2. The LEGO study (2019, resurfaces yearly).** "LEGO returns 11%/yr,
beating the S&P 500, gold and fine wine." Two economists + 2,300 sets. Cited
by press for years. Mechanic: **the asset-class-vs-stocks horse race is the
single most proven viral frame for collectible data** — it gives finance
press a headline and collectors bragging rights. → Transfer: our table above
is the LEGO study for Pokémon, except LIVE with a URL. This is also the
journalist pitch: "citable daily benchmark," which is how the LEGO study
achieved evergreen status.

**3. StockX (2016).** Branded itself "the stock market of things" — the
finance metaphor itself was the entire marketing engine (bid/ask, tickers,
"IPOs" for sneakers). → Transfer: our Google-Finance-clone UI is the
metaphor made visible; screenshots/video where it "looks exactly like
checking stocks, but it's Charizards" carry the idea with no words.

**4. r/PokeInvesting empirics (600k weekly visitors).** 2026's top posts:
Costco scalper trolley photo (5,385 upvotes, 1,533 comments — OUTRAGE),
connected-artwork post (1,901 upvotes — BEAUTY). Market-analysis threads
underperform both. → Transfer: do NOT post an essay. Post a *feeling* with
data behind it: a horse race (tribal identity) + a beautiful chart. Analysis
lives in the first comment, Show-HN style.

**5. Timing tailwind (verified news).** 30th-anniversary boom, CNBC coverage
(May '26), Logan Paul's $16M Illustrator sale (Feb '26), Japanese index
doubling then correcting, scalper outrage weekly. "Is this a bubble?" is the
sub's live obsession — an honest daily benchmark is the tool that argument
was missing. We ride a wave already in motion; we don't have to create one.

## Competitive reality check (IMPORTANT — corrects LAUNCH.md)

We are **not** the only index. Verified: **PokéViews 100** (top-100 English,
equal-weighted, monthly rebalance, TCGplayer, methodology partly public, no
open code, unclear history depth), **Cardboard Tracker** ("S&P 500 for
trading cards," JS app, opaque), **TCGFish** market index. Never claim
"first/only." Differentiate on verifiable specifics: **500 constituents,
price-weighted with S&P-style divisor chaining (not equal-weight), daily
dynamic membership (not monthly), 2.5 years of daily history, open code,
glitch-guarded prices, per-card printing/staleness transparency + compare
links.** Prepared answer if raised: "Yep — PokéViews does an equal-weighted
top-100 monthly. I wanted something closer to how real indices work: 500
cards, divisor continuity, daily membership, and every assumption public."

## The virality mechanism stack (what "almost guarantees" it)

A post is near-guaranteed to outperform when it stacks ALL of these; our
rev-2 draft had 4–6, the pivot adds 1–3:

1. **Identity stakes** — forces two tribes to argue (collectors vs index-fund
   bros; both live on that sub). The photo-finish stat does this perfectly:
   bulls read "cardboard matched the S&P," bears read "stocks still won."
   Both comment. Comment velocity in hour one is what the algorithm ranks.
2. **One falsifiable, surprising number** — "+19.7% vs +20.9%" (not a vibe,
   a checkable claim with a URL).
3. **Skin-in-the-game lookup** — "search your card, tell me its rank" turns
   readers into commenters and comments into testimonials.
4. **Screenshot-able artifact** — the chart (and the demo video). Beauty
   travels on this sub.
5. **Creator present and candid in comments** — reply to everything in the
   first 2 hours; volunteering the caveats FIRST ("no dividends, ~15% sell
   fees/spread, raw ungraded only") converts would-be attackers into allies.
6. **Zero friction** — free, no signup, loads instantly. Already true.
7. **News-cycle draft** — attaches to the Logan Paul / bubble discourse
   already circulating. Reference it in the post.

## The recommended post (rev 3 — the horse race)

**Title:**
Over the last 12 months, the 500 most valuable English Pokémon cards returned
+19.7%. The S&P 500 returned +20.9%. I built a free live index so you can
watch the race (poké500.com)

**Body:** (chart image/video first)

Everyone's throwing around numbers right now — "average cards up 46%!", the
$16M Logan Paul Pikachu, "even Buffett should rethink." I wanted the real
number, so I built one: the S&Poké 500, a live index of the 500 most valuable
English raw singles, calculated like an actual market index (divisor chaining,
daily membership rebalancing) from TCGplayer market prices, with history back
to Feb 2024.

The race so far:

| | Top 500 Pokémon cards | S&P 500 |
|---|---|---|
| Last 12 months | **+19.7%** | +20.9% |
| 2026 so far | +7.9% | +10.6% |
| Since Feb 2024 | +35.6% | +51.5% |

Before anyone yells — yes: no dividends, you'd lose ~15% selling on TCGplayer,
and raw ungraded singles only. Stocks are still winning. But the top of the
card market keeping pace with the hottest stock market in memory, with a max
drawdown of 5.9%, is wilder than I expected when I started.

Other things the data shows: it takes $215 just to crack the top 500 (card
#500 is — of course — a Charizard). #1 isn't Base Set Zard, it's Charizard
Star Delta Species at $4,000. Moonbreon is #6 at $2,396. And ~90% of the top
500 don't move on a given day — the "market" is like 50 cards doing all the
work.

Site: poké500.com — free, no signup, no ads, updates daily ~4pm ET. Every
card links to TCGplayer/PriceCharting/eBay so you can check me, and the
methodology (including the ugly parts) is public.

**Search your biggest card and tell me its rank.** And if you think a price
is wrong, say so — "why does card X show $Y" always has an interesting answer.

**First comment (post immediately, Show-HN style):** methodology summary +
the caveats restated + "ask me anything about the math." Owns the top slot,
frames the debate.

## Asset strategy

- **Reddit (analysis wave):** static chart/screenshot + the table. Data subs
  reward images-with-numbers over video.
- **r/PokemonTCG (casual wave, Day 1–2):** the demo VIDEO leads, lighter text.
- **X/TikTok:** video + "photo finish" framing. 3-tweet thread max.
- **Show HN (Day 3–7):** unchanged from LAUNCH.md, but add the vs-S&P table
  to the first comment — HN loves an honest benchmark with caveats.
- **Journalist pitch:** lead with the table (the LEGO-study lesson: press
  runs comparison stats, not features).

## Timing

Best window 8–11am ET weekday (sub's US morning scroll + full day of
compounding). A 10pm ET post spends its critical first hours in low traffic.
If soft-launch-tonight matters for feedback, fine — but the horse-race post
deserves the morning slot. Consider: soft feedback post tonight OR hold
everything to ~9am ET.

## Future accelerants (post-launch, highest leverage first)

1. **S&P overlay line on the chart** (~1 session of work: fetch SPX daily
   closes, second line + toggle). Makes the race the product, not just a
   post. The two-line chart is the shareable image forever after.
2. Daily auto-post bot + weekly movers ritual (already in LAUNCH.md).
3. Milestone triggers ("index crosses 1,400", "cards overtake S&P YTD").
4. The vs-S&P table auto-updated on-site = permanent journalist bait.
