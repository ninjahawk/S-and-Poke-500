#!/usr/bin/env python3
"""Publish the full "any card" catalog + daily prices to docs/data/catalog/.

Why this exists
---------------
The index only ever publishes its top 500. The iOS app wants users to be able
to add *any* raw English Pokemon card to a portfolio, which needs the whole
universe -- every set, every card, today's price -- as static JSON on Pages.

build_index.py already downloads exactly that every day: it fetches all ~220
TCGplayer category-3 groups' products and prices, ranks them, and throws the
other ~29,000 cards away. So this script does not re-download anything. During
its normal run build_index.py side-writes the raw fetched universe to a local
cache (.cache/tcg_snapshot.json, gitignored); this script reads that cache and
turns it into the published files. If the cache is missing or stale it does
nothing at all -- unless run with --fetch, which re-downloads with the same
throttling (used for the very first publish and as a manual escape hatch).

Isolation contract (same as record_card_history.py, deliberately boring):

  * Runs as its own workflow step with continue-on-error: true, AFTER the
    index has been built and committed.
  * The whole body is wrapped in try/except and the process ALWAYS exits 0.
    Nothing it does can turn the daily build red or touch the index files.
  * On an hourly no-op run (TCGCSV unchanged, so build_index exited early and
    wrote no cache) this makes zero network requests and writes nothing.

Universe and price rule are the index's, unchanged, because they come from the
same tcg_common helpers: singles only (must carry a card Number), no sealed, no
jumbo/oversized/box-topper, no "miscellaneous", no [staff]/(staff), no
miscut/misprint/error, no JP-only "-P" promos; price = the highest TCGplayer
*market* price across a product's regular printings with 1st Edition rows
excluded (1st Ed used only as a fallback when a product has nothing else), and
no price at all when TCGplayer has no market price that day.

These published prices are RAW: the index's glitch guard (rolling-median hold)
is NOT applied here, because the guard needs a per-card history this catalog
does not keep. Every output file says so in its `note` field.

Output
------
docs/data/catalog/sets.json
    {"generated", "asOfDate", "sets": [{id, name, abbr, count, priced,
     published}]}  -- newest set first.

docs/data/catalog/sets/<setId>.json
    {"note", "setId", "setName", "asOfDate", "cards": [{id, name, number,
     rarity, printing, image, price, prevPrice, pricedAsOf}]}  -- cards sorted
    by collector number then name. `prevPrice` is the `price` from the previous
    day's committed copy of this same file (null on the first run, or when the
    card was not in that copy). A same-day re-run keeps the existing baseline
    rather than flattening it to today's price.

docs/data/catalog/search.json
    {"asOfDate", "cards": [[id, name, setId, number], ...]}  -- array-of-arrays
    across every set, kept deliberately small for a single app-launch download.

Usage:
    python3 scripts/publish_catalog.py            # publish from build_index's cache
    python3 scripts/publish_catalog.py --fetch    # re-download, then publish
    python3 scripts/publish_catalog.py --size     # report published bytes
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tcg_common as tc  # noqa: E402

REPO_ROOT = os.path.normpath(os.path.join(HERE, os.pardir))
DATA_DIR = os.path.join(REPO_ROOT, "docs", "data")
CATALOG_DIR = os.path.join(DATA_DIR, "catalog")
SETS_DIR = os.path.join(CATALOG_DIR, "sets")
SETS_INDEX_PATH = os.path.join(CATALOG_DIR, "sets.json")
SEARCH_PATH = os.path.join(CATALOG_DIR, "search.json")

# Where build_index.py side-writes the universe it already downloaded.
CACHE_PATH = os.path.join(REPO_ROOT, ".cache", "tcg_snapshot.json")

NOTE = ("Raw TCGplayer market price for ungraded English singles (max across "
        "regular printings, 1st Edition excluded), via tcgcsv.com. Unguarded: "
        "the S&Poke 500 index's glitch filter is NOT applied to these prices, "
        "so a thinly traded card can print an outlier on any given day.")

# search.json is downloaded whole by the app on launch, so it has a budget.
SEARCH_BUDGET_BYTES = 2 * 1024 * 1024

_NUM_LEAD = re.compile(r"^(\D*)(\d+)")


def load_json(path, default):
    """Read JSON, falling back to `default` on anything unreadable."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return default


def dump_json(path, payload):
    """Write compactly -- these files are downloaded by a phone, not read by a human."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"))
    return os.path.getsize(path)


def today_iso():
    return datetime.now(timezone.utc).date().isoformat()


# --------------------------------------------------------------------------
# The snapshot build_index.py hands over
# --------------------------------------------------------------------------

def write_cache(catalog, prices, printings, stamp, path=None):
    """Persist one day's fetched universe for this script to consume.

    Called by build_index.py as a pure side-write inside its own try/except --
    if this raises, the index build is unaffected and the catalog simply is not
    republished that day.
    """
    path = path or CACHE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "asOfDate": today_iso(),
        "sourceStamp": stamp,
        "catalog": catalog,
        "prices": prices,
        "printings": printings or {},
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"))
    os.replace(tmp, path)
    return path


def read_cache(path=None):
    """Today's cached snapshot, or None if there isn't a usable one.

    A cache from a previous day is ignored on purpose: republishing yesterday's
    prices under today's date would be a lie, and it would also burn the
    prevPrice baseline (every card would show no change).
    """
    cache = load_json(path or CACHE_PATH, None)
    if not isinstance(cache, dict):
        return None
    if not isinstance(cache.get("catalog"), dict) or not isinstance(cache.get("prices"), dict):
        return None
    if cache.get("asOfDate") != today_iso():
        return None
    if not cache["catalog"]:
        return None
    return cache


def fetch_snapshot(verbose=True):
    """Re-download the universe with tcg_common's normal throttling.

    Only used by --fetch (the first publish, or a manual repair). It is the
    same ~220-group walk build_index.py does, so never run it alongside one.
    """
    printings = {}
    catalog = tc.build_catalog(verbose=verbose)
    prices = tc.live_prices(verbose=verbose, subtype_out=printings)
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "asOfDate": today_iso(),
        "sourceStamp": tc.source_stamp(),
        "catalog": catalog,
        "prices": prices,
        "printings": printings,
    }


# --------------------------------------------------------------------------
# Shaping
# --------------------------------------------------------------------------

def number_key(number, name=""):
    """Sort key for a collector number: alpha prefix, then the number as a number.

    Collector numbers are strings of several shapes -- "12/181", "170/181",
    "SWSH066", "TG12/TG30", "H1". Plain string sort puts "10/181" before
    "2/181", which reads as broken in a card list, so the leading integer is
    compared numerically and cards with the same prefix stay together.
    """
    s = (number or "").strip()
    match = _NUM_LEAD.match(s)
    if match:
        return (0, match.group(1).lower(), int(match.group(2)), s.lower(), (name or "").lower())
    return (1, s.lower(), 0, s.lower(), (name or "").lower())


def set_published(group):
    """Group publish date as YYYY-MM-DD, or None."""
    raw = group.get("publishedOn")
    if isinstance(raw, str) and len(raw) >= 10:
        candidate = raw[:10]
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
        except ValueError:
            return None
        return candidate
    return None


def previous_prices(set_id, as_of, sets_dir=None):
    """{cardId: price} from the committed copy of this set's file.

    Returns the baseline today's `prevPrice` should be taken from:

      * previous day's file  -> that file's `price` values (a real 1-day move);
      * a file already written TODAY (workflow retry, manual re-run) -> that
        file's own `prevPrice` values, so a same-day republish keeps pointing
        at yesterday instead of collapsing every change to zero. This is the
        same baseline rule build_index.py uses for the index's daily change.
      * no file, or an unreadable one -> {} (everything publishes as null).
    """
    sets_dir = sets_dir or SETS_DIR
    existing = load_json(os.path.join(sets_dir, f"{set_id}.json"), None)
    if not isinstance(existing, dict):
        return {}
    cards = existing.get("cards")
    if not isinstance(cards, list):
        return {}
    prior_as_of = existing.get("asOfDate")
    same_day = isinstance(prior_as_of, str) and prior_as_of >= as_of
    field = "prevPrice" if same_day else "price"
    out = {}
    for card in cards:
        if not isinstance(card, dict) or card.get("id") is None:
            continue
        value = card.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
            out[str(card["id"])] = round(float(value), 2)
    return out


def build_set_file(set_id, set_name, as_of, cards, prices, printings, prev):
    """One docs/data/catalog/sets/<setId>.json payload."""
    rows = []
    for meta in cards:
        pid = str(meta["id"])
        price = prices.get(pid)
        price = round(float(price), 2) if isinstance(price, (int, float)) and price > 0 else None
        rows.append({
            "id": pid,
            "name": meta.get("name") or "",
            "number": meta.get("number") or "",
            "rarity": meta.get("rarity") or "",
            "printing": (printings.get(pid) or None) if price is not None else None,
            "image": meta.get("image") or "",
            "price": price,
            "prevPrice": prev.get(pid),
            "pricedAsOf": as_of if price is not None else None,
        })
    rows.sort(key=lambda c: number_key(c["number"], c["name"]))
    return {
        "note": NOTE,
        "setId": str(set_id),
        "setName": set_name,
        "asOfDate": as_of,
        "cards": rows,
    }


def publish(snapshot, groups, catalog_dir=None):
    """Write every catalog file from one snapshot. Returns a summary dict."""
    catalog_dir = catalog_dir or CATALOG_DIR
    sets_dir = os.path.join(catalog_dir, "sets")
    as_of = snapshot.get("asOfDate") or today_iso()
    cards = snapshot["catalog"]
    prices = snapshot["prices"]
    printings = snapshot.get("printings") or {}

    by_set = {}
    for meta in cards.values():
        by_set.setdefault(str(meta.get("setId")), []).append(meta)

    group_by_id = {str(g.get("groupId")): g for g in groups if g.get("groupId") is not None}

    sets_rows = []
    search_rows = []
    total_cards = 0
    for set_id, members in by_set.items():
        group = group_by_id.get(set_id, {})
        set_name = tc.clean_set_name(group.get("name")) or (members[0].get("setName") or set_id)
        prev = previous_prices(set_id, as_of, sets_dir=sets_dir)
        payload = build_set_file(set_id, set_name, as_of, members, prices, printings, prev)
        dump_json(os.path.join(sets_dir, f"{set_id}.json"), payload)

        priced = sum(1 for c in payload["cards"] if c["price"] is not None)
        total_cards += len(payload["cards"])
        sets_rows.append({
            "id": set_id,
            "name": set_name,
            "abbr": (group.get("abbreviation") or None),
            "count": len(payload["cards"]),
            "priced": priced,
            "published": set_published(group),
        })
        for card in payload["cards"]:
            search_rows.append([card["id"], card["name"], set_id, card["number"],
                                card["price"]])

    # Newest set first; a set with no publish date sorts to the bottom rather
    # than pretending to be either the newest or the oldest.
    dated = sorted((s for s in sets_rows if s["published"]),
                   key=lambda s: (s["published"], s["name"]), reverse=True)
    undated = sorted((s for s in sets_rows if not s["published"]), key=lambda s: s["name"])
    sets_rows = dated + undated
    sets_bytes = dump_json(os.path.join(catalog_dir, "sets.json"), {
        "generated": datetime.now(timezone.utc).isoformat(),
        "asOfDate": as_of,
        "sets": sets_rows,
    })

    # search.json ships whole to the phone. Build it full; if it blows the
    # budget, drop the cards TCGplayer has no market price for -- they are the
    # ones a portfolio can do the least with -- and say so in the file.
    def _set_order(set_id):
        try:
            return (0, int(set_id))
        except (TypeError, ValueError):
            return (1, 0)

    search_rows.sort(key=lambda r: (_set_order(r[2]), number_key(r[3], r[1])))
    full = [r[:4] for r in search_rows]
    payload = {"asOfDate": as_of, "cards": full}
    search_bytes = dump_json(os.path.join(catalog_dir, "search.json"), payload)
    trimmed = False
    if search_bytes > SEARCH_BUDGET_BYTES:
        payload = {
            "asOfDate": as_of,
            "note": "Cards with no TCGplayer market price today are omitted to keep this file small.",
            "cards": [r[:4] for r in search_rows if r[4] is not None],
        }
        search_bytes = dump_json(os.path.join(catalog_dir, "search.json"), payload)
        trimmed = True

    return {
        "asOfDate": as_of,
        "sets": len(sets_rows),
        "cards": total_cards,
        "priced": sum(s["priced"] for s in sets_rows),
        "setsBytes": sets_bytes,
        "searchBytes": search_bytes,
        "searchCards": len(payload["cards"]),
        "searchTrimmed": trimmed,
    }


def dir_bytes(path=None):
    path = path or CATALOG_DIR
    total = 0
    files = 0
    for root, _dirs, names in os.walk(path):
        for name in names:
            total += os.path.getsize(os.path.join(root, name))
            files += 1
    return total, files


def size_report(path=None):
    path = path or CATALOG_DIR
    if not os.path.isdir(path):
        return "docs/data/catalog/ does not exist yet."
    total, files = dir_bytes(path)
    return f"{path}: {files} files, {total:,} B ({total / 1_048_576:.2f} MB)."


def run(argv=()):
    if "--size" in argv:
        print(size_report())
        return

    if "--fetch" in argv:
        print("Re-fetching the full TCGCSV universe (~220 groups, throttled) ...", flush=True)
        snapshot = fetch_snapshot()
    else:
        snapshot = read_cache()
        if snapshot is None:
            print("No fresh snapshot cache from today's index build; nothing to publish.")
            return

    groups = tc.fetch_groups()
    summary = publish(snapshot, groups)
    total, files = dir_bytes()
    print(
        f"catalog: {summary['sets']} sets, {summary['cards']:,} cards "
        f"({summary['priced']:,} priced) as of {summary['asOfDate']} | "
        f"search.json {summary['searchBytes']:,} B "
        f"({summary['searchCards']:,} cards"
        f"{', null-price cards dropped' if summary['searchTrimmed'] else ''}) | "
        f"{files} files, {total:,} B total ({total / 1_048_576:.2f} MB)",
        flush=True,
    )


if __name__ == "__main__":
    try:
        run(sys.argv[1:])
    except Exception as err:  # noqa: BLE001 - must never fail the daily build
        print(f"publish_catalog: skipped ({type(err).__name__}: {err})", file=sys.stderr)
    sys.exit(0)
