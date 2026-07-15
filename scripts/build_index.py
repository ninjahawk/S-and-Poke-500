#!/usr/bin/env python3
"""Build the S&Poke 500 index from live Pokemon card prices.

The S&Poke 500 is a price-weighted index of the 500 most valuable English,
raw/ungraded Pokemon cards -- the Pokemon-card equivalent of the S&P 500.

Data source: pokemontcg.io (free), which embeds TCGplayer market prices in each
card. This script:
  1. Fetches high-value cards via a market-price range query.
  2. Picks the top 500 by representative market price.
  3. Rolls them into a single price-weighted index using an index divisor so the
     number stays continuous when the basket rebalances (standard index math,
     same idea the S&P 500 uses).
  4. Writes docs/data/latest.json (today's snapshot) and appends a point to
     docs/data/history.json (the time series the chart reads).

Only the Python standard library is used, so it runs on a bare GitHub Actions
runner with no `pip install` step. Set POKEMONTCG_API_KEY for higher rate limits.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://api.pokemontcg.io/v2/cards"
BASE_INDEX_VALUE = 1000.0  # the index starts here on the first real run
TARGET_SIZE = 500          # top N cards in the basket
PAGE_SIZE = 250            # pokemontcg.io max page size

# Finishes we consider when pricing a card. A card's representative price is the
# max market price across whichever of these it has.
FINISHES = [
    "normal",
    "holofoil",
    "reverseHolofoil",
    "1stEditionHolofoil",
    "1stEditionNormal",
    "unlimitedHolofoil",
]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, os.pardir, "docs", "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #
def api_get(params):
    """GET the cards endpoint with query params, returning parsed JSON."""
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "s-and-poke-500/1.0"})
    key = os.environ.get("POKEMONTCG_API_KEY")
    if key:
        req.add_header("X-Api-Key", key)
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:  # noqa: BLE001 - retry any transient failure
            last_err = err
            time.sleep(2 ** attempt)
    raise RuntimeError(f"pokemontcg.io request failed: {url}\n{last_err}")


def price_query(threshold):
    """Build a q= expression matching cards whose market price clears threshold."""
    clauses = [
        f"tcgplayer.prices.{finish}.market:[{threshold} TO *]" for finish in FINISHES
    ]
    return "(" + " OR ".join(clauses) + ")"


def representative_price(card):
    """Highest available market price across a card's finishes (mid as fallback)."""
    prices = (card.get("tcgplayer") or {}).get("prices") or {}
    best = 0.0
    for finish, values in prices.items():
        if not isinstance(values, dict):
            continue
        val = values.get("market")
        if val is None:
            val = values.get("mid")
        if isinstance(val, (int, float)) and val > best:
            best = float(val)
    return best


def fetch_card_pool():
    """Return {card_id: card_record} for all high-value cards.

    Lowers the price threshold until we have a comfortable margin above the
    target basket size, so the top 500 cut is stable. If the price-range query
    isn't supported or returns too few, falls back to a full scan of priced cards.
    """
    for threshold in (100, 50, 25, 10):
        print(f"Fetching cards with market price >= ${threshold} ...", flush=True)
        try:
            pool = paginate({"q": price_query(threshold)})
        except Exception as err:  # noqa: BLE001 - query may be unsupported; try fallback
            print(f"  range query failed ({err}); will try a full scan", flush=True)
            break
        print(f"  collected {len(pool)} priced cards", flush=True)
        if len(pool) >= TARGET_SIZE:
            return pool

    # Fallback: scan every card that carries TCGplayer pricing and filter locally.
    print("Falling back to full scan of priced cards ...", flush=True)
    pool = paginate({"q": "tcgplayer.prices.market:*"}, floor=5.0)
    if len(pool) < TARGET_SIZE:
        # Last resort: scan all cards, price them ourselves.
        pool = paginate({}, floor=5.0)
    print(f"  full scan collected {len(pool)} priced cards", flush=True)
    if not pool:
        raise RuntimeError("No priced cards returned from pokemontcg.io")
    return pool


def paginate(query, floor=0.0):
    """Page through the cards endpoint, returning {id: card} for priced cards."""
    pool = {}
    page = 1
    while True:
        params = {
            "page": page,
            "pageSize": PAGE_SIZE,
            "select": "id,name,number,rarity,set,images,tcgplayer",
        }
        params.update(query)
        data = api_get(params)
        cards = data.get("data", [])
        for card in cards:
            price = representative_price(card)
            if price <= floor:
                continue
            card_set = card.get("set") or {}
            pool[card["id"]] = {
                "id": card["id"],
                "name": card.get("name", "Unknown"),
                "number": card.get("number", ""),
                "rarity": card.get("rarity", ""),
                "setName": card_set.get("name", ""),
                "setId": card_set.get("id", ""),
                "image": (card.get("images") or {}).get("small", ""),
                "price": round(price, 2),
            }
        total = data.get("totalCount", 0)
        if not cards or page * PAGE_SIZE >= total or page >= 200:
            break
        page += 1
    return pool


# --------------------------------------------------------------------------- #
# Index math
# --------------------------------------------------------------------------- #
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return default


def build():
    pool = fetch_card_pool()

    # Today's basket: top 500 by price.
    ranked = sorted(pool.values(), key=lambda c: c["price"], reverse=True)
    basket = ranked[:TARGET_SIZE]
    today_prices = {c["id"]: c["price"] for c in pool.values()}
    sum_today = sum(c["price"] for c in basket)

    # Previous state -- ignored if it was sample/preview data.
    prev = load_json(LATEST_PATH, {})
    if prev.get("sample"):
        prev = {}
    prev_divisor = prev.get("divisor")
    prev_index = prev.get("index")
    prev_prices = {c["id"]: c.get("price") for c in prev.get("constituents", [])}
    prev_ids = list(prev_prices.keys())

    if not prev_divisor or not prev_ids:
        # First real run: anchor the index at BASE_INDEX_VALUE.
        divisor = sum_today / BASE_INDEX_VALUE
        index_value = BASE_INDEX_VALUE
        prev_index = None
    else:
        # Reprice YESTERDAY's basket at today's prices; that move is the index's
        # return. Then rebalance the divisor so the new basket is continuous.
        sum_old_today = sum(
            today_prices.get(cid, prev_prices.get(cid) or 0.0) for cid in prev_ids
        )
        sum_old_today = sum_old_today or sum_today
        index_value = sum_old_today / prev_divisor
        divisor = prev_divisor * (sum_today / sum_old_today) if sum_old_today else prev_divisor

    # Per-card daily change and market breadth.
    advancing = declining = unchanged = 0
    for card in basket:
        prior = prev_prices.get(card["id"])
        if prior and prior > 0:
            card["prevPrice"] = round(prior, 2)
            card["changePct"] = round((card["price"] / prior - 1) * 100, 2)
            card["isNew"] = False
            if card["changePct"] > 0:
                advancing += 1
            elif card["changePct"] < 0:
                declining += 1
            else:
                unchanged += 1
        else:
            card["prevPrice"] = None
            card["changePct"] = None
            card["isNew"] = bool(prev_ids)  # "new" only if there was a prior basket
    for rank, card in enumerate(basket, start=1):
        card["rank"] = rank

    movable = [c for c in basket if c["changePct"] is not None]
    movable.sort(key=lambda c: c["changePct"], reverse=True)
    mover_fields = ("id", "name", "image", "setName", "price", "prevPrice", "changePct")
    gainers = [{k: c[k] for k in mover_fields} for c in movable[:10] if c["changePct"] > 0]
    losers = [
        {k: c[k] for k in mover_fields}
        for c in reversed(movable[-10:])
        if c["changePct"] < 0
    ]

    now = datetime.now(timezone.utc)
    as_of = now.strftime("%Y-%m-%d")
    change_pct = None
    change_abs = None
    if prev_index:
        change_abs = round(index_value - prev_index, 2)
        change_pct = round((index_value / prev_index - 1) * 100, 2)

    latest = {
        "sample": False,
        "generated": now.isoformat(),
        "asOfDate": as_of,
        "index": round(index_value, 2),
        "prevIndex": round(prev_index, 2) if prev_index else None,
        "change": change_abs,
        "changePct": change_pct,
        "divisor": divisor,
        "baseValue": BASE_INDEX_VALUE,
        "constituentCount": len(basket),
        "totalValue": round(sum_today, 2),
        "breadth": {"advancing": advancing, "declining": declining, "unchanged": unchanged},
        "gainers": gainers,
        "losers": losers,
        "constituents": basket,
    }

    # History time series (the chart reads this). Reset if it was sample data.
    history = load_json(HISTORY_PATH, {})
    if not isinstance(history, dict) or history.get("sample"):
        history = {"sample": False, "points": []}
    points = [p for p in history.get("points", []) if p.get("date") != as_of]
    points.append(
        {
            "date": as_of,
            "index": round(index_value, 2),
            "totalValue": round(sum_today, 2),
            "count": len(basket),
        }
    )
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
        f"| basket {len(basket)} | total ${sum_today:,.0f} | divisor {divisor:.4f}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        build()
    except Exception as err:  # noqa: BLE001 - surface a clean CI failure
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
