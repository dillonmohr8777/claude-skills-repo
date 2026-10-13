"""Landing-page QA at 390, 768 and 1440 widths with pass/fail per check.

Checks HTTP status, horizontal overflow, console errors, broken images, form present,
tel:/mailto: links, tap targets under 44px, title and meta description, and
screenshots every width. Loads pages only; never fills or submits forms.
"""

from __future__ import annotations

import sys
from typing import Any

import bb

AGENT = "lp_qa"
WIDTHS = (390, 768, 1440)
TOUCH_WIDTHS = (390, 768)
HEIGHTS = {390: 844, 768: 1024, 1440: 900}
MIN_TAP = 44
ADVISORY = {"mailto_link"}

METRICS_JS = """
() => {
  const vw = window.innerWidth;
  const doc = document.documentElement;
  const overflow = Math.max(doc.scrollWidth, document.body ? document.body.scrollWidth : 0) - vw;
  const sel = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button]';
  const small = [];
  for (const el of document.querySelectorAll(sel)) {
    if (el.tagName === 'A' && el.closest('p, li > p')) continue;  // inline text links are exempt
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (r.width === 0 || r.height === 0 || st.visibility === 'hidden' || st.display === 'none') continue;
    if (r.width < MIN_TAP || r.height < MIN_TAP) {
      small.push({tag: el.tagName.toLowerCase(),
                  text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 40),
                  w: Math.round(r.width), h: Math.round(r.height)});
    }
  }
  const broken = [...document.images]
    .filter(i => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src))
    .map(i => i.currentSrc || i.src);
  return {overflow_px: overflow, small_tap_targets: small.length,
          small_samples: small.slice(0, 10), broken_images: broken.slice(0, 20)};
}
""".replace("MIN_TAP", str(MIN_TAP))


class Collector:
    """Console errors and failed image responses for the current load."""

    def __init__(self) -> None:
        self.console_errors: list[str] = []
        self.failed_images: list[str] = []

    def reset(self) -> None:
        self.console_errors, self.failed_images = [], []

    def attach(self, page: Any) -> None:
        page.on("console", self._on_console)
        page.on("pageerror", lambda err: self.console_errors.append(f"pageerror: {str(err)[:300]}"))
        page.on("response", self._on_response)

    def _on_console(self, msg: Any) -> None:
        if msg.type != "error":
            return
        location = getattr(msg, "location", None) or {}
        if "favicon" in str(location.get("url", "")):  # the browser's own favicon probe, not the page
            return
        self.console_errors.append(msg.text[:300])

    def _on_response(self, resp: Any) -> None:
        try:
            if resp.request.resource_type == "image" and resp.status >= 400:
                self.failed_images.append(resp.url[:300])
        except Exception:
            pass


def html_checks(html: str) -> dict:
    doc = bb.parse_html(html)
    title = " ".join(doc.title.split())
    desc = " ".join(doc.metas.get("description", "").split())
    tels = sorted({ln["href"] for ln in doc.links if ln["href"].lower().startswith("tel:")})
    mails = sorted({ln["href"] for ln in doc.links if ln["href"].lower().startswith("mailto:")})
    return {
        "title": _check(10 <= len(title) <= 65, f"{len(title)} chars: {title[:80]!r}"),
        "meta_description": _check(50 <= len(desc) <= 160, f"{len(desc)} chars"),
        "form_present": _check(doc.forms > 0, f"{doc.forms} form(s)"),
        "tel_link": _check(bool(tels), ", ".join(tels[:3]) or "none"),
        "mailto_link": _check(bool(mails), ", ".join(mails[:3]) or "none", advisory=True),
    }


def _check(passed: bool | None, detail: Any, advisory: bool = False) -> dict:
    out = {"pass": passed, "detail": detail}
    if advisory:
        out["advisory"] = True
    return out


def width_checks(width: int, metrics: dict) -> dict:
    overflow = metrics.get("overflow_px", 0)
    checks = {"no_horizontal_overflow": _check(overflow <= 1, f"{overflow}px wider than viewport")}
    if width in TOUCH_WIDTHS:
        n = metrics.get("small_tap_targets", 0)
        checks["tap_targets_44px"] = _check(n == 0, {"count": n, "samples": metrics.get("small_samples", [])})
    return checks


def failed(checks: dict) -> list[str]:
    return [name for name, c in checks.items() if c["pass"] is False and not c.get("advisory")]


def check_target(page: Any, target: dict, run: bb.Run, collector: Collector) -> dict:
    url = target["url"]
    name = bb.target_name(target)
    widths: dict[int, dict] = {}
    shots: list[str] = []
    console: list[str] = []
    broken: set[str] = set()
    status_code = None
    html = ""
    for width in WIDTHS:
        collector.reset()
        page.set_viewport_size({"width": width, "height": HEIGHTS[width]})
        response = bb.load(page, url, settle_ms=1000)
        if width == WIDTHS[0]:
            status_code = response.status if response is not None else None
            html = page.content()
        metrics = page.evaluate(METRICS_JS) or {}
        broken.update(metrics.get("broken_images", []))
        broken.update(collector.failed_images)
        console.extend(f"[{width}] {e}" for e in collector.console_errors)
        widths[width] = width_checks(width, metrics)
        shot = bb.screenshot(page, run.shot(f"{name}-{width}"))
        if shot:
            shots.append(shot)

    checks = {
        "http_status": _check(status_code is not None and 200 <= status_code < 400, status_code),
        "console_errors": _check(not console, console[:10]),
        "broken_images": _check(not broken, sorted(broken)[:20]),
        **html_checks(html),
    }
    fails = failed(checks) + [f"{chk}@{w}" for w, c in widths.items() for chk in failed(c)]
    return {
        "status": "fail" if fails else "ok",
        "url": url,
        "failed": fails,
        "checks": checks,
        "widths": widths,
        "screenshots": shots,
    }


def main(argv: list[str] | None = None) -> int:
    args = bb.base_parser(__doc__.splitlines()[0]).parse_args(argv)
    targets = bb.load_targets(AGENT, args.targets)
    run = bb.Run(AGENT, max_targets=args.max_targets, max_minutes=args.max_minutes, out_root=args.out)
    collector = Collector()
    return bb.run_agent(
        run,
        targets,
        lambda page, t: check_target(page, t, run, collector),
        local=args.local,
        setup=collector.attach,
    )


if __name__ == "__main__":
    sys.exit(main())
