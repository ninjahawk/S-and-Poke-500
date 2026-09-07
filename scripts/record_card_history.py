#!/usr/bin/env python3
"""Record per-card daily prices into docs/data/cards_history.json.

The index series (docs/data/history.json) is index-level only. ROADMAP item 4
(portfolio tracker: "did my collection beat the index?") and the per-card
sparkline in the iOS app both need a *per-card* daily series, and the only way
to have a long one later is to start recording now.

Design rules, deliberately boring:

  * This script never fetches anything. It reads the already-built
    docs/data/latest.json and appends today's column. It cannot fail the daily
    build: everything is wrapped in try/except and the process always exits 0.
    It runs as its own workflow step, AFTER the index commit and BEFORE the
    newsletter step, with continue-on-error: true.
  * A price is recorded only when that card's print is `trusted` on that day.
    Untrusted (guard-held, carried forward, or stale) prices are recorded as
    null. Carrying an unconfirmed price into a per-card series would bake the
    same fake spikes the glitch guard exists to suppress -- a null is honest,
    a guessed price is not. A card that is not in the basket that day is also
    null.
  * Only constituents are recorded. `guardWindows` (ranks 501-1000) carries
    prices for cards that are explicitly *not* in the index; they are ignored.
  * Idempotent per date: re-running on the same date replaces that date's
    column, it never appends a duplicate.

File format (chosen for size and for a one-line Swift `Codable` decode):

    {
      "generated": "2026-09-06T21:30:00+00:00",
      "dates": ["2026-07-15", "2026-07-16", ...],          // sorted, unique
      "cards": {"183899": [4271.62, null, ...], ...}       // aligned to dates
    }

Swift: `struct CardsHistory: Codable { let generated: String; let dates:
[String]; let cards: [String: [Double?]] }`. Every series has exactly
`dates.count` entries, so `cards[id]![i]` pairs with `dates[i]`.

Usage:
    python3 scripts/record_card_history.py              # append today's column
    python3 scripts/record_card_history.py --backfill   # one-off, from git history
    python3 scripts/record_card_history.py --size       # report size + 1y projection

--backfill reconstructs the series for the *current* constituents from this
repo's own git history of docs/data/latest.json (one commit per day since
2026-07-15), taking each commit's own asOfDate and letting the newest commit
for a date win. It does not touch the TCGCSV 7z archive.
"""

import bisect
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, os.pardir))
DATA_DIR = os.path.join(REPO_ROOT, "docs", "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")
CARDS_PATH = os.path.join(DATA_DIR, "cards_history.json")

# Path as git knows it (POSIX separators), for `git log` / `git show`.
LATEST_GIT_PATH = "docs/data/latest.json"


def load_json(path, default):
    """Read JSON, falling back to `default` on anything unreadable."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return default


def empty_store():
    return {"generated": None, "dates": [], "cards": {}}


def normalize(store):
    """Coerce whatever is on disk into a well-formed store.

    Fails soft on purpose: a corrupt cards_history.json must never stop the
    daily build. The worst case is that we start the series over, and the
    file can be restored from git if that ever happens.
    """
    if not isinstance(store, dict):
        return empty_store()
    dates = store.get("dates")
    cards = store.get("cards")
    if not isinstance(dates, list) or not isinstance(cards, dict):
        return empty_store()
    dates = [d for d in dates if isinstance(d, str)]
    n = len(dates)
    clean = {}
    for pid, series in cards.items():
        if not isinstance(series, list):
            continue
        series = [x if isinstance(x, (int, float)) and not isinstance(x, bool) else None
                  for x in series]
        # Pad/trim defensively so every row stays aligned to `dates`.
        if len(series) < n:
            series = series + [None] * (n - len(series))
        elif len(series) > n:
            series = series[:n]
        clean[str(pid)] = series
    return {"generated": store.get("generated"), "dates": dates, "cards": clean}


def prices_from_latest(latest, only_ids=None):
    """{productId: price_or_None} for the constituents of one snapshot.

    Trusted prints get their price (2 dp); everything else gets None. Only
    `constituents` is read -- `guardWindows` holds ranks 501-1000, which are by
    definition not in the index.
    """
    out = {}
    for card in (latest.get("constituents") or []):
        if not isinstance(card, dict):
            continue
        pid = card.get("id")
        if pid is None:
            continue
        pid = str(pid)
        if only_ids is not None and pid not in only_ids:
            continue
        price = card.get("price")
        ok = (card.get("trusted") is True
              and isinstance(price, (int, float))
              and not isinstance(price, bool)
              and price > 0)
        out[pid] = round(float(price), 2) if ok else None
    return out


def record(store, date, prices):
    """Write one date's column into the store, in place. Idempotent per date.

    Cards absent from `prices` are explicitly nulled at that date (they were
    not constituents that day), so re-running a date is a true replacement.
    """
    dates = store["dates"]
    cards = store["cards"]
    if date in dates:
        idx = dates.index(date)
    else:
        idx = bisect.bisect_left(dates, date)
        dates.insert(idx, date)
        for series in cards.values():
            series.insert(idx, None)
    n = len(dates)
    for pid, price in prices.items():
        series = cards.get(pid)
        if series is None:
            series = [None] * n
            cards[pid] = series
        series[idx] = price
    for pid, series in cards.items():
        if len(series) < n:
            series.extend([None] * (n - len(series)))
        if pid not in prices:
            series[idx] = None
    return store


def prune(store):
    """Drop rows that are entirely null -- they carry no information."""
    store["cards"] = {pid: s for pid, s in store["cards"].items() if any(x is not None for x in s)}
    return store


def dump(store, path=None):
    """Write compactly. This file grows every day; indentation is not free."""
    path = path or CARDS_PATH
    store["generated"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(store, handle, separators=(",", ":"))
    return path


def size_report(path=None):
    """Current bytes + a straight-line projection to 365 daily columns."""
    path = path or CARDS_PATH
    if not os.path.exists(path):
        return "cards_history.json does not exist yet."
    size = os.path.getsize(path)
    store = normalize(load_json(path, empty_store()))
    n = len(store["dates"])
    cards = len(store["cards"])
    if n:
        per_date = size / n
        projected = per_date * 365
        return (f"{path}: {size:,} B over {n} dates x {cards} cards "
                f"({per_date:,.0f} B/date) -> ~{projected / 1_048_576:.2f} MB at 1 year "
                f"of daily data.")
    return f"{path}: {size:,} B, no dates recorded."


# --------------------------------------------------------------------------
# Daily path
# --------------------------------------------------------------------------

def run_daily():
    latest = load_json(LATEST_PATH, None)
    if not isinstance(latest, dict) or latest.get("sample"):
        print("No usable latest.json (missing or sample data); nothing recorded.")
        return
    date = latest.get("asOfDate")
    if not isinstance(date, str) or len(date) != 10:
        print(f"latest.json has no usable asOfDate ({date!r}); nothing recorded.")
        return
    prices = prices_from_latest(latest)
    if not prices:
        print("latest.json has no constituents; nothing recorded.")
        return

    store = normalize(load_json(CARDS_PATH, empty_store()))
    existed = date in store["dates"]
    record(store, date, prices)
    prune(store)
    dump(store)
    trusted = sum(1 for v in prices.values() if v is not None)
    print(f"cards_history.json: {'replaced' if existed else 'appended'} {date} "
          f"({trusted}/{len(prices)} trusted) | "
          f"{len(store['dates'])} dates x {len(store['cards'])} cards")
    print(size_report())


# --------------------------------------------------------------------------
# One-off backfill from this repo's git history
# --------------------------------------------------------------------------

def git(*args):
    return subprocess.run(
        ["git", "-C", REPO_ROOT, *args],
        capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
    ).stdout


def backfill_columns(only_ids):
    """[(date, {pid: price_or_None})] from git history, oldest date first.

    `git log` is newest-first, so the first commit seen for a date is the most
    recent one for that date -- that is the one that wins.
    """
    shas = [s for s in git("log", "--format=%H", "--", LATEST_GIT_PATH).split() if s]
    by_date = {}
    for sha in shas:
        try:
            snapshot = json.loads(git("show", f"{sha}:{LATEST_GIT_PATH}"))
        except (subprocess.CalledProcessError, ValueError):
            continue
        if not isinstance(snapshot, dict) or snapshot.get("sample"):
            continue
        date = snapshot.get("asOfDate")
        if not isinstance(date, str) or len(date) != 10 or date in by_date:
            continue
        prices = prices_from_latest(snapshot, only_ids=only_ids)
        # An all-null column (e.g. pre-glitch-guard snapshots that carried no
        # `trusted` flag) is pure padding -- skip the date entirely.
        if any(v is not None for v in prices.values()):
            by_date[date] = prices
    return sorted(by_date.items())


def run_backfill():
    latest = load_json(LATEST_PATH, None)
    if not isinstance(latest, dict) or not (latest.get("constituents") or []):
        print("No usable latest.json; cannot determine the current basket.")
        return
    only_ids = {str(c["id"]) for c in latest["constituents"] if isinstance(c, dict) and c.get("id")}
    print(f"Backfilling the current {len(only_ids)} constituents from git history ...")

    store = normalize(load_json(CARDS_PATH, empty_store()))
    known = set(store["dates"])
    added = skipped = 0
    for date, prices in backfill_columns(only_ids):
        if date in known:
            skipped += 1
            continue
        record(store, date, prices)
        added += 1
    prune(store)
    dump(store)
    print(f"Backfilled {added} dates ({skipped} already present). "
          f"Now {len(store['dates'])} dates x {len(store['cards'])} cards.")
    print(size_report())


def main(argv):
    if "--size" in argv:
        print(size_report())
    elif "--backfill" in argv:
        run_backfill()
    else:
        run_daily()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as err:  # noqa: BLE001 - must never fail the daily build
        print(f"record_card_history: skipped ({type(err).__name__}: {err})", file=sys.stderr)
    sys.exit(0)
