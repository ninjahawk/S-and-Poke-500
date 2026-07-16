# Soft-launch Reddit post — r/PokeInvesting (rev 2, finalized 2026-07-16)

Rev 1 read like a product changelog; rewritten as a data-drop post — findings
first, tool second. Numbers verified against live data at finalization:
index 1,355.70 (2026-07-15, −0.19%), base 1,000 @ 2024-02-08 (+35.6%),
basket total $244,438, cheapest constituent $214.90, breadth 32/30/394.

Post as a **text post with the chart image embedded at the top of the body**
(new Reddit supports inline images in text posts). Image: `chart-max.png`
(the MAX-range hero screenshot — sent in chat).

---

## Title

The 500 most valuable English Pokémon cards, tracked daily as one index: up 36% since Feb 2024. Buying one of each would run you $244,438.

## Body

*(chart image here)*

I got tired of per-card price lookups with no way to see the whole market, so I built a stock-market-style index of it — the S&Poké 500. Some things it surfaced that I haven't seen anywhere else:

- **It takes $215 just to crack the top 500.** Card #500 right now is — of course — a Charizard.
- **#1 isn't Base Set Zard.** It's Charizard Star (Delta Species) at $4,000, with Shining Charizard literally $1 behind at $3,999. Base Set Unlimited sits at #9 ($2,146).
- **Moonbreon check: #6 overall at $2,396** — the only modern card ahead of it is the Latias & Latios GX alt art at $3,279.
- **Vintage prices are STICKY.** On a typical day ~90% of the top 500 don't move at all. Yesterday: 32 up, 30 down, 394 flat. When someone says "the market is pumping," it's usually ~50 cards doing all the work.
- **The big picture:** flat-to-down through most of 2024, then two big legs up in 2025. Base 1,000 in Feb 2024 → **1,355.70** today.

Site: [poké500.com](https://xn--pok500-dva.com/) — free, no signup, no ads. Updates itself daily around 4pm ET.

How it works in one line: real index math (price-weighted with a divisor, like the Dow — membership rebalances as cards move in and out of the top 500), priced off TCGplayer market prices, raw English singles only (no 1st Editions, no sealed, no graded — the methodology page explains why).

Every card on the site links out to TCGplayer, PriceCharting, and eBay solds so you can call BS on any price — and please do. "Why does card X show $Y" almost always has an interesting answer, usually a printing difference or a source difference.

It's a solo free project — if there's something you'd want tracked (weekly movers, a WOTC-era-only sub-index, whatever), say so and I'll build the good ideas.

---

## Video — DONE (2026-07-16)

A finished 33s demo mp4 (`poke500-demo.mp4`, 720×1280, silent, ~4.5 MB) was
produced with a scripted Playwright recording against a local copy of the
live site (card images localized so they render instantly) and sent to the
owner in chat. Shot order: cold open on 1,355.70 → 1Y→MAX zoom-out → tooltip
scrub across the chart → movers → top-10 crawl → Moonbreon modal → return to
hero. The hand-shot notes below are the fallback if a reshoot is ever needed.

## Video shoot — director's notes (35s silent vertical, one take)

Pre-flight: DND on; open poké500.com in the browser (URL bar visible =
branding); scroll the full page once to warm the image cache, back to top;
set range to **1M** (opening position); dark mode optional; record.

Move at half natural speed. Shot list:

| Time | Shot | Direction |
|---|---|---|
| 0–4s | Cold open | Hold on **1,355.70**, no touching |
| 4–10s | The zoom-out ⭐ | Tap **1Y**, beat, tap **MAX** — the money shot |
| 10–16s | The scrub | Press-drag to Feb 2024 (~1,000), hold, drag to today |
| 16–22s | Movers | Slow scroll through Today's movers |
| 22–29s | The rich list | Crawl ranks 1–6 ($4,000 Zard Star → Moonbreon) |
| 29–35s | Moonbreon close-up | Tap Umbreon VMAX row → modal ($2,396, #6 of 500), hold 2s, cut |

Post: same title/body, video inline at the top of the text post (Reddit app
supports inline video). Fallback: video post + body pasted as immediate first
comment. Videos autoplay muted in-feed — shot 1 must be the big number.

## Posting checklist (from LAUNCH.md)

- [ ] **r/PokeInvesting only** tonight — no crossposting; the rest of collector
      Reddit waits for Day 1–2, one sub per half-day.
- [ ] Attach `chart-max.png` at the top of the body.
- [ ] Reply to **every** comment in the first ~2 hours; prepared answers for
      the common criticisms are in `LAUNCH.md` → "Prepared answers".
- [ ] Tone: data/transparency, never investment advice.
- [ ] Watch referrers live at https://poke500.goatcounter.com — soft-post
      success bar is roughly 500–2k visits.
