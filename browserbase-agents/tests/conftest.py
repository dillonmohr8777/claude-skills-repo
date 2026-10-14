"""Offline test helpers: a fake Playwright page that serves fixture HTML, no network."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import bb

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


def html_to_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|template)\b.*?</\1>", "", html)
    html = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h\d|section|header|footer|span|td|a|button)>", "\n", html)
    text = re.sub(r"<[^>]+>", "", html)
    for ent, ch in (("&amp;", "&"), ("&nbsp;", " "), ("&#39;", "'"), ("&quot;", '"')):
        text = text.replace(ent, ch)
    return "\n".join(ln.strip() for ln in text.splitlines() if ln.strip())


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status


class FakePage:
    """Serves {url: html} (or {url: (status, html)}); unknown URLs 404 with empty body."""

    def __init__(self, pages: dict, metrics: dict | None = None, redirects: dict | None = None) -> None:
        self.pages = pages
        self.metrics = metrics or {}
        self.redirects = redirects or {}
        self.url = "about:blank"
        self.visited: list[str] = []
        self.viewports: list[dict] = []
        self.handlers: dict[str, list] = {}
        self._html = ""

    def goto(self, url: str, **_: object) -> FakeResponse:
        self.visited.append(url)
        self.url = self.redirects.get(url, url)
        entry = self.pages.get(url)
        if entry is None:
            entry = next(
                (v for k, v in self.pages.items() if k.endswith("*") and url.startswith(k[:-1])), (404, "")
            )
        status, self._html = entry if isinstance(entry, tuple) else (200, entry)
        return FakeResponse(status)

    def wait_for_load_state(self, *_: object, **__: object) -> None:
        pass

    def wait_for_timeout(self, *_: object) -> None:
        pass

    def content(self) -> str:
        return self._html

    def inner_text(self, *_: object, **__: object) -> str:
        return html_to_text(self._html)

    def screenshot(self, path: str, **_: object) -> None:
        Path(path).write_bytes(b"\x89PNG fake")

    def evaluate(self, _js: str) -> dict:
        m = self.metrics
        return m(self.viewports[-1]["width"]) if callable(m) else m

    def set_viewport_size(self, size: dict) -> None:
        self.viewports.append(size)

    def on(self, event: str, handler) -> None:
        self.handlers.setdefault(event, []).append(handler)


@pytest.fixture
def run(tmp_path):
    return bb.Run("test_agent", out_root=tmp_path / "out", stop_file=tmp_path / "STOP")
