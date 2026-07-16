#!/usr/bin/env python3
"""Send the daily S&Poké 500 "market close" email via Buttondown.

Runs as the final step of the update-index workflow (stdlib only, like
build_index.py). It exits 0 as a no-op unless ALL of these hold:

  1. BUTTONDOWN_API_KEY is set — a repo Actions secret the owner adds once
     Buttondown approves the account. Until then every run skips silently.
  2. latest.json was built from TODAY's TCGCSV snapshot (sourceStamp date ==
     today UTC). The early-morning builds that append a point from
     yesterday's snapshot must NOT email: the real market data lands ~20:05
     UTC and the ~20:23 build is the one that counts as the "close".
  3. No email for this close was already sent (subject check via the API),
     so same-day workflow re-runs can't double-send.

API: https://docs.buttondown.com/api-emails-introduction
Note: if Buttondown gates the emails API behind a paid plan, the POST will
fail with 401/403/402 — the error text below says what to do.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.buttondown.com/v1/emails"
SITE = "https://xn--pok500-dva.com/"
SITE_NAME = "poké500.com"
DATA = Path(__file__).resolve().parent.parent / "docs" / "data" / "latest.json"
MOVERS_SHOWN = 3


def api_request(key, url, payload=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Token {key}",
            "Content-Type": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fmt_price(p):
    return f"${p:,.2f}"


def mover_lines(movers):
    return "\n".join(
        f"- {m['name']} ({m['setName']}) — {fmt_price(m['price'])} "
        f"({m['changePct']:+.2f}%)"
        for m in movers[:MOVERS_SHOWN]
    )


def compose(latest):
    index = latest["index"]
    chg = latest["changePct"]
    as_of = latest["asOfDate"]
    breadth = latest["breadth"]
    direction = "up" if chg > 0 else "down" if chg < 0 else "flat"

    subject = f"S&Poké 500: {index:,.2f} ({chg:+.2f}%) — market close {as_of}"

    move_txt = (
        f"{direction} **{abs(chg):.2f}%** on the day"
        if direction != "flat"
        else "flat on the day"
    )
    parts = [
        f"The S&Poké 500 closed at **{index:,.2f}** on {as_of}, {move_txt}.",
        f"Breadth: {breadth['advancing']} advancing · "
        f"{breadth['declining']} declining · {breadth['unchanged']} unchanged.",
    ]

    gainers, losers = latest.get("gainers", []), latest.get("losers", [])
    if gainers:
        parts.append("**Top gainers**\n\n" + mover_lines(gainers))
    if losers:
        parts.append("**Top decliners**\n\n" + mover_lines(losers))
    if not gainers and not losers:
        parts.append(
            "No confirmed single-card moves today — vintage prices are "
            "sticky, and only cards with a confirmed TCGplayer price on "
            "both days count as movers."
        )

    parts.append(f"[See the full index, chart, and all 500 cards →]({SITE})")
    parts.append(
        "---\n\n"
        f"The S&Poké 500 is a price-weighted index of the 500 most valuable "
        f"English raw Pokémon singles, priced from TCGplayer market data. "
        f"You're getting this because you subscribed at {SITE_NAME}. "
        f"One email per market day. Not financial advice."
    )
    return subject, "\n\n".join(parts)


def main():
    key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not key:
        print("BUTTONDOWN_API_KEY not set - skipping newsletter (add the "
              "repo secret to enable).")
        return 0

    latest = json.loads(DATA.read_text())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stamp_day = latest["sourceStamp"][:10]
    if stamp_day != today:
        print(f"Data is from the {stamp_day} snapshot, not today's - "
              "skipping (the post-20:05-UTC build sends the close).")
        return 0

    subject, body = compose(latest)

    try:
        recent = api_request(key, f"{API}?page=1")
        sent = {e.get("subject", "") for e in recent.get("results", [])}
        if any(f"market close {latest['asOfDate']}" in s for s in sent):
            print(f"Already sent an email for {latest['asOfDate']} - skipping.")
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

    print(f"Sent: {subject!r} (id {result.get('id')}, "
          f"status {result.get('status')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
