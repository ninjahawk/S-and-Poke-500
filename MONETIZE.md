# Monetization plan (drafted 2026-07-16, owner-approved direction)

The index itself stays **free forever** — the freely checkable number IS the
marketing. Monetization is a multiplier on traffic, not a substitute: the
flywheel (LAUNCH.md) comes first. Sequence below is ordered by
effort-to-payoff at each stage of audience size.

## 1. Affiliate links — FIRST MOVE (works even at low traffic)

Every card modal already links out to TCGplayer and eBay ("compare" links).
Swap them for affiliate versions — zero UX change, aligned incentives (we
send TCGplayer buyers; friendlier than any data-usage argument), and
high-value singles are the best possible affiliate basket (a referred $1,400
Umbreon sale pays real money).

- **eBay Partner Network** (https://partnernetwork.ebay.com) — pays a % of
  referred sales. Owner signs up with the live site; payout via PayPal/bank.
- **TCGplayer affiliate program** — runs through Impact (impact.com);
  historically ~1%+ of sales. Owner applies with the site.
- **Owner steps**: create both accounts, get the tracking IDs/link formats.
- **Claude step (small, one pass)**: convert every compare link sitewide once
  IDs exist. Disclose affiliate links in the footer + about page (FTC).

Even modest traffic should cover all running costs (domain, Buttondown if we
outgrow free).

## 2. Newsletter + site sponsorship (once the list has a pulse)

A weekly email read by 500–1,000 Pokémon investors is valuable to: card
shops, grading services (PSA / CGC / TAG), collectibles insurance, breakers.
One tasteful "this week's issue is brought to you by…" line — the standard
niche-finance-newsletter model, applied to Pokémon. Later, a single sponsor
slot on the site. **No AdSense-style banner plaster** — the clean
Google-Finance look is the brand.

## 3. Premium tier (the real business — only after traction)

The layer under the free index, ~$3–5/mo:
- **Price-move alerts** ("email me when any top-100 card moves >10% in a
  week") — trivially computable from data we already build daily.
- **Watchlists.**
- **Portfolio tracker** — "enter your collection, see its value, did you
  beat the S&Poké 500?" The killer feature; collectors crave exactly this,
  and it's a natural extension of latest.json/history.json.

## 4. Longer shots

- License the index data/API to other hobby tools.
- Weekly market-recap YouTube short / TikTok (very memeable; ad revenue +
  funnel).
- Print-on-demand "S&Poké 500" merch for the r/PokeInvesting crowd.
- Eventual exit: niche sites with a real newsletter + organic traffic sell
  for meaningful multiples.

## Caveats (respect these when the money starts)

- The site footer says "independent, **non-commercial** fan project" — that
  wording is part of the trademark-comfort posture and MUST be updated the
  moment revenue flows (drop "non-commercial", keep the affiliation
  disclaimers; add affiliate disclosure).
- Commercial use makes the card **images** slightly more sensitive (the one
  real copyright surface — see CLAUDE.md legal posture). The images-off
  switch already exists; PriceCharting operates commercially with images,
  but keep this in mind if anything escalates.
- Don't resell raw TCGplayer/TCGCSV price data in a paid product — the
  *index* and derived analytics are our own work; raw price redistribution
  is the gray zone to avoid.
- Never paywall the index number itself.
