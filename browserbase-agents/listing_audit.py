"""Audit Yelp and Apple Maps listings for presence and NAP consistency.

For each business it searches the public Yelp and Apple Maps pages, compares the
name, address and phone it finds against the expected values in targets, and reports
missing or inconsistent listings with the URL where the owner can claim or add one.
It never creates, claims, or edits a listing.
"""

from __future__ import annotations

import re
import sys
import urllib.parse
from typing import Any

import bb

AGENT = "listing_audit"
YELP_SEARCH = "https://www.yelp.com/search?find_desc={name}&find_loc={city}"
APPLE_SEARCH = "https://maps.apple.com/?q={q}"
CLAIM_URLS = {
    "yelp": "https://biz.yelp.com/claim",
    "apple_maps": "https://businessconnect.apple.com/",
}
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\b[2-9]\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
STOPWORDS = {"the", "and", "of", "llc", "inc", "co", "company", "&"}
STREET_ABBR = {
    "street": "st",
    "avenue": "ave",
    "road": "rd",
    "boulevard": "blvd",
    "drive": "dr",
    "lane": "ln",
    "court": "ct",
    "place": "pl",
    "suite": "ste",
    "highway": "hwy",
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
    "parkway": "pkwy",
}


def name_tokens(name: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", name.lower().replace("'", ""))
    return {w for w in words if w not in STOPWORDS}


def name_match(expected: str, found: str, threshold: float = 0.6) -> bool:
    want = name_tokens(expected)
    if not want:
        return False
    return len(want & name_tokens(found)) / len(want) >= threshold


def digits(value: str) -> str:
    d = re.sub(r"\D", "", value or "")
    return d[1:] if len(d) == 11 and d.startswith("1") else d


def norm_address(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", (value or "").lower())
    return " ".join(STREET_ABBR.get(w, w) for w in words)


def street_key(address: str) -> str:
    """House number plus first street word, e.g. '123 main'."""
    words = norm_address(address).split()
    if len(words) >= 2 and words[0].isdigit():
        return f"{words[0]} {words[1]}"
    return " ".join(words[:2])


def nap_check(expected: dict, page_text: str) -> dict:
    """Compare expected name/address/phone against a listing page's visible text."""
    text_phones = {digits(m.group(0)) for m in PHONE_RE.finditer(page_text or "")}
    text_addr = norm_address(page_text)
    lines = [ln.strip() for ln in (page_text or "").splitlines() if ln.strip()]
    name_ok = any(name_match(expected["name"], ln) for ln in lines[:200])
    phone = digits(expected.get("phone", ""))
    street = street_key(expected.get("address", ""))
    fields = {
        "name": name_ok,
        "phone": (phone in text_phones) if phone else None,
        "address": (f" {street} " in f" {text_addr} ") if street else None,
    }
    mismatched = [k for k, v in fields.items() if v is False]
    return {"fields": fields, "mismatched": mismatched}


def yelp_listing_url(search_html: str, name: str) -> str | None:
    for link in bb.parse_html(search_html).links:
        href = link["href"]
        if href.startswith("/biz/") or "yelp.com/biz/" in href:
            if link["text"] and name_match(name, link["text"]):
                return urllib.parse.urljoin("https://www.yelp.com", href.split("?")[0])
    return None


def classify(source: str, nap: dict | None, listing_url: str | None) -> dict:
    claim = CLAIM_URLS[source]
    if nap is None or not nap["fields"]["name"]:
        return {"state": "missing", "listing_url": listing_url, "claim_url": claim}
    state = "inconsistent" if nap["mismatched"] else "consistent"
    return {"state": state, "listing_url": listing_url, "claim_url": claim, **nap}


def audit_yelp(page: Any, target: dict, run: bb.Run) -> dict:
    url = YELP_SEARCH.format(
        name=urllib.parse.quote_plus(target["name"]), city=urllib.parse.quote_plus(target.get("city", ""))
    )
    bb.load(page, url)
    if bb.looks_blocked(bb.page_text(page)):
        return {
            "state": "unknown",
            "error": "Yelp showed a block/captcha page",
            "claim_url": CLAIM_URLS["yelp"],
        }
    listing = yelp_listing_url(page.content(), target["name"])
    if not listing:
        bb.screenshot(page, run.shot(f"{target['name']}-yelp-search"), full_page=False)
        return classify("yelp", None, None)
    bb.load(page, listing)
    text = bb.page_text(page)
    shot = bb.screenshot(page, run.shot(f"{target['name']}-yelp"), full_page=False)
    return {**classify("yelp", nap_check(target, text), listing), "screenshot": shot}


def audit_apple(page: Any, target: dict, run: bb.Run) -> dict:
    query = f"{target['name']} {target.get('address', '')} {target.get('city', '')}"
    bb.load(page, APPLE_SEARCH.format(q=urllib.parse.quote_plus(" ".join(query.split()))), settle_ms=4000)
    text = bb.page_text(page)
    shot = bb.screenshot(page, run.shot(f"{target['name']}-apple"), full_page=False)
    if not text.strip():
        return {
            "state": "unknown",
            "error": "Apple Maps page rendered no text",
            "claim_url": CLAIM_URLS["apple_maps"],
            "screenshot": shot,
        }
    return {**classify("apple_maps", nap_check(target, text), page.url), "screenshot": shot}


SOURCES = {"yelp": audit_yelp, "apple_maps": audit_apple}


def check_target(page: Any, target: dict, run: bb.Run) -> dict:
    listings: dict[str, dict] = {}
    for source, audit in SOURCES.items():
        try:
            listings[source] = audit(page, target, run)
        except Exception as exc:  # one source failing must not hide the other
            listings[source] = {
                "state": "unknown",
                "error": f"{type(exc).__name__}: {exc}",
                "claim_url": CLAIM_URLS[source],
            }
    states = {v["state"] for v in listings.values()}
    status = "warn" if states & {"missing", "inconsistent"} else ("error" if states == {"unknown"} else "ok")
    return {
        "status": status,
        "expected": {k: target.get(k) for k in ("name", "address", "city", "phone")},
        "listings": listings,
    }


def main(argv: list[str] | None = None) -> int:
    args = bb.base_parser(__doc__.splitlines()[0]).parse_args(argv)
    targets = bb.load_targets(AGENT, args.targets)
    run = bb.Run(AGENT, max_targets=args.max_targets, max_minutes=args.max_minutes, out_root=args.out)
    return bb.run_agent(run, targets, lambda page, t: check_target(page, t, run), local=args.local)


if __name__ == "__main__":
    sys.exit(main())
