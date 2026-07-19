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

## Title (pick one; A recommended)

**A (workflow wow + traction + candor hook):**
I built a live "S&P 500 for Pokémon cards" with Claude Code — entirely from
my phone, never opened an editor. It launched last week, its first Reddit
post hit 18k views, and it runs itself for $0/month (poké500.com)

**B (Fable 5 + failure hook):**
Claude Code on Fable 5 built, launched, and now runs my Pokémon card market
index — pipeline, site, daily automation, even the launch strategy. It also
took the site down once. Honest report (poké500.com)

## Body (hero screenshot at top)

> **What it is:** the S&Poké 500 — a live, price-weighted index of the 500
> most valuable English raw Pokémon cards, computed like a real market index
> (S&P-style divisor chaining, daily membership rebalancing) from TCGplayer
> market prices, with daily history back to Feb 2024. It looks like Google
> Finance, except the tickers are Charizards. Free, no signup, no ads:
> poké500.com. It launched Wednesday and real collectors are using it — the
> launch post on a collector sub did 18k views and 43 shares on day one.
>
> **The part that belongs on this sub:** I built and run this entirely from
> my phone with Claude Code (on Fable 5), using remote sessions. I never
> opened an editor. Sessions did the data engineering (reconstructing 2.5
> years of daily index history from a price archive), the frontend, the
> GitHub Action that updates it every day, the unit tests, the launch
> research, and the copy for the launch posts — including drafting replies
> when comments came in faster than I could think. The repo's CLAUDE.md is
> the institutional memory: sessions sometimes run in parallel, and each one
> reads the current state, does its job, and writes back what the next one
> needs to know. My actual job has mostly been screenshots, approvals, and
> the handful of things an agent can't do (buy the domain, click "enable
> Pages").
>
> **Professional-grade is a real bar, so evidence:** the index survived
> contact with the pickiest audience there is — collectors who know their
> card prices to the cent. That's because the sessions didn't just wire up
> an API: they caught that TCGplayer's "market price" is broken for 1st
> Edition trophy cards (a ~$20k Shadowless 1st Ed Charizard shows $250) and
> excluded them; built a rolling-median glitch guard because the source
> occasionally prints a $500 price for a $2,200 card; and figured out that
> without forward-filling thin trading days, the index fakes a crash every
> quiet week. That's the unglamorous data-quality work that separates a demo
> from a product, and the model did it — and explained why — before I knew
> to ask.
>
> **What went wrong, because nothing about this was hands-free:** one
> session deleted a "redundant" CNAME file and deregistered the domain from
> GitHub's edge — site down until a later session diagnosed it. The fix and
> the lesson are now in CLAUDE.md, and no session has repeated it. Mobile
> CSS bugs shipped twice and were only caught because I use the site on my
> phone and sent screenshots. The workflow works, but it works because
> mistakes get written down where the next session will read them.
>
> **A prompt I actually used** (flair rule — this one produced the mobile
> fix): [OWNER: paste a verbatim prompt from your history here; drafted
> stand-in below]
>
> > "movers list is clipping on my phone again, price and % pushed off
> > screen — screenshot attached. fix it and figure out why this keeps
> > happening on mobile so it stops"
>
> **Stack:** GitHub Pages + one GitHub Action, ~stdlib Python, vanilla JS,
> no server, no database, no API keys. $0/month.
>
> If you collected as a kid: **look up your childhood card and tell me its
> rank.** Card #500 costs about $219 right now, and #1 isn't the card you
> think it is.

## First comment (owner posts immediately — workflow deep-dive, Show-HN style)

> How the automation actually works, for anyone who wants details: a GitHub
> Action runs hourly but exits in seconds unless the upstream price mirror's
> daily stamp changed, so the real build happens once a day (~4:23pm ET) —
> fetches prices, applies the glitch guard, continues the divisor chain,
> commits two JSON files the static frontend reads. The index math is
> S&P-style divisor chaining so the level stays continuous as cards enter
> and leave the top 500. All of it is open — methodology on the site,
> including the ugly parts — and every card links to
> TCGplayer/PriceCharting/eBay so you can check the prices yourself.
>
> On the Claude Code side: remote sessions from the phone app, CLAUDE.md as
> shared state between sessions, PRs opened and merged by the sessions
> themselves. Happy to answer anything about the workflow, the index math,
> or what Fable 5 handled well vs where it needed adult supervision.

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
