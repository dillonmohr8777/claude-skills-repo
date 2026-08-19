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

def evaluate(candidate, target_width, problems=None):
    """
    Download and decode a candidate. Returns a dict or None.

    On failure it records why into `problems`, because "no logo found" and
    "the network refused every download" look identical from the outside and
    lead to opposite next steps.
    """
    url = candidate["url"]
    try:
        data, ctype, final = get(url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        if problems is not None:
            problems.append(("network", url, f"{type(exc).__name__}: {exc}"))
        return None
    except ValueError as exc:
        if problems is not None:
            problems.append(("url", url, str(exc)))
        return None
    if not data or len(data) < 64:
        if problems is not None:
            problems.append(("empty", url, f"{len(data) if data else 0} bytes"))
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


# Plate fills. White for dark marks, near-black for light ones. The dark fill is
# deliberately not the Align cover navy, so the plate reads as a deliberate card
# rather than a hole punched in the panel.
PLATE_LIGHT = (255, 255, 255)
PLATE_DARK = (11, 14, 18)


def ensure_visible(colour, against, target=2.0):
    """
    Nudge a colour's lightness until it separates from the plate fill.

    Hue is preserved by scaling the channels together, so the border stays
    recognisably the client's colour. Only lightness moves, and only as far as
    it must. A mark whose dominant colour is already distinct is untouched.
    """
    lum_against = li.relative_luminance(*against)
    r, g, b = colour
    if li.contrast_ratio(li.relative_luminance(r, g, b), lum_against) >= target:
        return colour, False
    darken = lum_against > 0.5  # light plate needs a darker border, and vice versa
    for _ in range(24):
        if darken:
            r, g, b = int(r * 0.88), int(g * 0.88), int(b * 0.88)
        else:
            r = min(255, int(r * 1.14) + 6)
            g = min(255, int(g * 1.14) + 6)
            b = min(255, int(b * 1.14) + 6)
        if li.contrast_ratio(li.relative_luminance(r, g, b), lum_against) >= target:
            break
    return (r, g, b), True


def choose_plate(img):
    """
    Decide plate polarity from how the mark actually reads, not a fixed cutoff.

    The mark is measured against both candidate fills and the one it reads
    better on wins, which handles mid-tone marks sensibly instead of forcing a
    luminance threshold that is wrong near the middle.
    """
    median = li.ink_analysis(img, PLATE_LIGHT)["median_luminance"]
    on_light = li.contrast_ratio(median, li.relative_luminance(*PLATE_LIGHT))
    on_dark = li.contrast_ratio(median, li.relative_luminance(*PLATE_DARK))
    if on_light >= on_dark:
        return PLATE_LIGHT, "light", on_light
    return PLATE_DARK, "dark", on_dark


def apply_plate(img, notes):
    """Put the mark on a bordered plate sized from the artwork itself."""
    fill, polarity, contrast_on_fill = choose_plate(img)
    raw_border = li.dominant_colour(img)
    border, adjusted = ensure_visible(raw_border, fill)

    short = min(img.w, img.h)
    border_width = max(6, round(short * 0.045))
    pad = max(10, round(short * 0.09))
    radius = max(10, round(min(img.w + 2 * pad, img.h + 2 * pad) * 0.12))

    plated = li.make_plate(img, border, fill, pad, border_width, radius)

    def hexof(c):
        return "#%02X%02X%02X" % c

    notes.append(
        f"placed on a {polarity} plate {hexof(fill)} with a {border_width}px "
        f"{hexof(border)} border taken from the mark"
        + (f" (lightened or darkened from {hexof(raw_border)} to stay visible)"
           if adjusted else ""))
    return plated, {
        "applied": True,
        "polarity": polarity,
        "fill": hexof(fill),
        "border": hexof(border),
        "border_source": hexof(raw_border),
        "border_adjusted": adjusted,
        "border_width_px": border_width,
        "pad_px": pad,
        "mark_contrast_on_plate": round(contrast_on_fill, 2),
    }


def process(entry, min_width, target_width, aggressive):
    """Clean the chosen raster. Returns (image, notes)."""
    img = entry["img"]
    notes = []

    # Whether the asset still carries an unremovable background box has to be
    # judged here, before trimming. Trimming crops to the mark's bounding box,
    # after which a perfectly good transparent logo whose ink fills that box is
    # indistinguishable from one that still has a solid backing plate.
    opaque_risk = False
    if not entry["has_alpha"]:
        img, removed = li.remove_background(img)
        if removed > 0.01:
            notes.append(f"removed flat background ({removed * 100:.0f}% of pixels)")
            img, fringed = li.defringe(img)
            if fringed:
                notes.append(f"defringed {fringed} edge pixels")
        else:
            notes.append("background is not flat and could not be keyed")
            opaque_risk = True
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

    return img, notes, {"opaque_risk": opaque_risk}


def doctor(base, host):
    """
    Answer one question: can this machine fetch from this site at all?

    Worth its own mode because a locked-down network and a site with no usable
    logo both end with an empty hand, and the fixes are opposite. One needs a
    proxy exception; the other needs the file supplied by hand.
    """
    print(f"logo fetch doctor for {host}")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    print(f"  proxy env      {proxy or 'not set'}")

    try:
        html_bytes, ctype, final = get(base + "/")
    except Exception as exc:
        print(f"  homepage       UNREACHABLE ({type(exc).__name__}: {exc})")
        print()
        print("This machine cannot reach the site. Nothing about the company's "
              "artwork can be concluded from here.")
        print("Either run the fetch from a network that permits outbound HTTPS "
              "to the client's domain, or download the logo by hand and pass "
              "it to prepare_client_deck.py with --client-logo.")
        return 5
    html = html_bytes.decode("utf8", "replace")
    print(f"  homepage       OK ({len(html_bytes):,} bytes, {ctype or 'no type'})")

    candidates = discover(base, html) + probe_well_known(base)
    print(f"  candidates     {len(candidates)} found in markup and well-known paths")
    if not candidates:
        print()
        print("The page loaded but advertises no logo candidate. That is a "
              "property of the site, not of this machine.")
        return 3

    problems, reached = [], 0
    for cand in candidates[:6]:
        entry = evaluate(cand, 1200, problems)
        if entry is not None:
            reached += 1
    print(f"  downloads      {reached} of {min(len(candidates), 6)} "
          f"probed candidate(s) decoded")
    for kind, url, why in problems[:4]:
        print(f"    {kind:8} {url[:64]}  {why[:50]}")

    print()
    if reached:
        print("Egress works and at least one candidate decodes. A normal run "
              "should succeed; if it does not, the failure is the quality gate "
              "rather than the network.")
        return 0
    blocked = [x for x in problems if x[0] == "network"]
    if blocked and len(blocked) == len(problems):
        print("The homepage loads but every asset download is refused. This is "
              "an egress restriction on subresources, not a site without a logo.")
        return 5
    print("Candidates downloaded but none decoded. This is an artwork problem, "
          "not a network one. Supply the logo by hand.")
    return 3


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--domain", required=True,
                    help="company domain or URL, e.g. acme.com")
    ap.add_argument("--out", help="output PNG path (not needed with --doctor)")
    ap.add_argument("--doctor", action="store_true",
                    help="report whether this machine can reach the site and "
                         "download an asset from it, then stop")
    ap.add_argument("--name", help="company name, recorded in the provenance file")
    ap.add_argument("--min-width", type=int, default=600,
                    help="reject anything narrower after trimming (default 600)")
    ap.add_argument("--target-width", type=int, default=1200,
                    help="rasterise vectors at this width (default 1200)")
    ap.add_argument("--resample", action="store_true",
                    help="also downscale oversized rasters to --target-width")
    ap.add_argument("--plate", choices=("always", "auto", "never"), default="always",
                    help="put the mark on a bordered plate. 'always' (default) "
                         "treats every client the same way; 'auto' plates only "
                         "when the bare mark would fail on navy; 'never' places "
                         "the mark directly")
    ap.add_argument("--cover-bg", default="232E3E",
                    help="hex of the field the mark sits on, for the legibility "
                         "check (default 232E3E, the Align cover navy)")
    ap.add_argument("--allow-low-quality", action="store_true",
                    help="write the file even if it fails the quality gate")
    ap.add_argument("--json", action="store_true", help="machine-readable summary")
    args = ap.parse_args()
    if not args.doctor and not args.out:
        ap.error("--out is required unless you pass --doctor")

    base, host = normalise_domain(args.domain)
    if args.doctor:
        return doctor(base, host)

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
    problems = []
    for cand in sorted(candidates, key=lambda c: -KIND_SCORE.get(c["kind"], 0)):
        entry = evaluate(cand, args.target_width, problems)
        if entry is None or "img" not in entry:
            continue
        entry["score"] = score(entry)  # reverse variants are preferred for navy
        scored.append(entry)
        log(f"  {entry['kind']:16} {entry['width']:>5}x{entry['height']:<5} "
            f"alpha={'y' if entry['has_alpha'] else 'n'} score={entry['score']} "
            f"{entry['url'][:70]}")

    if not scored:
        blocked = [p for p in problems if p[0] == "network"]
        if candidates and len(blocked) == len(problems) and blocked:
            log(f"error: all {len(blocked)} candidate download(s) failed at the "
                f"network layer, so this is an egress problem rather than a "
                f"site with no usable logo.")
            log(f"  first failure: {blocked[0][1]}")
            log(f"  reason: {blocked[0][2]}")
            log("Run with --doctor to confirm, or supply the file manually "
                "with --client-logo on prepare_client_deck.py.")
            return 5
        log(f"error: no decodable logo candidate found "
            f"({len(candidates)} candidate(s) examined, "
            f"{len(problems)} rejected)")
        for kind, url, why in problems[:5]:
            log(f"  {kind:8} {url[:70]}  {why[:60]}")
        return 3

    best = max(scored, key=lambda e: e["score"])
    log(f"chosen: {best['url']}")

    img, notes, meta = process(best, args.min_width, args.target_width, args.resample)
    for note in notes:
        log(f"  {note}")

    # Size and shape are judged on the mark itself, before any plate is added,
    # so plate padding cannot disguise a logo that was too small to use.
    problems = []
    if img.w < args.min_width:
        problems.append(
            f"only {img.w}px wide after trimming; the cover zone needs at least "
            f"{args.min_width}px to stay sharp")
    ratio = img.w / max(1, img.h)
    if ratio > 12 or ratio < 0.08:
        problems.append(f"extreme aspect ratio {ratio:.1f}:1; likely not the mark")

    bg = tuple(int(args.cover_bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    bare = li.ink_analysis(img, bg)
    log(f"  bare on #{args.cover_bg.lstrip('#').upper()}: "
        f"contrast {bare['contrast']:.2f}:1, "
        f"{bare['low_contrast_share'] * 100:.0f}% of ink below 3:1")

    # The plate rule. A prospect's mark is designed for their background, not
    # for Align navy, so rather than rejecting it or recolouring it, it goes on
    # a card of the opposite polarity edged in its own colour. `auto` plates
    # only when the bare mark would fail; `always` plates every client for a
    # consistent cover across decks.
    plate = {"applied": False}
    needs_plate = bare["contrast"] < 3.0 or bare["low_contrast_share"] > 0.5
    if args.plate == "always" or (args.plate == "auto" and needs_plate):
        img, plate = apply_plate(img, notes)
        for note in notes[-1:]:
            log(f"  {note}")
    elif needs_plate:
        problems.append(
            f"the mark reads at only {bare['contrast']:.2f}:1 against the navy cover "
            f"field, and {bare['low_contrast_share'] * 100:.0f}% of its ink falls "
            f"below 3:1. It will disappear on the slide. Re-run without "
            f"--plate never, or use the client's reverse variant.")

    if meta["opaque_risk"] and not plate["applied"]:
        problems.append(
            "the background could not be keyed, so the mark will show as a "
            "rectangle on navy. A plate would cover this; re-run without "
            "--plate never.")

    # Final legibility, measured against whatever the mark now sits on.
    if plate["applied"]:
        fill = tuple(int(plate["fill"][1:][i:i + 2], 16) for i in (0, 2, 4))
        final = li.ink_analysis(img, fill)
        log(f"  on plate {plate['fill']}: mark contrast "
            f"{plate['mark_contrast_on_plate']:.2f}:1")
        if plate["mark_contrast_on_plate"] < 3.0:
            problems.append(
                f"even on a {plate['polarity']} plate the mark only reaches "
                f"{plate['mark_contrast_on_plate']:.2f}:1; the artwork may be a "
                f"gradient or photographic lockup that needs manual treatment")
    else:
        final = bare

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
            "cover_background": "#" + args.cover_bg.lstrip("#").upper(),
            "bare_contrast": round(bare["contrast"], 2),
            "bare_low_contrast_share": round(bare["low_contrast_share"], 3),
            "final_contrast": round(final["contrast"], 2),
        },
        "plate": plate,
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
