# Branch ledger (as of 2026-07-16)

Remote sessions can't delete branches or push tags (only their own designated
branch), so this file is the durable record. **Owner: the "safe to delete"
branches below can be removed in the GitHub UI** (repo → Branches → trash
icon) — everything in them is either merged into `main` or preserved in
`archive/`.

## Active

| Branch | Status |
| --- | --- |
| `main` | THE branch. Site serves from it (`/docs`), Actions run from it. |
| `claude/newsletter-creation-gbl2t4` | 2026-07-16 session (newsletter + consolidation). Merged via PRs #13–16; safe to delete once its final PR lands. |

## Open — parallel sessions from 2026-07-16, check before touching

| Branch | Final SHA | Contents |
| --- | --- | --- |
| `claude/reddit-post-soft-launch-2lo8tx` | `1a20a42` | Soft-launch session: REDDIT_POST.md + VIRALITY.md (both now copied to `main` — the branch copies are snapshots), demo video mp4 (marked "remove before merge"), LAUNCH.md competitor edits (folded into main). Nothing else to merge; safe to delete once its session is done. |
| `claude/reddit-post-metrics-du0hya` | `0b2c85b` | Metrics/day-0 session: status records (folded into main's CLAUDE.md), poke500.com alias copy edits, AND `send_daily_email.py` — a DAILY Buttondown pipeline **superseded by the merged weekly `send_newsletter.py`** (owner chose weekly). Do NOT merge this branch; if any copy edits are wanted, cherry-pick them. |

## Safe to delete (fully merged into main)

| Branch | Final SHA | What it was |
| --- | --- | --- |
| `claude/pokemon-price-tracker-7qiczh` | `1e291ef` | Initial site + tracker build. |
| `claude/spoke-500-tracker-l6t00v` | `98df48c` | Early index work. |
| `claude/card-image-layout-shift-ttuvvu` | `54b17a5` | Card-image layout fix. |
| `claude/pricing-accuracy-sources-wafpwg` | `f5a0f1e` | Pricing audit; staff/JP-promo/staleness fixes. |
| `claude/continue-6bvev4` | `2ea1c24` | Glitch guard + movers gate. |
| `claude/continue-previous-gwpi5f` | `a88a926` | Daily densify, image switch, about page. |

## Safe to delete (never merged, content preserved)

| Branch | Final SHA | What it was |
| --- | --- | --- |
| `claude/launch-readiness-l0o8yt` | `5193529` | Alt logo + hourly change-detecting updates. The hourly-update mechanism landed on main separately; the alt logo is saved as `archive/logo-variant-2026-07-15.png`. Nothing else unique. |
