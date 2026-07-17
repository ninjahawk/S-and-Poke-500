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

The issue is a rich HTML email (Google-Finance-style: headline close, the
week's chart as a hosted PNG, stat rows, mover rows with card thumbnails).
The chart is rendered with matplotlib (installed by the workflow), committed
to docs/email/ and served by Pages; the send waits until the image URL is
live so no subscriber can open the email before its chart exists. If ANY
part of the rich path fails (matplotlib missing, render error, push or
deploy timeout), the issue falls back to the plain-markdown compose — a
plain but correct email always beats a broken pretty one. Subjects in both
formats end with the issue_anchor() substring ("week ending <Mon D, YYYY>"):
the already-sent dedupe gate matches on it (and on the legacy ISO-date form,
in case an issue sent before this format change gets a same-day re-run).

API: https://docs.buttondown.com/api-emails-introduction
Note: if Buttondown gates the emails API behind a paid plan, the POST will
fail with 401/402/403 — the error text below says what to do.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

API = "https://api.buttondown.com/v1/emails"
SITE = "https://xn--pok500-dva.com/"
SITE_NAME = "poké500.com"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "docs" / "data"
EMAIL_DIR = ROOT / "docs" / "email"
LATEST = DATA_DIR / "latest.json"
HISTORY = DATA_DIR / "history.json"
STATE = DATA_DIR / "newsletter_state.json"
MOVERS_SHOWN = 3
FRIDAY = 4  # date.weekday()
DEPLOY_TIMEOUT_S = 240  # max wait for Pages to serve the chart

# Email palette: mid-tone colors that read on BOTH Gmail light and dark
# mode (dark mode inverts surfaces but not images or explicit text colors).
GREEN, RED = "#188038", "#c5221f"
CHART_GREEN, CHART_RED = "#34a853", "#ea4335"
BLUE, MUTED, HAIR = "#1a73e8", "#80868b", "#dadce033"


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
        "refIndex": baseline["index"] if baseline else ref["index"],
        "low": lo,
        "high": hi,
        "gainers": gainers,
        "losers": losers,
        "firstIssue": baseline is None,
    }


def friendly_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%A, %B ") + str(d.day)


def issue_anchor(iso):
    """Dedupe anchor, unique per close date, human-readable because
    Buttondown renders the subject as the email's visible headline."""
    d = date.fromisoformat(iso)
    return f"week ending {d.strftime('%b')} {d.day}, {d.year}"


def issue_subject(chg, as_of):
    """One subject for both compose paths. Inbox research: front-load a
    concrete number (mobile truncates ~35 chars), plain statement over
    cleverness for a finance audience; the anchor rides at the end."""
    verb = "rose" if chg > 0.005 else "fell" if chg < -0.005 else "held steady"
    amount = "" if verb == "held steady" else f" {abs(chg):.2f}%"
    return f"Pokémon cards {verb}{amount} this week — {issue_anchor(as_of)}"


def mover_lines(movers):
    return "\n".join(
        f"- **{m['name']}** · {m['setName']} — ${m['price']:,.2f} "
        f"(**{m['weekPct']:+.2f}%** this week)"
        for m in movers
    )


def compose(latest, history, state):
    """Markdown body, styled for Buttondown's default email template.

    Design notes (owner asked for "very nice looking"): a big H1 close the
    reader sees before scrolling, the site's ▲/▼ triangles for brand
    consistency, movers as bolded lists (lists survive every email client;
    markdown tables don't), and a quiet one-line footer. The subject MUST
    end with issue_anchor(as_of) — the already-sent dedupe gate matches
    on it.
    """
    as_of = latest["asOfDate"]
    index = latest["index"]
    wk = week_stats(latest, history, state)
    chg = wk["changePct"]
    direction = "up" if chg > 0.005 else "down" if chg < -0.005 else "flat"

    subject = issue_subject(chg, as_of)

    tri = {"up": "▲", "down": "▼", "flat": "—"}[direction]
    headline = f"# {index:,.2f} {tri} {abs(chg):.2f}%"
    move_txt = (
        f"**{direction} {abs(chg):.2f}%** {wk['changeLabel']}"
        if direction != "flat"
        else f"**flat** {wk['changeLabel']}"
    )
    parts = [
        headline,
        f"The S&Poké 500 closed at **{index:,.2f}** on "
        f"{friendly_date(as_of)}, {move_txt}.",
        f"**Week's range:** {wk['low']:,.2f} – {wk['high']:,.2f}",
    ]

    if wk["gainers"]:
        parts.append("### ▲ Top gainers this week\n\n" + mover_lines(wk["gainers"]))
    if wk["losers"]:
        parts.append("### ▼ Top decliners this week\n\n" + mover_lines(wk["losers"]))
    if wk["firstIssue"]:
        parts.append(
            "Starting next Friday: the week's biggest gainers and losers, "
            "card by card."
        )
    elif not wk["gainers"] and not wk["losers"]:
        parts.append(
            "No confirmed single-card moves this week — vintage prices are "
            "sticky, and only cards with confirmed TCGplayer prices at both "
            "ends of the week count as movers."
        )

    parts.append(
        f"[**See the live index, chart, and all 500 cards →**]({SITE})"
    )
    parts.append(
        "---\n\n"
        f"The S&Poké 500 is a price-weighted index of the 500 most valuable "
        f"English raw Pokémon singles, priced from TCGplayer market data. "
        f"You're getting this because you subscribed at {SITE_NAME}. "
        f"Sent every Friday. Not financial advice."
    )
    return subject, "\n\n".join(parts)


def render_chart(history, as_of, out_path):
    """Draw the week's line chart as a transparent PNG. False on any failure
    (matplotlib missing, bad data) — the caller falls back to plain text."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter

        points = history["points"] if isinstance(history, dict) else history
        start = date.fromisoformat(as_of).toordinal() - 8
        week = [p for p in points
                if date.fromisoformat(p["date"]).toordinal() >= start
                and p["date"] <= as_of]
        if len(week) < 2:
            return False
        xs = [date.fromisoformat(p["date"]) for p in week]
        ys = [p["index"] for p in week]
        line = CHART_GREEN if ys[-1] >= ys[0] else CHART_RED
        gray = "#9096a0"

        fig, ax = plt.subplots(figsize=(11.2, 3.4), dpi=100)
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.plot(xs, ys, color=line, linewidth=3.4, solid_capstyle="round", zorder=3)
        pad = (max(ys) - min(ys)) or max(ys) * 0.01
        ax.fill_between(xs, ys, min(ys) - pad * 0.35, color=line, alpha=0.10, zorder=1)
        ax.scatter([xs[-1]], [ys[-1]], s=90, color=line, zorder=4)
        ax.scatter([xs[-1]], [ys[-1]], s=280, color=line, alpha=0.22, zorder=4)
        ax.axhline(ys[0], color=gray, linestyle=(0, (4, 4)), linewidth=1.4,
                   alpha=0.55, zorder=2)
        ax.set_ylim(min(ys) - pad * 0.35, max(ys) + pad * 0.3)
        ax.set_xlim(xs[0], xs[-1])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.grid(axis="y", color=gray, alpha=0.18, linewidth=1.2)
        ax.set_axisbelow(True)
        ax.tick_params(colors=gray, labelsize=15, length=0, pad=8)
        ax.yaxis.tick_right()
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%a"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.tight_layout(pad=1.2)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=100, transparent=True)
        plt.close(fig)
        return True
    except Exception as e:  # any failure -> plain-text fallback, never a crash
        print(f"chart render failed ({e!r}) - falling back to plain email")
        return False


def publish_chart(path, url):
    """Commit+push the chart and wait until Pages actually serves it, so the
    email can never reference an image that isn't live. False -> fallback."""
    try:
        rel = str(path.relative_to(ROOT))
        subprocess.run(["git", "add", rel], cwd=ROOT, check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m",
                            f"chore: weekly email chart ({path.stem})"],
                           cwd=ROOT, check=True)
            subprocess.run(["git", "push"], cwd=ROOT, check=True)
        want = path.stat().st_size
        deadline = time.monotonic() + DEPLOY_TIMEOUT_S
        while time.monotonic() < deadline:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 200 and len(resp.read()) == want:
                        return True
            except urllib.error.HTTPError:
                pass  # 404 until the Pages deploy lands
            time.sleep(10)
        print("chart deploy timed out - falling back to plain email")
        return False
    except Exception as e:
        print(f"chart publish failed ({e!r}) - falling back to plain email")
        return False


def _pct_html(pct, size=14):
    up = pct >= 0
    return (f'<span style="color:{GREEN if up else RED};font-weight:700;'
            f'font-size:{size}px;white-space:nowrap">'
            f'{"▲" if up else "▼"} {abs(pct):.2f}%</span>')


def _mover_row(m, last):
    border = "" if last else f"border-bottom:1px solid {HAIR};"
    thumb = (f'<img src="{m["image"]}" width="32" alt="" '
             f'style="border-radius:4px;display:block">') if m.get("image") else ""
    return f'''<tr>
<td style="padding:10px 0;{border}width:40px;vertical-align:middle">{thumb}</td>
<td style="padding:10px 10px;{border}vertical-align:middle">
  <span style="font-weight:600;font-size:15px;line-height:1.3">{m["name"]}</span><br>
  <span style="font-size:12.5px;color:{MUTED}">{m["setName"]}</span></td>
<td style="padding:10px 0;{border}text-align:right;vertical-align:middle;white-space:nowrap;width:86px">
  <span style="font-size:14.5px">${m["price"]:,.0f}</span><br>{_pct_html(m["weekPct"], 13)}</td></tr>'''


def _movers_html(title, color, movers):
    rows = "".join(_mover_row(m, i == len(movers) - 1)
                   for i, m in enumerate(movers))
    return (f'<div style="margin-top:26px">'
            f'<div style="font-size:12px;font-weight:700;color:{color};'
            f'letter-spacing:1px;text-transform:uppercase;padding-bottom:2px">{title}</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></div>')


def _stat_row(label, value_html, last=False):
    border = "" if last else f"border-bottom:1px solid {HAIR};"
    return (f'<tr><td style="padding:9px 0;{border}font-size:13.5px;color:{MUTED}">{label}</td>'
            f'<td style="padding:9px 0;{border}text-align:right;font-size:14px;'
            f'font-weight:600;white-space:nowrap">{value_html}</td></tr>')


def compose_rich(latest, history, state, chart_url):
    """The rich HTML issue. Buttondown renders the subject as the email's
    headline, so the subject IS the design's H1 — the dedupe anchor rides
    at the end where inbox truncation hides it."""
    as_of = latest["asOfDate"]
    index = latest["index"]
    wk = week_stats(latest, history, state)
    chg = wk["changePct"]
    subject = issue_subject(chg, as_of)

    points = history["points"] if isinstance(history, dict) else history
    year_start = f"{as_of[:4]}-01-01"
    ytd_ref = next((p for p in points if p["date"] >= year_start), None)
    ytd_html = (_pct_html((index / ytd_ref["index"] - 1.0) * 100.0)
                if ytd_ref and ytd_ref["date"] != as_of else "&mdash;")

    stats = [
        _stat_row("Week's range", f"{wk['low']:,.2f} &ndash; {wk['high']:,.2f}"),
        _stat_row("Previous close", f"{wk['refIndex']:,.2f}"),
        _stat_row(f"{as_of[:4]} so far", ytd_html, last=True),
    ]

    blocks = [f'''<div style="font-size:15px;line-height:1.5">
<div style="margin-top:6px;font-size:14px;color:{MUTED}">The Pokémon card market this week</div>
<a href="{SITE}" style="text-decoration:none;color:inherit">
<div style="font-size:46px;letter-spacing:-1px;line-height:1.2;margin:2px 0 2px">{index:,.2f}</div>
<div style="margin-bottom:4px">{_pct_html(chg, 17)}&nbsp; <span style="font-size:13.5px;color:{MUTED}">{wk["changeLabel"]}</span></div>
<img src="{chart_url}" width="560" alt="One-week chart: the index closed at {index:,.2f}" style="width:100%;height:auto;display:block;margin:10px 0 4px;border:none"></a>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px">{"".join(stats)}</table>''']

    if wk["gainers"]:
        blocks.append(_movers_html("▲ Top gainers this week", GREEN, wk["gainers"]))
    if wk["losers"]:
        blocks.append(_movers_html("▼ Top decliners this week", RED, wk["losers"]))
    if wk["firstIssue"]:
        blocks.append(
            f'<div style="margin-top:22px;font-size:13px;color:{MUTED}">'
            f'Starting next Friday: the week&rsquo;s biggest gainers and '
            f'losers, card by card.</div>')
    elif not wk["gainers"] and not wk["losers"]:
        blocks.append(
            f'<div style="margin-top:22px;font-size:13px;color:{MUTED}">'
            f'No confirmed single-card moves this week &mdash; vintage prices '
            f'are sticky, and only cards with confirmed prices at both ends '
            f'of the week count as movers.</div>')

    blocks.append(f'''<div style="text-align:center;margin:30px 0 6px">
<a href="{SITE}" style="display:inline-block;background:{BLUE};color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:13px 30px;border-radius:24px">See the full index →</a></div>
<div style="text-align:center;font-size:12px;color:{MUTED};line-height:1.6;margin-top:16px">
Price-weighted index of the 500 most valuable English raw Pokémon singles, from TCGplayer market data.<br>Every Friday · Not financial advice · <a href="{SITE}" style="color:{MUTED}">{SITE_NAME}</a></div>
</div>''')
    return subject, "".join(blocks)


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

    try:
        recent = api_request(key, f"{API}?page=1")
        sent = {e.get("subject", "") for e in recent.get("results", [])}
        # Match the current anchor AND the legacy ISO-date form, so an
        # issue sent before an anchor-format change can never be re-sent
        # by a same-day workflow re-run under the new format.
        anchors = (issue_anchor(as_of), f"week ending {as_of}")
        if any(a in s for a in anchors for s in sent):
            print(f"Already sent the issue for {as_of} - skipping.")
            return 0

        # Rich path — only attempted after every gate has passed, so a
        # chart is never published for an issue that won't send. Any
        # failure inside falls back to the plain-markdown compose.
        chart_path = EMAIL_DIR / f"chart-{as_of}.png"
        chart_url = f"{SITE}email/chart-{as_of}.png"
        if render_chart(history, as_of, chart_path) and \
                publish_chart(chart_path, chart_url):
            subject, body = compose_rich(latest, history, state, chart_url)
        else:
            subject, body = compose(latest, history, state)

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
