#!/usr/bin/env python3
"""Send the S&Poke 500 daily-close email through Buttondown.

Runs right after build_index.py in the daily workflow. Reads the freshly
committed docs/data/latest.json and emails subscribers the closing level,
day change, breadth, and confirmed top movers. Standard library only, same
as the builder, so it needs no pip install on the CI runner.

Safety rails (both can be bypassed with --force for manual testing):
  * Fresh-prices gate: sends only when the TCGCSV snapshot date matches the
    index date (i.e. tonight's ~20:05 UTC drop). Stamp-mismatch rebuilds like
    the 03:43 densify pickup reprice against yesterday's snapshot and would
    email an all-zero "close."
  * Dedupe gate: lists recent Buttondown emails and refuses to send a second
    email whose subject carries the same close date.

Usage:
  BUTTONDOWN_API_KEY=... python3 scripts/send_daily_email.py         # normal
  python3 scripts/send_daily_email.py --dry-run [out.html]           # preview
  BUTTONDOWN_API_KEY=... python3 scripts/send_daily_email.py --force # testing
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LATEST_PATH = os.path.join(HERE, os.pardir, "docs", "data", "latest.json")

API_BASE = "https://api.buttondown.com/v1"
SITE_URL = "https://xn--pok500-dva.com/"
SITE_NAME = "poké500.com"

# Light-theme site palette; email clients overwhelmingly render on white.
INK = "#202124"
MUTED = "#5f6368"
UP = "#137333"
DOWN = "#a50e0e"
RULE = "#dadce0"


def fmt_price(value):
    return "${:,.2f}".format(value)


def fmt_level(value):
    return "{:,.2f}".format(value)


def pretty_date(iso_date):
    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%B %-d, %Y")


def delta_html(change, change_pct, size="15px"):
    up = change >= 0
    color = UP if up else DOWN
    arrow = "&#9650;" if up else "&#9660;"  # ▲ ▼
    sign = "+" if up else "&minus;"
    return (
        f'<span style="color:{color};font-size:{size};font-weight:600;">'
        f"{arrow} {sign}{fmt_level(abs(change))} ({sign}{abs(change_pct):.2f}%)</span>"
    )


def movers_table(title, movers):
    rows = []
    for c in movers[:5]:
        up = c["changePct"] >= 0
        color = UP if up else DOWN
        sign = "+" if up else "&minus;"
        rows.append(
            '<tr>'
            f'<td style="padding:7px 0;border-bottom:1px solid {RULE};">'
            f'<span style="color:{INK};font-size:14px;">{c["name"]}</span><br>'
            f'<span style="color:{MUTED};font-size:12px;">{c.get("setName") or ""}</span></td>'
            f'<td style="padding:7px 0 7px 12px;border-bottom:1px solid {RULE};text-align:right;white-space:nowrap;">'
            f'<span style="color:{INK};font-size:14px;">{fmt_price(c["price"])}</span><br>'
            f'<span style="color:{color};font-size:12.5px;font-weight:600;">{sign}{abs(c["changePct"]):.2f}%</span></td>'
            '</tr>'
        )
    if not rows:
        rows.append(
            f'<tr><td style="padding:7px 0;color:{MUTED};font-size:13.5px;">'
            "No confirmed movers</td></tr>"
        )
    return (
        f'<h3 style="margin:22px 0 2px;font-size:13px;font-weight:600;color:{MUTED};'
        f'text-transform:uppercase;letter-spacing:0.4px;">{title}</h3>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="border-collapse:collapse;">' + "".join(rows) + "</table>"
    )


def render(d):
    """Return (subject, html_body) for the day's close."""
    date_h = pretty_date(d["asOfDate"])
    level = fmt_level(d["index"])
    pct = d["changePct"]
    sign = "+" if d["change"] >= 0 else "−"
    subject = f"S&Poké 500 close: {level} ({sign}{abs(pct):.2f}%) — {date_h}"

    b = d.get("breadth") or {}
    breadth = (
        f'<span style="color:{UP};">{b.get("advancing", 0)} advancing</span> &nbsp;·&nbsp; '
        f'<span style="color:{DOWN};">{b.get("declining", 0)} declining</span> &nbsp;·&nbsp; '
        f'<span style="color:{MUTED};">{b.get("unchanged", 0)} unchanged</span>'
    )

    html = f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;text-align:left;">
  <tr><td style="padding:8px 0 14px;border-bottom:2px solid {INK};">
    <span style="font-size:19px;font-weight:700;color:{INK};">S&amp;Poké&nbsp;500</span>
    <span style="font-size:13px;color:{MUTED};"> &nbsp;Daily close · {date_h}</span>
  </td></tr>
  <tr><td style="padding:24px 0 4px;">
    <span style="font-size:40px;font-weight:700;color:{INK};letter-spacing:-0.5px;">{level}</span>
    &nbsp; {delta_html(d["change"], pct)}
  </td></tr>
  <tr><td style="padding:2px 0 18px;font-size:13px;color:{MUTED};">
    {breadth}<br>
    <span style="font-size:12px;">Breadth and movers count only cards with a confirmed price on both days.</span>
  </td></tr>
  <tr><td>
    {movers_table("Top gainers", d.get("gainers") or [])}
    {movers_table("Top losers", d.get("losers") or [])}
  </td></tr>
  <tr><td style="padding:26px 0 6px;">
    <a href="{SITE_URL}" style="background:#1a73e8;color:#ffffff;text-decoration:none;
       font-size:14px;font-weight:600;padding:10px 22px;border-radius:6px;display:inline-block;">
       View the full index &rarr;</a>
  </td></tr>
  <tr><td style="padding:22px 0 8px;border-top:1px solid {RULE};font-size:12px;color:{MUTED};line-height:1.6;">
    The S&amp;Poké&nbsp;500 is a free, price-weighted index of the 500 most valuable English raw
    Pokémon card singles, priced from TCGplayer market data and updated daily —
    <a href="{SITE_URL}#methodology" style="color:{MUTED};">how these prices work</a>.<br>
    Informational only — not investment advice. Not affiliated with Nintendo, The Pokémon
    Company, TCGplayer, or S&amp;P Global.<br>
    You're receiving this because you subscribed at <a href="{SITE_URL}" style="color:{MUTED};">{SITE_NAME}</a>.
  </td></tr>
</table>
</td></tr></table>
"""
    return subject, html


def api(path, key, payload=None):
    req = urllib.request.Request(
        API_BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Token {key}",
            "Content-Type": "application/json",
            "User-Agent": "spoke500-daily-email",
        },
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def already_sent(key, date_h):
    """True if a Buttondown email for this close date already exists."""
    try:
        listing = api("/emails?ordering=-creation_date&page_size=15", key)
    except Exception as exc:  # fail-open would risk double emails; fail closed
        print(f"Could not list existing emails ({exc}); refusing to send.")
        return True
    return any(date_h in (e.get("subject") or "") for e in listing.get("results", []))


def main():
    argv = sys.argv[1:]
    dry_run = "--dry-run" in argv
    force = "--force" in argv

    with open(LATEST_PATH, encoding="utf-8") as handle:
        d = json.load(handle)

    stamp_date = (d.get("sourceStamp") or "")[:10]
    if stamp_date != d["asOfDate"] and not force:
        print(
            f"Snapshot {stamp_date or 'unknown'} != index date {d['asOfDate']} "
            "(no fresh prices today yet); not sending."
        )
        return

    subject, html = render(d)

    if dry_run:
        out = next((a for a in argv if not a.startswith("--")), "daily-email-preview.html")
        with open(out, "w", encoding="utf-8") as handle:
            handle.write(html)
        print(f"Subject: {subject}\nPreview written to {out}")
        return

    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not key:
        print("BUTTONDOWN_API_KEY not set; skipping email.")
        return

    date_h = pretty_date(d["asOfDate"])
    if not force and already_sent(key, date_h):
        print(f"An email for {date_h} already exists; not sending again.")
        return

    try:
        created = api("/emails", key, {"subject": subject, "body": html, "status": "about_to_send"})
    except urllib.error.HTTPError as exc:
        print(f"Buttondown API error {exc.code}: {exc.read().decode()[:500]}")
        sys.exit(1)
    print(f"Sent: {subject} (id {created.get('id')})")


if __name__ == "__main__":
    main()
