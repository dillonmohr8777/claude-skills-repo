#!/usr/bin/env python3
"""
Find, fetch, and clean a client or prospect logo for the Align cover slide.

    python3 fetch_client_logo.py --domain acme.com --out acme-logo.png

It reads the company's own site, ranks every logo candidate it can find, takes
the best one, removes a flat background if the asset is not already transparent,
strips the halo that leaves, trims the margins, and checks the result is good
enough for a deck. It writes a `.source.json` beside the PNG recording where the
artwork came from and what was done to it, because the skill requires a source
locator for any placed mark.

Ranking is by role first, then by whether the asset needs modification:

    header logo  >  og:image  >  apple-touch-icon  >  favicon

with a bonus for vector and for already-transparent assets, and a further bonus
for a URL naming a reverse or white variant. Role has to dominate: a favicon
served as an SVG is still a favicon, and an earlier version that ranked every
vector equally picked 32px icons over the real logo on every real site tried.

Quality gate. The cover zone is 2.9 inches wide, so anything under
`--min-width` (default 600px) after trimming is too soft to place and the script
exits non-zero rather than handing back a blurry mark. A favicon will always
fail this, by design.

Exit codes:
    0  a logo good enough to place
    2  found something, but it failed the quality gate
    3  found nothing usable
    4  network or site unreachable

Stdlib only. Pillow is used if already installed, for JPEG and WebP sources and
better resampling, but is never required.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logo_image as li  # noqa: E402

UA = ("Mozilla/5.0 (compatible; AlignHCM-BrandSystem/1.0; "
      "+https://www.alignhcm.com/)")
TIMEOUT = 25

# What role the asset plays on the page, best to worst. This is deliberately
# separate from whether the asset is vector: a favicon is still a favicon when
# it is an SVG, and must not outrank the header logo just for being one.
KIND_SCORE = {
    "site-logo-img": 700,
    "og-image": 500,
    "logo-api": 450,
    "apple-touch-icon": 300,
    "icon": 200,
}

WELL_KNOWN = [
    "/logo.svg", "/assets/logo.svg", "/assets/img/logo.svg",
    "/static/logo.svg", "/images/logo.svg", "/img/logo.svg",
    "/logo.png", "/assets/logo.png", "/images/logo.png",
]


def log(msg):
    print(msg, file=sys.stderr)


def get(url, referer=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "*/*",
        **({"Referer": referer} if referer else {}),
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read(), resp.headers.get("Content-Type", ""), resp.geturl()


def normalise_domain(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parts = urllib.parse.urlparse(value)
    return parts.scheme + "://" + parts.netloc, parts.netloc


# ---------------------------------------------------------------------------
# Candidate discovery
# ---------------------------------------------------------------------------

def _abs(base, href):
    return urllib.parse.urljoin(base, href.strip())


def _size_from_attr(attr):
    m = re.search(r"(\d+)\s*x\s*(\d+)", attr or "", re.I)
    return int(m.group(1)) if m else 0


def discover(base, html):
    """Every plausible logo URL on the page, tagged with what kind it is."""
    found = []
    seen = set()

    def add(url, kind, hint=0):
        if not url or url.startswith("data:"):
            return
        url = _abs(base, url)
        if url in seen:
            return
        seen.add(url)
        found.append({"url": url, "kind": kind, "hint": hint})

    for m in re.finditer(r"<link\b[^>]*>", html, re.I):
        tag = m.group(0)
        rel = (re.search(r'rel=["\']([^"\']+)', tag, re.I) or [None, ""])[1].lower()
        href = (re.search(r'href=["\']([^"\']+)', tag, re.I) or [None, ""])[1]
        sizes = (re.search(r'sizes=["\']([^"\']+)', tag, re.I) or [None, ""])[1]
        if not href:
            continue
        if "apple-touch-icon" in rel:
            add(href, "apple-touch-icon", _size_from_attr(sizes) or 180)
        elif "icon" in rel:
            add(href, "icon", _size_from_attr(sizes))
        elif "mask-icon" in rel and href.lower().endswith(".svg"):
            add(href, "icon", 0)

    for prop in ("og:image", "twitter:image", "og:logo"):
        for m in re.finditer(
                r'<meta\b[^>]*(?:property|name)=["\']' + re.escape(prop)
                + r'["\'][^>]*>', html, re.I):
            content = (re.search(r'content=["\']([^"\']+)', m.group(0), re.I)
                       or [None, ""])[1]
            add(content, "og-image")

    # <img> whose src, alt, class, or id mentions a logo. Ranked above og:image
    # because og:image is often a social card, not the mark.
    for m in re.finditer(r"<img\b[^>]*>", html, re.I):
        tag = m.group(0)
        if not re.search(r"logo|brand|wordmark", tag, re.I):
            continue
        src = (re.search(r'\bsrc=["\']([^"\']+)', tag, re.I) or [None, ""])[1]
        if not src:
            srcset = (re.search(r'\bsrcset=["\']([^"\']+)', tag, re.I) or [None, ""])[1]
            if srcset:
                src = srcset.split(",")[-1].strip().split()[0]
        if src:
            add(src, "site-logo-img", _size_from_attr(tag))

    # Inline <svg> inside a logo-ish wrapper is common but not separately
    # fetchable, so it is intentionally out of scope here.
    return found


def probe_well_known(base):
    out = []
    for path in WELL_KNOWN:
        out.append({"url": base + path, "kind": "site-logo-img",
                    "hint": 0, "speculative": True})
    return out


# ---------------------------------------------------------------------------
# Rasterising
# ---------------------------------------------------------------------------

def force_svg_size(svg_bytes, width):
    """
    Rewrite the SVG's own width and height to the size we want.

    Only rsvg-convert and inkscape accept a width flag. LibreOffice rasterises
    at the file's intrinsic size, so a 32px favicon stays 32px and the whole
    point of preferring vector is lost. Setting the attributes in the file makes
    every backend agree.
    """
    head_end = svg_bytes.find(b">")
    if head_end == -1 or b"<svg" not in svg_bytes[:head_end + 1]:
        return svg_bytes
    head = svg_bytes[:head_end + 1].decode("utf8", "replace")

    box = re.search(r'viewBox\s*=\s*["\']\s*[\d.eE+-]+[ ,]+[\d.eE+-]+[ ,]+'
                    r'([\d.eE+-]+)[ ,]+([\d.eE+-]+)', head)
    if box:
        vw, vh = float(box.group(1)), float(box.group(2))
    else:
        w = re.search(r'\bwidth\s*=\s*["\']([\d.]+)', head)
        h = re.search(r'\bheight\s*=\s*["\']([\d.]+)', head)
        if not (w and h):
            return svg_bytes
        vw, vh = float(w.group(1)), float(h.group(1))
    if vw <= 0 or vh <= 0:
        return svg_bytes

    height = max(1, round(width * vh / vw))
    head = re.sub(r'\s\bwidth\s*=\s*["\'][^"\']*["\']', "", head)
    head = re.sub(r'\s\bheight\s*=\s*["\'][^"\']*["\']', "", head)
    head = head[:-1].rstrip() + f' width="{width}" height="{height}">'
    return head.encode("utf8") + svg_bytes[head_end + 1:]


def svg_to_png(svg_bytes, width):
    """Rasterise SVG via whatever converter exists. Returns PNG bytes or None."""
    svg_bytes = force_svg_size(svg_bytes, width)
    with tempfile.TemporaryDirectory() as tmp:
        svg = os.path.join(tmp, "in.svg")
        with open(svg, "wb") as fh:
            fh.write(svg_bytes)

        from shutil import which
        if which("rsvg-convert"):
            png = os.path.join(tmp, "out.png")
            r = subprocess.run(["rsvg-convert", "-w", str(width), "-o", png, svg],
                               capture_output=True)
            if r.returncode == 0 and os.path.exists(png):
                with open(png, "rb") as fh:
                    return fh.read()
        if which("inkscape"):
            png = os.path.join(tmp, "out.png")
            r = subprocess.run(
                ["inkscape", svg, "--export-type=png", f"--export-filename={png}",
                 f"--export-width={width}"], capture_output=True)
            if r.returncode == 0 and os.path.exists(png):
                with open(png, "rb") as fh:
                    return fh.read()
        if which("soffice"):
            r = subprocess.run(
                ["soffice", f"-env:UserInstallation=file://{tmp}/lo", "--headless",
                 "--norestore", "--convert-to", "png", "--outdir", tmp, svg],
                capture_output=True, timeout=300)
            png = os.path.join(tmp, "in.png")
            if os.path.exists(png):
                with open(png, "rb") as fh:
                    return fh.read()
    return None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def evaluate(candidate, target_width):
    """Download and decode a candidate. Returns a dict or None."""
    url = candidate["url"]
    try:
        data, ctype, final = get(url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None
    if not data or len(data) < 64:
        return None

    is_svg = (b"<svg" in data[:2048].lower()
              or "svg" in ctype.lower()
              or url.lower().split("?")[0].endswith(".svg"))
    rasterised_from_svg = False

    if is_svg:
        png = svg_to_png(data, target_width)
        if png is None:
            return {"url": url, "kind": candidate["kind"],
                    "error": "no SVG rasteriser available"}
        data = png
        rasterised_from_svg = True

    try:
        img = li.load_any(data)
    except ValueError as exc:
        return {"url": url, "kind": candidate["kind"], "error": str(exc)}

    return {
        "url": final,
        "kind": candidate["kind"],
        "img": img,
        "width": img.w,
        "height": img.h,
        "vector": rasterised_from_svg,
        "has_alpha": li.has_real_alpha(img),
    }


# Many sites ship a reverse mark for dark backgrounds alongside the primary.
# The Align cover is navy, so that variant is the one worth having.
REVERSE_HINT = re.compile(r"reverse|reversed|white|light|inverse|inverted|knockout|-kb|on-dark",
                          re.I)


def score(entry, prefer_reverse=True):
    """
    Rank by role first, then by whether it needs modification, then by size.

    Role dominates on purpose. A favicon served as SVG is still a favicon, and
    an earlier version that scored every vector identically picked 32px icons
    over the 512px header logo on every real site it was tried against.
    """
    if "img" not in entry:
        return -1
    base = KIND_SCORE.get(entry["kind"], 100)
    if entry["vector"]:
        base += 400  # scales to any size, usually already transparent
    if entry["has_alpha"]:
        base += 200  # no keying needed
    # Size still matters for a vector, because the rasteriser available here may
    # not honour a requested width and the intrinsic size is what we get.
    base += min(entry["width"], 2000) // 10
    ratio = entry["width"] / max(1, entry["height"])
    if 0.95 < ratio < 1.05 and entry["width"] <= 256:
        base -= 150  # a small square mark is almost certainly an icon
    if prefer_reverse and REVERSE_HINT.search(entry["url"]):
        base += 350
    return base


def process(entry, min_width, target_width, aggressive):
    """Clean the chosen raster. Returns (image, notes)."""
    img = entry["img"]
    notes = []

    if not entry["has_alpha"]:
        img, removed = li.remove_background(img)
        if removed > 0.01:
            notes.append(f"removed flat background ({removed * 100:.0f}% of pixels)")
            img, fringed = li.defringe(img)
            if fringed:
                notes.append(f"defringed {fringed} edge pixels")
        else:
            notes.append("background is not flat; left unmodified")
    else:
        notes.append("source already transparent; no keying needed")

    img, cropped = li.trim(img)
    if cropped:
        notes.append(f"trimmed to {img.w}x{img.h}")

    if entry["vector"] and img.w < target_width:
        notes.append("vector source; re-rasterise larger if more size is needed")
    if aggressive and img.w > target_width:
        img = li.scale_to_width(img, target_width)
        notes.append(f"resampled down to {target_width}px wide")

    return img, notes


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--domain", required=True,
                    help="company domain or URL, e.g. acme.com")
    ap.add_argument("--out", required=True, help="output PNG path")
    ap.add_argument("--name", help="company name, recorded in the provenance file")
    ap.add_argument("--min-width", type=int, default=600,
                    help="reject anything narrower after trimming (default 600)")
    ap.add_argument("--target-width", type=int, default=1200,
                    help="rasterise vectors at this width (default 1200)")
    ap.add_argument("--resample", action="store_true",
                    help="also downscale oversized rasters to --target-width")
    ap.add_argument("--cover-bg", default="232E3E",
                    help="hex of the field the mark sits on, for the legibility "
                         "check (default 232E3E, the Align cover navy)")
    ap.add_argument("--allow-low-quality", action="store_true",
                    help="write the file even if it fails the quality gate")
    ap.add_argument("--json", action="store_true", help="machine-readable summary")
    args = ap.parse_args()

    base, host = normalise_domain(args.domain)

    try:
        html_bytes, _, final_url = get(base + "/")
        html = html_bytes.decode("utf8", "replace")
        base = final_url.rstrip("/") if final_url else base
    except Exception as exc:
        log(f"error: could not reach {base}: {exc}")
        log("If this machine is behind a restrictive proxy, supply the logo "
            "manually with --client-logo on prepare_client_deck.py.")
        return 4

    candidates = discover(base, html)
    log(f"discovered {len(candidates)} candidate(s) on {host}")
    candidates += probe_well_known(base)

    scored = []
    for cand in sorted(candidates, key=lambda c: -KIND_SCORE.get(c["kind"], 0)):
        entry = evaluate(cand, args.target_width)
        if entry is None or "img" not in entry:
            continue
        entry["score"] = score(entry)  # reverse variants are preferred for navy
        scored.append(entry)
        log(f"  {entry['kind']:16} {entry['width']:>5}x{entry['height']:<5} "
            f"alpha={'y' if entry['has_alpha'] else 'n'} score={entry['score']} "
            f"{entry['url'][:70]}")

    if not scored:
        log("error: no decodable logo candidate found")
        return 3

    best = max(scored, key=lambda e: e["score"])
    log(f"chosen: {best['url']}")

    img, notes = process(best, args.min_width, args.target_width, args.resample)
    for note in notes:
        log(f"  {note}")

    problems = []
    if img.w < args.min_width:
        problems.append(
            f"only {img.w}px wide after trimming; the cover zone needs at least "
            f"{args.min_width}px to stay sharp")
    if not li.has_real_alpha(img):
        problems.append("still fully opaque; it will show as a rectangle on navy")
    ratio = img.w / max(1, img.h)
    if ratio > 12 or ratio < 0.08:
        problems.append(f"extreme aspect ratio {ratio:.1f}:1; likely not the mark")

    # Legibility on the cover field. A transparent background is not enough: a
    # dark mark keyed onto the navy panel is invisible, which is the most common
    # way an auto-fetched logo fails once it is actually on the slide.
    bg = tuple(int(args.cover_bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    ink = li.ink_analysis(img, bg)
    log(f"  legibility on #{args.cover_bg.lstrip('#').upper()}: "
        f"contrast {ink['contrast']:.2f}:1, "
        f"{ink['low_contrast_share'] * 100:.0f}% of ink below 3:1")
    if ink["contrast"] < 3.0 or ink["low_contrast_share"] > 0.5:
        problems.append(
            f"the mark reads at only {ink['contrast']:.2f}:1 against the navy cover "
            f"field, and {ink['low_contrast_share'] * 100:.0f}% of its ink falls "
            f"below 3:1. It will disappear on the slide. Look for the client's "
            f"reverse or white logo variant, or place this one on the approved "
            f"light-background plate described in powerpoint-deck-system.md.")

    payload = {
        "client": args.name or host,
        "domain": host,
        "source_url": best["url"],
        "source_kind": best["kind"],
        "vector_source": best["vector"],
        "original_size": [best["width"], best["height"]],
        "final_size": [img.w, img.h],
        "processing": notes,
        "legibility": {
            "background": "#" + args.cover_bg.lstrip("#").upper(),
            "contrast": round(ink["contrast"], 2),
            "low_contrast_share": round(ink["low_contrast_share"], 3),
        },
        "needs_human_review": any("removed flat background" in n for n in notes),
        "problems": problems,
        "passed": not problems,
    }

    if problems and not args.allow_low_quality:
        log("")
        for p in problems:
            log(f"REJECTED: {p}")
        log("\nGet the official asset from the company brand kit or press page, "
            "or re-run with --allow-low-quality to write it anyway.")
        if args.json:
            print(json.dumps(payload, indent=2))
        return 2

    out_dir = os.path.dirname(os.path.abspath(args.out)) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(li.encode_png(img))
    with open(args.out + ".source.json", "w") as fh:
        json.dump(payload, fh, indent=2)

    log(f"\nwrote {args.out} ({img.w}x{img.h})")
    log(f"wrote {args.out}.source.json")
    if payload["needs_human_review"]:
        log("NOTE: the background was keyed out. Look at the result on the navy "
            "cover before sending this deck.")
    if args.json:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
