"""Unit tests for scripts/record_card_history.py — the per-card daily series
that feeds ROADMAP item 4 (portfolio vs. the index) and the app's sparklines.

Covers: append, idempotent replace, null-when-untrusted, basket churn,
guardWindows exclusion, file format, corrupt-input tolerance, and the
never-fail-the-build contract. No network, no git writes.

Run: python3 -m unittest discover tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import record_card_history as rch  # noqa: E402


def card(pid, price, trusted=True, **extra):
    out = {"id": pid, "name": f"Card {pid}", "price": price, "trusted": trusted}
    out.update(extra)
    return out


def make_latest(as_of, constituents, **extra):
    out = {
        "sample": False,
        "asOfDate": as_of,
        "constituents": constituents,
        "guardWindows": {"999": [10.0, 10.0]},
    }
    out.update(extra)
    return out


class TempDataMixin:
    """Point the module's data paths into a temp dir per test."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        (base / "docs" / "data").mkdir(parents=True)
        self.latest_path = base / "docs" / "data" / "latest.json"
        self.cards_path = base / "docs" / "data" / "cards_history.json"
        patches = [
            mock.patch.object(rch, "DATA_DIR", str(base / "docs" / "data")),
            mock.patch.object(rch, "LATEST_PATH", str(self.latest_path)),
            mock.patch.object(rch, "CARDS_PATH", str(self.cards_path)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def write_latest(self, latest):
        self.latest_path.write_text(json.dumps(latest), encoding="utf-8")

    def read_cards(self):
        return json.loads(self.cards_path.read_text(encoding="utf-8"))


class TestPricesFromLatest(unittest.TestCase):
    def test_trusted_price_is_recorded_rounded(self):
        latest = make_latest("2026-07-15", [card("1", 100.005)])
        self.assertEqual(rch.prices_from_latest(latest), {"1": 100.0})

    def test_untrusted_price_is_null_not_carried(self):
        latest = make_latest("2026-07-15", [card("1", 100.0, trusted=False)])
        self.assertEqual(rch.prices_from_latest(latest), {"1": None})

    def test_missing_trusted_flag_is_null(self):
        latest = make_latest("2026-07-15", [{"id": "1", "price": 100.0}])
        self.assertEqual(rch.prices_from_latest(latest), {"1": None})

    def test_zero_or_missing_price_is_null(self):
        latest = make_latest("2026-07-15", [card("1", 0), card("2", None)])
        self.assertEqual(rch.prices_from_latest(latest), {"1": None, "2": None})

    def test_guard_windows_are_ignored(self):
        latest = make_latest("2026-07-15", [card("1", 100.0)])
        self.assertNotIn("999", rch.prices_from_latest(latest))

    def test_ids_are_strings(self):
        latest = make_latest("2026-07-15", [card(183899, 100.0)])
        self.assertEqual(list(rch.prices_from_latest(latest)), ["183899"])

    def test_only_ids_filters_the_basket(self):
        latest = make_latest("2026-07-15", [card("1", 100.0), card("2", 200.0)])
        self.assertEqual(rch.prices_from_latest(latest, only_ids={"2"}), {"2": 200.0})


class TestRecord(unittest.TestCase):
    def test_append_builds_aligned_series(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0, "2": 20.0})
        rch.record(store, "2026-07-16", {"1": 11.0, "2": 21.0})
        self.assertEqual(store["dates"], ["2026-07-15", "2026-07-16"])
        self.assertEqual(store["cards"], {"1": [10.0, 11.0], "2": [20.0, 21.0]})

    def test_dates_stay_sorted_when_recorded_out_of_order(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-16", {"1": 11.0})
        rch.record(store, "2026-07-15", {"1": 10.0})
        self.assertEqual(store["dates"], ["2026-07-15", "2026-07-16"])
        self.assertEqual(store["cards"]["1"], [10.0, 11.0])

    def test_rerunning_a_date_replaces_never_duplicates(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0})
        rch.record(store, "2026-07-15", {"1": 12.5})
        self.assertEqual(store["dates"], ["2026-07-15"])
        self.assertEqual(store["cards"]["1"], [12.5])

    def test_replacing_a_date_nulls_cards_that_left_the_basket(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0, "2": 20.0})
        rch.record(store, "2026-07-15", {"1": 10.0})
        self.assertEqual(store["cards"]["2"], [None])

    def test_card_absent_that_day_is_null(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0, "2": 20.0})
        rch.record(store, "2026-07-16", {"1": 11.0})
        self.assertEqual(store["cards"]["2"], [20.0, None])

    def test_new_card_backfills_nulls_for_earlier_dates(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0})
        rch.record(store, "2026-07-16", {"1": 11.0, "2": 99.0})
        self.assertEqual(store["cards"]["2"], [None, 99.0])

    def test_every_series_matches_dates_length(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0})
        rch.record(store, "2026-07-16", {"2": 20.0})
        rch.record(store, "2026-07-17", {"1": 12.0, "3": 30.0})
        n = len(store["dates"])
        for series in store["cards"].values():
            self.assertEqual(len(series), n)

    def test_prune_drops_all_null_rows(self):
        store = rch.empty_store()
        rch.record(store, "2026-07-15", {"1": 10.0, "2": None})
        rch.prune(store)
        self.assertEqual(list(store["cards"]), ["1"])


class TestNormalize(unittest.TestCase):
    def test_garbage_becomes_an_empty_store(self):
        for junk in (None, [], "nope", {"dates": "x", "cards": {}}, {"dates": [], "cards": []}):
            self.assertEqual(rch.normalize(junk)["dates"], [])
            self.assertEqual(rch.normalize(junk)["cards"], {})

    def test_short_and_long_series_are_realigned(self):
        store = rch.normalize({
            "dates": ["a", "b", "c"],
            "cards": {"1": [1.0], "2": [1.0, 2.0, 3.0, 4.0]},
        })
        self.assertEqual(store["cards"]["1"], [1.0, None, None])
        self.assertEqual(store["cards"]["2"], [1.0, 2.0, 3.0])

    def test_non_numeric_cells_become_null(self):
        store = rch.normalize({"dates": ["a", "b"], "cards": {"1": ["x", True]}})
        self.assertEqual(store["cards"]["1"], [None, None])


class TestRunDaily(TempDataMixin, unittest.TestCase):
    def test_first_run_creates_the_file_in_the_documented_shape(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0), card("2", 20.0)]))
        rch.run_daily()
        out = self.read_cards()
        self.assertEqual(sorted(out), ["cards", "dates", "generated"])
        self.assertEqual(out["dates"], ["2026-07-15"])
        self.assertEqual(out["cards"], {"1": [10.0], "2": [20.0]})
        self.assertIsInstance(out["generated"], str)

    def test_second_day_appends(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        self.write_latest(make_latest("2026-07-16", [card("1", 11.0)]))
        rch.run_daily()
        out = self.read_cards()
        self.assertEqual(out["dates"], ["2026-07-15", "2026-07-16"])
        self.assertEqual(out["cards"]["1"], [10.0, 11.0])

    def test_same_day_rerun_is_idempotent(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        rch.run_daily()
        rch.run_daily()
        out = self.read_cards()
        self.assertEqual(out["dates"], ["2026-07-15"])
        self.assertEqual(out["cards"]["1"], [10.0])

    def test_untrusted_day_records_null_not_the_stale_price(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        self.write_latest(make_latest("2026-07-16", [card("1", 10.0, trusted=False)]))
        rch.run_daily()
        self.assertEqual(self.read_cards()["cards"]["1"], [10.0, None])

    def test_file_is_written_compactly(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        raw = self.cards_path.read_text(encoding="utf-8")
        self.assertNotIn("\n", raw)
        self.assertNotIn(", ", raw)

    def test_missing_latest_writes_nothing(self):
        rch.run_daily()
        self.assertFalse(self.cards_path.exists())

    def test_sample_latest_is_ignored(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)], sample=True))
        rch.run_daily()
        self.assertFalse(self.cards_path.exists())

    def test_latest_without_asofdate_writes_nothing(self):
        self.write_latest({"sample": False, "constituents": [card("1", 10.0)]})
        rch.run_daily()
        self.assertFalse(self.cards_path.exists())

    def test_corrupt_store_is_rebuilt_not_fatal(self):
        self.cards_path.write_text("{not json", encoding="utf-8")
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        self.assertEqual(self.read_cards()["cards"]["1"], [10.0])


class TestNeverFailsTheBuild(unittest.TestCase):
    """The whole point of this script: it can never turn the daily build red.

    Run the real file as a subprocess from a copy planted in a throwaway
    directory, so its REPO_ROOT is not a git repo and its data files are
    missing/corrupt. Every path must still exit 0.
    """

    def run_script(self, *args, latest=None):
        import shutil
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "docs" / "data").mkdir(parents=True)
            script = root / "scripts" / "record_card_history.py"
            shutil.copyfile(rch.__file__, script)
            if latest is not None:
                (root / "docs" / "data" / "latest.json").write_text(latest, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(script), *args],
                capture_output=True, text=True, cwd=str(root),
            )

    def test_daily_exits_zero_with_no_data_at_all(self):
        self.assertEqual(self.run_script().returncode, 0)

    def test_daily_exits_zero_on_corrupt_latest(self):
        self.assertEqual(self.run_script(latest="{not json").returncode, 0)

    def test_backfill_exits_zero_outside_a_git_repo(self):
        latest = json.dumps(make_latest("2026-07-15", [card("1", 10.0)]))
        self.assertEqual(self.run_script("--backfill", latest=latest).returncode, 0)

    def test_size_exits_zero_with_no_file(self):
        self.assertEqual(self.run_script("--size").returncode, 0)


class TestBackfill(TempDataMixin, unittest.TestCase):
    def fake_git(self, snapshots):
        """snapshots: [(sha, latest_dict)] in git-log order (newest first)."""
        shas = "\n".join(sha for sha, _ in snapshots)
        blobs = {f"{sha}:{rch.LATEST_GIT_PATH}": json.dumps(obj) for sha, obj in snapshots}

        def _git(*args):
            if args[0] == "log":
                return shas
            if args[0] == "show":
                return blobs[args[1]]
            raise AssertionError(f"unexpected git call: {args}")

        return mock.patch.object(rch, "git", side_effect=_git)

    def test_newest_commit_per_date_wins(self):
        snapshots = [
            ("c", make_latest("2026-07-16", [card("1", 12.0)])),
            ("b", make_latest("2026-07-15", [card("1", 11.0)])),  # newer of the two
            ("a", make_latest("2026-07-15", [card("1", 10.0)])),
        ]
        self.write_latest(make_latest("2026-07-16", [card("1", 12.0)]))
        with self.fake_git(snapshots):
            rch.run_backfill()
        out = self.read_cards()
        self.assertEqual(out["dates"], ["2026-07-15", "2026-07-16"])
        self.assertEqual(out["cards"]["1"], [11.0, 12.0])

    def test_backfill_is_limited_to_the_current_basket(self):
        snapshots = [("a", make_latest("2026-07-15", [card("1", 10.0), card("2", 20.0)]))]
        self.write_latest(make_latest("2026-07-16", [card("1", 12.0)]))
        with self.fake_git(snapshots):
            rch.run_backfill()
        self.assertEqual(list(self.read_cards()["cards"]), ["1"])

    def test_all_untrusted_column_is_skipped(self):
        snapshots = [
            ("b", make_latest("2026-07-16", [card("1", 12.0)])),
            ("a", make_latest("2026-07-15", [card("1", 10.0, trusted=False)])),
        ]
        self.write_latest(make_latest("2026-07-16", [card("1", 12.0)]))
        with self.fake_git(snapshots):
            rch.run_backfill()
        self.assertEqual(self.read_cards()["dates"], ["2026-07-16"])

    def test_backfill_does_not_clobber_an_already_recorded_date(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 99.0)]))
        rch.run_daily()
        snapshots = [("a", make_latest("2026-07-15", [card("1", 10.0)]))]
        with self.fake_git(snapshots):
            rch.run_backfill()
        self.assertEqual(self.read_cards()["cards"]["1"], [99.0])

    def test_backfill_is_rerunnable(self):
        snapshots = [("a", make_latest("2026-07-15", [card("1", 10.0)]))]
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        with self.fake_git(snapshots):
            rch.run_backfill()
            rch.run_backfill()
        out = self.read_cards()
        self.assertEqual(out["dates"], ["2026-07-15"])
        self.assertEqual(out["cards"]["1"], [10.0])


class TestSizeReport(TempDataMixin, unittest.TestCase):
    def test_reports_missing_file(self):
        self.assertIn("does not exist", rch.size_report(str(self.cards_path)))

    def test_projects_one_year(self):
        self.write_latest(make_latest("2026-07-15", [card("1", 10.0)]))
        rch.run_daily()
        self.assertIn("at 1 year", rch.size_report(str(self.cards_path)))


if __name__ == "__main__":
    unittest.main()
