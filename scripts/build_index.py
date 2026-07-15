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
    print("Fetching catalog + live prices from TCGCSV ...", flush=True)
    catalog = tc.build_catalog()
    prices = tc.live_prices()
    if len(prices) < tc.TARGET_SIZE:
        raise RuntimeError(f"Only {len(prices)} priced cards from TCGCSV")

    # Previous state -- ignored if it was sample/preview data.
    prev = load_json(LATEST_PATH, {})
    if prev.get("sample"):
        prev = {}
    prev_divisor = prev.get("divisor")
    prev_index = prev.get("index")
    prev_prices = {c["id"]: c.get("price") for c in prev.get("constituents", []) if c.get("price")}
    prev_ids = [c["id"] for c in prev.get("constituents", [])] or None

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
    else:
        baseline_index = prev_index
        baseline_prices = prev_prices

    # tc.step_index keys baskets by TCGplayer productId; prev_ids from a stored
    # snapshot are the same string ids, so the chain is continuous. Passing
    # yesterday's prices as `carry` forward-fills any card that has no market
    # print today, so a thin-trading day can't spuriously crash the index.
    step = tc.step_index(prices, catalog, prev_ids, prev_divisor, carry=prev_prices)

    # Per-card daily change + breadth.
    constituents = []
    advancing = declining = unchanged = 0
    for rank, (pid, price) in enumerate(step["basket"], start=1):
        meta = catalog[pid]
        prior = baseline_prices.get(pid)
        change_pct = None
        if prior and prior > 0:
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
        })

    movable = [c for c in constituents if c["changePct"] is not None]
    movable.sort(key=lambda c: c["changePct"], reverse=True)
    fields = ("id", "name", "image", "setName", "price", "prevPrice", "changePct")
    gainers = [{k: c[k] for k in fields} for c in movable[:10] if c["changePct"] > 0]
    losers = [{k: c[k] for k in fields} for c in reversed(movable[-10:]) if c["changePct"] < 0]

    now = datetime.now(timezone.utc)
    as_of = now.date().isoformat()
    index_value = step["index"]
    change_abs = round(index_value - baseline_index, 2) if baseline_index else None
    change_pct = round((index_value / baseline_index - 1) * 100, 2) if baseline_index else None

    latest = {
        "sample": False,
        "generated": now.isoformat(),
        "asOfDate": as_of,
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
