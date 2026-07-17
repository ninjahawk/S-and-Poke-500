# Venue research v2 — every candidate sub, independently graded (2026-07-17)

**v2 upgrade (~19:00 UTC):** v1's grades relied on secondary snapshots
(gummysearch/thehiveindex/ban reports). v2 adds **primary rule text** —
the actual current sidebar/wiki rules of 18 subreddits, read 2026-07-17
via a live Reddit mirror (reddit.com itself is unreachable from the dev
env; safereddit.com serves real sidebar text). Rows marked ✅ are graded
on those verbatim rules; unmarked rows remain secondary-source snapshots.
Grades are mine (Claude's), independently re-derived. The owner's
60-second sidebar check before posting still stands — mirrors lag and
mods have discretion everywhere.

## Grading rubric (weights, unchanged from v1)

| Factor | Weight | What it measures |
|---|---|---|
| Wow-fit | 30% | Would THIS audience say "wooow that's cool" at THIS content? |
| Reach × activity | 25% | Members × how alive the sub actually is |
| Rule survival | 20% | Probability the post stays up (verified rules > hope) |
| Conversion | 15% | Visits that become return visitors / newsletter subs |
| Asset readiness | 10% | Do we already have the right post material? |

## THE VERDICT — the "absolute most engaged wow-eyes" question, settled

**r/InternetIsBeautiful, confirmed — and now on primary evidence.** The
decisive v2 finding is negative space: **every other multi-million
generalist "wow" sub verifiably bans us.** Verbatim, read today:

- r/Damnthatsinteresting (20.5M): "Spam includes, but is not limited to,
  self-promo" (R5) + "No screenshots/memes/infographics" (R4).
- r/interestingasfuck (16.6M): "No self-promotion, bots or any kind of
  spam" — plus new-account posts need mod approval.
- r/nostalgia (1.6M): "No posts to webstores, blogs or websites."
- r/mildlyinteresting (25.3M): photo-only OC, no links (unverified this
  pass, well-documented).

IIB is structurally the ONLY sub above ~5M where a self-made free website
is *the sanctioned content type* — its rule list reads like our spec
sheet (single-purpose site ✓, free ✓, no signup needed ✓, no store ✓,
not a webgame ✓, not an aggregator ✓). One shot per domain, ever;
Sunday-morning plan stands. Full verified-rules notes below.

## The matrix (weighted score /10; ✅ = primary rule text read 2026-07-17)

| Venue | Members | Score | Verdict |
|---|---|---|---|
| **r/InternetIsBeautiful** ✅ | **16.6M** | **9.0 ↑** | **THE pick, now rules-verified — see risk list before posting** |
| r/dataisbeautiful ✅ | 21.8M | 8.4 | Loaded & going today (chart asset built); rules re-verified ✓ |
| r/PokeInvesting (weekly ritual) | 318k | 8.3 | Done for launch; Friday movers ritual = permanent channel |
| **r/pokemoncardcollectors** ✅ | 129k | **8.0 NEW** | Bullseye: "Anything TCG welcome… value/pricing posts encouraged" — friendliest rules of any card sub |
| **r/PokemonCardValue** ✅* | 143k | **7.5 NEW** | The sub IS "what's my card worth" (+48%/yr). *Sidebar clean; rules live in a pinned post — owner must read it first |
| r/theydidthemath ✅ | 2.4M | 7.0 NEW | `[Self]` flair = "You did the math and want to share it!" — sanctioned lane for an unreasonable-effort math post |
| r/webdev (Showoff Saturday) ✅ | 3.3M | 7.0 ↑ | Saturday-only, verified verbatim; dev framing ($0 stack) |
| **r/pokemon (OC path)** ✅ | 4.9M | 6.9 ↑ | Upgraded from 5.4*: full rules read. Link posts banned, but OC post + ONE self-promo top-level comment is explicitly legal — see mechanics below |
| r/SideProject ✅ | 780k | 6.7 | "Sharing what you built is the point of the sub" (verified); low urgency |
| r/datasets ✅ | 221k | 5.9 NEW | Self-promo allowed WITH disclosure; publish the index as a dataset |
| r/IMadeThis ✅ | 36k | 5.8 | Welcome by design, tiny; +101%/yr; filler |
| r/Flipping ✅ | 498k | 5.4 NEW | Sunday self-promo thread only (postable all week). Bonus play: their sidebar curates an "Online Tools" list with price trackers — modmail a pitch for a free permanent link |
| r/coolguides ✅ | 6.1M | 5.0 NEW | Image-only, no links, "infographics will be removed" — a ranked-table image w/ URL watermark is a judgment-call post with ~zero conversion; skip-tier |
| r/AlphaAndBetaUsers / r/shamelessplug / r/EntrepreneurRideAlong | small | ~4 | Promo-welcome but junk traffic; only as filler |
| r/coolgithubprojects, r/opensource, r/Python | small–mid | ~4 | Code isn't the hook; slow-week filler |
| r/pkmntcg ✅ | 139k | 3.5 | Gameplay/deck-building sub — wrong content type |
| r/wallstreetbets | 10M+ | 3.5 | Promo-hostile, brand mismatch; skip |
| r/IsMyPokemonCardFake ✅ | 111k | 3.0 | Authentication-only focus (+76%/yr though); wrong fit |
| r/sportscards ✅ | 122k | 3.0 | Pokémon off-topic; +58%/yr — files under future "sports-card 500" |
| r/baseballcards & sports-card subs | ~100k+ | 3.0 | Same as above |
| r/nostalgia ✅ | 1.6M | 2.0 ↓ | RULE-FATAL for us: "No posts to webstores, blogs or websites" |
| r/pkmntcgcollections | 12.7k | 2.0 | Tiny + wrong content type (collection photos) |
| r/pokemontrades ✅ | 625k | 1.0 | Strict trading-transactions sub; no value/promo content |
| r/Damnthatsinteresting ✅ | 20.5M | 0 ↓ | RULE-FATAL: self-promo = spam (R5), no infographics (R4) |
| r/interestingasfuck ✅ | 16.6M | 0 | RULE-FATAL: "No self-promotion, bots or any kind of spam" |
| r/PKMNTCGDeals ✅ | 141k | 0 NEW | RULE-FATAL: "Self-promotions are not allowed" + sealed-products-only |
| r/PokemonTCG | 1.4M | 0 | DEAD END (owner rules check 2026-07-17, see REDDIT_POST.md) |

## r/InternetIsBeautiful — verified rules read-through (the one-shot checklist)

We pass every content rule **by construction**: single-purpose site,
free, interactive, no store, no webgame, no article/video, no download.
Three verified rules need active care:

1. **90/10 self-promo rule (verified verbatim):** "If almost all your
   activity on Reddit is advertising something you made, you will not be
   allowed to post here." Owner's account must show normal non-promo
   activity — wave-1/wave-2 comment replies help but ALSO comment on
   things that aren't ours before Sunday.
2. **AI rule (new since v1, verified):** submissions are banned "if
   their primary content is produced by AI, or if AI is used to drive
   functionality." We pass — the site's content is real market data and
   nothing in the product runs on AI. If asked in comments whether AI
   helped build it, answer honestly; the rule governs what the site *is*,
   not the dev tooling. Do not volunteer a debate in the post itself.
3. **Personal-info rule (verified):** sites "that simply serve as
   waitlists or newsletter sign ups" are banned. We're fine — the site is
   fully usable with zero signup — but the subscribe promo must never
   become a gate or dominant first-visit experience before Sunday.
4. **Hug-of-death flair exists** — GitHub Pages + CDN images will hold;
   nothing to do.
5. Domain can be submitted ONCE ever; no resubmission. Sunday morning
   slot per the calendar; title already drafted (v1, unchanged):

> A free, live stock-market-style index of the 500 most valuable Pokémon
> cards — one number for the whole card market, updated daily

## r/pokemon — the legal OC path (4.9M, biggest untapped reach)

Rule 11 verbatim: links to personal sites are banned as posts, BUT "OC
submitters may include one self-promotional top-level comment or mention
… to accompany their original content," and may reply with links when
asked. So the shape is: post genuine OC — an original data-story (e.g.
"I tracked the 500 most valuable Pokémon cards every day for 2.5 years —
here's what happened," original chart image or 50+ word discussion
post), keep ALL links/URLs out of the title and body, then immediately
post ONE top-level comment with the site link. Tripwires: "no screenshots
or merchandise" (use an original-render chart, not a site screenshot —
mod-discretion risk), no memes outside Mon/Tue, no art on weekends,
title guidelines. Survival ~mid: worth doing AFTER IIB and only with the
owner re-reading the sidebar. Different sub ⇒ the IIB one-domain rule is
not affected.

## r/theydidthemath — the sanctioned nerd-flex lane (2.4M)

Verified: `[Self]` = "You did the math and want to share it!" and
`[Off-Site]` exists for external links. The McBroken mechanic (comically
unreasonable rigor applied to something silly) is this sub's native
dialect. Post shape: "[Self] I applied the S&P 500's actual divisor-
chaining methodology to Pokémon cards, daily, for 2.5 years" — walk the
math (divisor, forward-fill, glitch guard), end with the live site.
Comment rules demand civility + cited sources; we cite everything by
design. Needs one new asset: the written-up math walk (half-session).

## New card-sub intel (the conversion plays)

- **r/pokemoncardcollectors (129k)** — sidebar literally: "Anything
  Pokemon TCG/Collectibles is welcome here!… Value/Pricing Posts: All
  questions are welcome and members are encouraged to assist." A free
  value-lookup tool is on-mission. Use the wave-2 casual template
  (REDDIT_POST.md) with fresh numbers. Highest rules-safety of any card
  sub; natural newsletter converts.
- **r/PokemonCardValue (143k, +48%/yr)** — the entire sub is "what's my
  card worth?" posts, i.e. our exact use case, growing fast. Rules are
  NOT in the sidebar ("PLEASE READ RULES PRIOR TO POSTING" pinned post,
  unreadable from here) — owner reads the pin first; if tools/promo are
  banned, the fallback is answering value questions with the site as a
  cited source (genuinely helpful, no post needed).
- **r/IsMyPokemonCardFake sidebar** maps the whole card-sub ecosystem —
  it's where these subs cross-recommend each other. Getting poké500
  into sidebars/wikis as a resource (modmail ask, like r/Flipping's
  "Online Tools" list) is the permanent-backlink long game: one polite
  modmail each to r/pokemoncardcollectors + r/Flipping mods.

## The calendar (one venue per day, per LAUNCH.md rules)

| When | Venue | Asset |
|---|---|---|
| **Fri (today)** | r/dataisbeautiful + r/PokeInvesting edit & replies | cards-vs-S&P chart (built) |
| **Sat** | r/webdev Showoff Saturday | site + $0-stack framing (LAUNCH.md HN comment is the template) |
| **Sun morning** | **r/InternetIsBeautiful — the big one** | the site itself (run the risk checklist above) |
| **Mon 9–11am ET** | Show HN | LAUNCH.md draft (update vs-S&P numbers first) |
| **Tue–Wed** | r/pokemoncardcollectors | wave-2 casual template, fresh numbers |
| **Fri 7/24** | r/PokeInvesting weekly movers ritual begins | weekly movers + chart |
| Week 2 | r/PokemonCardValue (after owner reads pinned rules) | casual template |
| Week 2 | r/theydidthemath `[Self]` | needs the math-walk write-up |
| Backlog | r/pokemon OC path, r/SideProject, r/datasets, Flipping Sunday thread, sidebar-listing modmails | per notes above |

Weekend timing for IIB is deliberate: browse-for-fun traffic peaks, and
Sunday keeps Saturday for the flair-gated r/webdev slot. If the owner
only has energy for ONE more post ever, it's still the IIB one — and
that conclusion is now backed by the verified rule text of every rival
mega-sub, not just vibes.

## Method & sources (v2)

Member counts/growth: gummysearch.com per-sub pages (snapshot ~2026-07).
Rule text: safereddit.com (Redlib mirror) sidebar/wiki captures,
2026-07-17 — r/pokemon full rules wiki included. Self-promo landscape
cross-checks: thehiveindex.com, redship.io, soar.sh subreddit databases.
reddit.com and web.archive.org are both unreachable from the dev env;
if a mirror dies, redlib instances rotate (catsarch/perennialte were 403
today; safereddit worked). All grades assume the owner's pre-post
sidebar check as the final gate.
