#!/usr/bin/env python3
"""
Check a BigOrange.Marketing asset against the token ledger for its surface.

BigOrange has one orange in the logo (#FF7C00, sampled from the PNG) but the
live WordPress theme (Beaver Builder) paints #F68326 with a #D66509 border and a
#428BCA link blue, and the site sets Raleway, Open Sans and Poppins while decks
and PDFs set Montserrat. So the approved set differs per
surface (see references/tokens.md). This lints against the palette for the
surface you name and calls out anything off-ledger. Align HCM and Momentum 360
colours are banned everywhere: they are Dillon's other brands, not BigOrange.

Usage:
    python3 brand_lint.py --surface deck deck.js
    python3 brand_lint.py --surface document theme.css plan.css --strict
    python3 brand_lint.py --surface web page.html
    python3 brand_lint.py --list

Exit code 1 if any error-level finding is present (0 if only warnings).
"""

import argparse
import collections
import os
import re
import sys

SURFACES = {
    "deck": {
        "label": "PowerPoint decks (BigOrange primary deck reference, 2026-09-02)",
        "colours": {
            "#FF7C00": "BigOrange orange, sampled from the logo. Blocks, numerals, eyebrows.",
            "#D96400": "Deep orange for small text on light fields.",
            "#121212": "Ink. Dark slide grounds, titles on white.",
            "#2B2B2B": "Ink 2. Secondary dark card.",
            "#6E6A66": "Mute. Footer, captions.",
            "#F6F1EA": "Pith. Light card ground.",
            "#FFF3E8": "Peel. Warm tint card.",
            "#E4DDD4": "Line. Hairlines, grid.",
            "#CFC8C0": "Soft. Reverse muted text.",
            "#EDE7E0": "Reverse. Body text on dark.",
            "#1E6B3C": "Leaf. Sparse positive accent (charts only).",
            "#FFFFFF": "White.",
        },
        "fonts": ["Montserrat", "Arial"],
    },
    "document": {
        "label": "PDF documents: plans, blog PDFs, guides (doc-kit theme.css)",
        "colours": {
            "#FF7C00": "BigOrange orange.",
            "#D96400": "Deep orange, links.",
            "#121212": "Ink.",
            "#2B2B2B": "Ink 2.",
            "#6E6A66": "Mute.",
            "#F6F1EA": "Pith.",
            "#FFF3E8": "Peel.",
            "#E4DDD4": "Line.",
            "#CFC8C0": "Soft.",
            "#EDE7E0": "Reverse.",
            "#1E6B3C": "Leaf.",
            "#FFFFFF": "White.",
        },
        "fonts": ["Montserrat", "Source Serif 4", "Inter", "Arial", "Georgia"],
    },
    "web": {
        "label": "bigorange.marketing WordPress theme (Beaver Builder, observed 2026-09-02)",
        "colours": {
            "#F68326": "Theme accent orange: primary CTA fill (Beaver Builder skin, observed 2026-09-02).",
            "#D66509": "Theme CTA border orange.",
            "#FF7700": "Orange painted in older theme CSS (observed 2026-07-16).",
            "#FF7C00": "Logo orange. Acceptable where the logo sits.",
            "#428BCA": "Theme link and nav blue.",
            "#333333": "Theme dark text.",
            "#0D0D0D": "Theme near-black.",
            "#F2F2F2": "Theme light background.",
            "#FFFFFF": "White.",
        },
        "fonts": ["Raleway", "Open Sans", "Poppins", "Arial"],
    },
    "editorial": {
        "label": "Blog HTML shipped into WordPress (must match the theme)",
        "colours": {
            "#F68326": "Theme accent orange.",
            "#D66509": "Theme CTA border orange.",
            "#FF7700": "Older theme orange.",
            "#428BCA": "Theme link blue.",
            "#333333": "Theme dark text.",
            "#0D0D0D": "Theme near-black.",
            "#F2F2F2": "Theme light background.",
            "#F6F1EA": "Pith (tables, callouts).",
            "#FFF3E8": "Peel (direct-answer callout).",
            "#FFFFFF": "White.",
        },
        "fonts": ["Raleway", "Open Sans", "Poppins", "Arial"],
    },
    "social": {
        "label": "Instagram, LinkedIn, static social",
        "colours": {
            "#FF7C00": "BigOrange orange.",
            "#121212": "Ink.",
            "#F6F1EA": "Pith.",
            "#FFF3E8": "Peel.",
            "#FFFFFF": "White.",
        },
        "fonts": ["Montserrat", "Arial"],
    },
}

KNOWN_BAD = {
    "#232E3E": "Align HCM deck navy. Not BigOrange.",
    "#E97722": "Align HCM deck orange. Not BigOrange.",
    "#FF9902": "Align HCM web orange. Not BigOrange.",
    "#1A334E": "Align HCM deep navy. Not BigOrange.",
    "#2A80C2": "Momentum 360 / NeedMomentum blue. Not BigOrange.",
    "#2456C4": "Momentum report accent. Not BigOrange.",
    "#2B1A10": "Dark brown from the retired September v0 PDFs. Do not reuse.",
}

HEX_RE = re.compile(r"#([0-9A-Fa-f]{6})\b")
JS_HEX_RE = re.compile(r"['\"]([0-9A-Fa-f]{6})['\"]")
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.I)
JS_FONT_RE = re.compile(r"fontFace\s*:\s*['\"]([^'\"]+)['\"]", re.I)
GENERIC_FAMILIES = {"sans-serif", "serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif", "ui-serif", "inherit", "initial", "unset", "revert"}


def norm(h):
    return "#" + h.upper()


def lint_file(path, surface, strict):
    findings = []
    try:
        with open(path, "r", errors="replace") as fh:
            text = fh.read()
    except (IsADirectoryError, FileNotFoundError, PermissionError) as e:
        return [("error", 0, f"cannot read: {e}")]
    palette = SURFACES[surface]["colours"]
    allowed_fonts = [f.lower() for f in SURFACES[surface]["fonts"]]
    neutral = {"#FFFFFF", "#000000"}
    is_js = path.endswith(".js")
    for i, line in enumerate(text.splitlines(), 1):
        raws = HEX_RE.findall(line)
        if is_js:
            raws += JS_HEX_RE.findall(line)
        for raw in raws:
            h = norm(raw)
            if h in KNOWN_BAD:
                findings.append(("error", i, f"{h} is off-brand. {KNOWN_BAD[h]}"))
            elif h not in palette and h not in neutral:
                other = [s for s, d in SURFACES.items() if h in d["colours"] and s != surface]
                if other:
                    role = SURFACES[other[0]]["colours"][h]
                    findings.append(("error", i, f"{h} is not in the {surface} palette. It belongs to {'/'.join(other)} ({role})."))
                else:
                    findings.append(("warn", i, f"{h} is not in any BigOrange ledger. Confirm before shipping."))
        fams = []
        for decl in FONT_FAMILY_RE.findall(line):
            parts = [f.strip().strip("'\"").lower() for f in decl.split(",") if f.strip()]
            if parts:
                fams.append(parts[0])
        for f in JS_FONT_RE.findall(line):
            fams.append(f.strip().lower())
        for primary in fams:
            if primary.startswith("var(") or primary.startswith("--") or primary in GENERIC_FAMILIES:
                continue
            if primary not in allowed_fonts:
                findings.append(("warn" if not strict else "error", i, f"font '{primary}' is not in the {surface} stack ({', '.join(SURFACES[surface]['fonts'])})."))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--surface", choices=sorted(SURFACES))
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for name in sorted(SURFACES):
            d = SURFACES[name]
            print(f"\n[{name}] {d['label']}")
            for hexv, role in d["colours"].items():
                print(f"  {hexv}  {role}")
            print(f"  fonts: {', '.join(d['fonts'])}")
        print("\n[never use]")
        for hexv, why in KNOWN_BAD.items():
            print(f"  {hexv}  {why}")
        return 0
    if not args.files or not args.surface:
        ap.error("need --surface and at least one file (or use --list)")
    totals = collections.Counter()
    for path in args.files:
        if os.path.isdir(path):
            continue
        findings = lint_file(path, args.surface, args.strict)
        if findings:
            print(f"\n{path}")
            for level, line, msg in findings:
                print(f"  {level:5} {line:>5}: {msg}")
        for level, _, _ in findings:
            totals[level] += 1
    print(f"\n{totals['error']} error(s), {totals['warn']} warning(s) across {len(args.files)} file(s), surface={args.surface}")
    return 1 if totals["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
