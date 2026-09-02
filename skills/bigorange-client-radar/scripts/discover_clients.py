#!/usr/bin/env python3
"""
discover_clients.py -- BigOrange client radar

Discovers which companies BigOrange Marketing (bigorange.marketing) presents
as clients: case studies, testimonials, portfolio pages, and client logo
strips. Public access only (plus an optional read-only WordPress Application
Password for private/draft posts). Never writes to WordPress. Never sends
anything anywhere.

Python 3.11 stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import html
import html.parser
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "bigorange-client-radar/1.0 (+dillon@momentum360)"
BASE = "https://bigorange.marketing"
REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_REQUESTS = 0.5

TERM_PATTERN = re.compile(
    r"case[\s-]?study|casestudy|portfolio|client|testimonial|results|success|work",
    re.IGNORECASE,
)

HTML_PAGES = [
    "/",
    "/about-big-orange-marketing/",
    "/industries/",
    "/msp-it-services-marketing-agency/",
    "/manufacturing-services-marketing-agency/",
    "/landscaping-marketing-services/",
    "/marketing-agency-for-builders/",
    "/services/",
]

HUB_INDUSTRY_MAP = {
    "/marketing-agency-for-builders/": "home-builders",
    "/msp-it-services-marketing-agency/": "msp",
    "/manufacturing-services-marketing-agency/": "manufacturing",
    "/landscaping-marketing-services/": "landscaping",
}

SEARCH_TERMS = [
    "case study",
    "portfolio",
    "client",
    "testimonial",
    "results",
    "success story",
]

BUILTIN_SUPPRESS = {
    "bigorange", "big orange marketing", "big orange", "storybrand", "hubspot",
    "google", "wp engine", "wpengine", "clutch", "expertise", "semrush", "moz",
    "yoast", "wordpress", "facebook", "linkedin", "instagram", "cincinnati",
    "ohio", "twitter", "youtube", "tiktok", "pinterest", "gmail", "microsoft",
    "apple", "amazon", "meta", "big orange marketing agency",
}

GENERIC_WORDS = {
    "home", "about", "services", "contact", "blog", "industries", "team",
    "careers", "privacy", "terms", "sitemap", "news", "resources", "insights",
    "case study", "case studies", "portfolio", "testimonials", "results",
    "success", "success stories", "our work", "work", "clients", "client",
    "landing page", "learn more", "read more", "click here", "logo", "logos",
}


# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------

class FetchError(Exception):
    def __init__(self, url, reason):
        super().__init__(f"{url}: {reason}")
        self.url = url
        self.reason = reason


def build_opener():
    return urllib.request.build_opener()


def fetch(url, auth_header=None, timeout=REQUEST_TIMEOUT):
    """Fetch a URL, return (status, body_bytes, headers). Raises FetchError."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    if auth_header:
        req.add_header("Authorization", auth_header)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raise FetchError(url, f"HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise FetchError(url, f"URLError {e.reason}") from e
    except Exception as e:  # noqa: BLE001 - fail soft, record reason
        raise FetchError(url, f"{type(e).__name__}: {e}") from e


def fetch_json(url, auth_header=None, timeout=REQUEST_TIMEOUT):
    status, body, _ = fetch(url, auth_header=auth_header, timeout=timeout)
    return json.loads(body.decode("utf-8", errors="replace"))


def fetch_text(url, auth_header=None, timeout=REQUEST_TIMEOUT):
    status, body, _ = fetch(url, auth_header=auth_header, timeout=timeout)
    return body.decode("utf-8", errors="replace")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# Fixture mode (reads local files instead of network)
# --------------------------------------------------------------------------

class FixtureSource:
    """Reads canned JSON/HTML from a local directory instead of the network.

    Expected files inside the fixture dir (all optional -- missing files
    behave as if that source returned nothing):
      categories.json, tags.json
      posts.json                 (result of a posts listing / search)
      pages.json
      media.json
      <slugified-page-path>.html  e.g. "home.html", "about.html"
    Fixture dirs indicate which HTML page maps to which file via a
    "pages.json" manifest of the shape {"/": "home.html", "/about/": "about.html"}
    OR, simpler for this skill, fixtures/README.md documents the convention:
    "home.html" == "/", and any other *.html file is scanned too.
    """

    def __init__(self, directory: Path):
        self.dir = directory

    def _read_json(self, name):
        path = self.dir / name
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def categories(self):
        return self._read_json("categories.json") or []

    def tags(self):
        return self._read_json("tags.json") or []

    def posts(self, **kwargs):
        return self._read_json("posts.json") or []

    def pages(self):
        return self._read_json("pages.json") or []

    def media(self):
        return self._read_json("media.json") or []

    def html_pages(self):
        """Return list of (path_label, html_text) for every *.html fixture file."""
        out = []
        if not self.dir.exists():
            return out
        for p in sorted(self.dir.glob("*.html")):
            out.append((f"/{p.stem}/", p.read_text(encoding="utf-8")))
        return out


# --------------------------------------------------------------------------
# HTML parsing
# --------------------------------------------------------------------------

LOGO_HINT = re.compile(r"logo|client|customer|partner|brand", re.IGNORECASE)
CASE_STUDY_HEADING = re.compile(r"case\s*stud(y|ies)", re.IGNORECASE)
# Matches a run of Title-Case words (a plausible company name) after "for" or
# after "Case Study:" style lead-ins. Interior lowercase connector words
# (of, and, the, &) are allowed inside the run so "Bank of America" survives.
NAME_RUN = r"(?:[A-Z][A-Za-z0-9&.'\-]*(?:\s+(?:of|and|the|&|for)\s+[A-Z][A-Za-z0-9&.'\-]*|\s+[A-Z][A-Za-z0-9&.'\-]*){0,3})"
FOR_COMPANY = re.compile(r"\bfor\s+(" + NAME_RUN + r")\b")
CASE_STUDY_NAME = re.compile(r"case\s*stud(?:y|ies)\s*[:\-]?\s*(" + NAME_RUN + r")\b", re.IGNORECASE)
ATTRIBUTION = re.compile(
    r"^\s*[-\u2014,]?\s*([A-Z][A-Za-z.'\- ]{1,40}),?\s*"
    r"(?:[A-Za-z .&\-]{2,40},\s*)?"
    r"([A-Z][A-Za-z0-9&.,'\- ]{2,60})\s*$"
)
# Common suffix words that mark the end of a company name in loosely-matched
# phrases like "Bright Path Dental Marketing Results".
NAME_STOPWORDS = {
    "marketing", "results", "seo", "website", "websites", "services",
    "program", "case", "study", "story", "journey", "overview", "recap",
    "review", "campaign", "project", "site", "recap.", "results.",
    # common case-study headline verbs/adverbs that follow a client name,
    # e.g. "Aeko Tech Gets 3x More Leads" -> stop before "Gets"
    "gets", "finds", "connects", "shows", "converts", "quickly", "launches",
    "boosts", "grows", "increases", "doubles", "triples", "drives",
    "delivers", "wins", "lands", "secures", "achieves", "sees", "earns",
    "generates", "improves", "reaches", "hits", "scales", "expands",
    "transforms", "streamlines", "cuts", "saves", "reduces", "builds",
}


def trim_to_company_name(phrase: str, max_words: int = 3) -> str:
    """Trim a loosely-matched capitalized phrase down to a plausible company
    name by stopping at the first known stopword or after max_words words."""
    words = phrase.strip().split()
    kept = []
    for w in words:
        bare = w.strip(".,").lower()
        if bare in NAME_STOPWORDS:
            break
        kept.append(w)
        if len(kept) >= max_words:
            break
    return " ".join(kept).strip(" -:,.")


class BigOrangeHTMLParser(html.parser.HTMLParser):
    """Walks a page and collects candidate evidence tuples.

    Produces a list of dicts: {kind, text}
      kind in {"logo-alt", "figcaption", "testimonial", "case-study-title"}
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.evidence = []
        self._tag_stack = []
        self._text_buffer = []
        self._current_tag = None
        self._capture_text_for = None  # tag name we're accumulating text for
        self._heading_text = []
        self._in_heading = False
        self._in_blockquote = False
        self._blockquote_text = []
        self._in_figcaption = False
        self._figcaption_text = []
        self._pending_attribution_tags = {"strong", "cite", "p", "b", "em", "span"}
        self._after_blockquote_watch = 0
        self._after_blockquote_text = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self._tag_stack.append(tag)

        if tag == "img":
            alt = (attrs_d.get("alt") or "").strip()
            title = (attrs_d.get("title") or "").strip()
            cls = (attrs_d.get("class") or "")
            src = (attrs_d.get("src") or "")
            blob = f"{alt} {title} {cls} {src}"
            if alt and LOGO_HINT.search(blob):
                self.evidence.append({"kind": "logo-alt", "text": alt[:200]})
            elif alt and len(alt) >= 3 and not LOGO_HINT.search(blob):
                # still might be a bare company-name alt in a logo strip context
                pass

        if tag in ("h1", "h2", "h3", "h4"):
            self._in_heading = True
            self._heading_text = []

        if tag == "blockquote":
            self._in_blockquote = True
            self._blockquote_text = []

        if tag == "figcaption":
            self._in_figcaption = True
            self._figcaption_text = []

        if self._after_blockquote_watch > 0 and tag in self._pending_attribution_tags:
            self._after_blockquote_watch += 0  # keep watching, text handled in handle_data

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1", "h2", "h3", "h4") and self._in_heading:
            text = "".join(self._heading_text).strip()
            text = re.sub(r"\s+", " ", text)
            if text and CASE_STUDY_HEADING.search(text):
                self.evidence.append({"kind": "case-study-title", "text": text[:200]})
            self._in_heading = False
            self._heading_text = []

        if tag == "blockquote" and self._in_blockquote:
            text = "".join(self._blockquote_text).strip()
            text = re.sub(r"\s+", " ", text)
            if text:
                self.evidence.append({"kind": "testimonial", "text": text[:200]})
            self._in_blockquote = False
            # start watching the next few tags for an attribution line
            self._after_blockquote_watch = 6
            self._after_blockquote_text = []

        if tag == "figcaption" and self._in_figcaption:
            text = "".join(self._figcaption_text).strip()
            text = re.sub(r"\s+", " ", text)
            if text:
                self.evidence.append({"kind": "figcaption", "text": text[:200]})
            self._in_figcaption = False
            self._figcaption_text = []

        if self._after_blockquote_watch > 0:
            self._after_blockquote_watch -= 1

    def handle_data(self, data):
        if self._in_heading:
            self._heading_text.append(data)
        if self._in_blockquote:
            self._blockquote_text.append(data)
        if self._in_figcaption:
            self._figcaption_text.append(data)
        if self._after_blockquote_watch > 0 and data.strip():
            self._after_blockquote_text.append(data.strip())
            joined = " ".join(self._after_blockquote_text)
            m = ATTRIBUTION.match(joined)
            if m:
                self.evidence.append({
                    "kind": "testimonial",
                    "text": f"attribution: {joined[:190]}",
                })
                self._after_blockquote_watch = 0
                self._after_blockquote_text = []


def parse_html_for_evidence(text: str):
    parser = BigOrangeHTMLParser()
    try:
        parser.feed(text)
    except Exception:  # noqa: BLE001 - malformed HTML, best effort
        pass
    return list(parser.evidence)


def extract_case_study_links(text: str, base_url: str):
    """Find hrefs that look like case-study / portfolio pages."""
    links = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', text):
        href = m.group(1)
        if TERM_PATTERN.search(href):
            if href.startswith("/"):
                links.add(BASE + href)
            elif href.startswith(BASE):
                links.add(href)
    return links


# --------------------------------------------------------------------------
# Candidate model
# --------------------------------------------------------------------------

def normalize_name(raw: str) -> str:
    name = raw.strip()
    name = re.sub(r"\s+", " ", name)
    name = name.strip(" -|,.:;")
    if name.isupper() and len(name) > 1:
        name = name.title()
    return name


def name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


BLOG_TITLE_FIRST_WORDS = {
    "how", "why", "what", "when", "where", "who", "top", "best", "the",
    "our", "this", "that", "these", "those", "a", "an", "and", "or", "but",
    "for", "with", "from", "your", "you", "we", "i", "it", "its", "get",
    "getting", "does", "do", "can", "should", "will", "may", "might",
    "guide", "tips", "ways", "reasons", "things", "steps", "questions",
    "signs", "myths", "mistakes", "secrets", "benefits", "ultimate",
}


def is_suppressed(name: str, domain: str, suppress_names: set, suppress_domains: set) -> bool:
    key = name_key(name)
    if not key or len(name.strip()) < 3:
        return True
    lname = name.lower().strip()
    if lname in GENERIC_WORDS:
        return True
    words = lname.split()
    if words and (words[0] in BLOG_TITLE_FIRST_WORDS or words[0].isdigit()):
        return True
    if key in {name_key(s) for s in BUILTIN_SUPPRESS}:
        return True
    for s in suppress_names:
        sk = name_key(s)
        if sk and (sk == key or sk in key or key in sk):
            return True
    if domain:
        d = domain.lower().lstrip("www.")
        if d in suppress_domains:
            return True
    return False


def load_canonical_suppress(path: Path):
    names = set()
    domains = set()
    if not path.exists():
        return names, domains
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return names, domains
    for c in data.get("clients", []):
        if c.get("displayName"):
            names.add(c["displayName"])
        for a in c.get("aliases", []) or []:
            names.add(a)
        for d in c.get("emailDomains", []) or []:
            domains.add(d.lower())
    return names, domains


class Candidate:
    def __init__(self, name, industry_guess="unknown", domain=None):
        self.name = name
        self.industry_guess = industry_guess
        self.domain = domain
        self.evidence = []  # list of dicts

    def add_evidence(self, url, kind, text):
        self.evidence.append({
            "url": url,
            "kind": kind,
            "text": text[:200],
            "seen_at": now_iso(),
        })

    def confidence(self):
        kinds = {e["kind"] for e in self.evidence}
        has_case_study = "case-study-title" in kinds or "rest-post" in kinds
        if has_case_study or len(kinds) >= 2:
            return "high"
        if "testimonial" in kinds or "case-study-title" in kinds:
            return "medium"
        return "low"

    def to_dict(self):
        return {
            "name": self.name,
            "domain": self.domain,
            "industry_guess": self.industry_guess,
            "confidence": self.confidence(),
            "evidence": self.evidence,
        }


class Roster:
    def __init__(self):
        self._by_key = {}

    def get_or_create(self, name, industry_guess="unknown", domain=None):
        key = name_key(name)
        if key in self._by_key:
            c = self._by_key[key]
            if c.industry_guess == "unknown" and industry_guess != "unknown":
                c.industry_guess = industry_guess
            if not c.domain and domain:
                c.domain = domain
            return c
        c = Candidate(normalize_name(name), industry_guess=industry_guess, domain=domain)
        self._by_key[key] = c
        return c

    def all(self):
        return list(self._by_key.values())


# --------------------------------------------------------------------------
# Discovery pipeline
# --------------------------------------------------------------------------

def sleep_politely(quiet):
    time.sleep(SLEEP_BETWEEN_REQUESTS)


def discover_via_rest(roster: Roster, errors: list, auth_header, quiet, fixture: FixtureSource = None):
    matched_term_ids = {"category": set(), "tag": set()}

    if fixture:
        cats = fixture.categories()
        tags = fixture.tags()
    else:
        try:
            cats = fetch_json(f"{BASE}/wp-json/wp/v2/categories?per_page=100", auth_header=auth_header)
            sleep_politely(quiet)
        except FetchError as e:
            errors.append(str(e))
            cats = []
        try:
            tags = fetch_json(f"{BASE}/wp-json/wp/v2/tags?per_page=100", auth_header=auth_header)
            sleep_politely(quiet)
        except FetchError as e:
            errors.append(str(e))
            tags = []

    for term in cats:
        if TERM_PATTERN.search(term.get("slug", "")) or TERM_PATTERN.search(term.get("name", "")):
            matched_term_ids["category"].add(term["id"])
    for term in tags:
        if TERM_PATTERN.search(term.get("slug", "")) or TERM_PATTERN.search(term.get("name", "")):
            matched_term_ids["tag"].add(term["id"])

    posts = []
    case_study_links = set()

    if fixture:
        posts = fixture.posts()
    else:
        fields = "id,link,title,excerpt,date,modified"
        if matched_term_ids["category"]:
            ids = ",".join(str(i) for i in matched_term_ids["category"])
            try:
                url = f"{BASE}/wp-json/wp/v2/posts?per_page=100&categories={ids}&_fields={fields}"
                posts.extend(fetch_json(url, auth_header=auth_header))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))
        if matched_term_ids["tag"]:
            ids = ",".join(str(i) for i in matched_term_ids["tag"])
            try:
                url = f"{BASE}/wp-json/wp/v2/posts?per_page=100&tags={ids}&_fields={fields}"
                posts.extend(fetch_json(url, auth_header=auth_header))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))
        for term in SEARCH_TERMS:
            try:
                url = f"{BASE}/wp-json/wp/v2/posts?search={urllib.parse.quote(term)}&per_page=50&_fields={fields}"
                posts.extend(fetch_json(url, auth_header=auth_header))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))

        # optional: private/draft posts if auth provided
        if auth_header:
            try:
                url = f"{BASE}/wp-json/wp/v2/posts?status=private,draft&per_page=100&_fields={fields}"
                posts.extend(fetch_json(url, auth_header=auth_header))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))

    seen_ids = set()
    for post in posts:
        pid = post.get("id")
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        raw_title = post.get("title", "")
        if isinstance(raw_title, dict):
            raw_title = raw_title.get("rendered", "")
        title = html.unescape(re.sub(r"<[^>]+>", "", str(raw_title)))
        link = post.get("link", "")
        if TERM_PATTERN.search(link) or CASE_STUDY_HEADING.search(title):
            case_study_links.add(link)

        # Only pull a company name out of the title when it is explicitly a
        # case-study title (e.g. "Case Study: Acme Corp") -- generic blog
        # titles that merely contain a search term ("... for Marketers")
        # are not treated as naming a client.
        is_case_study_shaped = bool(CASE_STUDY_HEADING.search(title)) or bool(TERM_PATTERN.search(link) and re.search(r"case-?stud|portfolio", link, re.IGNORECASE))
        name = None
        if is_case_study_shaped:
            m = CASE_STUDY_NAME.search(title) or FOR_COMPANY.search(title)
            if m:
                name = trim_to_company_name(m.group(1))
        if name:
            name = normalize_name(name)
            if name and len(name) >= 3:
                c = roster.get_or_create(name)
                c.add_evidence(link or f"{BASE}/?p={pid}", "rest-post", title)

    # pages
    if fixture:
        pages = fixture.pages()
    else:
        try:
            fields = "id,link,title,modified"
            url = f"{BASE}/wp-json/wp/v2/pages?per_page=100&_fields={fields}"
            pages = fetch_json(url, auth_header=auth_header)
            sleep_politely(quiet)
        except FetchError as e:
            errors.append(str(e))
            pages = []

    for page in pages:
        link = page.get("link", "")
        if link and TERM_PATTERN.search(link):
            case_study_links.add(link)

    # media library logo search
    if fixture:
        media = fixture.media()
    else:
        try:
            fields = "id,source_url,alt_text,title"
            url = f"{BASE}/wp-json/wp/v2/media?per_page=100&search=logo&_fields={fields}"
            media = fetch_json(url, auth_header=auth_header)
            sleep_politely(quiet)
        except FetchError as e:
            errors.append(str(e))
            media = []

    for m in media:
        alt = (m.get("alt_text") or "").strip()
        title = m.get("title", {})
        title_text = title.get("rendered", "") if isinstance(title, dict) else str(title)
        title_text = html.unescape(title_text).strip()
        src = m.get("source_url", "")
        candidate_text = alt or title_text
        # strip generic "logo" wording to isolate a company name
        cleaned = re.sub(r"\b(logo|client|customer|partner)\b", "", candidate_text, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_|")
        if cleaned and len(cleaned) >= 3:
            name = normalize_name(cleaned)
            c = roster.get_or_create(name)
            c.add_evidence(src or f"{BASE}/wp-json/wp/v2/media/{m.get('id')}", "media-library", candidate_text)

    return case_study_links


def discover_via_html(roster: Roster, errors: list, case_study_links: set, quiet, fixture: FixtureSource = None):
    pages_to_scan = []

    if fixture:
        pages_to_scan = fixture.html_pages()
    else:
        for path in HTML_PAGES:
            url = BASE + path
            try:
                text = fetch_text(url)
                pages_to_scan.append((path, text))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))

        for link in list(case_study_links)[:40]:
            try:
                text = fetch_text(link)
                pages_to_scan.append((link, text))
                sleep_politely(quiet)
            except FetchError as e:
                errors.append(str(e))

    for path_label, text in pages_to_scan:
        industry = HUB_INDUSTRY_MAP.get(path_label, "unknown")
        evidence_items = parse_html_for_evidence(text)
        # discover more case-study links from home/hub pages
        more_links = extract_case_study_links(text, BASE)
        case_study_links.update(more_links)

        for item in evidence_items:
            kind = item["kind"]
            text_val = item["text"]
            name = None
            if kind == "logo-alt":
                name = re.sub(r"\b(logo|client|customer|partner)\b", "", text_val, flags=re.IGNORECASE)
                name = re.sub(r"\s+", " ", name).strip(" -_|")
            elif kind == "figcaption":
                name = text_val
            elif kind == "case-study-title":
                m = CASE_STUDY_NAME.search(text_val) or FOR_COMPANY.search(text_val)
                name = trim_to_company_name(m.group(1)) if m else None
            elif kind == "testimonial":
                if text_val.startswith("attribution: "):
                    m = ATTRIBUTION.match(text_val[len("attribution: "):])
                    name = m.group(2) if m else None
                else:
                    name = None

            if not name:
                continue
            name = normalize_name(name)
            if not name or len(name) < 3:
                continue
            c = roster.get_or_create(name, industry_guess=industry)
            c.add_evidence(path_label, kind, text_val)


def build_roster_output(candidates, suppress_names, suppress_domains, limit=None):
    kept = []
    for c in candidates:
        if is_suppressed(c.name, c.domain or "", suppress_names, suppress_domains):
            continue
        kept.append(c)

    conf_order = {"high": 0, "medium": 1, "low": 2}
    kept.sort(key=lambda c: (conf_order.get(c.confidence(), 3), c.name.lower()))

    if limit:
        kept = kept[:limit]

    return kept


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def make_auth_header(args):
    user = args.auth_user or os.environ.get("BIGORANGE_WP_USER")
    pw = args.auth_pass or os.environ.get("BIGORANGE_WP_APP_PASSWORD")
    if user and pw:
        token = base64.b64encode(f"{user}:{pw}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"
    return None


def print_table(candidates, quiet):
    if quiet:
        return
    print(f"{'CONFIDENCE':<10} {'INDUSTRY':<14} {'NAME':<40} EVIDENCE KINDS")
    print("-" * 100)
    for c in candidates:
        kinds = sorted({e['kind'] for e in c.evidence})
        print(f"{c.confidence():<10} {c.industry_guess:<14} {c.name[:40]:<40} {', '.join(kinds)}")


def main():
    parser = argparse.ArgumentParser(description="Discover BigOrange Marketing's client roster from public sources.")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "state" / "roster.json"))
    parser.add_argument("--dry-run", action="store_true", help="Print table only, do not write output.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of candidates in output.")
    parser.add_argument("--auth-user", default=None)
    parser.add_argument("--auth-pass", default=None)
    parser.add_argument("--diff", default=None, help="Path to a previous roster.json to diff against.")
    parser.add_argument("--fixture", default=None, help="Read from a local fixture directory instead of the network.")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--canonical-clients",
        default="/home/user/client-operations-canonical/registry/clients.json",
        help="Path to Dillon's own canonical client registry, used to suppress false positives.",
    )
    args = parser.parse_args()

    errors = []
    auth_header = make_auth_header(args)
    if auth_header and not args.quiet:
        print("NOTE: WordPress Application Password auth in use. This script performs read-only GET "
              "requests only; it never writes to WordPress.", file=sys.stderr)

    fixture = FixtureSource(Path(args.fixture)) if args.fixture else None

    roster = Roster()
    case_study_links = discover_via_rest(roster, errors, auth_header, args.quiet, fixture=fixture)
    discover_via_html(roster, errors, case_study_links, args.quiet, fixture=fixture)

    suppress_names, suppress_domains = load_canonical_suppress(Path(args.canonical_clients))

    kept = build_roster_output(roster.all(), suppress_names, suppress_domains, limit=args.limit)

    counts = {"high": 0, "medium": 0, "low": 0}
    for c in kept:
        counts[c.confidence()] += 1

    output = {
        "generated_at": now_iso(),
        "source": "public" if not auth_header else "public+auth",
        "counts": {**counts, "total": len(kept)},
        "clients": [c.to_dict() for c in kept],
        "errors": errors,
    }

    if args.dry_run:
        print_table(kept, args.quiet)
        if errors and not args.quiet:
            print("\nErrors:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
        if not args.quiet:
            print(f"\nTotal candidates: {len(kept)} (high={counts['high']} medium={counts['medium']} low={counts['low']})")
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"Wrote {out_path} ({len(kept)} clients)")

    if args.diff:
        # local import to avoid a hard dependency when --diff is unused
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import diff_roster  # noqa: E402

        prev_path = Path(args.diff)
        events_path = out_path.parent / "events.json"
        events, markdown = diff_roster.diff_rosters(prev_path, out_path, events_path)
        if not args.quiet:
            print(f"Wrote {events_path} ({len(events)} events)")
            if markdown:
                print("\n" + markdown)

    return 0


if __name__ == "__main__":
    sys.exit(main())
