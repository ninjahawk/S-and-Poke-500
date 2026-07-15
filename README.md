# The S&Poké 500

**A price-weighted index of the 500 most valuable Pokémon cards — the Pokémon-card
equivalent of the S&P 500.** One number that tells you, at a glance, whether the
overall Pokémon card market is heating up, cooling off, or topping out.

It's a static website (GitHub Pages) fed by a daily GitHub Action. There's no
server to go down: the site is just HTML/CSS/JS reading two JSON files, and a
scheduled job refreshes those files once a day.

## How the index works

- **Universe:** the 500 most valuable English, raw (ungraded) card *singles*, by
  TCGplayer market price. Sealed product (booster boxes, ETBs) and thinly-traded
  oddities (jumbo/oversized box toppers, staff promos, error cards, "miscellaneous"
  listings) are excluded so the ranking reflects the real singles market.
- **Data source:** [TCGCSV](https://tcgcsv.com), a free daily mirror of TCGplayer's
  public catalog and market prices. It also publishes a dated price **archive** back
  to **2024-02-08**, which is what the history is reconstructed from.
- **Price rule:** a card's representative price is the highest TCGplayer *market*
  price across its printings/conditions (actual sales-derived value — no aspirational
  listing/mid prices).
- **Method:** price-weighted. The index tracks the combined market price of the
  basket, divided by an *index divisor* — the same trick the S&P 500 uses so the
  number stays continuous when cards enter or leave the top 500. The index is
  rebased to **1,000** on the first archived day (2024-02-08).
- **Movement:** up when the basket gets pricier, down when it cools. Daily change,
  per-card moves, market breadth (advancing vs. declining), and "market mood" are
  all derived from the same daily snapshot.

### About the history
The chart is reconstructed weekly from the TCGCSV price archive (2024-02-08 →
today) and then grows one point per day going forward. Basket membership is
recomputed on every date — a card is in the 500 only on the days its market price
actually ranks it there — so it's a real index with dynamic membership, not
"today's winners" painted onto the past. The archive is where the free data floor
is: reliable raw-single prices don't exist much before 2024, so the chart starts
there rather than fabricating a deeper line.

## One-time setup (do these in the repo settings)

The daily job and the code are already here. To go live:

1. **Enable Pages:** Settings → Pages → *Build and deployment* → Deploy from a
   branch → Branch: `main`, Folder: **`/docs`** (not `/ (root)` — the root
   serves this README instead of the app).
2. **Custom domain (`poké500.com`):** the repo ships `CNAME` files (root **and**
   `docs/`) pointing at `xn--pok500-dva.com` (the punycode form of the
   internationalized domain `poké500.com`) — the root one is the file the Pages UI
   manages; don't delete it. Point the domain's DNS at GitHub Pages (apex `A`
   records + a `www` `CNAME`), confirm the domain shows under Settings → Pages,
   and enable *Enforce HTTPS* once the certificate is issued.
3. **Daily updates** run automatically (see the workflow below). Trigger the first
   one by hand with Actions → *Update S&Poké 500 index* → *Run workflow*.

## Project layout

```
docs/                     # the website (served by GitHub Pages)
  index.html
  styles.css
  app.js                  # dashboard + interactive S&P-style chart scrubber
  og-image.png            # social-share card (Open Graph / Twitter preview)
  CNAME                   # custom domain (poké500.com / xn--pok500-dva.com)
  data/
    latest.json           # today's snapshot: index, movers, all 500 cards
    history.json          # the index time series (the chart)
scripts/
  tcg_common.py           # shared: TCGCSV catalog/prices + index math
  build_index.py          # daily pipeline (stdlib only): live prices -> index -> JSON
  backfill_history.py     # one-time: rebuild history from the TCGCSV price archive
  make_sample.py          # regenerate offline sample preview data (legacy)
.github/workflows/
  update-index.yml        # runs the daily pipeline and commits the data
```

## Running the pipeline yourself

```bash
# Daily build — standard library only, no dependencies:
python3 scripts/build_index.py

# One-time history backfill — needs py7zr to read the archive:
pip install py7zr
python3 scripts/backfill_history.py
```

Both reach `tcgcsv.com` over the network. No API key required.

---

*Not financial advice. Prices are TCGplayer market data via [tcgcsv.com](https://tcgcsv.com),
refreshed daily. Independent fan project — not affiliated with Nintendo, The Pokémon
Company, TCGplayer, or S&P Global.*
