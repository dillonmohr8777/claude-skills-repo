"""Read the Google Ads / Meta Ads Manager UI for policy, billing and account-status text.

Needs a logged-in persistent Browserbase context (BB_CONTEXT_ID). If a target lands
on a login page it is reported as needs_login and skipped. Never clicks or edits.
"""

from __future__ import annotations

import re
import sys
from typing import Any

import bb

AGENT = "ad_ui_check"

LOGIN_URL_HINTS = (
    "accounts.google.com",
    "/signin",
    "servicelogin",
    "facebook.com/login",
    "/loginpage",
    "login.php",
)
LOGIN_TEXT_HINTS = (
    "sign in",
    "log in",
    "log into",
    "forgot password",
    "email or phone",
    "to continue to google ads",
    "use your google account",
)

POLICY_PATTERNS = (
    r"disapproved",
    r"limited by policy",
    r"eligible \(limited\)",
    r"policy violation",
    r"violat\w+ .*polic",
    r"\brejected\b",
    r"doesn.t comply",
    r"ad account (?:is )?restricted",
    r"appeal",
)
BILLING_PATTERNS = (
    r"payment (?:was )?declined",
    r"payment (?:failed|issue|problem)",
    r"add a payment method",
    r"update (?:your )?payment",
    r"outstanding balance",
    r"billing (?:problem|issue|threshold|information)",
    r"account spending limit",
    r"your ads (?:have|are) (?:stopped|paused)",
    r"insufficient funds",
    r"prepay",
)
STATUS_PATTERNS = (
    r"account (?:status|is|has been)\b.*",
    r"account (?:suspended|disabled|restricted|paused|cancel+ed|active)\b.*",
    r"(?:suspended|disabled) (?:ad )?account\b.*",
)


def is_login_page(url: str, text: str) -> bool:
    u = (url or "").lower()
    if any(h in u for h in LOGIN_URL_HINTS):
        return True
    t = (text or "").lower()[:4000]
    return sum(h in t for h in LOGIN_TEXT_HINTS) >= 2 and len(text or "") < 6000


def _matching_lines(lines: list[str], patterns: tuple[str, ...], limit: int = 20) -> list[str]:
    found: list[str] = []
    for line in lines:
        low = line.lower()
        if any(re.search(p, low) for p in patterns) and line not in found:
            found.append(line[:200])
            if len(found) >= limit:
                break
    return found


def extract_signals(text: str) -> dict:
    lines = [" ".join(ln.split()) for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if 3 <= len(ln) <= 400]
    status = _matching_lines(lines, STATUS_PATTERNS, limit=3)
    return {
        "policy": _matching_lines(lines, POLICY_PATTERNS),
        "billing": _matching_lines(lines, BILLING_PATTERNS),
        "account_status": status[0] if status else "not found on page",
    }


def check_target(page: Any, target: dict, run: bb.Run) -> dict:
    url = target["url"]
    bb.load(page, url, settle_ms=4000)
    text = bb.page_text(page)
    shot = bb.screenshot(page, run.shot(bb.target_name(target)), full_page=False)
    base = {"platform": target.get("platform", ""), "url": url, "final_url": page.url, "screenshot": shot}
    if is_login_page(page.url, text):
        return {
            "status": "needs_login",
            **base,
            "note": "landed on a login page; log in once in the persistent context",
        }
    signals = extract_signals(text)
    bad_status = re.search(r"suspend|disabl|restrict|cancel|paused", signals["account_status"].lower())
    flagged = bool(signals["policy"] or signals["billing"] or bad_status)
    return {"status": "warn" if flagged else "ok", **base, **signals}


def main(argv: list[str] | None = None) -> int:
    args = bb.base_parser(__doc__.splitlines()[0]).parse_args(argv)
    targets = bb.load_targets(AGENT, args.targets)
    run = bb.Run(AGENT, max_targets=args.max_targets, max_minutes=args.max_minutes, out_root=args.out)
    return bb.run_agent(run, targets, lambda page, t: check_target(page, t, run), local=args.local)


if __name__ == "__main__":
    sys.exit(main())
