# S&Poké 500 — price-glitch guard: RESOLVED (2026-07-15, late session)

The handoff that used to live in this file is **complete**. Kept as a short
record; `CLAUDE.md` has the current project state.

## What was decided and shipped

- **Movers decision (was the open item):** Option 1 in its cleaner form — a
  card's daily change is computed **only between two guard-confirmed prints**
  (`trusted` on both compared days). Held/carried/just-released endpoints get
  `changePct: null`; the movers panel, breadth, table, and modal all inherit
  the rule automatically. No blunt % cap; the index level stays fully honest.
- **Extra hole found & fixed while activating** (missed by the prior session):
  guard windows were persisted only for the 500 constituents, so the daily
  builder trusted any print from a card *below* the cutoff — a one-day glitch
  spike (the Psyduck $9.36→$490.24 case) would have entered the basket at the
  fake price. Now a `guardWindows` watch zone (ranks 501–1000 by effective
  price, ~500 entries, ~35 KB) is persisted in `latest.json`, seeded by the
  backfill and continued by the daily build.
- **Frontend fix the gate exposed:** `changePct == null` used to render as a
  "New" badge / "New entry" — correct when null only meant new entrants, wrong
  once gating made null common. Now `isNew` gets the badge; gated cards show
  "—" with a tooltip, and the modal says "no confirmed daily change".
- **Data regenerated with the guard** (full backfill + daily build, verified):
  129 weekly points 2024-02-08 (=1,000) → 2026-07-15, index **1,355.70**
  (−0.19% 1D), divisor 180.3037. All invariants pass (`sum(prices)==totalValue`,
  `totalValue/divisor==index`, breadth consistent, no >10% weekly index jumps,
  worst surviving mover +28%). Spot-checked the known problem cards: Charizard
  ex 84199 held at $500 (snap gated), Lugia 86905 flat $2,225, Shuckle 89189 at
  real $249.99 with the release-day jump gated, Pikachu 88075 gated.

## Resolution (2026-07-16 ~00:00 UTC)

Merged to `main` (fast-forward push, `4676db7`) under the owner's blanket
delegation ("keep doing it until it's 100% correct"); Pages deployed it and the
edge was verified (index 1,355.70, invariants hold, guardWindows present).
Independently, the owner completed all three manual launch steps (Pages folder
→ `/docs`, registrar DNS, Enforce HTTPS) — **the site is fully live at
https://xn--pok500-dva.com/**. Current state lives in `CLAUDE.md`.
