"""Shared Browserbase plumbing for the agents in this folder.

Everything here is read-only: open and release a Browserbase session, read page
text, take screenshots, and run a capped loop over targets that writes a JSON
receipt. Agents never click, type, or submit; they only navigate and read.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
API_BASE = "https://api.browserbase.com/v1"
DEFAULT_OUT = HERE / "out"
STOP_FILE = HERE / "STOP"
LOCAL_TARGETS = HERE / "targets.local.json"
EXAMPLE_TARGETS = HERE / "targets.example.json"

Opener = Callable[..., Any]


class BrowserbaseError(RuntimeError):
    pass


# --- Browserbase REST -------------------------------------------------------


def _api(
    method: str,
    path: str,
    key: str,
    body: dict | None = None,
    opener: Opener = urllib.request.urlopen,
    timeout: float = 30,
) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API_BASE + path,
        data=data,
        method=method,
        headers={"X-BB-API-Key": key, "Content-Type": "application/json"},
    )
    try:
        with opener(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise BrowserbaseError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc
    return json.loads(raw) if raw else {}


def _require(env: dict, name: str) -> str:
    value = env.get(name)
    if not value:
        raise BrowserbaseError(f"{name} is not set")
    return value


def session_body(env: dict) -> dict:
    """Body for POST /v1/sessions. Adds a persistent context when BB_CONTEXT_ID is set.
    BB_SESSION_TIMEOUT (default 300 s), BB_PROXIES=1, BB_AGENT and BB_CLIENT tune timeout, proxy and tags."""
    settings: dict[str, Any] = {"solveCaptchas": True}
    context_id = env.get("BB_CONTEXT_ID")
    if context_id:
        settings["context"] = {"id": context_id, "persist": True}
    return {
        "projectId": _require(env, "BROWSERBASE_PROJECT_ID"),
        "timeout": int(env.get("BB_SESSION_TIMEOUT") or 300),  # explicit: the project default is 3 hours
        "browserSettings": settings,
        "proxies": env.get("BB_PROXIES") == "1",  # proxy traffic is the costly part; opt in per run
        "userMetadata": {"agent": env.get("BB_AGENT", "browserbase-agents"),
                         "client": env.get("BB_CLIENT", "momentum-360"), "run": uuid.uuid4().hex[:8]},
    }


def create_session(env: dict | None = None, opener: Opener = urllib.request.urlopen) -> dict:
    env = dict(os.environ) if env is None else env
    session = _api("POST", "/sessions", _require(env, "BROWSERBASE_API_KEY"), session_body(env), opener)
    if not session.get("id") or not session.get("connectUrl"):
        raise BrowserbaseError(f"unexpected session response keys: {sorted(session)}")
    return session


def release_session(
    session_id: str, env: dict | None = None, opener: Opener = urllib.request.urlopen
) -> None:
    env = dict(os.environ) if env is None else env
    body = {"status": "REQUEST_RELEASE", "projectId": env.get("BROWSERBASE_PROJECT_ID")}
    _api("POST", f"/sessions/{session_id}", _require(env, "BROWSERBASE_API_KEY"), body, opener)


@contextlib.contextmanager
def open_page(
    local: bool = False, env: dict | None = None, opener: Opener = urllib.request.urlopen
) -> Iterator[Any]:
    """Yield a Playwright page on a Browserbase session; always release it.

    local=True launches a local Chromium instead (for smoke tests, no Browserbase
    minutes, no logged-in context). BB_LOCAL_CHROMIUM overrides its executable.
    """
    from playwright.sync_api import sync_playwright

    env = dict(os.environ) if env is None else env
    session: dict | None = None
    browser = None
    with sync_playwright() as pw:
        try:
            if local:
                browser = pw.chromium.launch(executable_path=env.get("BB_LOCAL_CHROMIUM") or None)
                context = browser.new_context()
            else:
                session = create_session(env, opener)
                browser = pw.chromium.connect_over_cdp(session["connectUrl"])
                context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            yield page
        finally:
            if browser is not None:
                with contextlib.suppress(Exception):
                    browser.close()
            if session is not None:
                try:
                    release_session(session["id"], env, opener)
                except Exception as exc:  # report, but never mask the original error
                    print(f"[bb] WARNING: could not release session {session['id']}: {exc}", file=sys.stderr)


# --- Page helpers -----------------------------------------------------------


def load(page: Any, url: str, settle_ms: int = 1500, timeout_ms: int = 45000) -> Any:
    """Navigate and give the page a moment to settle. Returns the main response."""
    response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=10000)
    if settle_ms:
        page.wait_for_timeout(settle_ms)
    return response


def page_text(page: Any, timeout_ms: int = 10000) -> str:
    try:
        return page.inner_text("body", timeout=timeout_ms) or ""
    except Exception:
        return ""


def screenshot(page: Any, path: Path, full_page: bool = True) -> str | None:
    """Save a PNG; return its path relative to the agent output root, or None."""
    try:
        page.screenshot(path=str(path), full_page=full_page)
    except Exception as exc:
        print(f"[bb] screenshot failed for {path.name}: {exc}", file=sys.stderr)
        return None
    return path.name


BLOCK_HINTS = (
    "unusual traffic",
    "are you a robot",
    "verify you are human",
    "access denied",
    "captcha",
    "request blocked",
)


def looks_blocked(text: str) -> bool:
    head = text.lower()[:2000]
    return any(h in head for h in BLOCK_HINTS)


class LinkParser(HTMLParser):
    """Collects <a> tags (href, text, aria-label), <title>, metas, forms."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.metas: dict[str, str] = {}
        self.title = ""
        self.forms = 0
        self.cells: list[str] = []
        self._a: dict[str, str] | None = None
        self._in_title = False
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        if tag == "a":
            self._a = {"href": a.get("href", ""), "text": "", "aria": a.get("aria-label", "")}
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.metas[key] = a.get("content", "")
        elif tag == "form":
            self.forms += 1
        elif tag in ("td", "th"):
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._a is not None:
            self._a["text"] = " ".join(self._a["text"].split())
            self.links.append(self._a)
            self._a = None
        elif tag == "title":
            self._in_title = False
        elif tag in ("td", "th") and self._cell is not None:
            self.cells.append(" ".join("".join(self._cell).split()))
            self._cell = None

    def handle_data(self, data: str) -> None:
        if self._a is not None:
            self._a["text"] += data
        if self._in_title:
            self.title += data
        if self._cell is not None:
            self._cell.append(data)


def parse_html(html: str) -> LinkParser:
    parser = LinkParser()
    parser.feed(html or "")
    return parser


def slug(value: str, limit: int = 60) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:limit] or "target"


# --- Targets and run loop ---------------------------------------------------


def load_targets(agent: str, path: str | Path | None = None) -> list[dict]:
    """Targets for one agent. Prefers targets.local.json (gitignored, Mac only)."""
    if path is None:
        path = LOCAL_TARGETS if LOCAL_TARGETS.exists() else EXAMPLE_TARGETS
        if path == EXAMPLE_TARGETS:
            print(
                f"[{agent}] NOTE: using targets.example.json (fake example.com targets). "
                "Create targets.local.json for real runs.",
                file=sys.stderr,
            )
    data = json.loads(Path(path).read_text())
    targets = data.get(agent, [])
    if not isinstance(targets, list):
        raise ValueError(f"'{agent}' in {path} must be a list")
    return targets


def target_name(target: dict) -> str:
    return str(target.get("name") or target.get("url") or target.get("business_name") or "unnamed")


@dataclass
class Run:
    """One capped pass over targets. Writes out/<agent>/<date>/receipt-<time>.json."""

    agent: str
    max_targets: int = 25
    max_minutes: float = 15.0
    out_root: Path = DEFAULT_OUT
    stop_file: Path = STOP_FILE
    clock: Callable[[], float] = time.monotonic
    now: dt.datetime = field(default_factory=dt.datetime.now)
    results: list[dict] = field(default_factory=list)
    stopped_reason: str | None = None
    skipped: int = 0
    fatal: str | None = None

    def __post_init__(self) -> None:
        self.started = self.clock()
        self.out_dir = Path(self.out_root) / self.agent / self.now.strftime("%Y-%m-%d")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.stamp = self.now.strftime("%H%M%S")
        self.receipt_path = self.out_dir / f"receipt-{self.stamp}.json"

    def stop_reason(self, done: int) -> str | None:
        if self.stop_file.exists():
            return f"STOP file present ({self.stop_file.name})"
        if done >= self.max_targets:
            return f"max targets reached ({self.max_targets})"
        if (self.clock() - self.started) / 60 >= self.max_minutes:
            return f"max minutes reached ({self.max_minutes:g})"
        return None

    def shot(self, label: str) -> Path:
        return self.out_dir / f"{self.stamp}-{slug(label)}.png"

    def each(self, targets: list[dict], check: Callable[[dict], dict]) -> None:
        for i, target in enumerate(targets):
            reason = self.stop_reason(i)
            if reason:
                self.stopped_reason = reason
                self.skipped = len(targets) - i
                print(f"[{self.agent}] stopping: {reason}; {self.skipped} target(s) not run", file=sys.stderr)
                break
            name = target_name(target)
            try:
                data = dict(check(target))
                status = data.pop("status", "ok")
                self.results.append({"target": name, "status": status, **data})
            except Exception as exc:
                first_line = (str(exc).strip().splitlines() or [""])[0]
                error = f"{type(exc).__name__}: {first_line}"[:400]
                self.results.append({"target": name, "status": "error", "error": error})
                print(f"[{self.agent}] {name}: FAILED {error}", file=sys.stderr)

    def counts(self) -> Counter:
        return Counter(r["status"] for r in self.results)

    def write_receipt(self, extra: dict | None = None) -> Path:
        receipt = {
            "agent": self.agent,
            "started_at": self.now.isoformat(timespec="seconds"),
            "finished_at": dt.datetime.now().isoformat(timespec="seconds"),
            "read_only": True,
            "caps": {"max_targets": self.max_targets, "max_minutes": self.max_minutes},
            "stopped_reason": self.stopped_reason,
            "skipped": self.skipped,
            "fatal": self.fatal,
            "counts": dict(self.counts()),
            "results": self.results,
            **(extra or {}),
        }
        self.receipt_path.write_text(json.dumps(receipt, indent=2, default=str))
        return self.receipt_path

    def summary(self) -> str:
        counts = ", ".join(f"{k}={v}" for k, v in sorted(self.counts().items())) or "none"
        parts = [f"{self.agent}: {len(self.results)} target(s) [{counts}]"]
        if self.fatal:
            parts.append(f"FATAL {self.fatal}")
        if self.stopped_reason:
            parts.append(f"stopped: {self.stopped_reason}")
        parts.append(f"receipt {self.receipt_path}")
        return " | ".join(parts)

    def finish(self, extra: dict | None = None) -> int:
        self.write_receipt(extra)
        print(self.summary())
        return 1 if self.fatal or self.counts().get("error") else 0


def base_parser(description: str, default_max: int = 25) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--targets", help="targets JSON (default: targets.local.json, else example)")
    p.add_argument("--max-targets", type=int, default=default_max)
    p.add_argument("--max-minutes", type=float, default=15.0)
    p.add_argument("--out", default=str(DEFAULT_OUT), help="output root (default: ./out)")
    p.add_argument(
        "--local", action="store_true", help="use a local Chromium instead of Browserbase (smoke tests)"
    )
    return p


def run_agent(
    run: Run,
    targets: list[dict],
    check: Callable[[Any, dict], dict],
    local: bool = False,
    setup: Callable[[Any], None] | None = None,
    extra: Callable[[], dict] | None = None,
) -> int:
    """Open one browser session for the whole run, check each target, write the receipt."""
    try:
        if run.stop_file.exists():
            run.stopped_reason = f"STOP file present ({run.stop_file.name})"
            run.skipped = len(targets)
        else:
            with open_page(local=local) as page:
                if setup:
                    setup(page)
                run.each(targets, lambda t: check(page, t))
    except Exception as exc:
        run.fatal = f"{type(exc).__name__}: {exc}"
    return run.finish(extra() if extra else None)
