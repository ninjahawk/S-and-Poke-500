# Email spam-risk audit (2026-07-17, independent research)

Question: given how the newsletter operates today, are we at risk of
being marked spam by Google (Gmail filtering) or by individual
recipients? Answer: **low risk today — with ONE structural weak point
(punycode links) to fix before the list grows.** No emergency; nothing
here overrides the retention directive's "don't fiddle with the
pipeline" rule.

## Verified green (what already protects us)

1. **Authentication is Buttondown's job and they do it on every plan**:
   SPF + DKIM automatic (even on free), every email is one-click-
   unsubscribe compliant (RFC 8058 — the thing Gmail actually checks),
   and the shared `buttondown.email` sending domain's reputation is
   actively maintained (~85% of their users send on it). Gmail's
   stricter enforcement (since Nov 2025, rejects unauthenticated mail)
   is satisfied by their infra, not ours — nothing for us to configure.
2. **Volume rules don't bind us for years**: the Gmail/Yahoo "bulk
   sender" regime (aligned DMARC, spam-rate <0.30%, etc.) starts at
   **5,000+ emails/day to one provider**. We send weekly to a list of
   ~2. And Buttondown meets the bulk bar anyway.
3. **Individual-report armor is already project law**: double opt-in
   (Gmail's spam models heavily weight "did this person ask for this"),
   weekly cadence locked, subject matches the signup promise ("Weekly
   market updates to your inbox"), unsubscribe always works, list lives
   only in Buttondown. The retention directive in CLAUDE.md *is* the
   anti-spam playbook.
4. **Empirical**: preview drafts landed in the owner's Gmail inbox —
   the current setup demonstrably delivers.

## The one real finding: punycode links (fix before the list grows)

Every link AND the chart image in both compose paths use
`SITE = "https://xn--pok500-dva.com/"` (`send_newsletter.py:53`), and
Buttondown's click-tracking is **opt-in and off by default**, so spam
scanners and hover-preview both see raw `xn--` URLs.

Why that matters: `xn--` (IDN/punycode) domains are a documented
phishing heuristic — homograph attacks use them to spoof brands, so
security filters score them and trained users distrust them. A
recipient hovering "See the full index →" sees `xn--pok500-dva.com`,
which reads as gibberish/sketchy → that's how you get individual
"report spam" clicks, which is the exact metric Gmail cares most about.

Honest sizing: we spoof nobody (the é is ours), the From domain is
clean `buttondown.email`, volume is trivial, and drafts already inbox —
so this is a **compounding risk, not a current failure**. But it's also
the cheapest fix on the board:

- **The fix**: switch the email templates' links to
  `https://poke500.com/` (owned, verified 301 → canonical, all four
  http/https × apex/www combinations tested 2026-07-16). Redirect hops
  are utterly normal in email (every ESP click-tracker is one); a clean
  ASCII apex is categorically less alarming than `xn--`. Chart `<img>`
  can move too (Gmail's image proxy follows 301s) or stay put — images
  don't show URLs to humans. This is a `send_newsletter.py` change ⇒
  retention rules apply: unit tests updated + passing, extra-careful
  review, owner aware. Best shipped BEFORE the list is big; fine to
  ship after issue #1 (a 2-subscriber send with punycode links is
  no-risk).
- **The later upgrade (list ≳ 50–100)**: custom sending domain — free
  on Buttondown — e.g. mail from `poke500.com` with aligned
  DMARC + their (now-required-for-new-domains) custom click-tracking
  domain. Own-domain reputation starts from zero, which is exactly why
  you do it while the list is small-ish but NOT while the account is
  freshly approved and the pipeline is unproven. Doing it also unlocks
  Google Postmaster Tools (unusable on the shared domain).

## Minor notes

- **First-issue latency**: launch-day subscribers get their first email
  only when the `BUTTONDOWN_API_KEY` secret lands — the longer that
  gap, the more "who is this?" spam-report risk on issue #1. One more
  reason the key is owner-todo #1.
- **Footer/postal address**: CAN-SPAM wants a physical mailing address
  in commercial email; Buttondown manages footer compliance — owner
  should just glance at Buttondown Settings once to confirm an address
  is set.
- **Content shape is fine**: real text alongside images, alt text on
  the chart, plain-markdown fallback path. Keep subjects factual (no
  "$$$", no urgency words) — already the law from the subject-line
  research.
- **Site-side Google (search) spam**: unrelated to email ops; punycode
  domains index fine and the ASCII 301 is the textbook-correct setup.
  Nothing to do.

## Sources

Buttondown: docs.buttondown.com (email infrastructure, click-tracking),
buttondown.com/blog (deliverability, personal-domain, custom
click-tracking domains, privacy). Gmail/Yahoo 2026 requirements:
powerdmarc.com, emailwarmup.com, redsift.com, gmass.co guides
(thresholds cross-checked across four sources). Punycode-as-phishing-
heuristic: Huntress, Jamf, isMalicious, Wikipedia (IDN homograph
attack). All read 2026-07-17.
