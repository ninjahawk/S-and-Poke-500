# The S&Poké 500

**A price-weighted index of the 500 most valuable Pokémon cards — the Pokémon-card
equivalent of the S&P 500.** One number that tells you, at a glance, whether the
overall Pokémon card market is heating up, cooling off, or topping out.

It's a static website (GitHub Pages) fed by a daily GitHub Action. There's no
server to go down: the site is just HTML/CSS/JS reading two JSON files, and a
scheduled job refreshes those files once a day.

## How the index works

- **Universe:** the 500 most valuable English, raw (ungraded) cards, by TCGplayer
  market price (data from [pokemontcg.io](https://pokemontcg.io)).
- **Method:** price-weighted. The index tracks the combined market price of the
  basket, divided by an *index divisor* — the same trick the S&P 500 uses so the
  number stays continuous when cards enter or leave the top 500. The index is
  rebased to **1,000** on the first live update.
- **Movement:** up when the basket gets pricier, down when it cools. Daily change,
  per-card moves, market breadth (advancing vs. declining), and "market mood" are
  all derived from the same daily snapshot.

### Honest caveat about history
The free price API only reports a **current** snapshot — no historical prices. So
the chart's history starts empty and grows by one point per day from launch. The
longer it runs, the more useful the trend line becomes. (A paid historical source
could backfill it later; the code is structured to allow that.)

The site ships with clearly-labelled **sample data** so you can see the design
immediately. The first real Action run discards the sample and starts a clean,
real history.

## One-time setup (do these in the repo settings)

The daily job and the code are already here. To go live:

1. **Merge this branch into `main`.**
2. **Enable Pages:** Settings → Pages → *Build and deployment* → Deploy from a
   branch → Branch: `main`, Folder: `/docs`. Your site appears at
   `https://<your-username>.github.io/S-and-Poke-500/`.
3. **(Recommended) Add an API key** for higher rate limits: get a free key at
   [pokemontcg.io](https://pokemontcg.io), then Settings → Secrets and variables →
   Actions → *New repository secret* → name `POKEMONTCG_API_KEY`. The pipeline runs
   without one too, just at lower limits.
4. **Kick off the first real update:** Actions → *Update S&Poké 500 index* → *Run
   workflow*. This replaces the sample data with live prices. After that it runs
   automatically every day.

## Project layout

```
docs/                     # the website (served by GitHub Pages)
  index.html
  styles.css
  app.js                  # dashboard + interactive S&P-style chart scrubber
  data/
    latest.json           # today's snapshot: index, movers, all 500 cards
    history.json          # the daily index time series (the chart)
scripts/
  build_index.py          # daily pipeline: fetch prices -> compute index -> write JSON
  make_sample.py          # regenerate the sample preview data (offline)
.github/workflows/
  update-index.yml        # runs the pipeline daily and commits the data
```

## Running the pipeline yourself

```bash
python3 scripts/build_index.py      # needs internet to reach api.pokemontcg.io
```

No dependencies — standard library only. Set `POKEMONTCG_API_KEY` in your
environment for higher rate limits.

---

*Not financial advice. Prices are TCGplayer market data via pokemontcg.io, refreshed
daily. Built for fun and market curiosity.*
