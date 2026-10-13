"""Watch public Google Business Profile knowledge panels and diff against the last run.

For each business (name + city) it loads the public Google Search knowledge panel and
reads rating, review count, hours, phone, website, address and the "Suggest an edit" /
"Own this business?" signals. Public pages only, no login, never clicks.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import bb

AGENT = "gbp_watch"
SEARCH_URL = "https://www.google.com/search?hl=en&gl=us&q={q}"
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
WATCH_FIELDS = (
    "rating",
    "review_count",
    "hours",
    "phone",
    "website",
    "address",
    "suggest_an_edit",
    "claim_prompt",
)

RATING_RE = re.compile(
    r"\b([1-5][.,]\d)\b[\s★☆]*\n?\s*\(?(\d[\d,.]*\s*[Kk]?)\)?\s*(?:Google\s+)?reviews?", re.IGNORECASE
)
RATING_PAREN_RE = re.compile(r"\b([1-5][.,]\d)\b[\s★☆]*\n?\s*\((\d[\d,.]*\s*[Kk]?)\)")
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\b[2-9]\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")


def _labelled(text: str, label: str) -> str | None:
    m = re.search(rf"^\s*{label}\s*:\s*(.+)$", text, re.IGNORECASE | re.MULTILINE)
    return " ".join(m.group(1).split()) if m else None


def _count(raw: str) -> int:
    raw = raw.strip().replace(",", "")
    if raw.lower().endswith("k"):
        return int(float(raw[:-1]) * 1000)
    return int(float(raw))


def _unwrap(href: str) -> str:
    if href.startswith("/url?"):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return (qs.get("q") or qs.get("url") or [href])[0]
    return href


def parse_panel(html: str, text: str) -> dict:
    doc = bb.parse_html(html)
    out: dict[str, Any] = {"rating": None, "review_count": None}
    m = RATING_RE.search(text) or RATING_PAREN_RE.search(text)
    if m:
        out["rating"] = float(m.group(1).replace(",", "."))
        out["review_count"] = _count(m.group(2))

    phone = _labelled(text, "Phone")
    if not phone:
        pm = PHONE_RE.search(text)
        phone = pm.group(0) if pm else None
    out["phone"] = phone
    out["address"] = _labelled(text, "Address")
    out["hours_status"] = _labelled(text, "Hours")

    weekly: dict[str, str] = {}
    cells = doc.cells
    for i, cell in enumerate(cells[:-1]):
        day = cell.strip().lower()
        if day in DAYS and day not in weekly:
            weekly[day] = cells[i + 1]
    out["hours"] = weekly or None

    website = None
    for link in doc.links:
        label = f"{link['text']} {link['aria']}".strip().lower()
        if label == "website" or link["aria"].lower().startswith("website") or label.startswith("website "):
            website = _unwrap(link["href"])
            break
    out["website"] = website

    low = text.lower()
    out["suggest_an_edit"] = "suggest an edit" in low
    out["claim_prompt"] = "own this business" in low or "claim this business" in low
    out["panel_found"] = bool(out["rating"] or out["phone"] or out["address"] or website)
    return out


def latest_previous(out_root: Path, current: Path) -> dict:
    """Map target -> result from the newest earlier receipt, or {}."""
    receipts = sorted(
        (Path(out_root) / AGENT).glob("*/receipt-*.json"), key=lambda p: (p.parent.name, p.name)
    )
    receipts = [p for p in receipts if p.resolve() != current.resolve()]
    if not receipts:
        return {}
    try:
        data = json.loads(receipts[-1].read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return {r["target"]: r for r in data.get("results", []) if r.get("status") != "error"}


def diff(before: dict | None, after: dict) -> list[dict]:
    if not before:
        return []
    return [
        {"field": f, "before": before.get(f), "after": after.get(f)}
        for f in WATCH_FIELDS
        if before.get(f) != after.get(f)
    ]


def check_target(page: Any, target: dict, run: bb.Run, previous: dict) -> dict:
    query = f"{target['name']} {target.get('city', '')}".strip()
    bb.load(page, SEARCH_URL.format(q=urllib.parse.quote_plus(query)))
    text = bb.page_text(page)
    shot = bb.screenshot(page, run.shot(bb.target_name(target)), full_page=False)
    if bb.looks_blocked(text):
        raise RuntimeError("Google showed a block/captcha page")
    data = parse_panel(page.content(), text)
    prev = previous.get(bb.target_name(target))
    changes = diff(prev, data)
    if not data["panel_found"]:
        status = "warn"
    elif changes:
        status = "changed"
    else:
        status = "ok"
    return {
        "status": status,
        "query": query,
        "screenshot": shot,
        **data,
        "changes": changes,
        "first_run": prev is None,
    }


def main(argv: list[str] | None = None) -> int:
    args = bb.base_parser(__doc__.splitlines()[0]).parse_args(argv)
    targets = bb.load_targets(AGENT, args.targets)
    run = bb.Run(AGENT, max_targets=args.max_targets, max_minutes=args.max_minutes, out_root=args.out)
    previous = latest_previous(Path(args.out), run.receipt_path)
    return bb.run_agent(run, targets, lambda page, t: check_target(page, t, run, previous), local=args.local)


if __name__ == "__main__":
    sys.exit(main())
