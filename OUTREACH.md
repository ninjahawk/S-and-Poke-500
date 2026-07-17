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

## EXECUTION RUNBOOK (added 2026-07-17, DIB post live)

Owner's order of operations TODAY — outreach never displaces the DIB
comment window (first ~2h decide the post's reach):

1. **DIB comment replies** (~2h, rank lookups + candid caveats).
2. **GitHub repo topics** (30 sec, repo Settings → ⚙ next to About):
   `pokemon-tcg`, `pokemon-cards`, `pokemon`, `price-tracker`,
   `market-index`, `tcgplayer`, `github-pages`.
3. **Google Alerts** (2 min, google.com/alerts): `"pokemon card index"`,
   `"best pokemon card price tools"`, `"S&Poké 500" OR "poke500"`.
4. **Send the timing-insensitive asks** (drafts below): misprint +
   Delightful TCG roundup-inclusion emails, the three sidebar modmails,
   AlternativeTo listing.
5. **Conditional big swing**: if the DIB post is clearly working
   (≳500 upvotes or climbing fast tonight), email cllct AND DM
   @darrenrovell on X with the cards-vs-S&P chart while it's live
   social proof. Otherwise hold cllct for Monday after Show HN.
6. **Hold for Monday post-HN** (stronger proof): PokéBeach, CardChill,
   Nerdbeak, PokeGuardian. Product Hunt launch also waits (mid-week).

### Contact routes (found 2026-07-17)

| Target | Route |
|---|---|
| PokéBeach | pokebeach.com/contact (webmaster "Water Pokemon Master"); NOTE their filter: include the word "Pokemon" in the body. X: @pokebeach_wpm |
| cllct | cllct.com/contact-us; founder Darren Rovell (@darrenrovell on X — DM with the chart, he lives for collectibles-vs-stocks stats) |
| CardChill | cardchill.com/contact (address the market columnist Mike Pokemonski) |
| Nerdbeak | site footer/contact page (no address surfaced in research) |
| misprint | support@misprint.com or X @MisprintInc (YC startup; founder is ex-Goldman equity analyst — lead with the divisor math) |
| Delightful TCG | Shopify contact page (delightfultcg.com → contact) |
| PokeGuardian | site contact form (about page had none; check footer) |
| Subreddit mods | "Message the mods" on r/PokeInvesting, r/pokemoncardcollectors, r/Flipping |

### Today's paste-ready drafts

**misprint roundup ask** (to support@misprint.com, subject: "Addition
for your Pokémon price-tools comparison"):
> Hi — your "best place to track Pokémon card values" comparison is the
> best-organized guide out there. One category none of the entries
> cover: a whole-market index. I built poké500.com (link:
> https://poke500.com/) — a free S&P-500-style index of the 500 most
> valuable English raw singles: price-weighted, S&P-style divisor
> chaining, daily membership rebalancing, history to Feb 2024, open
> methodology, no signup. It answers "is the market up or down today?"
> rather than per-card lookup, so it complements rather than competes
> with the tools you list. If it fits the guide I'd be honored to be
> included — happy to provide screenshots or a blurb. I built it and
> run it solo; it's free and has no ads.

**Delightful TCG roundup ask** (contact form; same body as above with
the first line swapped to reference their "How to track Pokémon card
prices (2026)" guide).

**Sidebar modmail — r/PokeInvesting** (message the mods):
> Hi mods — I'm the builder of poké500.com (the S&Poké 500 index that
> was posted here this week and seemed to land well). If you think it's
> useful to the community, I'd be grateful for a mention in the wiki or
> sidebar resources — it's free, no signup, no ads, and the methodology
> is fully public. Either way, thanks for running the sub; happy to
> answer any questions about the data.

**Sidebar modmail — r/pokemoncardcollectors** (same shape, swap the
first parenthetical to "a free live index of the 500 most valuable
English cards — one number for whether the market's up or down, plus
per-card ranks/prices"; no "posted here" claim since we haven't yet).

**Sidebar modmail — r/Flipping** (their sidebar's Online Tools list):
> Hi mods — your sidebar's Online Tools list is a great resource. I
> built poké500.com, a free daily price index of the 500 most valuable
> English Pokémon singles (TCGplayer market data, no signup, no ads).
> Flippers use it to check whether the Pokémon market's running hot or
> cold at a glance. If you think it earns a spot in the tools list I'd
> be grateful — and totally understand if not.

**AlternativeTo blurb** (create listing, category price tracking):
> S&Poké 500 (poké500.com) — a free, live stock-market-style index of
> the 500 most valuable English Pokémon cards. One number for the whole
> card market, updated daily from TCGplayer market prices with real
> index mechanics (price-weighted, divisor chaining, daily membership).
> Interactive chart back to Feb 2024, sortable top-500 table, per-card
> price links. Free, no signup, no ads.

**awesome-tcg list entry** (github.com/TCG-Price-Lookup/awesome-tcg —
owner submits via web-UI edit/PR; remote sessions can't touch external
repos): add under the most fitting data/tools section:
`- [S&Poké 500](https://poke500.com/) — free daily price-weighted index
of the 500 most valuable English Pokémon singles (S&P-style divisor
chaining, open methodology, JSON data).`

**cllct / Rovell pitch** (email via contact-us; X DM = first two
sentences + the chart image):
> Subject: A daily "S&P 500 for Pokémon cards" — free data for your TCG
> coverage
>
> Hi — I built poké500.com, a free price-weighted index of the 500 most
> valuable English Pokémon cards (real index math: divisor chaining,
> daily membership, history to Feb 2024). The stat your readers will
> argue about: over the last 12 months the top-500 Pokémon cards
> returned +10.2% vs the S&P 500's +20.9% — but last April, while the
> S&P had round-tripped to flat, the cards were +13.5%. Cite the daily
> number any time; if a story needs a custom chart or stat (movers,
> breadth, the vs-S&P race), I'll build it free, credited or not. The
> data itself is open JSON. Nothing for sale — free site, no ads.

Monday drafts (PokéBeach/CardChill/Nerdbeak/PokeGuardian) use the Tier
1 press template above + one personalized first line each; refresh all
numbers from latest.json before sending.

### Kept out of today on purpose

- Product Hunt (stacks with Show HN, mid-next-week), Bulbapedia (needs
  press first), smpratte (earn the mention, don't pitch), Feedspot
  podcast tier (week 3+, only if earlier tiers convert).

## National press beat map (researched 2026-07-17)

The Pokémon-card market is an ACTIVE beat at national outlets right now
(boom + crime-wave + Logan Paul $16M Pikachu cycle, spring 2026). Every
piece found cites Circana spending stats or single-card auction
anecdotes — none cites a market-wide index. That's our opening: pitch
the daily benchmark as the missing number for the beat, using the Tier
1–2 press template. **Timing: fold into the Monday/week-2 press round
(post-HN proof), not before.** Named reporters, verified from
bylines/search:

| Outlet / reporter | Evidence on the beat | Route |
|---|---|---|
| **Bloomberg — Chris Almeida** | "Pokémon Card Boom Sparks a Crime Wave as Values Soar" + video (2026-04-24) | Bloomberg tips page / X |
| **CNN Business — Vanessa Yurkevich & Isaac Tellechea** | "Pokémon cards are igniting an international crime spree" (2026-04-04); widely syndicated to local TV sites | CNN tips; Yurkevich active on X |
| **CNBC (byline TBD — page bot-blocked; owner: check byline on phone)** | "Crypto bros, scalpers and Logan Paul…" (2026-05-22) + two video segments + a 2026-03-29 piece; CNBC is the most repeat-coverage outlet found | cnbc.com tips / reporter email pattern firstname.lastname@nbcuni.com once byline known |
| **CBS Boston** | "Pokémon cards as an investment?" consumer piece | Only if a Boston hook appears; low priority |
| **Moneywise** | Syndicated the Bloomberg crime angle | Contact form; long-tail SEO value |

Also found (context, not targets): Yahoo Finance ran a Reddit-sourced
"cards crush S&P 500" aggregation — the vs-S&P genre is proven
mainstream bait, which validates leading national pitches with the
cards-vs-S&P chart (hosted: poke500.com/cards-vs-sp500.png). Angle for
crime-beat reporters: "every theft story needs a 'values have risen X%'
line — here's a citable daily number instead of an anecdote."

## COLD-PITCH CAMPAIGN (launched 2026-07-17, owner call: all tiers at once)

Owner decision: don't wait for HN proof — pitch the whole beat now.
"All we need is one yes." Rules that make cold pitches convert (and
protect the Gmail): every email INDIVIDUALLY sent + personalized first
line (never BCC, never identical copy), ≤15/day, no attachments (links
only), one follow-up after 3–4 business days then stop forever, always
disclose "I built this", never "first/only index".

### Master pitch (press) — v1, stats as of 2026-07-16 close

Subject: `A daily "S&P 500" for Pokémon cards — free data for your
market coverage` (crime-beat variant: `A citable number for
Pokémon-card stories — free daily index`)

> Hi [name] — [PERSONAL LINE, see tracker].
>
> I run the S&Poké 500 (https://poke500.com/) — a free daily
> price-weighted index of the 500 most valuable English Pokémon cards,
> with real index mechanics: S&P-style divisor chaining, daily
> membership rebalancing, history back to Feb 2024, methodology fully
> public. Yesterday's close: 1,254.19.
>
> One stat readers argue about: over the last 12 months the top-500
> cards returned +10.2% vs the S&P 500's +20.9% — but in April, when
> stocks had round-tripped to flat, cards were up +13.5%. Chart:
> https://poke500.com/cards-vs-sp500.png
>
> Cite the daily number any time — no permission needed. If a story
> needs a custom chart or stat (weekly movers, market breadth, the
> vs-S&P race), I'll build it free, credited or not; the raw data is
> open JSON. Nothing for sale — free site, no ads, no signup. I built
> and run it solo.

### Campaign tracker (status: D=drafted, S=sent, R=replied, Y=yes)

| # | Target | Route | Personal line | Status |
|---|---|---|---|---|
| 1 | Rich Mueller, Sports Collectors Daily | editor@sportscollectorsdaily.com | "SCD's Pokémon coverage keeps crossing from hobby news into market territory — figured you could use a market-wide number to anchor those pieces." | S |
| 2 | Alts.co | hello@alts.co | "Benchmark horse-races are your genre — cards-vs-S&P finally has a real index on the cards side." | S |
| 3 | Chris Almeida, Bloomberg | calmeida@bloomberg.net BOUNCED 2026-07-17 (550) → use bloomberg.com/tips or X | "Your April crime-wave piece was the best reporting on this market all year — and every story on that beat needs a 'values are up X%' line with something real behind it." | S(bounced) |
| 4 | Vanessa Yurkevich, CNN Business | vanessa.yurkevich@cnn.com (PATTERN GUESS) | "Your April crime-spree piece nailed the stakes — the missing ingredient in every card-crime story is a citable 'how much have values actually risen' number." | S |
| 5 | Isaac Tellechea, CNN Business | isaac.tellechea@cnn.com (PATTERN GUESS) | same angle as #4, don't send both the same day — stagger | S |
| 6 | **Arjun Kharpal**, CNBC (senior tech correspondent, London — byline confirmed by owner 2026-07-17) | arjun.kharpal@nbcuni.com (PATTERN GUESS; verified fallbacks from byline: X @ArjunKharpal, LinkedIn /in/arjunkharpal) | "Your May piece on crypto money rotating into cards is the story my data keeps confirming — here's a daily number for the next one." | |
| 7 | PokéBeach | pokebeach.com/contact (BODY MUST CONTAIN "Pokemon") | "PokéBeach is where I check Pokemon TCG news daily — for the market/30th-anniversary beat, here's a benchmark number free to cite." | |
| 8 | PokeGuardian | news-tip form was BROKEN 2026-07-17 — retry in a few days or X DM | "Your daily news cadence is exactly where a daily market close belongs." | blocked |
| 9 | Mike Pokemonski, CardChill | cardchill.com/contact | "A recurring market column deserves a recurring benchmark — happy to build custom charts for any column, free, forever." | |
| 10 | Nerdbeak | site contact | "Your 'market is crashing, sort of' piece is the most data-honest take out there — my breadth/movers numbers are exactly that kind of material." | |
| 11 | cllct / Darren Rovell | cllct.com/contact-us + X DM @darrenrovell (chart attached to DM) | existing cllct draft above | |
| 12 | ONE37pm | site contact form | "Your collectibles coverage keeps asking 'is the boom real' — here's the daily number that answers it." | |
| 13 | Moneywise | moneywise.com/contact ("pitch a story" flow) | humanized story-pitch sent (angle: "cards beat the S&P in April, lag over 12mo — timing is the story") | S |
| 14 | CBS Boston (did cards-as-investment piece) | station tips form | "Your cards-as-investment piece asked the right question — here's the market-wide answer, updated daily." | |

Deliberately excluded: gaming press (Kotaku/TheGamer — no card-market
coverage found, wrong beat), Yahoo Finance (aggregator; they pick up
from Reddit/other coverage on their own), smpratte (never cold-pitch).

Follow-up template (one per target, day 3–4, then never again):
> Hi [name] — quick nudge on the note below. One thing I can offer
> beyond the data: [custom chart matched to their beat]. If it's not
> for you, no reply needed and I won't follow up again.

## Future accelerant (ROADMAP candidate, not now)

An **embeddable ticker widget** (one `<script>`/iframe line: "S&Poké
500: 1,254.19 −0.07%", links home) is the terminal form of "a tool
that's just there" — every embedding site becomes a permanent referrer.
Natural post-PWA roadmap item; the public JSON already makes it
possible for anyone motivated.
