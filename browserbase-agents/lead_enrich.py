"""Enrich a lead CSV with public contact info (website, phone, email, socials).

Reads business_name, city and optional website. When the website is missing it looks
it up on a search results page. It then reads the homepage and a contact page for
phone, email and social links. Respects robots.txt, rate limits per host, and stops
at 50 rows per run. Never fills or submits a form.
"""

from __future__ import annotations

import csv
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections.abc import Callable
from pathlib import Path
from typing import Any

import bb

AGENT = "lead_enrich"
HARD_CAP = 50
USER_AGENT = "bb-agents-lead-enrich/1.0 (read-only)"
SEARCH_URL = "https://html.duckduckgo.com/html/?q={q}"
LOCAL_CSV = bb.HERE / "leads.local.csv"
EXAMPLE_CSV = bb.HERE / "leads.example.csv"

# Matched against whole host labels, so "example-plumbing.com" is not mistaken for "bing".
DIRECTORY_LABELS = {
    "yelp",
    "facebook",
    "instagram",
    "linkedin",
    "yellowpages",
    "bbb",
    "mapquest",
    "angi",
    "angieslist",
    "thumbtack",
    "houzz",
    "nextdoor",
    "tripadvisor",
    "google",
    "bing",
    "duckduckgo",
    "twitter",
    "tiktok",
    "youtube",
    "manta",
    "chamberofcommerce",
    "porch",
    "homeadvisor",
    "wikipedia",
    "apple",
    "foursquare",
}
DIRECTORY_HOSTS = {"x.com"}
SOCIALS = {
    "facebook": ("facebook.com",),
    "instagram": ("instagram.com",),
    "linkedin": ("linkedin.com",),
    "x": ("x.com", "twitter.com"),
    "tiktok": ("tiktok.com",),
    "youtube": ("youtube.com",),
}
OUT_FIELDS = ("website", "website_source", "phone", "email", *SOCIALS, "contact_page", "status", "notes")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}")
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\b([2-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b")
JUNK_EMAIL = re.compile(
    r"\.(png|jpe?g|gif|svg|webp)$|@(example|domain|email|sentry|wixpress)\.", re.IGNORECASE
)


# --- politeness -------------------------------------------------------------


def http_get(url: str, timeout: float = 15) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(500_000).decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""


class Robots:
    """robots.txt cache. Missing or 4xx robots means allowed; 5xx or unreachable means not."""

    def __init__(self, fetch: Callable[[str], tuple[int, str]] = http_get) -> None:
        self.fetch = fetch
        self.cache: dict[str, urllib.robotparser.RobotFileParser | bool] = {}

    def allowed(self, url: str) -> bool:
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self.cache:
            try:
                status, body = self.fetch(origin + "/robots.txt")
            except Exception:
                status, body = 599, ""
            if 400 <= status < 500:
                self.cache[origin] = True
            elif status >= 500:
                self.cache[origin] = False
            else:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(body.splitlines())
                self.cache[origin] = rp
        rule = self.cache[origin]
        if isinstance(rule, bool):
            return rule
        return rule.can_fetch(USER_AGENT, url) and rule.can_fetch("*", url)


class RateLimiter:
    def __init__(
        self,
        min_interval: float = 3.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.min_interval, self.clock, self.sleep = min_interval, clock, sleep
        self.last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        host = urllib.parse.urlsplit(url).netloc
        last = self.last.get(host)
        if last is not None:
            gap = self.min_interval - (self.clock() - last)
            if gap > 0:
                self.sleep(gap)
        self.last[host] = self.clock()


# --- parsing ----------------------------------------------------------------


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower().removeprefix("www.")


def is_directory(url: str) -> bool:
    host = _host(url)
    labels = set(host.split(".")[:-1])
    return bool(labels & DIRECTORY_LABELS) or host in DIRECTORY_HOSTS


def unwrap_result(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    qs = urllib.parse.parse_qs(parsed.query)
    for key in ("uddg", "u", "url", "q"):
        if key in qs and qs[key][0].startswith("http"):
            return qs[key][0]
    return href


def pick_website(search_html: str) -> str | None:
    for link in bb.parse_html(search_html).links:
        url = unwrap_result(link["href"])
        if url.startswith("http") and not is_directory(url):
            parts = urllib.parse.urlsplit(url)
            return f"{parts.scheme}://{parts.netloc}/"
    return None


def format_phone(m: re.Match) -> str:
    return f"({m.group(1)}) {m.group(2)}-{m.group(3)}"


def extract_contacts(html: str, text: str, base_url: str) -> dict:
    doc = bb.parse_html(html)
    phones: list[str] = []
    emails: list[str] = []
    socials: dict[str, str] = {}
    contact_page = None
    for link in doc.links:
        href = link["href"].strip()
        low = href.lower()
        if low.startswith("tel:"):
            m = PHONE_RE.search(urllib.parse.unquote(href[4:]))
            if m:
                phones.append(format_phone(m))
        elif low.startswith("mailto:"):
            addr = urllib.parse.unquote(href[7:]).split("?")[0].strip()
            if EMAIL_RE.fullmatch(addr):
                emails.append(addr.lower())
        else:
            absolute = urllib.parse.urljoin(base_url, href)
            host = _host(absolute)
            for key, domains in SOCIALS.items():
                if key not in socials and any(host == d or host.endswith("." + d) for d in domains):
                    socials[key] = absolute
            if (
                contact_page is None
                and host == _host(base_url)
                and ("contact" in low or "contact" in link["text"].lower())
            ):
                contact_page = absolute
    phones += [format_phone(m) for m in PHONE_RE.finditer(text or "")]
    emails += [e.lower() for e in EMAIL_RE.findall(text or "")]
    emails = [e for e in dict.fromkeys(emails) if not JUNK_EMAIL.search(e)]
    return {
        "phones": list(dict.fromkeys(phones)),
        "emails": emails,
        "socials": socials,
        "contact_page": contact_page,
    }


# --- run --------------------------------------------------------------------


class Enricher:
    def __init__(self, page: Any, run: bb.Run, robots: Robots, limiter: RateLimiter) -> None:
        self.page, self.run, self.robots, self.limiter = page, run, robots, limiter

    def _visit(self, url: str) -> tuple[str, str] | None:
        if not self.robots.allowed(url):
            return None
        self.limiter.wait(url)
        bb.load(self.page, url, settle_ms=800)
        return self.page.content(), bb.page_text(self.page)

    def __call__(self, row: dict) -> dict:
        name = (row.get("business_name") or "").strip()
        city = (row.get("city") or "").strip()
        if not name:
            raise ValueError("row has no business_name")
        notes: list[str] = []
        website = (row.get("website") or "").strip()
        source = "input" if website else ""
        if website and not website.startswith("http"):
            website = "https://" + website
        if not website:
            search = SEARCH_URL.format(q=urllib.parse.quote_plus(f"{name} {city}"))
            got = self._visit(search)
            if got is None:
                notes.append("search page disallowed by robots.txt")
            else:
                website = pick_website(got[0]) or ""
                source = "search" if website else ""
                if not website:
                    notes.append("no non-directory website in search results")
        out = {**row, "website": website, "website_source": source}
        if not website:
            return {"status": "no_website", **out, "notes": "; ".join(notes)}

        home = self._visit(website)
        if home is None:
            notes.append("homepage disallowed by robots.txt")
            return {"status": "robots_blocked", **out, "notes": "; ".join(notes)}
        shot = bb.screenshot(self.page, self.run.shot(name), full_page=False)
        found = extract_contacts(home[0], home[1], website)
        if found["contact_page"]:
            contact = self._visit(found["contact_page"])
            if contact is None:
                notes.append("contact page disallowed by robots.txt")
            else:
                more = extract_contacts(contact[0], contact[1], found["contact_page"])
                found["phones"] = list(dict.fromkeys(found["phones"] + more["phones"]))
                found["emails"] = list(dict.fromkeys(found["emails"] + more["emails"]))
                found["socials"] = {**more["socials"], **found["socials"]}
        out.update(
            {
                "phone": found["phones"][0] if found["phones"] else "",
                "email": found["emails"][0] if found["emails"] else "",
                "contact_page": found["contact_page"] or "",
                **{k: found["socials"].get(k, "") for k in SOCIALS},
            }
        )
        got_any = out["phone"] or out["email"]
        return {
            "status": "ok" if got_any else "partial",
            **out,
            "screenshot": shot,
            "notes": "; ".join(notes),
        }


def read_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for i, row in enumerate(rows):
        row.setdefault("name", row.get("business_name") or f"row {i + 1}")
    return rows


def write_csv(path: Path, rows: list[dict], results: list[dict]) -> Path:
    in_fields = [k for k in (rows[0].keys() if rows else []) if k != "name"]
    fields = in_fields + [f for f in OUT_FIELDS if f not in in_fields]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row, res in zip(rows, results, strict=False):
            if res.get("status") == "error":
                res = {**row, "status": "error", "notes": res.get("error", "")}
            writer.writerow({k: res.get(k, row.get(k, "")) for k in fields})
    return path


def main(argv: list[str] | None = None) -> int:
    parser = bb.base_parser(__doc__.splitlines()[0], default_max=HARD_CAP)
    parser.add_argument("--csv", help="input CSV (default: leads.local.csv, else leads.example.csv)")
    parser.add_argument("--min-interval", type=float, default=3.0, help="seconds between hits per host")
    args = parser.parse_args(argv)
    path = Path(args.csv) if args.csv else (LOCAL_CSV if LOCAL_CSV.exists() else EXAMPLE_CSV)
    rows = read_rows(path)
    run = bb.Run(
        AGENT, max_targets=min(args.max_targets, HARD_CAP), max_minutes=args.max_minutes, out_root=args.out
    )
    robots, limiter = Robots(), RateLimiter(args.min_interval)
    out_csv = run.out_dir / f"enriched-{run.stamp}.csv"

    def extra() -> dict:
        write_csv(out_csv, rows[: len(run.results)], run.results)
        return {"input_csv": str(path), "enriched_csv": str(out_csv), "hard_cap": HARD_CAP}

    return bb.run_agent(
        run, rows, lambda page, row: Enricher(page, run, robots, limiter)(row), local=args.local, extra=extra
    )


if __name__ == "__main__":
    sys.exit(main())
