#!/usr/bin/env python3
"""One-time backfill of the S&Poke 500 history from TCGCSV's price archive.

Reconstructs the index week-by-week from 2024-02-08 (the earliest archived day)
to today, using the *same* universe, price rule, and divisor math as the live
daily build -- so the backfilled history and the going-forward daily points form
one continuous, consistent series.

The basket membership is recomputed on every date (a card is in the 500 only on
the days its market price actually ranks it there), so the index is a real
price-weighted index with dynamic membership, not "today's winners" painted onto
the past.

Run locally (needs `pip install py7zr`); commit the resulting JSON. The daily
GitHub Action (build_index.py) only needs the standard library and continues the
series from here.

    python3 scripts/backfill_history.py
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tcg_common as tc  # noqa: E402

DATA_DIR = os.path.join(HERE, os.pardir, "docs", "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

STEP_DAYS = 7    # weekly sampling for history depth (daily granularity accrues going forward)
STALE_DAYS = tc.STALE_DAYS  # forward-fill cap, shared with the daily builder


def sample_dates(latest):
    """Weekly dates from the archive start, then the two most recent *distinct*
    archive days so the final snapshot carries a real 1-day change."""
    start = datetime.strptime(tc.ARCHIVE_START, "%Y-%m-%d").date()
    dates = []
    d = start
    while d < latest - timedelta(days=1):
        dates.append(d)
        d += timedelta(days=STEP_DAYS)
    for extra in (latest - timedelta(days=1), latest):
        if extra not in dates:
            dates.append(extra)
    return sorted(set(dates))


def main():
    print("Building catalog (English Pokemon singles) ...", flush=True)
    catalog = tc.build_catalog(verbose=True)
    print(f"  {len(catalog)} singles", flush=True)

    latest = tc.latest_archive_date()
    dates = sample_dates(latest)
    print(f"Latest archive: {latest}. Reconstructing {len(dates)} points "
          f"({dates[0]} -> {dates[-1]}) ...", flush=True)

    points = []
    prev_ids = None
    prev_divisor = None
    prev_eff = None           # previous step's effective (forward-filled) prices, for 1D change
    last = None

    carry = {}                # productId -> last-known price (forward-fill)
    carry_dt = {}             # productId -> date last actually priced
    guard_windows = {}        # productId -> [recent prices] (glitch guard state)
    trusted_cur = set()       # pids whose print the guard accepted on the latest day
    trusted_prev = set()      # ... and on the day before it (the 1D-change baseline)

    for i, d in enumerate(dates):
        ds = d.isoformat()
        # Reject TCGplayer glitch prints before they can fabricate movers/spikes.
        held = set()
        prices = tc.guard_prices(tc.archive_prices(ds), guard_windows, held=held)
        if len(prices) < tc.TARGET_SIZE:
            print(f"  {ds}: only {len(prices)} priced -- skipping", flush=True)
            continue

        step = tc.step_index(prices, catalog, prev_ids, prev_divisor, carry=carry)
        points.append({
            "date": ds,
            "index": round(step["index"], 2),
            "totalValue": round(step["sum_today"], 2),
            "count": len(step["ids"]),
        })

        # Effective prices as of the PREVIOUS priced day (before folding today in) --
        # this is the baseline for the latest day's per-card 1D change. Then fold
        # today's real prices into the forward-fill carry and drop stale entries.
        prev_eff = dict(carry)
        trusted_prev = trusted_cur
        trusted_cur = {pid for pid in prices if pid not in held}
        for pid, pr in prices.items():
            carry[pid] = pr
            carry_dt[pid] = d
        carry = {pid: p for pid, p in carry.items() if (d - carry_dt[pid]).days <= STALE_DAYS}

        prev_ids = step["ids"]
        prev_divisor = step["divisor"]
        last = step
        last_date = ds
        if i % 10 == 0 or i == len(dates) - 1:
            print(f"  {ds}: index {step['index']:.2f} "
                  f"(basket {len(step['ids'])}, ${step['sum_today']:,.0f})", flush=True)

    if not last:
        raise RuntimeError("No points reconstructed")

    now = datetime.now(timezone.utc)
    as_of = last_date  # the latest archived day this snapshot reflects
    prev_index = points[-2]["index"] if len(points) >= 2 else None

    # Build today's full constituent snapshot with per-card 1D change.
    constituents = []
    advancing = declining = unchanged = 0
    for rank, (pid, price) in enumerate(last["basket"], start=1):
        meta = catalog[pid]
        prior = (prev_eff or {}).get(pid)
        # Same rule as the daily builder: a per-card "today %" only exists
        # between two guard-confirmed prints. A held/carried endpoint would
        # surface filter drift (e.g. a late-accepted re-rating) as a giant fake
        # one-day move, so those cards show no daily change instead.
        pair_ok = pid in trusted_cur and pid in trusted_prev
        change_pct = None
        if prior and prior > 0 and pair_ok:
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
            "isNew": prior is None and prev_eff is not None,
            # Seed the glitch-guard window so the daily builder continues it.
            "priceWindow": [round(x, 2) for x in guard_windows.get(pid, [])] or None,
            "trusted": pid in trusted_cur,
            "prevTrusted": pid in trusted_prev,
        })

    movable = [c for c in constituents if c["changePct"] is not None]
    movable.sort(key=lambda c: c["changePct"], reverse=True)
    fields = ("id", "name", "image", "setName", "price", "prevPrice", "changePct")
    gainers = [{k: c[k] for k in fields} for c in movable[:10] if c["changePct"] > 0]
    losers = [{k: c[k] for k in fields} for c in reversed(movable[-10:]) if c["changePct"] < 0]

    # Guard-window watch zone. The daily builder can only distrust a print if
    # it has the card's recent history; persisting windows for the basket alone
    # would leave every card *below* the cutoff "fresh" each day, so a one-day
    # glitch spike on a near-threshold card would enter the basket at the fake
    # price. Persist windows for the next 500 cards under the basket too
    # (ranks 501-1000 by effective price): spikes from the realistic entry zone
    # get held at their median instead of admitted.
    basket_ids = set(last["ids"])
    watch = tc.rank_basket(carry, catalog, size=2 * tc.TARGET_SIZE)
    guard_out = {
        pid: [round(x, 2) for x in guard_windows[pid]]
        for pid, _ in watch
        if pid not in basket_ids and guard_windows.get(pid)
    }

    change_abs = round(last["index"] - prev_index, 2) if prev_index else None
    change_pct = round((last["index"] / prev_index - 1) * 100, 2) if prev_index else None

    latest = {
        "sample": False,
        "generated": now.isoformat(),
        "asOfDate": as_of,
        "index": round(last["index"], 2),
        "prevIndex": round(prev_index, 2) if prev_index else None,
        "change": change_abs,
        "changePct": change_pct,
        "divisor": last["divisor"],
        "baseValue": tc.BASE_INDEX_VALUE,
        "constituentCount": len(constituents),
        "totalValue": round(last["sum_today"], 2),
        "breadth": {"advancing": advancing, "declining": declining, "unchanged": unchanged},
        "gainers": gainers,
        "losers": losers,
        "guardWindows": guard_out,
        "constituents": constituents,
    }
    history = {"sample": False, "generated": now.isoformat(), "points": points}

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LATEST_PATH, "w", encoding="utf-8") as handle:
        json.dump(latest, handle, indent=2)
    with open(HISTORY_PATH, "w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)

    print(f"\nDone. {len(points)} history points, index now {last['index']:.2f} "
          f"({'+' if (change_pct or 0) >= 0 else ''}{change_pct}% 1D).", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # noqa: BLE001
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
