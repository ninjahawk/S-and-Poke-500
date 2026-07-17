"""Unit tests for scripts/send_newsletter.py — every send gate and the
composed email, with the Buttondown API fully mocked (no network ever).

Run: python3 -m unittest discover tests
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import send_newsletter as sn  # noqa: E402

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def make_latest(as_of=TODAY, stamp_day=TODAY, index=1254.19, constituents=None):
    return {
        "asOfDate": as_of,
        "sourceStamp": f"{stamp_day}T20:05:04+0000",
        "index": index,
        "constituents": constituents if constituents is not None else [
            {"id": "1", "name": "Card A", "setName": "Set One",
             "price": 100.0, "trusted": True},
            {"id": "2", "name": "Card B", "setName": "Set Two",
             "price": 200.0, "trusted": True},
        ],
    }


def make_history(as_of=TODAY):
    return {"points": [
        {"date": "2026-01-02", "index": 1000.0},
        {"date": "2026-07-05", "index": 1200.0},
        {"date": as_of, "index": 1254.19},
    ]}


def make_state(last_sent, prices=None):
    return {
        "lastSentAsOf": last_sent,
        "baseline": {
            "asOf": last_sent,
            "index": 1240.0,
            "prices": prices or {"1": [90.0, True], "2": [210.0, True]},
        },
    }


class TempDataMixin:
    """Point the module's data paths into a temp dir per test."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.latest_p = base / "latest.json"
        self.history_p = base / "history.json"
        self.state_p = base / "newsletter_state.json"
        for attr, p in (("LATEST", self.latest_p), ("HISTORY", self.history_p),
                        ("STATE", self.state_p)):
            patcher = mock.patch.object(sn, attr, p)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_data(self, latest=None, history=None, state=None):
        self.latest_p.write_text(json.dumps(latest or make_latest()))
        self.history_p.write_text(json.dumps(history or make_history()))
        if state is not None:
            self.state_p.write_text(json.dumps(state))


class GateTests(TempDataMixin, unittest.TestCase):
    def test_gate_no_key_skips_without_network(self):
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": ""}), \
             mock.patch.object(sn, "api_request") as api:
            self.assertEqual(sn.main(), 0)
            api.assert_not_called()

    def test_gate_stale_snapshot_skips(self):
        self.write_data(latest=make_latest(stamp_day="2000-01-01"))
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request") as api:
            self.assertEqual(sn.main(), 0)
            api.assert_not_called()

    def test_gate_not_issue_day_skips(self):
        # Sent 2 days ago; today would have to be Friday AND >0 days for a
        # send — force the not-issue-day branch regardless of weekday.
        self.write_data(state=make_state(TODAY))
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request") as api:
            self.assertEqual(sn.main(), 0)
            api.assert_not_called()

    def test_gate_dedupe_skips_before_post(self):
        self.write_data()
        already = {"results": [{"subject": f"x {sn.issue_anchor(TODAY)} x"}]}
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", return_value=already) as api:
            self.assertEqual(sn.main(), 0)
            api.assert_called_once()  # the GET only, never the POST
            self.assertFalse(self.state_p.exists())

    def test_gate_dedupe_matches_legacy_iso_anchor(self):
        # An issue sent under the old "week ending <ISO date>" subject must
        # still block a same-day re-send after the anchor format change.
        self.write_data()
        already = {"results": [{"subject": f"anything week ending {TODAY} x"}]}
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", return_value=already) as api:
            self.assertEqual(sn.main(), 0)
            api.assert_called_once()
            self.assertFalse(self.state_p.exists())


class SendPathTests(TempDataMixin, unittest.TestCase):
    def run_main(self):
        calls = []

        def fake_api(key, url, payload=None):
            calls.append((url, payload))
            if payload is None:
                return {"results": []}
            return {"id": "em_1", "status": "about_to_send"}

        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", side_effect=fake_api):
            rc = sn.main()
        return rc, calls

    def test_first_issue_sends_and_saves_state(self):
        self.write_data()
        rc, calls = self.run_main()
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)  # GET then POST
        url, payload = calls[1]
        self.assertEqual(payload["status"], "about_to_send")
        self.assertIn(sn.issue_anchor(TODAY), payload["subject"])
        self.assertIn("1,254.19", payload["body"])
        state = json.loads(self.state_p.read_text())
        self.assertEqual(state["lastSentAsOf"], TODAY)
        self.assertEqual(state["baseline"]["prices"]["1"], [100.0, True])

    def test_http_error_returns_1_and_keeps_no_state(self):
        self.write_data()
        import urllib.error
        err = urllib.error.HTTPError("u", 402, "payment", {},
                                     __import__("io").BytesIO(b"denied"))
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", side_effect=err):
            self.assertEqual(sn.main(), 1)
        self.assertFalse(self.state_p.exists())


class IssueDayTests(unittest.TestCase):
    def test_first_issue_any_day(self):
        self.assertTrue(sn.is_issue_day("2026-07-15", None))  # a Wednesday
        self.assertTrue(sn.is_issue_day("2026-07-15", {}))

    def test_friday_sends(self):
        self.assertTrue(
            sn.is_issue_day("2026-07-17", {"lastSentAsOf": "2026-07-15"}))

    def test_non_friday_skips_within_week(self):
        self.assertFalse(
            sn.is_issue_day("2026-07-16", {"lastSentAsOf": "2026-07-15"}))

    def test_catchup_after_8_days(self):
        self.assertTrue(
            sn.is_issue_day("2026-07-23", {"lastSentAsOf": "2026-07-15"}))

    def test_same_day_never_resends(self):
        self.assertFalse(
            sn.is_issue_day("2026-07-17", {"lastSentAsOf": "2026-07-17"}))


class SubjectTests(unittest.TestCase):
    def test_anchor_is_human_readable_and_unique_per_date(self):
        self.assertEqual(sn.issue_anchor("2026-07-17"),
                         "week ending Jul 17, 2026")

    def test_subject_frontloads_move_and_ends_with_anchor(self):
        self.assertEqual(
            sn.issue_subject(1.234, "2026-07-17"),
            "Pokémon cards rose 1.23% this week — week ending Jul 17, 2026")
        self.assertIn("fell 0.50%", sn.issue_subject(-0.5, "2026-07-17"))
        flat = sn.issue_subject(0.0, "2026-07-17")
        self.assertIn("held steady", flat)
        self.assertNotIn("%", flat)


class PreviewTests(unittest.TestCase):
    """issue_preview feeds Buttondown's `description` (the preheader).
    Its whole job is to NOT repeat the subject in the inbox."""

    def test_leads_with_top_gainer_when_movers_exist(self):
        wk = {"gainers": [{"name": "Card A"}], "losers": [{"name": "Card B"}]}
        p = sn.issue_preview(wk)
        self.assertTrue(p.startswith("Card A"))
        self.assertNotIn("week ending", p)

    def test_falls_back_to_top_loser_then_generic(self):
        self.assertTrue(sn.issue_preview(
            {"gainers": [], "losers": [{"name": "Card B"}]}).startswith("Card B"))
        generic = sn.issue_preview({"gainers": [], "losers": []})
        self.assertNotIn("week ending", generic)
        # reader-facing copy rules (owner): never index-internals jargon
        for banned in ("baseline", "per-card"):
            self.assertNotIn(banned, generic.lower())

    def test_never_equals_subject(self):
        wk = {"gainers": [], "losers": []}
        self.assertNotEqual(sn.issue_preview(wk),
                            sn.issue_subject(1.0, "2026-07-17"))


class ComposeTests(unittest.TestCase):
    def test_first_issue_has_movers_teaser_and_no_movers(self):
        subject, body = sn.compose(make_latest(), make_history(), None)
        self.assertIn(sn.issue_anchor(TODAY), subject)  # dedupe anchor
        self.assertIn("1,254.19", body)
        self.assertIn("Starting next Friday", body)
        self.assertNotIn("baseline", body)  # no pipeline jargon in copy
        self.assertNotIn("Top gainers", body)
        self.assertIn(sn.SITE, body)

    def test_weekly_movers_only_trusted_and_capped(self):
        cons = [
            {"id": str(i), "name": f"C{i}", "setName": "S",
             "price": 100.0 + i, "trusted": True}
            for i in range(6)
        ]
        cons.append({"id": "u", "name": "Untrusted", "setName": "S",
                     "price": 500.0, "trusted": False})
        prices = {str(i): [100.0, True] for i in range(6)}
        prices["u"] = [100.0, True]
        latest = make_latest(constituents=cons)
        subject, body = sn.compose(latest, make_history(),
                                   make_state("2026-07-10", prices))
        self.assertIn("Top gainers", body)
        self.assertNotIn("Untrusted", body)
        # capped at MOVERS_SHOWN gainers
        self.assertEqual(body.count("this week)"), sn.MOVERS_SHOWN)

    def test_flat_week_wording(self):
        latest = make_latest(index=1240.0)
        state = make_state("2026-07-10", {"1": [100.0, True]})
        latest["constituents"] = [{"id": "1", "name": "Card A", "setName": "S",
                                   "price": 100.0, "trusted": True}]
        subject, body = sn.compose(latest, make_history(), state)
        self.assertIn("flat", body)


class ComposeRichTests(unittest.TestCase):
    CHART = "https://example.test/chart.png"

    def test_subject_keeps_dedupe_anchor_and_direction_verb(self):
        subject, body = sn.compose_rich(make_latest(), make_history(), None,
                                        self.CHART)
        self.assertIn(sn.issue_anchor(TODAY), subject)
        self.assertIn("rose", subject)
        self.assertIn(self.CHART, body)

    def test_first_issue_no_movers_but_teaser(self):
        _, body = sn.compose_rich(make_latest(), make_history(), None,
                                  self.CHART)
        self.assertNotIn("Top gainers", body)
        self.assertIn("Starting next Friday", body)
        self.assertNotIn("baseline", body)
        self.assertIn("1,254.19", body)

    def test_site_linked_from_hero_button_and_footer(self):
        _, body = sn.compose_rich(make_latest(), make_history(), None,
                                  self.CHART)
        self.assertGreaterEqual(body.count(f'href="{sn.SITE}"'), 3)
        self.assertIn(sn.SITE_NAME, body)

    def test_reader_links_are_ascii_chart_url_is_canonical(self):
        # Punycode URLs in email bodies trip phishing heuristics
        # (DELIVERABILITY.md): reader-facing links must use the ASCII
        # alias, while the chart is published/polled on the canonical
        # Pages domain so sending never depends on the alias redirect.
        self.assertNotIn("xn--", sn.SITE)
        self.assertIn("xn--", sn.SITE_CANONICAL)
        for state in (None, make_state("2026-07-10", {"1": [100.0, True]})):
            _, rich = sn.compose_rich(make_latest(), make_history(), state,
                                      self.CHART)
            self.assertNotIn("xn--", rich)
            _, plain = sn.compose(make_latest(), make_history(), state)
            self.assertNotIn("xn--", plain)

    def test_movers_render_with_baseline_untrusted_excluded(self):
        cons = [
            {"id": "1", "name": "Winner", "setName": "S", "price": 110.0,
             "trusted": True, "image": "https://img/x.jpg"},
            {"id": "2", "name": "Untrusted", "setName": "S", "price": 300.0,
             "trusted": False},
        ]
        prices = {"1": [100.0, True], "2": [100.0, True]}
        _, body = sn.compose_rich(make_latest(constituents=cons),
                                  make_history(),
                                  make_state("2026-07-10", prices), self.CHART)
        self.assertIn("Winner", body)
        self.assertIn("https://img/x.jpg", body)
        self.assertNotIn("Untrusted", body)

    def test_flat_week_wording(self):
        latest = make_latest(index=1240.0)
        latest["constituents"] = []
        state = make_state("2026-07-10", {})
        subject, _ = sn.compose_rich(latest, make_history(), state, self.CHART)
        self.assertIn("held steady", subject)
        self.assertNotIn("%", subject.split("—")[0])


class RichPathSelectionTests(TempDataMixin, unittest.TestCase):
    def run_main(self, chart_ok, publish_ok=True):
        calls = []

        def fake_api(key, url, payload=None):
            calls.append((url, payload))
            return {"results": []} if payload is None else {"id": "e", "status": "about_to_send"}

        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", side_effect=fake_api), \
             mock.patch.object(sn, "render_chart", return_value=chart_ok), \
             mock.patch.object(sn, "publish_chart", return_value=publish_ok) as pub:
            rc = sn.main()
        return rc, calls, pub

    def test_rich_body_when_chart_succeeds(self):
        self.write_data()
        rc, calls, _ = self.run_main(chart_ok=True)
        self.assertEqual(rc, 0)
        payload = calls[-1][1]
        self.assertIn("<img", payload["body"])
        self.assertIn(sn.issue_anchor(TODAY), payload["subject"])
        # preheader rides along and is not a subject repeat
        self.assertTrue(payload["description"])
        self.assertNotEqual(payload["description"], payload["subject"])

    def test_plain_fallback_when_render_fails(self):
        self.write_data()
        rc, calls, pub = self.run_main(chart_ok=False)
        self.assertEqual(rc, 0)
        payload = calls[-1][1]
        self.assertNotIn("<img", payload["body"])
        self.assertIn(sn.issue_anchor(TODAY), payload["subject"])
        pub.assert_not_called()  # no publish attempt without a rendered chart

    def test_plain_fallback_when_publish_fails(self):
        self.write_data()
        rc, calls, _ = self.run_main(chart_ok=True, publish_ok=False)
        self.assertEqual(rc, 0)
        self.assertNotIn("<img", calls[-1][1]["body"])

    def test_no_chart_work_when_already_sent(self):
        self.write_data()
        already = {"results": [{"subject": f"x week ending {TODAY}"}]}
        with mock.patch.dict("os.environ", {"BUTTONDOWN_API_KEY": "k"}), \
             mock.patch.object(sn, "api_request", return_value=already), \
             mock.patch.object(sn, "render_chart") as rc_mock:
            self.assertEqual(sn.main(), 0)
            rc_mock.assert_not_called()


class RenderChartTests(unittest.TestCase):
    def test_renders_real_png_with_dense_week(self):
        import tempfile
        pts = {"points": [
            {"date": f"2026-07-{d:02d}", "index": 1240.0 + d} for d in range(9, 17)
        ]}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "c.png"
            ok = sn.render_chart(pts, "2026-07-16", out)
            self.assertTrue(ok)
            self.assertGreater(out.stat().st_size, 5000)
            self.assertEqual(out.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_too_few_points_returns_false(self):
        pts = {"points": [{"date": "2026-07-16", "index": 1250.0}]}
        self.assertFalse(sn.render_chart(pts, "2026-07-16", Path("/tmp/x.png")))


class ApiRequestHeaderTests(unittest.TestCase):
    def capture(self, payload):
        captured = {}

        class FakeResp:
            def read(self):
                return b"{}"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout=None):
            captured["headers"] = dict(req.header_items())
            captured["method"] = req.get_method()
            return FakeResp()

        with mock.patch.object(sn.urllib.request, "urlopen", fake_urlopen):
            sn.api_request("KEY", sn.API, payload)
        return captured

    def test_get_pins_version_no_danger_header(self):
        c = self.capture(None)
        self.assertEqual(c["method"], "GET")
        headers = {k.lower(): v for k, v in c["headers"].items()}
        self.assertEqual(headers["x-api-version"], "2026-04-01")
        self.assertNotIn("x-buttondown-live-dangerously", headers)

    def test_post_carries_danger_header(self):
        c = self.capture({"a": 1})
        self.assertEqual(c["method"], "POST")
        headers = {k.lower(): v for k, v in c["headers"].items()}
        self.assertEqual(headers["x-buttondown-live-dangerously"], "true")


if __name__ == "__main__":
    unittest.main()
