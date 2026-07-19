# r/ClaudeAI showcase post — runbook (drafted 2026-07-19)

Venue: **r/ClaudeAI** (~1M members). Goal stack, in order: clicks → site
visits → "professional-grade with Fable 5" proof. Newsletter converts on-site
(banner + dialog) — **no newsletter mention in post or first comment**, same
reasoning as the wave-2 decision in `REDDIT_POST.md`.

## Venue research (what the sub rewards / punishes)

- **Flair: "Built with Claude"** — showcase posts are expected to include
  (1) what you built, (2) how you built it, (3) screenshots or a demo, and
  (4) **at least one actual prompt you used**. The draft below satisfies all
  four; the prompt slot is marked for the owner to swap in a verbatim one.
- The sub is **skeptical and allergic to hype**. Its top threads are usage-limit
  complaints; its best-loved showcases are real products with real outcomes
  (a "did my taxes with Claude" post got picked up by Inc). Praise arrives
  only after candor: what broke, what it cost, what you'd do differently.
  → Our CNAME incident is an ASSET here, not a liability. Lead with it in
  the honesty section; it's the credibility signal that separates this from
  "Claude built my SaaS in an hour" slop posts.
- **Timing tailwind**: Fable 5 is new and "what can it actually do" is the
  sub's live question. A concrete, launched, verifiable answer rides that
  wave — same mechanic as VIRALITY.md §5 (we don't create the wave).
- Mechanism stack (VIRALITY.md) mapped to this sub: identity stakes =
  "vibe coding is slop" vs "it's production-grade now" (both tribes live
  there, both comment); falsifiable claim = the live site itself + $0/month;
  skin-in-the-game = "look up your childhood card" (devs have childhood
  cards too); screenshot-able = the Google-Finance-but-Charizards hero;
  candor = CNAME story; zero friction = free/no signup.

## Sequencing (recommendation)

Post **Sunday 2026-07-20, 8–11am ET** — weekend morning is strong for a
builder sub, and it keeps Monday clear for Show HN (`REDDIT_POST.md` wave-2
plan). One venue at a time still applies; if Show HN slips, r/ClaudeAI can
take Monday instead. Different audience than HN with only mild overlap, so
back-to-back days are acceptable; same-morning is not.

## ⚠️ Before posting (owner checklist)

1. Refresh all numbers from `docs/data/latest.json` (they drift daily; the
   ones below are the **2026-07-18 close**: index 1,259.40, +25.9% since
   Feb 2024, #500 = Reshiram ex at ~$219).
2. Swap the prompt block for a real prompt from your history if the drafted
   one isn't close to verbatim (flair rule).
3. Screenshot: the site hero (chart on MAX) — regenerate per REDDIT_POST.md
   §Assets if needed. Screenshot beats video on this sub (text-heavy readers).
4. Standing rules apply: never claim "first/only index" (PokéViews exists);
   disclose you built it; no newsletter plug.

## Voice rule (why this draft looks the way it does)

r/ClaudeAI instantly clocks and mocks AI-written showcase posts: bolded
section labels, tidy parallel structure, "here's the evidence" framing.
The post below is deliberately loose — first person, story order, no
headers, sentences of uneven length. When refreshing numbers or editing,
keep it that way; if a paragraph starts sounding like a landing page,
cut it.

## Title (pick one; A recommended — short and weird beats long and braggy)

**A:**
Charizard has a ticker now. Claude Code runs a live S&P-style index of
the 500 most valuable Pokémon cards — built entirely from my phone
(poké500.com)

**B:**
Claude Code built me the S&P 500, but for Pokémon cards. It's been
running itself for a week (poké500.com)

**C:**
asked Claude Code for "the S&P 500 but Pokémon cards." a week later it's
live, self-updating, and collectors are fact-checking it (poké500.com)

## Body (hero screenshot at top)

> I collect Pokémon cards and I always wanted one number for "is the
> market up or down today," the way you'd check the S&P. Couldn't find
> one I trusted, so I built it. Well — Claude built it. I supervised from
> my phone.
>
> The whole thing was done through Claude Code remote sessions (running
> Fable 5). I never opened an editor or a terminal once. I'd describe
> what I wanted, a session would go build it, open a PR, merge it. The
> repo has a CLAUDE.md that works like a handoff doc — every session
> reads it first, does its job, writes back what the next session needs
> to know. Sometimes I had two running on different problems at the same
> time. My actual contributions were screenshots, "yes do that," and the
> stuff an AI literally can't do, like buying the domain.
>
> It's live at poké500.com. 500 most valuable English raw cards,
> price-weighted with real divisor chaining like an actual index, 2.5
> years of daily history, updates itself every day around 4pm ET through
> a GitHub Action. GitHub Pages, no server, no database. Costs me $0 a
> month.
>
> The thing that actually sold me on this workflow was the data quality
> stuff I would never have caught myself. TCGplayer's market price for
> 1st Edition trophy cards is just broken — a Shadowless 1st Ed Charizard
> that's worth ~$20k shows $250 — and Claude noticed, explained why, and
> excluded them before I knew there was a problem. It also built a filter
> for days when the source prints an obviously wrong price, because
> apparently that happens. I posted the site to a collector sub last week
> and it did 18k views. Those people check card prices to the cent. The
> numbers held up.
>
> It was not hands-free though. One session decided the CNAME file was
> "redundant," deleted it, and knocked the whole domain offline. A later
> session figured out what happened, fixed it, and wrote a warning into
> CLAUDE.md so it never happens again — which is honestly the part that
> impressed me most. And the mobile layout broke twice, caught only
> because I use the site on my phone and sent screenshots. You are still
> the QA department.
>
> A prompt I actually used, since the flair asks for one:
> [OWNER: paste a real prompt from your history; stand-in below]
>
> > "movers list is clipping on my phone again, price and % pushed off
> > screen — screenshot attached. fix it and figure out why this keeps
> > happening on mobile so it stops"
>
> If you collected as a kid, go look up your card. #1 is not the card
> you think it is, and it takes about $219 just to crack the top 500.

## First comment (owner posts immediately — casual, not a spec sheet)

> since someone will ask how the automation works: a github action runs
> hourly but bails in seconds unless the price source actually updated,
> so the real build happens once a day. fetches prices, filters
> glitches, does the divisor math, commits two json files, and the
> static site just reads those. methodology is public on the site
> including the ugly parts, and every card links out to
> tcgplayer/pricecharting/ebay so you can check me.
>
> happy to answer anything — honestly the most interesting conversation
> is what Fable 5 handled completely on its own vs where it needed
> babysitting, ask away.

## Prepared answers (these WILL come)

- **"AI slop / did a human review this?"** → The output is externally
  checkable, which beats review: every price links to its sources, the
  methodology is public, the email pipeline has 34 unit tests, and the
  harshest reviewers already showed up — collectors on the launch post
  cross-checking card prices. Where it broke (CNAME, mobile CSS), I say so
  in the post.
- **"How much usage / what plan / what did it cost?"** → This sub's #1
  obsession. OWNER: fill in your real plan + rough session count honestly;
  a straight answer here earns more goodwill than anything else in the
  thread. Don't dodge it.
- **"Not the first Pokémon index"** → standing prepared answer
  (VIRALITY.md): "Yep — PokéViews does an equal-weighted top-100 with
  monthly rebalancing. I wanted something closer to how real indices work:
  500 cards, divisor continuity, daily membership, every assumption
  public."
- **"Why is card X $Y?"** → same engagement engine as wave 1: different
  trackers measure different markets; link the card's compare links.
- **"How do I follow it?"** → the only sanctioned newsletter mention, reply
  only if asked: "There's a weekly Friday recap email on the site (or just
  check the number — it updates daily ~4pm ET)."
- **"Can I see the code?"** → repo is public; link it. This is r/ClaudeAI's
  version of "pics or it didn't happen."

## Measuring

Scoreboard: https://poke500.goatcounter.com — reddit.com referrer.
Baselines: wave 1 did ~1.6% CTR (18k views → 293 visits). r/ClaudeAI is
lower purchase-intent for the site itself but far larger; watch whether
dev traffic bounces or scrubs the chart. Success bar: 500+ visits and a
front-page run on the sub. Log owner-reported metrics here, wave-1 style.
