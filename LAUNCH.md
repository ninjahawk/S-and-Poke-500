# S&Poké 500 — maximum-hype launch playbook

Everything is paste-ready. Site: **https://xn--pok500-dva.com/** (poké500.com).
Stats: **https://poke500.goatcounter.com** (watch referrers live during each post).

## Positioning (pick per audience, never mix)

- **Collectors:** "One number for the whole Pokémon card market — a live S&P-500-style
  index of the 500 most valuable English cards, free, updated daily."
- **Hacker News / devs:** "A stock-market index for Pokémon cards: $0/month —
  GitHub Pages + one GitHub Action, no server, no API keys, methodology fully open."
- **Normies / video:** "I built a stock market for Pokémon cards."

The differentiators to hammer: real index mechanics (500 cards, S&P-style
divisor chaining, DAILY membership — vs PokéViews 100's equal-weighted
monthly top-100; see VIRALITY.md §competitors — **never claim "first/only
index," others exist**), it's **transparent** (open methodology, open code,
compare links on every card), and it's **free with no signup**.

## Sequencing

**Day 0 (after today's ~20:05 UTC build verifies green): soft launch, collector Reddit.**
One community, one post, so early feedback surfaces any issue before the big swing.
Best posting window: 8–11am ET.

**Day 1–2: the rest of collector Reddit + Discords**, one sub per half-day. Never
crosspost simultaneously — it reads as spam and the mods talk to each other.

**Day 3–7 (a weekday, 9–11am ET): Show HN.** The site will have a few days of real
daily updates and maybe testimonial comments by then.

**Week 2+: evergreen** — short-form video, journalist pitches, the flywheel below.

## Paste-ready posts

### r/PokeInvesting (Day 0 — the bullseye audience)
> **Title:** I built a free S&P 500-style index for the Pokémon card market — 500 most
> valuable English cards, updated daily (poké500.com)
>
> **Body:** I wanted a single number that answers "is the Pokémon market up or down?"
> the way the S&P 500 does for stocks — so I built one. The S&Poké 500 tracks the 500
> most valuable English raw singles by TCGplayer market price, with real index math
> (divisor chaining, dynamic membership), history back to Feb 2024, and daily
> auto-updates. It's free, no signup, no ads.
>
> Methodology is fully documented on-site — including the ugly parts: which printings
> are priced, why 1st Editions are excluded, how obviously-broken source prints get
> filtered, and why a card only shows a daily % between two confirmed prices. Every
> card links out to TCGplayer/PriceCharting/eBay so you can check me.
>
> Would love brutal feedback — especially from anyone who thinks a card is mispriced,
> because "why does card X show $Y" almost always has an interesting answer.

### r/PokemonTCG (Day 1 — bigger, more casual; lead with the fun)
> **Title:** One number for the whole Pokémon card market — I made a free "stock
> market index" of the 500 most valuable cards
>
> Body: shorter version of the above; open with the chart ("up 36% since Feb 2024"),
> close with the feedback ask. Check sub rules for self-promo day/flair first.

### Show HN (Day 3–7)
> **Title:** Show HN: A stock-market index for Pokémon cards ($0/mo on GitHub Pages)
>
> **First comment (post it yourself immediately):** Architecture: static site on
> GitHub Pages; one GitHub Action runs hourly, checks a daily price mirror's
> last-updated stamp, and does a real build once a day — S&P-style divisor math in
> ~300 lines of stdlib Python, committing two JSON files the frontend reads. No
> server, no database, no API keys, $0/month. The interesting engineering was data
> quality: the source occasionally prints a $500 market price for a $2,200 card, so
> there's a rolling-median glitch guard, and per-card daily moves only display
> between two guard-confirmed prints — the index level uses everything, but we
> refuse to show a made-up "today %". Happy to answer anything about the index math.
>
> (HN loves: the $0 architecture, the data-cleaning war stories, honest limitations.
> HN punishes: hype adjectives, dodging methodology questions.)

### X/Twitter thread (any time after Day 0; screenshots > links for reach)
1. "The S&P 500, but for Pokémon cards. I built it. It's free." + hero screenshot
2. Chart screenshot: "Feb 2024 → today: +35%. Now you can actually see it."
3. One juicy card story (e.g. the $2,146 Shadowless Charizard + why trackers disagree)
4. "How it works" (methodology screenshot) 5. link + "index updates daily ~4pm ET"

### TikTok / Shorts / Reels script (~30s)
Hook: "This is the stock market… for Pokémon cards." → scroll the top 10 ("a
Charizard worth more than my car") → the chart ("the whole market, one line — up
35% in two years") → "free, link in bio, updates every day at 4pm Eastern."

### Journalist / community-site pitch (PokéBeach, PokeGuardian, TCGplayer Infinite writers)
> Subject: A free daily "S&P 500" for Pokémon cards — data source for your market coverage
>
> Hi — I run poké500.com, a free price-weighted index of the 500 most valuable
> English Pokémon cards (real index math, daily updates, history to Feb 2024,
> methodology public). Feel free to cite the index number in market coverage —
> happy to provide data, charts, or a weekly movers summary for your pieces.

## Rules of engagement

- **Always disclose you built it.** "I made this" outperforms stealth posting and
  is required by most subs and HN culture anyway.
- **One venue at a time**; reply to every comment in the first 2 hours (algorithms
  reward early engagement, and methodology replies ARE the marketing).
- Frame as **data/transparency, never investment advice** — the footer already
  disclaims; keep that tone in comments.
- Reddit 9:1 rule: keep participating in these subs normally around the launch.

## Prepared answers (the criticisms WILL come)

- **"Price doesn't match PriceCharting/TCGplayer!"** → Different sources measure
  different markets (eBay solds vs TCGplayer sales); on TCGplayer there are 3
  separate Base Set Charizard products and the listings ≠ Market Price. Link
  the on-site methodology + the card's compare links. (Full worked example:
  Shadowless Charizard — our $2,146.38 IS TCGplayer's market price to the cent.)
- **"Why price-weighted, not market-cap?"** → No population/print-run data exists
  for raw cards; price-weighting is the honest option (same reason the Dow does it).
- **"Why no 1st Editions / graded / Japanese / sealed?"** → Defined universe:
  English raw singles that actually trade on the priced venue. 1st Ed trophy cards
  trade at auction, so their TCGplayer "market price" is broken ($250 vs $20k) —
  excluding them is accuracy, not laziness. Graded/sealed = different markets,
  future sub-indices maybe.
- **"Only ~50 cards moved today?"** → Correct — vintage prices are sticky; that IS
  the finding. Breadth shows it honestly.
- **"Card images copyright?"** → Nominative use, same as every price tracker;
  images come from TCGplayer's CDN; disclaimer in footer.

## Flywheel (week 2+, highest-leverage first)

1. **Daily "market close" auto-post** — a small GitHub Action off latest.json posting
   "S&Poké 500 closed at 1,355.70 (−0.19%) · top mover: X +28%" to X/Bluesky/a
   Discord webhook. (I can build this in an afternoon once you create the accounts —
   it's the single best retention mechanic.)
2. **Weekly movers recap** posted to r/PokeInvesting — becomes a ritual.
3. **Milestone posts** ("index crosses 1,400") — pre-write, post on trigger.
4. **Google Search Console** — submit the sitemap so "pokemon card market index"
   starts ranking (needs your Google account, 5 minutes).
5. **Get cited once** by PokéBeach/PokeGuardian and SEO + credibility compound.

## Measuring (GoatCounter)

Watch **referrers** per wave (reddit.com / news.ycombinator.com / t.co show up
automatically). Append `?utm_source=hn` etc. to links you post if you want
explicit campaign splits. Rough success bars: soft Reddit post 500–2k visits;
good Show HN 5–20k on day one; any single TikTok can 10x everything. Return
visits (people checking "the number" daily) are the real win metric — that's
what the flywheel exists for.
