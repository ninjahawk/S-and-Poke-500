# Earned-media & embed plan — become the number people cite (2026-07-17)

Goal (owner directive): embed poké500 as a tool that's "just there" —
cited by writers, on-screen in weekly market videos, listed in tool
roundups and sidebars — generating passive visits and newsletter
conversion with zero spend. Everything here is FREE; the currency is
our data, our charts, and (sparingly) a mention in the weekly email.

## The strategic read (from competitive research, 2026-07-17)

- **The "citable benchmark" lane is unclaimed.** PokéViews (PV100,
  equal-weight monthly) and TCGFish ("professional indices") exist as
  destination sites, but no search trace shows press citing either as
  *the* market number. The LEGO study became evergreen because
  journalists could cite one stat; nobody owns that for Pokémon yet.
- **We are not another price-lookup tool.** PriceCharting, TCGFish,
  Pokémon Wizard, PokeDATA, Collectr etc. compete on per-card lookup
  and portfolios. Our pitch is orthogonal: ONE market-wide number,
  daily, with real index mechanics and open methodology. Pitch it as
  infrastructure ("cite it, chart it, build on it"), never as a rival
  app — that keeps every tool-maker a potential citer, not a competitor.
- **Weekly market content creators need us most.** There are standing
  weekly formats ("Pokémon Market Monday", "Falling Friday" YouTube
  updates; Special Conditions, PokéDads podcasts) that must fill a
  "how's the market?" segment every single week. A free daily index +
  ready-made chart is a gift to their prep time. Recurring citation =
  the exact "just there" embedding we want.

## The barter menu (what we offer — all free to us)

1. **Free data, forever**: `latest.json` + `history.json` are public
   URLs on Pages — a no-key API. Anyone can overlay the index or quote
   the close. Offer it explicitly ("pull the number straight from the
   site, no key, no rate limit worth mentioning").
2. **Custom charts on request**: any window/comparison as a clean PNG,
   credited "chart: poké500.com" — we auto-generate these anyway.
3. **Weekly movers summary**: the newsletter's stats, offered as quote
   material (they get research done for them; attribution is the price).
4. **A one-line mention in the next weekly issue** ("Good reads this
   week: …") when someone covers us or their content is genuinely
   relevant. HARD LIMITS (retention directive): max one such line per
   issue, only genuinely useful links, never a trade obligation written
   down as a quota, never an ad block. If in doubt, offer data instead
   of the mention.
5. **An "As featured in" row on /about** once coverage exists —
   reciprocal links they'll appreciate.

Never offered: money, subscriber data (never — retention rule 5),
guaranteed editorial in our email, exclusivity.

## Target list, graded (fit /10 · likely free coverage · what to ask)

### Tier 1 — Pokémon TCG market press (pitch in week 2, after IIB + HN)

| Target | Fit | Ask + angle |
|---|---|---|
| **PokéBeach** (news tip line) | 9 | The 30th-anniversary/market-boom beat needs a benchmark; offer the daily number + charts for market pieces. Biggest Pokémon TCG news site. |
| **PokeGuardian** | 8.5 | Same pitch; daily news cadence = many chances to cite. |
| **CardChill — Mike Pokemonski** (named market columnist) | 8.5 | A market analyst with a recurring column is the single best "cites us weekly" candidate in press. Personal pitch: free data + custom charts for his columns. |
| **Nerdbeak** (wrote "market is crashing, sort of") | 8 | They already write nuanced market takes with data hunger; our breadth/movers stats are exactly their material. |
| **PokeInsider / pokemoninvesting.com** | 7 | Smaller market blogs; easy yeses, long-tail SEO links. |

### Tier 2 — collectibles & alt-asset media (pitch week 2–3)

| Target | Fit | Ask + angle |
|---|---|---|
| **cllct** | 8.5 | Constantly covering the TCG surge ("is it here to stay?"); pitch the vs-S&P horse-race stat + daily benchmark for their Pokémon stories. Mainstream-adjacent reach. |
| **Sports Collectors Daily / ONE37pm** | 6.5 | Occasional Pokémon coverage; include in the same email round, low effort. |
| **Alts.co / alt-asset newsletters** | 7 | Their readers eat benchmarks ("cards vs S&P" IS their genre). A newsletter citing a newsletter converts unusually well. |

### Tier 3 — weekly market YouTube/podcasts (pitch week 2–4, owner comfort permitting)

| Target | Fit | Ask + angle |
|---|---|---|
| **Weekly market-update channels** ("Pokémon Market Monday", "Falling Friday" formats) | 9 | Offer the index as a recurring 20-second segment: "the S&Poké 500 closed the week at X, up Y%" + our chart on-screen with credit. Recurring > one feature. |
| **Special Conditions / PokéDads podcasts** | 7 | Market-discussion segments; offer weekly movers as talking points. Feedspot's CCG-podcast list (35 shows) is the extended directory when scaling this tier. |
| **smpratte / The Trophy King** | 6 | The vintage-market authority; aspirational — don't cold-pitch first, earn a mention via coverage elsewhere (he's cited-by-everyone, pitches-from-no-one). |

### Tier 4 — tool roundups & SEO listicles (rolling; highest passive value per ask)

| Target | Fit | Ask |
|---|---|---|
| **misprint.com** "Best place to track Pokémon card values (tools compared)" | 8.5 | Ask to be added as the free "whole-market index" entry — a category no listed tool fills. |
| **Delightful TCG** "How to track Pokémon card prices (2026 guide)" | 8 | Same inclusion ask. |
| Any future "best Pokémon price tools" article (Google Alert: set one) | 8 | Same; these rank for years = permanent referral pipes. |

### Tier 5 — permanent listings, do once (this week, zero risk)

- **GitHub repo topics**: add `pokemon-tcg`, `pokemon-cards`,
  `price-tracker`, `market-index` topics to the repo (Settings → topics,
  owner or web UI) — GitHub topic pages are browsed and scraped by
  roundup writers. FREE and instant.
- **awesome-tcg list (TCG-Price-Lookup/awesome-tcg)**: open a PR adding
  poké500 under data/indices — we can do this from a session.
- **AlternativeTo**: create the free listing (category: price tracking).
- **Product Hunt**: free launch; slot AFTER Show HN so momentum stacks
  (it's also its own traffic wave).
- **Subreddit sidebars/wikis**: r/PokeInvesting wiki, r/pokemoncardcollectors,
  r/Flipping "Online Tools" list — polite modmail each (per VENUES.md).
- **Relevant Discords** (PKMNTCGDeals' server, collector Discords):
  drop in #resources channels where allowed, owner-vetted.
- **Bulbapedia/wikis**: LOW priority — fan wikis have strict external-
  link/notability norms; revisit only after press coverage exists.

## Paste-ready pitch templates

**Press (Tier 1–2):**
> Subject: A free daily "S&P 500" for Pokémon cards — data source for
> your market coverage
>
> Hi [name] — I run poké500.com, a free price-weighted index of the 500
> most valuable English Pokémon cards: real index math (S&P-style
> divisor chaining, daily membership), history to Feb 2024, methodology
> fully public. Feel free to cite the daily number in market pieces —
> and if a story needs a specific chart or stat (weekly movers, breadth,
> the cards-vs-S&P comparison), I'll make it for you, free, credited or
> not. The underlying data is open JSON if you'd rather pull it
> yourselves. No product to sell — the site is free, no signup, no ads.

**Creator (Tier 3):**
> Subject: free weekly market number + chart for your market updates
>
> Hi [name] — love the weekly market updates. I built poké500.com, a
> free live index of the top 500 English cards (like a stock index, one
> number, updated daily ~4pm ET). If it's useful as a recurring segment
> ("the index closed the week at X, up Y%"), use it and the charts
> on-screen freely — a verbal credit is plenty. Happy to send a clean
> weekly chart PNG + the top movers every Friday so it's zero prep.

**Roundup inclusion (Tier 4):**
> Subject: addition for your Pokémon price-tools guide
>
> Hi — your tools comparison is the best-organized one out there. One
> category none of the entries cover: a whole-market index. poké500.com
> is a free S&P-500-style index of the 500 most valuable English cards
> (daily, open methodology, no signup) — the "is the market up or down
> today?" number rather than per-card lookup. If it fits the guide,
> I'd be honored to be included; happy to provide screenshots/blurbs.

Template rules: always disclose "I built this"; NEVER "first/only
index" (VIRALITY.md); no hype adjectives; the offer is data, not money.

## Sequencing & measurement

1. **This week**: Tier 5 once-only listings (topics, awesome-list PR,
   AlternativeTo) — no dependencies, pure upside.
2. **Week 2 (after IIB Sunday + Show HN Monday)**: Tier 1 press round +
   Tier 4 roundup asks, with "as seen on HN/Reddit, N readers" proof.
   Product Hunt mid-week.
3. **Week 2–4**: Tier 2, then Tier 3 creators (recurring-segment offer).
4. Set a Google Alert for "pokemon card index" + "best pokemon card
   price tools" (owner's Google account — same blocked-on-owner list as
   Search Console).

Measure in GoatCounter referrers (each pitch that converts becomes a
standing referrer row) and "Featured in" grows on /about. Success =
recurring citations, not one-off spikes: one weekly YouTube segment or
one columnist habit beats any single article.

## Future accelerant (ROADMAP candidate, not now)

An **embeddable ticker widget** (one `<script>`/iframe line: "S&Poké
500: 1,254.19 −0.07%", links home) is the terminal form of "a tool
that's just there" — every embedding site becomes a permanent referrer.
Natural post-PWA roadmap item; the public JSON already makes it
possible for anyone motivated.
