#!/usr/bin/env python3
"""Shared helpers for the S&Poke 500 pipeline.

Single data source: TCGCSV (https://tcgcsv.com), a free, daily mirror of
TCGplayer's public catalog + market prices, plus a dated price archive going
back to 2024-02-08. Using one source keeps the live snapshot and the backfilled
history perfectly consistent (same product IDs, same "TCGplayer market price"
definition the index has always used).

  - Category 3 is English Pokemon.
  - "Singles" (individual cards) are told apart from sealed product (booster
    boxes, ETBs, tins...) by the presence of a card `Number` in extendedData.
  - A card's representative price is the max TCGplayer market price across its
    regular printings (1st Edition rows excluded -- see _rep_from_rows).

Standard library only, so it runs on a bare CI runner with no pip install.
"""

import io
import json
import os
import re
import time
import urllib.request

TCGCSV = "https://tcgcsv.com"
CATEGORY = 3  # English Pokemon
USER_AGENT = "s-and-poke-500/2.0 (+https://poke500.com)"

BASE_INDEX_VALUE = 1000.0
TARGET_SIZE = 500
ARCHIVE_START = "2024-02-08"  # earliest daily price archive TCGCSV publishes

_SET_PREFIX = re.compile(r"^[A-Z0-9]{2,6}:\s+")  # "SWSH07: Evolving Skies" -> "Evolving Skies"

# Oddities that pollute a "most valuable cards" ranking: oversized/jumbo box
# toppers, catch-all "miscellaneous" listings, staff-only promos, and error
# cards. These are thinly traded with aspirational prices, so they'd whip the
# index around without representing the real market. Excluded from the universe.
_BAD_SET = ("jumbo", "miscellaneous", "oversized")
_BAD_NAME = ("box topper", "jumbo", "oversized", "(staff", "miscut", "misprint", "error)")


def _excluded(name, set_name):
    low_set = (set_name or "").lower()
    low_name = (name or "").lower()
    return any(k in low_set for k in _BAD_SET) or any(k in low_name for k in _BAD_NAME)


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:  # noqa: BLE001 - retry any transient failure
            last = err
            time.sleep(2 ** attempt)
    raise RuntimeError(f"TCGCSV request failed: {url}\n{last}")


def _get_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as err:  # noqa: BLE001
            last = err
            time.sleep(2 ** attempt)
    raise RuntimeError(f"TCGCSV download failed: {url}\n{last}")


def _extended(product, key):
    for entry in product.get("extendedData", []):
        if entry.get("name") == key:
            return entry.get("value")
    return None


def _is_single(product):
    """A card single carries a collector Number; sealed product does not."""
    return _extended(product, "Number") is not None


def clean_set_name(name):
    return _SET_PREFIX.sub("", name or "").strip()


def fetch_groups():
    return _get_json(f"{TCGCSV}/tcgplayer/{CATEGORY}/groups")["results"]


def build_catalog(verbose=False):
    """Return {productId: {name, number, rarity, setName, setId, image}} for
    every English Pokemon single. Sealed product is excluded so the "most
    valuable" ranking can't be polluted by booster boxes.
    """
    catalog = {}
    groups = fetch_groups()
    for i, group in enumerate(groups, 1):
        gid = group["groupId"]
        set_name = clean_set_name(group.get("name", ""))
        try:
            products = _get_json(f"{TCGCSV}/tcgplayer/{CATEGORY}/{gid}/products")["results"]
        except RuntimeError as err:
            if verbose:
                print(f"  group {gid} products failed: {err}", flush=True)
            continue
        for product in products:
            if not _is_single(product):
                continue
            if _excluded(product.get("name", ""), set_name):
                continue
            catalog[str(product["productId"])] = {
                "id": str(product["productId"]),
                "name": product.get("name", "Unknown"),
                "number": _extended(product, "Number") or "",
                "rarity": _extended(product, "Rarity") or "",
                "setName": set_name,
                "setId": str(gid),
                "image": product.get("imageUrl", ""),
            }
        if verbose and i % 25 == 0:
            print(f"  catalog: {i}/{len(groups)} sets, {len(catalog)} singles", flush=True)
        time.sleep(0.1)
    if not catalog:
        raise RuntimeError("TCGCSV returned an empty Pokemon catalog")
    return catalog


def _rep_from_rows(rows):
    """Highest TCGplayer *market* price across a product's regular printings.

    Market price only (no mid/listing fallback): the index tracks real,
    sales-derived value, not aspirational asking prices. A product with no
    market price on a given day simply isn't ranked that day.

    1st Edition printings are excluded from pricing: the truly expensive 1st
    Edition cards trade off-TCGplayer (auction houses/eBay), so TCGplayer's
    market price for them is thin to outright broken — e.g. Shadowless Base
    Set Charizard's 1st Edition row has shown $250 "market" against a real
    ~$20k+ street value, while Neo Destiny 1st Editions carry real prints.
    Mixing the two made the ranking incoherent (some cards priced 1st Ed,
    some not). Regular/Unlimited printings are liquid on TCGplayer, so the
    index prices every card by those. If a product has *only* 1st Edition
    rows, they're used as a fallback so the card can still rank.
    """
    best = 0.0
    fallback = 0.0
    for row in rows:
        val = row.get("marketPrice")
        if not isinstance(val, (int, float)) or val <= 0:
            continue
        if "1st edition" in (row.get("subTypeName") or "").lower():
            fallback = max(fallback, float(val))
        else:
            best = max(best, float(val))
    return best or fallback


def _prices_from_group_rows(results, out):
    grouped = {}
    for row in results:
        grouped.setdefault(str(row["productId"]), []).append(row)
    for pid, rows in grouped.items():
        price = _rep_from_rows(rows)
        if price > 0:
            out[pid] = round(price, 2)


def live_prices(verbose=False):
    """Today's representative price per product: {productId: price}."""
    prices = {}
    groups = fetch_groups()
    for i, group in enumerate(groups, 1):
        gid = group["groupId"]
        try:
            results = _get_json(f"{TCGCSV}/tcgplayer/{CATEGORY}/{gid}/prices")["results"]
        except RuntimeError:
            continue
        _prices_from_group_rows(results, prices)
        if verbose and i % 25 == 0:
            print(f"  live prices: {i}/{len(groups)} sets, {len(prices)} priced", flush=True)
        time.sleep(0.1)
    return prices


def latest_archive_date():
    """Most recent date that has a published price archive (probing back a few days)."""
    from datetime import datetime, timedelta, timezone

    today = datetime.now(timezone.utc).date()
    for back in range(0, 7):
        d = today - timedelta(days=back)
        url = f"{TCGCSV}/archive/tcgplayer/prices-{d.isoformat()}.ppmd.7z"
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return d
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError("No recent TCGCSV price archive found")


def archive_prices(date):
    """Representative price per product for a past date from the daily archive.

    Downloads the day's 7z, extracts only the Pokemon (category 3) price files,
    and returns {productId: price}. Returns {} if that date isn't published.
    """
    import py7zr  # lazy import; only the backfill needs it

    import tempfile

    url = f"{TCGCSV}/archive/tcgplayer/prices-{date}.ppmd.7z"
    try:
        blob = _get_bytes(url)
    except RuntimeError:
        return {}
    prices = {}
    with tempfile.TemporaryDirectory() as tmp:
        with py7zr.SevenZipFile(io.BytesIO(blob), "r") as archive:
            targets = [
                n for n in archive.getnames()
                if n.startswith(f"{date}/{CATEGORY}/") and n.endswith("/prices")
            ]
            if not targets:
                return {}
            archive.extract(path=tmp, targets=targets)
        for name in targets:
            path = os.path.join(tmp, *name.split("/"))
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as handle:
                _prices_from_group_rows(json.load(handle).get("results", []), prices)
    return prices


def rank_basket(prices, catalog, size=TARGET_SIZE):
    """Top-`size` singles by representative price. Returns [(productId, price)]."""
    ranked = sorted(
        ((pid, pr) for pid, pr in prices.items() if pid in catalog and pr and pr > 0),
        key=lambda kv: kv[1],
        reverse=True,
    )
    return ranked[:size]


def step_index(prices, catalog, prev_ids, prev_divisor, carry=None, size=TARGET_SIZE):
    """One index step against a day's prices.

    Price-weighted with an index divisor, exactly like the S&P 500: reprice
    yesterday's basket at today's prices to get the day's return, then rebalance
    the divisor so today's (possibly rebalanced) basket stays continuous.

    `carry` is a {productId: last-known price} map used to forward-fill: a card
    that has no *market* print on a given day (thin trading) keeps its most
    recent price instead of dropping to $0, which would otherwise crash the
    repriced-basket sum and fabricate a decline. Today's real prices always win
    over carried-forward ones. Callers maintain `carry` with a staleness cap.

    Returns a dict: index, divisor, ids, basket [(pid, price)], sum_today.
    """
    effective = dict(carry or {})
    effective.update(prices)  # today's real prices override carried-forward
    basket = rank_basket(effective, catalog, size)
    ids = [pid for pid, _ in basket]
    sum_today = sum(pr for _, pr in basket)
    if not prev_divisor or not prev_ids:
        divisor = sum_today / BASE_INDEX_VALUE if sum_today else 1.0
        index = BASE_INDEX_VALUE
    else:
        sum_old_today = sum(effective.get(pid, 0.0) for pid in prev_ids) or sum_today
        index = sum_old_today / prev_divisor
        divisor = prev_divisor * (sum_today / sum_old_today) if sum_old_today else prev_divisor
    return {
        "index": index,
        "divisor": divisor,
        "ids": ids,
        "basket": basket,
        "sum_today": sum_today,
    }
