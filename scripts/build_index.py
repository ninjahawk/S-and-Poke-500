#!/usr/bin/env python3
"""Daily build of the S&Poke 500 index from live TCGplayer market prices.

The S&Poke 500 is a price-weighted index of the 500 most valuable English,
raw/ungraded Pokemon card singles -- the Pokemon-card equivalent of the S&P 500.

Data source: TCGCSV (https://tcgcsv.com), a free daily mirror of TCGplayer's
public catalog + market prices. This script:
  1. Fetches today's market prices for every English Pokemon single.
  2. Ranks the top 500 by representative market price (max across printings).
  3. Continues the index from yesterday's snapshot using an index divisor, so the
     number stays continuous as the basket rebalances (same math the S&P 500 uses).
  4. Writes docs/data/latest.json and appends a point to docs/data/history.json.

History before today is produced once by backfill_history.py. This daily job only
uses the standard library, so it runs on a bare CI runner with no pip install.
"""

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tcg_common as tc  # noqa: E402

DATA_DIR = os.path.join(HERE, os.pardir, "docs", "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return default


def build():
    # Cheap change guard: the job runs hourly, but TCGCSV refreshes once a day
    # (~20:05 UTC). One tiny request tells us whether there's anything new; if
    # not, exit before the ~220-request price fetch. Fail-open on any doubt.
    prev_snapshot = load_json(LATEST_PATH, {})
    stamp = tc.source_stamp()
    if stamp and prev_snapshot.get("sourceStamp") == stamp:
        print(f"TCGCSV unchanged since {stamp}; nothing to do.", flush=True)
        return

    # Corruption tripwires -- fail loudly rather than quietly destroy the
    # series. load_json fails soft (returns {}), which is right for a genuine
    # first run but catastrophic mid-life: a missing/corrupt latest.json would
    # silently RE-BASE the index to 1000, and a corrupt history.json would
    # silently rewrite 2.5 years of points down to one. If one file is gone
    # while the other clearly shows an established series, something is broken;
    # abort so CI goes red and the file can be restored from git.
    history_points = (load_json(HISTORY_PATH, {}) or {}).get("points") or []
    if history_points and not prev_snapshot.get("divisor"):
        raise RuntimeError(
            "latest.json is missing/corrupt but history.json has "
            f"{len(history_points)} points -- refusing to re-base the index; "
            "restore docs/data/latest.json from git")
    if prev_snapshot.get("constituents") and not history_points:
        raise RuntimeError(
            "history.json is missing/corrupt but latest.json exists -- "
            "refusing to rewrite the series; restore docs/data/history.json "
            "from git")

    print("Fetching catalog + live prices from TCGCSV ...", flush=True)
    catalog = tc.build_catalog()
    subtypes = {}
    raw_prices = tc.live_prices(subtype_out=subtypes)
    if len(raw_prices) < tc.TARGET_SIZE:
        raise RuntimeError(f"Only {len(raw_prices)} priced cards from TCGCSV")

    # Previous state -- ignored if it was sample/preview data.
    prev = load_json(LATEST_PATH, {})
    if prev.get("sample"):
        prev = {}

    # Glitch guard: reference each live print against the median of the card's
    # recent prices (persisted per-card as `priceWindow`). A print that deviates
    # wildly is a TCGplayer blip -- hold the median instead of leaking a fake
    # spike/dip into the index; a level that persists eventually dominates the
    # window and is accepted. Same rolling-median rule the backfill seeds.
    guard_windows = {
        c["id"]: list(c["priceWindow"])
        for c in prev.get("constituents", [])
        if c.get("priceWindow")
    }
    # ... plus the persisted watch zone (ranks 501-1000): without history for
    # the cards just below the cutoff, a one-day glitch spike on any of them
    # would be trusted as "new" and enter the basket at the fake price.
    for pid, win in (prev.get("guardWindows") or {}).items():
        if win:
            guard_windows.setdefault(pid, list(win))
    held = set()
    prices = tc.guard_prices(raw_prices, guard_windows, held=held)
    prev_divisor = prev.get("divisor")
    prev_index = prev.get("index")
    prev_prices = {c["id"]: c.get("price") for c in prev.get("constituents", []) if c.get("price")}
    prev_ids = [c["id"] for c in prev.get("constituents", [])] or None

    # When a card was last *actually* priced by TCGplayer (vs carried forward).
    # Older snapshots didn't record pricedAsOf; treat their prices as fresh as
    # of that snapshot's date so the staleness clock starts now, not in error.
    prev_priced_asof = {
        c["id"]: c.get("pricedAsOf") or prev.get("asOfDate")
        for c in prev.get("constituents", [])
    }
    prev_printing = {c["id"]: c.get("printing") for c in prev.get("constituents", [])}

    # Daily change is always measured against the previous *day*, not the
    # previous run. If the committed snapshot is from earlier today (manual
    # re-run, workflow retry), its own baseline is yesterday's state -- reuse
    # that for change/breadth so a same-day refresh can't zero everything out.
    today_iso = datetime.now(timezone.utc).date().isoformat()
    if prev.get("asOfDate") == today_iso:
        baseline_index = prev.get("prevIndex") or prev_index
        baseline_prices = {
            c["id"]: c.get("prevPrice")
            for c in prev.get("constituents", [])
            if c.get("prevPrice")
        } or prev_prices
        baseline_trusted = {
            c["id"]: bool(c.get("prevTrusted")) for c in prev.get("constituents", [])
        }
    else:
        baseline_index = prev_index
        baseline_prices = prev_prices
        baseline_trusted = {
            c["id"]: bool(c.get("trusted")) for c in prev.get("constituents", [])
        }

    # tc.step_index keys baskets by TCGplayer productId; prev_ids from a stored
    # snapshot are the same string ids, so the chain is continuous. Passing
    # yesterday's prices as `carry` forward-fills any card that has no market
    # print today, so a thin-trading day can't spuriously crash the index.
    # The carry is capped at STALE_DAYS (same rule as the backfill): a card
    # TCGplayer hasn't priced in that long drops out rather than squatting in
    # the index on a permanently frozen price.
    def _age_days(iso):
        try:
            return (datetime.now(timezone.utc).date()
                    - datetime.strptime(iso, "%Y-%m-%d").date()).days
        except (TypeError, ValueError):
            return 0
    carry = {
        pid: pr for pid, pr in prev_prices.items()
        if _age_days(prev_priced_asof.get(pid)) <= tc.STALE_DAYS
    }
    step = tc.step_index(prices, catalog, prev_ids, prev_divisor, carry=carry)

    # Per-card daily change + breadth.
    today_asof = datetime.now(timezone.utc).date().isoformat()
    constituents = []
    advancing = declining = unchanged = 0
    for rank, (pid, price) in enumerate(step["basket"], start=1):
        meta = catalog[pid]
        prior = baseline_prices.get(pid)
        # Provenance: is this a real price from today's snapshot, or one carried
        # forward -- either because TCGplayer had no sales data for it, or its
        # print was held back by the glitch guard as an unconfirmed outlier?
        live_today = pid in raw_prices and pid not in held
        # A per-card "today %" is only meaningful between two *confirmed* prints.
        # If either endpoint was guard-held or carried forward, the difference is
        # filter drift, not a market move (the worst case: the day a re-rated
        # level is finally accepted, weeks of climb would print as one fake
        # +200% "today"). Those cards show no daily change and sit out of the
        # movers/breadth; TCGplayer's thin-card data can't support day-precision
        # moves for them, so we don't pretend it does. The index level itself
        # still reflects every effective price.
        change_pct = None
        if prior and prior > 0 and live_today and baseline_trusted.get(pid):
            change_pct = round((price / prior - 1) * 100, 2)
            if change_pct > 0:
                advancing += 1
            elif change_pct < 0:
                declining += 1
            else:
                unchanged += 1
        constituents.append({
            "rank": rank,
            "id": meta["id"],
            "name": meta["name"],
            "number": meta["number"],
            "rarity": meta["rarity"],
            "setName": meta["setName"],
            "setId": meta["setId"],
            "image": meta["image"],
            "price": round(price, 2),
            "prevPrice": round(prior, 2) if prior else None,
            "changePct": change_pct,
            "isNew": prior is None and bool(prev_ids),
            "printing": (subtypes.get(pid) if live_today else prev_printing.get(pid)) or None,
            "pricedAsOf": today_asof if live_today else prev_priced_asof.get(pid),
            "priceWindow": [round(x, 2) for x in guard_windows.get(pid, [])] or None,
            "trusted": live_today,
            "prevTrusted": bool(baseline_trusted.get(pid)),
        })

    movable = [c for c in constituents if c["changePct"] is not None]
    movable.sort(key=lambda c: c["changePct"], reverse=True)
    fields = ("id", "name", "image", "setName", "price", "prevPrice", "changePct")
    gainers = [{k: c[k] for k in fields} for c in movable[:10] if c["changePct"] > 0]
    losers = [{k: c[k] for k in fields} for c in reversed(movable[-10:]) if c["changePct"] < 0]

    # Persist guard windows for the watch zone below the basket (see the
    # seeding comment above): ranks 501-1000 by today's effective prices.
    basket_ids = set(step["ids"])
    watch = tc.rank_basket({**carry, **prices}, catalog, size=2 * tc.TARGET_SIZE)
    guard_out = {
        pid: [round(x, 2) for x in guard_windows[pid]]
        for pid, _ in watch
        if pid not in basket_ids and guard_windows.get(pid)
    }

    now = datetime.now(timezone.utc)
    as_of = now.date().isoformat()
    index_value = step["index"]
    change_abs = round(index_value - baseline_index, 2) if baseline_index else None
    change_pct = round((index_value / baseline_index - 1) * 100, 2) if baseline_index else None

    latest = {
        "sample": False,
        "generated": now.isoformat(),
        "sourceStamp": stamp,
        "asOfDate": as_of,
        "priceSource": "TCGplayer Market Price (via tcgcsv.com daily snapshot)",
        "staleDays": tc.STALE_DAYS,
        "index": round(index_value, 2),
        "prevIndex": round(baseline_index, 2) if baseline_index else None,
        "change": change_abs,
        "changePct": change_pct,
        "divisor": step["divisor"],
        "baseValue": tc.BASE_INDEX_VALUE,
        "constituentCount": len(constituents),
        "totalValue": round(step["sum_today"], 2),
        "breadth": {"advancing": advancing, "declining": declining, "unchanged": unchanged},
        "gainers": gainers,
        "losers": losers,
        "guardWindows": guard_out,
        "constituents": constituents,
    }

    # Append today's point to the history series (reset if it was sample data).
    history = load_json(HISTORY_PATH, {})
    if not isinstance(history, dict) or history.get("sample"):
        history = {"sample": False, "points": []}
    points = [p for p in history.get("points", []) if p.get("date") != as_of]
    points.append({
        "date": as_of,
        "index": round(index_value, 2),
        "totalValue": round(step["sum_today"], 2),
        "count": len(constituents),
    })
    points.sort(key=lambda p: p["date"])
    history = {"sample": False, "generated": now.isoformat(), "points": points}

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LATEST_PATH, "w", encoding="utf-8") as handle:
        json.dump(latest, handle, indent=2)
    with open(HISTORY_PATH, "w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)

    print(
        f"S&Poke 500 = {index_value:.2f} "
        f"({'+' if (change_pct or 0) >= 0 else ''}{change_pct}%) "
        f"| basket {len(constituents)} | total ${step['sum_today']:,.0f} "
        f"| divisor {step['divisor']:.4f}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        build()
    except Exception as err:  # noqa: BLE001 - surface a clean CI failure
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
