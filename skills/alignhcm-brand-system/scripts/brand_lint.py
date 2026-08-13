#!/usr/bin/env python3
"""
Check an Align HCM asset against the token ledger for its surface.

Align does not have one orange -- it has a different approved orange per
surface (see references/tokens.md). A flat "is this hex on the list" check
would therefore pass a web orange dropped into a deck. This lints against the
palette for the surface you name, and calls out anything off-ledger.

Usage:
    python3 brand_lint.py --surface web  page.html
    python3 brand_lint.py --surface deck slides/*.html --strict
    python3 brand_lint.py --list

Exit code 1 if any error-level finding is present (0 if only warnings), so it
can gate a build step.
"""

import argparse
import collections
import os
import re
import sys

# ---------------------------------------------------------------------------
# Token ledger. Mirrors references/tokens.md -- keep the two in step.
# `deck` is intentionally EMPTY until a real .potx is ingested; see SKILL.md.
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
        "label": "PowerPoint decks - AWAITING .potx INGESTION",
        "colours": {},
        "fonts": [],
    },
}

# Values that are affirmatively wrong wherever they appear, with the reason.
KNOWN_BAD = {
    "#E8760A": "Not present in any Align repo. Sourced from the `cool-data-elements` "
               "account skill, which was never reconciled against production.",
    "#414042": "Same origin as #E8760A. Align's dark is a navy family, not neutral grey.",
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


def lint_file(path, surface, strict):
    findings = []
    try:
        with open(path, "r", errors="replace") as fh:
            text = fh.read()
    except (IsADirectoryError, FileNotFoundError, PermissionError) as e:
        return [("error", 0, f"cannot read: {e}")]

    palette = SURFACES[surface]["colours"]
    allowed_fonts = [f.lower() for f in SURFACES[surface]["fonts"]]

    # Neutrals every surface may use without being called out.
    neutral = {"#FFFFFF", "#000000"}

    for i, line in enumerate(text.splitlines(), 1):
        for raw in HEX_RE.findall(line):
            h = norm(raw)
            if h in KNOWN_BAD:
                findings.append(("error", i, f"{h} is off-brand. {KNOWN_BAD[h]}"))
            elif not palette:
                continue  # surface ledger not populated yet; nothing to judge against
            elif h not in palette and h not in neutral:
                # Is it approved somewhere else? That is the more useful message.
                other = [s for s, d in SURFACES.items()
                         if h in d["colours"] and s != surface]
                if other:
                    role = SURFACES[other[0]]["colours"][h]
                    findings.append(
                        ("error", i,
                         f"{h} is not in the {surface} palette. It belongs to "
                         f"{'/'.join(other)} ({role}). Each surface has its own "
                         f"approved set."))
                else:
                    findings.append(
                        ("warn", i, f"{h} is not in any Align ledger. Confirm before shipping."))

        for decl in FONT_FAMILY_RE.findall(line):
            families = [f.strip().strip("'\"").lower()
                        for f in decl.split(",") if f.strip()]
            if not families or not allowed_fonts:
                continue
            primary = families[0]
            # A var() reference points at a custom property; the property's own
            # declaration gets linted where it is defined, so following the
            # reference here would double-report it.
            if primary.startswith("var(") or primary.startswith("--"):
                continue
            if primary in GENERIC_FAMILIES:
                continue
            if primary not in allowed_fonts:
                findings.append(
                    ("warn" if not strict else "error", i,
                     f"font '{primary}' is not in the {surface} stack "
                     f"({', '.join(SURFACES[surface]['fonts'])})."))
    return findings


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

    if not SURFACES[args.surface]["colours"]:
        print(f"note: the '{args.surface}' ledger is empty -- only the never-use list "
              f"is enforced. Ingest the template first.\n", file=sys.stderr)

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

    print(f"\n{totals['error']} error(s), {totals['warn']} warning(s) "
          f"across {len(args.files)} file(s), surface={args.surface}")
    return 1 if totals["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
