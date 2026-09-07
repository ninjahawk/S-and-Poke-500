"""Unit tests for scripts/publish_catalog.py — the "any card" catalog the iOS
app uses so a user can add a raw English single that is not in the top 500.

Covers: the universe filters (sealed / jumbo / staff / error / -P promos), the
representative-price rule (max market across regular printings, 1st Edition
excluded), prevPrice carry-over from the previously committed file, the cache
handshake with build_index.py, file shapes, sort order, and the
never-fail-the-build contract. All network access is mocked; nothing is fetched.

Run: python3 -m unittest discover tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import publish_catalog as pc  # noqa: E402
import tcg_common as tc  # noqa: E402


# --------------------------------------------------------------------------
# Fake TCGCSV payloads
# --------------------------------------------------------------------------

def group(gid, name, abbr="AAA", published="2019-02-01T00:00:00"):
    return {"groupId": gid, "name": name, "abbreviation": abbr,
            "publishedOn": published, "categoryId": 3}


def product(pid, name, number=None, rarity="Rare", image="http://img/x.jpg"):
    extended = []
    if number is not None:
        extended.append({"name": "Number", "value": number})
    extended.append({"name": "Rarity", "value": rarity})
    return {"productId": pid, "name": name, "imageUrl": image, "extendedData": extended}


def price_row(pid, market, subtype="Holofoil"):
    return {"productId": pid, "subTypeName": subtype, "marketPrice": market}


GROUPS = [
    group(2377, "SM - Team Up", abbr="TEU", published="2019-02-01T00:00:00"),
    group(3170, "SWSH07: Evolving Skies", abbr="EVS", published="2021-08-27T00:00:00"),
    group(9001, "Miscellaneous Items", abbr=None, published=None),
]

PRODUCTS = {
    # A normal set: two singles, one sealed box (no Number), one jumbo.
    2377: [
        product(183899, "Latias & Latios GX (Alternate Full Art)", "170/181"),
        product(183800, "Pikachu", "9/181"),
        product(183700, "Team Up Booster Box"),                      # sealed: no Number
        product(183701, "Pikachu (Jumbo)", "JUM1"),                  # jumbo
    ],
    # Filter torture: staff, error, JP -P promo, plus one keeper.
    3170: [
        product(250000, "Umbreon VMAX (Alternate Full Art)", "215/203"),
        product(250001, "Rayquaza VMAX [Staff] Prerelease", "111/203"),
        product(250002, "Charizard (Miscut error)", "20/203"),
        product(250003, "Pikachu", "227/S-P"),                       # JP-only promo
    ],
    # A whole group excluded by set name.
    9001: [
        product(260000, "Charizard", "1/1"),
    ],
}

PRICES = {
    2377: [
        # 1st Edition row is the highest but must be ignored; Holofoil wins.
        price_row(183899, 500.00, "1st Edition Holofoil"),
        price_row(183899, 120.50, "Holofoil"),
        price_row(183899, 90.00, "Normal"),
        # No market price at all -> the card publishes with price null.
        {"productId": 183800, "subTypeName": "Normal", "marketPrice": None},
        price_row(183700, 999.00, "Normal"),
    ],
    3170: [
        price_row(250000, 1400.00, "Holofoil"),
        price_row(250001, 60.00, "Holofoil"),
    ],
    9001: [price_row(260000, 12.00, "Holofoil")],
}


def fake_get_json(url):
    if url.endswith("/groups"):
        return {"results": GROUPS}
    parts = url.rstrip("/").split("/")
    kind, gid = parts[-1], int(parts[-2])
    if kind == "products":
        return {"results": PRODUCTS.get(gid, [])}
    if kind == "prices":
        return {"results": PRICES.get(gid, [])}
    raise AssertionError(f"unexpected URL {url}")


class CatalogMixin:
    """Publish into a temp dir with the network mocked out."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.catalog_dir = self.base / "docs" / "data" / "catalog"
        self.sets_dir = self.catalog_dir / "sets"
        self.cache_path = self.base / ".cache" / "tcg_snapshot.json"
        for target, value in (
            ("CATALOG_DIR", str(self.catalog_dir)),
            ("SETS_DIR", str(self.sets_dir)),
            ("SETS_INDEX_PATH", str(self.catalog_dir / "sets.json")),
            ("SEARCH_PATH", str(self.catalog_dir / "search.json")),
            ("CACHE_PATH", str(self.cache_path)),
        ):
            patch = mock.patch.object(pc, target, value)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch.object(tc, "_get_json", side_effect=fake_get_json)
        patch.start()
        self.addCleanup(patch.stop)
        patch = mock.patch.object(tc.time, "sleep", lambda *_a: None)
        patch.start()
        self.addCleanup(patch.stop)

    def snapshot(self, as_of="2026-09-06"):
        snap = pc.fetch_snapshot(verbose=False)
        snap["asOfDate"] = as_of
        return snap

    def publish(self, as_of="2026-09-06"):
        return pc.publish(self.snapshot(as_of), GROUPS, catalog_dir=str(self.catalog_dir))

    def read_set(self, set_id):
        return json.loads((self.sets_dir / f"{set_id}.json").read_text(encoding="utf-8"))

    def cards_by_id(self, set_id):
        return {c["id"]: c for c in self.read_set(set_id)["cards"]}


# --------------------------------------------------------------------------
# Universe filters — must match the index exactly
# --------------------------------------------------------------------------

class TestFilters(CatalogMixin, unittest.TestCase):
    def test_sealed_product_is_excluded(self):
        self.publish()
        self.assertNotIn("183700", self.cards_by_id("2377"))

    def test_jumbo_is_excluded(self):
        self.publish()
        self.assertNotIn("183701", self.cards_by_id("2377"))

    def test_staff_promo_is_excluded(self):
        self.publish()
        self.assertNotIn("250001", self.cards_by_id("3170"))

    def test_error_card_is_excluded(self):
        self.publish()
        self.assertNotIn("250002", self.cards_by_id("3170"))

    def test_jp_dash_p_promo_is_excluded(self):
        self.publish()
        self.assertNotIn("250003", self.cards_by_id("3170"))

    def test_excluded_set_produces_no_file(self):
        self.publish()
        self.assertFalse((self.sets_dir / "9001.json").exists())

    def test_real_singles_survive(self):
        summary = self.publish()
        self.assertEqual(sorted(self.cards_by_id("2377")), ["183800", "183899"])
        self.assertEqual(sorted(self.cards_by_id("3170")), ["250000"])
        self.assertEqual(summary["cards"], 3)
        self.assertEqual(summary["sets"], 2)


# --------------------------------------------------------------------------
# Price rule — max market across regular printings, 1st Edition excluded
# --------------------------------------------------------------------------

class TestPriceRule(CatalogMixin, unittest.TestCase):
    def test_max_regular_printing_wins_over_first_edition(self):
        self.publish()
        card = self.cards_by_id("2377")["183899"]
        self.assertEqual(card["price"], 120.50)
        self.assertEqual(card["printing"], "Holofoil")

    def test_no_market_price_publishes_null(self):
        self.publish()
        card = self.cards_by_id("2377")["183800"]
        self.assertIsNone(card["price"])
        self.assertIsNone(card["pricedAsOf"])
        self.assertIsNone(card["printing"])

    def test_priced_card_carries_the_as_of_date(self):
        self.publish(as_of="2026-09-06")
        self.assertEqual(self.cards_by_id("2377")["183899"]["pricedAsOf"], "2026-09-06")

    def test_first_edition_only_product_still_prices(self):
        rows = [price_row(1, 42.0, "1st Edition Holofoil")]
        out = {}
        tc._prices_from_group_rows(rows, out)
        self.assertEqual(out["1"], 42.0)

    def test_set_counts_priced_versus_total(self):
        self.publish()
        sets = json.loads((self.catalog_dir / "sets.json").read_text(encoding="utf-8"))["sets"]
        team_up = next(s for s in sets if s["id"] == "2377")
        self.assertEqual((team_up["count"], team_up["priced"]), (2, 1))


# --------------------------------------------------------------------------
# prevPrice
# --------------------------------------------------------------------------

class TestPrevPrice(CatalogMixin, unittest.TestCase):
    def test_first_run_has_no_previous_price(self):
        self.publish()
        self.assertIsNone(self.cards_by_id("2377")["183899"]["prevPrice"])

    def test_next_day_takes_yesterdays_price(self):
        self.publish(as_of="2026-09-06")
        self.publish(as_of="2026-09-07")
        card = self.cards_by_id("2377")["183899"]
        self.assertEqual(card["prevPrice"], 120.50)
        self.assertEqual(card["price"], 120.50)

    def test_same_day_rerun_keeps_the_earlier_baseline(self):
        # Day 1 at 100, day 2 at 120.50 -> prevPrice 100. Re-running day 2 must
        # keep prevPrice at 100, not collapse it to today's own price.
        self.write_existing("2377", "2026-09-05", [{"id": "183899", "price": 100.0}])
        self.publish(as_of="2026-09-06")
        self.assertEqual(self.cards_by_id("2377")["183899"]["prevPrice"], 100.0)
        self.publish(as_of="2026-09-06")
        self.assertEqual(self.cards_by_id("2377")["183899"]["prevPrice"], 100.0)

    def test_card_absent_yesterday_has_null_prev_price(self):
        self.write_existing("2377", "2026-09-05", [{"id": "999999", "price": 5.0}])
        self.publish(as_of="2026-09-06")
        self.assertIsNone(self.cards_by_id("2377")["183899"]["prevPrice"])

    def test_null_price_yesterday_is_not_a_baseline(self):
        self.write_existing("2377", "2026-09-05", [{"id": "183899", "price": None}])
        self.publish(as_of="2026-09-06")
        self.assertIsNone(self.cards_by_id("2377")["183899"]["prevPrice"])

    def test_unreadable_previous_file_is_tolerated(self):
        self.sets_dir.mkdir(parents=True, exist_ok=True)
        (self.sets_dir / "2377.json").write_text("{not json", encoding="utf-8")
        self.publish(as_of="2026-09-06")
        self.assertIsNone(self.cards_by_id("2377")["183899"]["prevPrice"])

    def write_existing(self, set_id, as_of, cards):
        self.sets_dir.mkdir(parents=True, exist_ok=True)
        (self.sets_dir / f"{set_id}.json").write_text(
            json.dumps({"setId": set_id, "setName": "x", "asOfDate": as_of, "cards": cards}),
            encoding="utf-8")


# --------------------------------------------------------------------------
# File shapes
# --------------------------------------------------------------------------

class TestOutputShape(CatalogMixin, unittest.TestCase):
    def test_set_file_documents_that_prices_are_unguarded(self):
        self.publish()
        payload = self.read_set("2377")
        self.assertEqual(list(payload)[0], "note")
        self.assertIn("Unguarded", payload["note"])

    def test_set_file_keys(self):
        self.publish()
        payload = self.read_set("2377")
        self.assertEqual(list(payload), ["note", "setId", "setName", "asOfDate", "cards"])
        self.assertEqual(payload["setName"], "SM - Team Up")
        self.assertEqual(sorted(payload["cards"][0]), sorted(
            ["id", "name", "number", "rarity", "printing", "image", "price",
             "prevPrice", "pricedAsOf"]))

    def test_cards_sort_by_number_numerically(self):
        self.publish()
        self.assertEqual([c["number"] for c in self.read_set("2377")["cards"]],
                         ["9/181", "170/181"])

    def test_sets_index_is_newest_first_with_abbr_and_published(self):
        self.publish()
        sets = json.loads((self.catalog_dir / "sets.json").read_text(encoding="utf-8"))
        self.assertEqual([s["id"] for s in sets["sets"]], ["3170", "2377"])
        self.assertEqual(sets["sets"][0]["abbr"], "EVS")
        self.assertEqual(sets["sets"][0]["published"], "2021-08-27")
        self.assertEqual(sets["asOfDate"], "2026-09-06")

    def test_missing_abbreviation_becomes_null(self):
        groups = [dict(GROUPS[0], abbreviation="")]
        pc.publish(self.snapshot(), groups, catalog_dir=str(self.catalog_dir))
        sets = json.loads((self.catalog_dir / "sets.json").read_text(encoding="utf-8"))["sets"]
        self.assertIsNone(next(s for s in sets if s["id"] == "2377")["abbr"])

    def test_undated_set_sorts_last(self):
        groups = [dict(GROUPS[0], publishedOn=None), GROUPS[1]]
        pc.publish(self.snapshot(), groups, catalog_dir=str(self.catalog_dir))
        sets = json.loads((self.catalog_dir / "sets.json").read_text(encoding="utf-8"))["sets"]
        self.assertEqual([s["id"] for s in sets], ["3170", "2377"])
        self.assertIsNone(sets[-1]["published"])

    def test_search_is_arrays_of_id_name_set_number(self):
        self.publish()
        payload = json.loads((self.catalog_dir / "search.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["asOfDate"], "2026-09-06")
        self.assertEqual(len(payload["cards"]), 3)
        row = next(r for r in payload["cards"] if r[0] == "183899")
        self.assertEqual(row, ["183899", "Latias & Latios GX (Alternate Full Art)",
                               "2377", "170/181"])

    def test_search_drops_unpriced_cards_when_over_budget(self):
        with mock.patch.object(pc, "SEARCH_BUDGET_BYTES", 1):
            summary = self.publish()
        payload = json.loads((self.catalog_dir / "search.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["searchTrimmed"])
        self.assertNotIn("183800", [r[0] for r in payload["cards"]])  # the null-price card
        self.assertIn("note", payload)

    def test_files_are_written_compactly(self):
        self.publish()
        raw = (self.catalog_dir / "search.json").read_text(encoding="utf-8")
        self.assertNotIn("\n", raw)
        self.assertNotIn(", ", raw)


# --------------------------------------------------------------------------
# The build_index.py handshake
# --------------------------------------------------------------------------

class TestCacheHandshake(CatalogMixin, unittest.TestCase):
    def test_round_trip(self):
        pc.write_cache({"1": {"id": "1"}}, {"1": 2.5}, {"1": "Holofoil"}, "stamp")
        cache = pc.read_cache()
        self.assertEqual(cache["prices"], {"1": 2.5})
        self.assertEqual(cache["sourceStamp"], "stamp")

    def test_yesterdays_cache_is_ignored(self):
        pc.write_cache({"1": {"id": "1"}}, {"1": 2.5}, {}, "stamp")
        stale = json.loads(self.cache_path.read_text(encoding="utf-8"))
        stale["asOfDate"] = "2000-01-01"
        self.cache_path.write_text(json.dumps(stale), encoding="utf-8")
        self.assertIsNone(pc.read_cache())

    def test_missing_and_corrupt_caches_are_ignored(self):
        self.assertIsNone(pc.read_cache())
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text("{nope", encoding="utf-8")
        self.assertIsNone(pc.read_cache())

    def test_empty_catalog_cache_is_ignored(self):
        pc.write_cache({}, {}, {}, "stamp")
        self.assertIsNone(pc.read_cache())

    def test_run_without_a_cache_publishes_nothing_and_fetches_nothing(self):
        with mock.patch.object(tc, "fetch_groups", side_effect=AssertionError("fetched!")):
            pc.run([])
        self.assertFalse(self.catalog_dir.exists())

    def test_run_consumes_the_cache_written_by_a_build(self):
        snap = self.snapshot(as_of=pc.today_iso())
        pc.write_cache(snap["catalog"], snap["prices"], snap["printings"], "stamp")
        pc.run([])
        self.assertTrue((self.sets_dir / "2377.json").exists())


# --------------------------------------------------------------------------
# Never fail the build
# --------------------------------------------------------------------------

class TestNeverFailsTheBuild(unittest.TestCase):
    def _exit_code(self, argv, **env):
        import subprocess
        script = Path(__file__).resolve().parent.parent / "scripts" / "publish_catalog.py"
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run(
                [sys.executable, str(script), *argv], cwd=tmp,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).returncode

    def test_exits_zero_with_nothing_available(self):
        self.assertEqual(self._exit_code([]), 0)

    def test_size_exits_zero_with_no_catalog(self):
        self.assertEqual(self._exit_code(["--size"]), 0)

    def test_run_swallows_a_publishing_failure(self):
        with mock.patch.object(pc, "read_cache", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                pc.run([])  # run() itself propagates; only __main__ swallows

    def test_number_key_never_raises_on_odd_numbers(self):
        for number in ("", None, "170/181", "SWSH066", "TG12/TG30", "H1", "???", "1"):
            pc.number_key(number, "x")


class TestNumberKey(unittest.TestCase):
    def test_numeric_order_beats_string_order(self):
        rows = ["10/181", "2/181", "100/181"]
        self.assertEqual(sorted(rows, key=lambda n: pc.number_key(n)),
                         ["2/181", "10/181", "100/181"])

    def test_alpha_prefixes_group_together(self):
        rows = ["TG12", "1", "TG2", "SWSH066"]
        self.assertEqual(sorted(rows, key=lambda n: pc.number_key(n)),
                         ["1", "SWSH066", "TG2", "TG12"])

    def test_name_breaks_ties(self):
        self.assertLess(pc.number_key("1/10", "Abra"), pc.number_key("1/10", "Zubat"))


if __name__ == "__main__":
    unittest.main()
