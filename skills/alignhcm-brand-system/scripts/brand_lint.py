#!/usr/bin/env python3
"""
Check an Align HCM asset against the token ledger for its surface.

Align does not have one orange -- it has a different approved orange per
surface (see references/tokens.md). A flat "is this hex on the list" check
would therefore pass a web orange dropped into a deck. This lints against the
palette for the surface you name, and calls out anything off-ledger.

Text files (HTML, CSS, Markdown) are scanned for CSS-form colour and
font-family. Office packages (.docx, .pptx) are unzipped and their XML parts
are scanned for the attribute forms Office actually writes, because a compressed
zip contains no readable hex and would otherwise pass every check silently.

Usage:
    python3 brand_lint.py --surface web  page.html
    python3 brand_lint.py --surface document report.docx
    python3 brand_lint.py --surface deck deck.pptx --strict
    python3 brand_lint.py --list

Findings are located by line number for text and by part name for Office files.
Exit code 1 if any error-level finding is present (0 if only warnings), so it
can gate a build step.
"""

import argparse
import collections
import os
import re
import sys
import zipfile

# ---------------------------------------------------------------------------
# Token ledger. Mirrors references/tokens.md -- keep the two in step.
# Deck and document values come from the supplied primary deck reference.
# ---------------------------------------------------------------------------

SURFACES = {
    "web": {
        "label": "Web / HubSpot CMS (live alignhcm.com tokens, observed 2026-07-15)",
        "colours": {
            "#2C3C4C": "Slate - primary text, dark fields",
            "#1A334E": "Deep navy - cover, section breaks",
            "#041424": "Ink navy - deepest background, footer",
            "#FF9902": "Align orange - hero figures, CTAs",
            "#F79A20": "Warm orange - secondary glow, chart tint",
            "#EF6936": "Coral - evidence, highlight rules",
            "#EF6B51": "Coral alt - highlight rules",
            "#546474": "Muted slate - supporting copy, labels",
            "#F8FAFC": "Paper - light page background",
            "#FFFFFF": "White - cards, reverse type",
        },
        "fonts": ["Inter", "Segoe UI", "Arial", "sans-serif"],
    },
    "social": {
        "label": "LinkedIn carousel / social graphics (May-6 production standard)",
        "colours": {
            "#F05A28": "Gradient start - CTA, primary accent",
            "#FF6B35": "Gradient end - CTA hot stop",
            "#0A1628": "Ink navy ground",
            "#2D3748": "Navy mid",
            "#2BB5A0": "Teal - secondary accent",
            "#FFFFFF": "White - reverse type",
        },
        "fonts": ["Inter", "DM Sans", "Syne", "Plus Jakarta Sans"],
    },
    "motion": {
        "label": "Video / motion graphics (gfx3 motion master)",
        "colours": {
            "#F47A25": "Motion orange - primary accent",
            "#FF9A4D": "Orange hot - bar tops, glow",
            "#F4A96A": "Orange tint - eyebrow type",
            "#7FA9F0": "Steel blue - data, secondary",
            "#3D6DB5": "Steel blue deep - bar base",
            "#0A1424": "Ink 1 - stage base",
            "#0E1A2B": "Ink 2 - stage mid",
            "#14305A": "Navy lift - stage highlight",
            "#F7F4EE": "Cream - editorial type",
            "#8FA3BC": "Steel - support type",
            "#7E93AE": "Steel 2 - labels",
            "#5CDB95": "Green - positive delta",
        },
        "fonts": ["Gelasio", "Inter"],
    },
    "editorial": {
        # Lifted verbatim from the :root block shipped in all 10 vendor-intent
        # blog builds -- this is the production set, not an abridged one.
        "label": "Blog / long-form article HTML (vendor-intent batch :root)",
        "colours": {
            "#0A1628": "navy-deep",
            "#2D3748": "ink",
            "#4A5568": "ink-soft",
            "#7A8699": "muted",
            "#FBF9F6": "paper",
            "#FFFFFF": "card",
            "#E9E4DC": "line",
            "#D8D2C7": "line-strong",
            "#FF6B2B": "orange - article accent",
            "#F05A28": "orange-deep / gradient start",
            "#FF6B35": "gradient end",
            "#2BB5A0": "teal",
        },
        "fonts": ["Plus Jakarta Sans", "DM Sans"],
    },
    "deck": {
        "label": "PowerPoint decks (supplied primary reference, 2026-08-13)",
        "colours": {
            "#232E3E": "Primary navy - cover, cards, close",
            "#2B3849": "Navy card",
            "#1D2735": "Deep navy",
            "#26334A": "Timeline navy 1",
            "#2F4059": "Timeline navy 2",
            "#3A4E6B": "Timeline navy 3",
            "#465C7E": "Timeline navy 4",
            "#E97722": "Primary deck orange",
            "#B05512": "Contrast orange on light fields",
            "#94480F": "Dark orange for small light-field text",
            "#F6F8FA": "Paper",
            "#EDF2F8": "Pale alternating row",
            "#FFFFFF": "White",
            "#E3E8EE": "Light reverse text",
            "#C5CEDA": "Muted reverse text and footer",
            "#C7D2DF": "Light rules",
            "#4A5563": "Muted slate",
            "#55606E": "Muted slate 2",
            "#4A5C75": "Dark-card border",
        },
        "fonts": ["Cambria", "Calibri", "Arial"],
    },
    "document": {
        "label": "Formal Word reports, one-pagers, and sales collateral",
        "colours": {
            "#232E3E": "Primary navy",
            "#2B3849": "Navy card",
            "#1D2735": "Deep navy",
            "#E97722": "Primary document orange",
            "#B05512": "Contrast orange on light fields",
            "#94480F": "Dark orange for small light-field text",
            "#F6F8FA": "Paper",
            "#EDF2F8": "Pale alternating row",
            "#FFFFFF": "White",
            "#E3E8EE": "Light reverse text",
            "#C5CEDA": "Muted reverse text and footer",
            "#C7D2DF": "Light rules",
            "#4A5563": "Muted slate",
            "#55606E": "Muted slate 2",
            "#4A5C75": "Dark-card border",
        },
        "fonts": ["Cambria", "Calibri", "Arial"],
    },
}

# Values that are affirmatively wrong wherever they appear, with the reason.
# Stated as evidence, not as "some other skill said so": a value is an Align
# token only if it can be traced to a shipped Align file.
KNOWN_BAD = {
    "#E8760A": "Not present in any audited Align production file.",
    "#414042": "Not present in any audited Align production file. Align's dark "
               "family is navy, not neutral grey.",
    "#E8832A": "Retired 2026-08-17. Appeared only in historical brand "
               "documentation, never in a shipped asset.",
    "#F5A623": "Not present in any audited Align production file. Hardcoded as "
               "'Align orange' in the rfp-responder skill; unverified.",
    "#404040": "Not present in any audited Align production file. Hardcoded as "
               "'Align dark gray' in the rfp-responder skill; Align's dark "
               "family is navy.",
}

HEX_RE = re.compile(r"#([0-9A-Fa-f]{6})\b")
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.I)

# CSS generic families and system stacks are always acceptable as a primary --
# they resolve to whatever the platform provides and carry no brand signal.
GENERIC_FAMILIES = {
    "sans-serif", "serif", "monospace", "cursive", "fantasy",
    "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded",
    "inherit", "initial", "unset", "revert",
}


def norm(h):
    return "#" + h.upper()


# ---------------------------------------------------------------------------
# OPC (Office) support.
#
# A .docx/.pptx/.xlsx is a deflate-compressed zip, so reading one as text finds
# no hex at all and every check silently passes. These files are the highest
# volume branded output, so the package is opened and its XML parts are linted
# instead. zipfile is stdlib -- this adds no dependency.
# ---------------------------------------------------------------------------

OPC_MAGIC = b"PK\x03\x04"

# Parts worth linting, by package family. Anything carrying colour or font.
WORD_PARTS = (
    re.compile(r"^word/document\.xml$"),
    re.compile(r"^word/styles\.xml$"),
    re.compile(r"^word/theme/theme\d*\.xml$"),
    re.compile(r"^word/(header|footer)\d*\.xml$"),
    re.compile(r"^word/numbering\.xml$"),
)
PPT_PARTS = (
    re.compile(r"^ppt/slides/slide\d+\.xml$"),
    re.compile(r"^ppt/slideMasters/slideMaster\d+\.xml$"),
    re.compile(r"^ppt/slideLayouts/slideLayout\d+\.xml$"),
    re.compile(r"^ppt/theme/theme\d*\.xml$"),
    re.compile(r"^ppt/notesMasters/notesMaster\d+\.xml$"),
)

# Office writes colour as attributes, never as CSS "#RRGGBB".
OPC_COLOUR_RES = (
    # WordprocessingML
    re.compile(rb'<w:color[^>]*w:val="([0-9A-Fa-f]{6})"'),
    re.compile(rb'<w:highlight[^>]*w:val="([0-9A-Fa-f]{6})"'),
    re.compile(rb'<w:shd[^>]*w:fill="([0-9A-Fa-f]{6})"'),
    re.compile(rb'<w:shd[^>]*w:color="([0-9A-Fa-f]{6})"'),
    re.compile(rb'<w:bottom[^>]*w:color="([0-9A-Fa-f]{6})"'),
    # DrawingML, shared by both families
    re.compile(rb'<a:srgbClr[^>]*val="([0-9A-Fa-f]{6})"'),
    re.compile(rb'<srgbClr[^>]*val="([0-9A-Fa-f]{6})"'),
)

OPC_FONT_RES = (
    re.compile(rb'<w:rFonts[^>]*w:(?:ascii|hAnsi|cs|eastAsia)="([^"]+)"'),
    re.compile(rb'<a:latin[^>]*typeface="([^"]+)"'),
    re.compile(rb'<a:(?:ea|cs)[^>]*typeface="([^"]+)"'),
)

# Office sentinels that mean "no explicit colour", not a real value.
NON_COLOURS = {"auto", "nil", "none"}

# The stock Office 2007 theme scheme. The bundled Align reference still carries
# it (tokens.md: "The file's theme is stock Office. These explicit painted
# values, not accent1 through accent6, define the deck."). Flagging all twelve
# slots on every run buries real findings, so they are collapsed into one note.
STOCK_OFFICE_THEME = {
    "#1F497D", "#EEECE1", "#4F81BD", "#C0504D", "#9BBB59",
    "#8064A2", "#4BACC6", "#F79646", "#0000FF", "#800080",
}
THEME_PART_RE = re.compile(r"^(word|ppt|xl)/theme/theme\d*\.xml$")


def is_opc(path):
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == OPC_MAGIC
    except OSError:
        return False


def _opc_parts(names):
    """Pick the lintable parts, choosing the family from what the package holds."""
    selected = []
    for name in sorted(names):
        for pattern in WORD_PARTS + PPT_PARTS:
            if pattern.match(name):
                selected.append(name)
                break
    return selected


def _judge_colour(h, surface, location, findings):
    palette = SURFACES[surface]["colours"]
    neutral = {"#FFFFFF", "#000000"}
    if h in KNOWN_BAD:
        findings.append(("error", location, f"{h} is off-brand. {KNOWN_BAD[h]}"))
        return
    if not palette:
        return
    if h in palette or h in neutral:
        return
    other = [s for s, d in SURFACES.items() if h in d["colours"] and s != surface]
    if other:
        role = SURFACES[other[0]]["colours"][h]
        findings.append(
            ("error", location,
             f"{h} is not in the {surface} palette. It belongs to "
             f"{'/'.join(other)} ({role}). Each surface has its own approved set."))
    else:
        findings.append(
            ("warn", location, f"{h} is not in any Align ledger. Confirm before shipping."))


def _judge_font(face, surface, location, findings, strict):
    allowed = [f.lower() for f in SURFACES[surface]["fonts"]]
    if not allowed:
        return
    low = face.lower()
    # Office theme references resolve to the theme font pair, not an override.
    if low.startswith("+") or low in GENERIC_FAMILIES:
        return
    if low not in allowed:
        findings.append(
            ("warn" if not strict else "error", location,
             f"font '{face}' is not in the {surface} stack "
             f"({', '.join(SURFACES[surface]['fonts'])})."))


def lint_opc(path, surface, strict):
    """Lint the XML inside an Office package rather than its compressed bytes."""
    findings = []
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            parts = _opc_parts(names)
            if not parts:
                return [("warn", os.path.basename(path),
                         "Office package contains no recognised Word or PowerPoint "
                         "parts; nothing linted.")]
            for part in parts:
                data = zf.read(part)
                seen_colour, seen_font = set(), set()
                is_theme = bool(THEME_PART_RE.match(part))
                stock_hits = 0
                for pattern in OPC_COLOUR_RES:
                    for raw in pattern.findall(data):
                        value = raw.decode()
                        if value.lower() in NON_COLOURS:
                            continue
                        h = norm(value)
                        if h in seen_colour:
                            continue
                        seen_colour.add(h)
                        if is_theme and h in STOCK_OFFICE_THEME:
                            stock_hits += 1
                            continue
                        _judge_colour(h, surface, part, findings)
                if stock_hits:
                    findings.append(
                        ("info", part,
                         f"{stock_hits} stock Office theme slot(s) present and ignored. "
                         "This deck is defined by its painted values, not accent1-6."))
                for pattern in OPC_FONT_RES:
                    for raw in pattern.findall(data):
                        face = raw.decode()
                        if face in seen_font:
                            continue
                        seen_font.add(face)
                        _judge_font(face, surface, part, findings, strict)
    except zipfile.BadZipFile:
        return [("error", os.path.basename(path), "not a readable Office package")]
    return findings


def lint_text(path, surface, strict):
    findings = []
    try:
        with open(path, "r", errors="replace") as fh:
            text = fh.read()
    except (IsADirectoryError, FileNotFoundError, PermissionError) as e:
        return [("error", "-", f"cannot read: {e}")]

    for i, line in enumerate(text.splitlines(), 1):
        for raw in HEX_RE.findall(line):
            _judge_colour(norm(raw), surface, f"L{i}", findings)

        for decl in FONT_FAMILY_RE.findall(line):
            families = [f.strip().strip("'\"")
                        for f in decl.split(",") if f.strip()]
            if not families:
                continue
            primary = families[0]
            # A var() reference points at a custom property; the property's own
            # declaration gets linted where it is defined, so following the
            # reference here would double-report it.
            if primary.lower().startswith("var(") or primary.startswith("--"):
                continue
            _judge_font(primary, surface, f"L{i}", findings, strict)
    return findings


def lint_file(path, surface, strict):
    """Dispatch on container type. Office packages are zips, not text."""
    if is_opc(path):
        return lint_opc(path, surface, strict)
    return lint_text(path, surface, strict)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to lint")
    ap.add_argument("--surface", choices=sorted(SURFACES), help="which palette applies")
    ap.add_argument("--strict", action="store_true",
                    help="treat font mismatches as errors too")
    ap.add_argument("--list", action="store_true", help="print the ledger and exit")
    args = ap.parse_args()

    if args.list:
        for name in sorted(SURFACES):
            d = SURFACES[name]
            print(f"\n[{name}] {d['label']}")
            if not d["colours"]:
                print("  (no tokens yet)")
            for hexv, role in d["colours"].items():
                print(f"  {hexv}  {role}")
            if d["fonts"]:
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
            kind = "office package" if is_opc(path) else "text"
            print(f"\n{path}  [{kind}]")
            width = max((len(str(loc)) for _, loc, _ in findings), default=6)
            for level, loc, msg in findings:
                print(f"  {level:5} {str(loc):<{width}}  {msg}")
        for level, _, _ in findings:
            totals[level] += 1

    summary = (f"\n{totals['error']} error(s), {totals['warn']} warning(s)")
    if totals["info"]:
        summary += f", {totals['info']} note(s)"
    print(f"{summary} across {len(args.files)} file(s), surface={args.surface}")
    return 1 if totals["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
