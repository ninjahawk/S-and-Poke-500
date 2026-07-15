# S&Poké 500 — session handoff (2026-07-15, price-glitch guard)

**Read this with `CLAUDE.md`.** This documents an in-progress data-accuracy
effort that is **not finished** and needs a decision + one regeneration run.

## TL;DR for the next session

- The **live site is fine and untouched** by this work. `docs/data/*.json` were
  reverted to the committed state (index **1082.17**, the OLD-methodology data),
  so the live site still shows the pre-existing glitchy movers (e.g. a fake
  "Charizard ex +240% today"). Nothing broken was pushed.
- **New, verified code is committed**: a price **glitch guard** in
  `scripts/tcg_common.py` (`guard_prices`, rolling-median), wired into
  `scripts/backfill_history.py` and `scripts/build_index.py`. It is unit-tested
  against the real failing cards. It is **not yet "activated"** — the data has
  NOT been regenerated with it (that needs one ~8-min backfill run).
- **One product decision is open** (owner deferred it to this session): how to
  present the daily **Top Movers / "today %"**, because TCGplayer's thin-vintage
  data cannot support reliable day-level moves. See "Open decision" below.

## What was done this session (all shipped to `main`, live)

1. **Modal image layout-shift fix** (`docs/styles.css`) — commit `0fecb02`.
   Reserved the card image's final height so the modal no longer jumps on load.
2. **Chart x-axis year labels** (`docs/app.js`) — commit `18d0e37`. 5Y/1Y now
   show `Feb '24` etc. instead of ambiguous `Feb 8`.
3. **Removed the "Market mood" overview row** (`index.html`, `app.js`,
   `styles.css`) — commit `8ebe05c`. Owner called it out; it's gone from live.

## The data-accuracy investigation (the hard part)

**Trigger:** owner asked to verify all math/dates/prices, then "make sure the
data accurately reflects real prices, both now and past."

**Findings (all verified against source):**
- Index math is exact (`sum(prices)=totalValue`, `totalValue/divisor=index`,
  change/%/breadth all consistent). Current prices match TCGplayer to the cent.
- **The committed history was a "Frankenstein":** 2024-02-08 → 2026-07-14 was
  built on the OLD methodology (36 bogus cards, mixed printings, 1st-Ed), while
  only the 2026-07-15 point used the corrected rules. Re-running the backfill
  makes all 129 points consistent. **This part is a clear, safe improvement.**
- **The "movers" are TCGplayer source glitches, not our bug.** TCGplayer's
  *market* price regularly prints wild values for thin vintage cards:
  - Charizard ex (FRLG) `84199`: market **$500 for 3+ months** while its
    cheapest listing was **$1,699.99** (impossible — market below low). Snapped
    to $1,699.99 on 07-15 → fake +240%.
  - Psyduck: `$9.36 → $490.24` = fake **+5,137%** (a cheap printing got picked).
  - Lugia `86905`: stable **$2,225**, glitch-*dipped* to $500 for 2 weeks, then
    recovered → a naive last-value guard reported the recovery as **+345%**.

**The guard we built (`tc.guard_prices`, in `tcg_common.py`):**
- Rolling-median filter. Each day's price is compared to the **median of the
  card's last `_GLITCH_WINDOW=5` prints**. If it's within `GLITCH_FACTOR=2.0`
  (0.5x–2x) of that median it's trusted; otherwise it's an outlier and the card
  **holds the median** for that day. Every raw print still enters the window, so
  a level that genuinely persists eventually dominates the median and is
  accepted. Median is robust to 1–2 point spikes AND dips (last-value compare is
  not — a dip poisons the baseline).
- State is a per-card window `{pid: [recent prices]}`. The backfill maintains it
  across all 129 points; the daily `build_index` persists it per constituent as
  a new `priceWindow` field in `latest.json` and continues it.
- **Unit-verified** on the exact real trajectories (do not re-derive; trust
  these): Lugia stays flat $2,225 (dip ignored, no fake mover); Charizard holds
  $500 (blip held); Golbat's 2-day $250 spike ignored; a genuine sustained
  $100→$300 re-rating IS accepted once it dominates the window; modest real
  moves pass through untouched.

**Why it's still not "done" — the residual problem (this is the open decision):**
The guard successfully kills the absurd glitches, BUT a median filter **lags on
genuine re-ratings and then releases them in one jump**, surfacing a real move
weeks late on the wrong day. Real examples from the source (raw → guarded eff):
- Shuckle `89189`: genuinely climbed `$24→$63→$69→$249.99` over June; guard held
  ~$24 then released to $249.99 on 07-15 → shows a fake "**+262% today**".
- Magikarp `87022`: really went `$220→$699.99` on 06-04 and held 8 weeks; guard
  surfaced it weeks late.
- Pikachu `88075`: source data is **genuinely broken** — oscillates
  `$5 ↔ $242 ↔ $800` week to week. No filter can make this a meaningful daily #.

**Conclusion reached (and the owner agreed the reasoning):** the *index level*
is now clean and honest with the guard; the *daily Top-Movers list* is
fundamentally unreliable because TCGplayer's thin-card data doesn't support
day-precision moves. More filter-tuning just relocates the noise.

## Open decision (owner deferred to next/Fable session)

How to present the movers / daily change. Options presented (owner did not pick;
they switched sessions for deeper reasoning):
1. **Cap displayed movers to a plausible range** (hide single-day moves beyond
   ~50% from the Top-Movers panel + breadth; index stays fully honest). Simple,
   display-only, no methodology change. Recommended as lowest-risk.
2. **Drop the daily Top-Movers panel + "today %" entirely**; present the S&Poké
   500 as the weekly index the data actually supports (level + chart + breadth).
   Most defensible, least theater.
3. **Keep movers as-is (guarded)** — faithful, but launch screenshots may still
   show big odd movers (late-surfacing real re-ratings like Shuckle +262%).

My recommendation if forced: **Option 1** for launch (keeps the feature,
removes the embarrassing numbers, index stays honest), and gate it on a
per-card "was this trusted on both compared days?" flag rather than a raw %
cap if time allows (cleaner than a blunt cap). Whatever is chosen, it's a
**display-layer change in `build_index.py`/`app.js`**, not a re-tune of the
guard.

## Exact steps to finish (once the movers policy is decided)

1. (Optional) implement the chosen movers-display policy in `build_index.py`
   (and/or `app.js`).
2. Regenerate the data with the guard — **one ~8-min run**:
   ```
   pip install py7zr
   python3 scripts/backfill_history.py     # rebuilds history.json + latest.json (guarded), ~8 min
   python3 scripts/build_index.py          # adds transparency fields + guards live snapshot
   ```
   The backfill re-downloads ~127 archive files; that's the slow part. Verify
   afterward: `sum(prices)=totalValue`, `totalValue/divisor=index`, and no
   absurd (>~50%) movers survive the chosen policy.
3. Commit `docs/data/{latest,history}.json` and push to `main` (Pages serves
   from `main`). Guarded index landed around **~1,287** in testing (vs 1,082
   old) — expect the public number to change materially; that's the corrected,
   consistent series (still rebased to 1,000 at 2024-02-08).

## Notes / gotchas learned this session

- **Do NOT ship a half-finished backfill.** A killed backfill leaves
  `docs/data/*.json` partially written and unshippable — always `git checkout --
  docs/data/*.json` to restore the live data if a run is interrupted.
- The backfill's sampled dates are a weekly grid from 2024-02-08 plus the last
  two consecutive days (07-14, 07-15). A glitch that persists across those last
  two days was what fooled the earlier (non-median) guard.
- `GLITCH_FACTOR=2.0` / `_GLITCH_WINDOW=5` are the current tunables in
  `tcg_common.py`. They were chosen against the real data; changing them needs
  re-validation (the fast way is the tail-replay below, not a full backfill).
- **Fast validation without an 8-min run:** replay just the recent tail through
  `tc.guard_prices` (fetch ~11 weekly-grid archive days ending 07-15, run raw vs
  guarded, compare the last-day movers). This is how the guard was validated
  this session — see the approach in the session transcript; ~1–2 min.

## Marketing / launch plan (delivered earlier this session, for reference)

Owner wants max hype. Plan given: Phase 0 polish (DNS + Enforce HTTPS still on
owner's to-do per CLAUDE.md; land a clean daily number). Phase 1 community-first
(Reddit r/PokemonTCG/r/PokeInvesting, Discord — lead with the free tool +
methodology transparency). Phase 2 broad (Show HN "Google Finance for Pokémon
cards", X card community, TikTok/Shorts "I built a stock market for Pokémon
cards"). Phase 3 flywheel: a daily "market close" auto-poster (another small
GitHub Action off the JSON) is the highest-leverage growth move; weekly movers
recap; pitch PokéBeach/PokeGuardian as a citable data source. Guardrails: frame
as data/transparency not "buy now"; keep the not-affiliated/not-advice footer.
**Launch should wait for a clean daily number** (i.e. after the movers decision
+ regeneration above).
