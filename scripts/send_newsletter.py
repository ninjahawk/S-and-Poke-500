#!/usr/bin/env python3
"""Send the weekly S&Poké 500 market-recap email via Buttondown.

Runs as the final step of the update-index workflow (stdlib only, like
build_index.py). It exits 0 as a no-op unless ALL of these hold:

  1. BUTTONDOWN_API_KEY is set — a repo Actions secret the owner adds once
     Buttondown approves the account. Until then every run skips silently.
  2. latest.json was built from TODAY's TCGCSV snapshot (sourceStamp date ==
     today UTC). The early-morning builds that append a point from
     yesterday's snapshot must NOT email: the real market data lands ~20:05
     UTC and the ~20:23 build is the one that counts as the "close".
  3. It's issue day: the very first issue goes out on the first fresh build
     after the key is added; after that, Fridays only (with a catch-up send
     if a Friday run was missed).
  4. No email for this issue was already sent (subject check via the API),
     so same-day workflow re-runs can't double-send.

Weekly numbers come from two places: the index's week-over-week change from
history.json, and per-card weekly movers from newsletter_state.json — a
baseline of each constituent's price captured when the previous issue was
sent (the workflow commits it after a send). The first issue has no baseline,
so it carries the index change only; movers start with issue #2.

API: https://docs.buttondown.com/api-emails-introduction
Note: if Buttondown gates the emails API behind a paid plan, the POST will
fail with 401/402/403 — the error text below says what to do.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

API = "https://api.buttondown.com/v1/emails"
SITE = "https://xn--pok500-dva.com/"
SITE_NAME = "poké500.com"
DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
LATEST = DATA_DIR / "latest.json"
HISTORY = DATA_DIR / "history.json"
STATE = DATA_DIR / "newsletter_state.json"
MOVERS_SHOWN = 3
FRIDAY = 4  # date.weekday()


def api_request(key, url, payload=None):
    headers = {
        "Authorization": f"Token {key}",
        "Content-Type": "application/json",
        # Pin the API version so Buttondown-side default changes can't alter
        # behavior under us.
        "X-API-Version": "2026-04-01",
    }
    if payload is not None:
        # As of API 2026-04-01, the first-ever POST with status
        # "about_to_send" on a key is rejected with 400
        # sending_requires_confirmation unless this opt-in header is present
        # (it's ignored once the key has sent before). Without it the very
        # first automated issue would fail.
        headers["X-Buttondown-Live-Dangerously"] = "true"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def is_issue_day(as_of, state):
    """First issue: any day. After that: Fridays, or 8+ days as catch-up."""
    last = (state or {}).get("lastSentAsOf")
    if not last:
        return True
    days = (date.fromisoformat(as_of) - date.fromisoformat(last)).days
    if days <= 0:
        return False
    return date.fromisoformat(as_of).weekday() == FRIDAY or days >= 8


def week_stats(latest, history, state):
    """Index change since last issue (or ~1 week), range, and card movers."""
    as_of = latest["asOfDate"]
    index = latest["index"]
    baseline = (state or {}).get("baseline")

    points = history["points"] if isinstance(history, dict) else history
    if baseline:
        since = baseline["asOf"]
        change_pct = (index / baseline["index"] - 1.0) * 100.0
        change_label = "since last week's issue"
    else:
        target = date.fromisoformat(as_of).toordinal() - 7
        past = [p for p in points if date.fromisoformat(p["date"]).toordinal() <= target]
        ref = past[-1] if past else points[0]
        since = ref["date"]
        change_pct = (index / ref["index"] - 1.0) * 100.0
        change_label = "over the past week"

    window = [p["index"] for p in points if p["date"] >= since]
    lo, hi = (min(window), max(window)) if window else (index, index)

    gainers, losers = [], []
    if baseline:
        base_prices = baseline["prices"]
        movers = []
        for c in latest["constituents"]:
            base = base_prices.get(c["id"])
            if not base or not c.get("trusted") or not base[1] or base[0] <= 0:
                continue
            pct = (c["price"] / base[0] - 1.0) * 100.0
            if abs(pct) >= 0.005:
                movers.append({**c, "weekPct": pct})
        movers.sort(key=lambda m: m["weekPct"], reverse=True)
        gainers = [m for m in movers if m["weekPct"] > 0][:MOVERS_SHOWN]
        losers = sorted(
            (m for m in movers if m["weekPct"] < 0), key=lambda m: m["weekPct"]
        )[:MOVERS_SHOWN]

    return {
        "changePct": change_pct,
        "changeLabel": change_label,
        "low": lo,
        "high": hi,
        "gainers": gainers,
        "losers": losers,
        "firstIssue": baseline is None,
    }


def mover_lines(movers):
    return "\n".join(
        f"- {m['name']} ({m['setName']}) — ${m['price']:,.2f} "
        f"({m['weekPct']:+.2f}% this week)"
        for m in movers
    )


def compose(latest, history, state):
    as_of = latest["asOfDate"]
    index = latest["index"]
    wk = week_stats(latest, history, state)
    chg = wk["changePct"]
    direction = "up" if chg > 0.005 else "down" if chg < -0.005 else "flat"

    subject = (
        f"S&Poké 500 weekly: {index:,.2f} ({chg:+.2f}%) — week ending {as_of}"
    )

    move_txt = (
        f"{direction} **{abs(chg):.2f}%** {wk['changeLabel']}"
        if direction != "flat"
        else f"flat {wk['changeLabel']}"
    )
    parts = [
        f"The S&Poké 500 closed at **{index:,.2f}** on {as_of}, {move_txt}.",
        f"Week's range: {wk['low']:,.2f} – {wk['high']:,.2f}.",
    ]

    if wk["gainers"]:
        parts.append("**Top gainers this week**\n\n" + mover_lines(wk["gainers"]))
    if wk["losers"]:
        parts.append("**Top decliners this week**\n\n" + mover_lines(wk["losers"]))
    if wk["firstIssue"]:
        parts.append(
            "Per-card weekly movers start with the next issue — this first "
            "one sets the baseline."
        )
    elif not wk["gainers"] and not wk["losers"]:
        parts.append(
            "No confirmed single-card moves this week — vintage prices are "
            "sticky, and only cards with confirmed TCGplayer prices at both "
            "ends of the week count as movers."
        )

    parts.append(
        f"[See the live index, chart, and all 500 cards →]({SITE})"
    )
    parts.append(
        "---\n\n"
        f"The S&Poké 500 is a price-weighted index of the 500 most valuable "
        f"English raw Pokémon singles, priced from TCGplayer market data. "
        f"You're getting this because you subscribed at {SITE_NAME}. "
        f"One email per week. Not financial advice."
    )
    return subject, "\n\n".join(parts)


def save_state(latest):
    STATE.write_text(json.dumps({
        "lastSentAsOf": latest["asOfDate"],
        "baseline": {
            "asOf": latest["asOfDate"],
            "index": latest["index"],
            "prices": {
                c["id"]: [c["price"], bool(c.get("trusted"))]
                for c in latest["constituents"]
            },
        },
    }) + "\n")


def main():
    key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not key:
        print("BUTTONDOWN_API_KEY not set - skipping newsletter (add the "
              "repo secret to enable).")
        return 0

    latest = json.loads(LATEST.read_text())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stamp_day = latest["sourceStamp"][:10]
    if stamp_day != today:
        print(f"Data is from the {stamp_day} snapshot, not today's - "
              "skipping (the post-20:05-UTC build sends the close).")
        return 0

    state = json.loads(STATE.read_text()) if STATE.exists() else None
    as_of = latest["asOfDate"]
    if not is_issue_day(as_of, state):
        print(f"Not an issue day (weekly cadence; last sent "
              f"{state['lastSentAsOf']}) - skipping.")
        return 0

    history = json.loads(HISTORY.read_text())
    subject, body = compose(latest, history, state)

    try:
        recent = api_request(key, f"{API}?page=1")
        sent = {e.get("subject", "") for e in recent.get("results", [])}
        if any(f"week ending {as_of}" in s for s in sent):
            print(f"Already sent the issue for {as_of} - skipping.")
            return 0

        result = api_request(key, API, {
            "subject": subject,
            "body": body,
            "status": "about_to_send",
        })
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        print(f"Buttondown API error {e.code}: {detail}", file=sys.stderr)
        if e.code in (401, 402, 403):
            print("Hint: account still under review, bad API key, or the "
                  "emails API needs a paid Buttondown plan.", file=sys.stderr)
        return 1

    save_state(latest)
    print(f"Sent: {subject!r} (id {result.get('id')}, "
          f"status {result.get('status')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
