#!/usr/bin/env python3
"""
Extract the exact brand system out of an Align HCM PowerPoint template.

A .pptx / .potx / .thmx is an OPC zip. Everything needed to reproduce the deck
brand -- theme colour slots, the major/minor font pair, slide dimensions, the
layout inventory, and the colours actually painted on the master -- is sitting
in XML inside it. This reads that directly, so there is no python-pptx
dependency and no guessing.

Usage:
    python3 extract_pptx_theme.py <template.potx> [--json out.json] [--md out.md]

Writes a token table to stdout by default. `--md` regenerates the reference
file that SKILL.md points at, which is how the attached template becomes the
authority instead of a hand-copied hex list.
"""

import argparse
import collections
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"

# Slots as PowerPoint's own UI labels them, in the order the theme editor shows.
SLOT_LABELS = [
    ("dk1", "Text/Background - Dark 1"),
    ("lt1", "Text/Background - Light 1"),
    ("dk2", "Text/Background - Dark 2"),
    ("lt2", "Text/Background - Light 2"),
    ("accent1", "Accent 1"),
    ("accent2", "Accent 2"),
    ("accent3", "Accent 3"),
    ("accent4", "Accent 4"),
    ("accent5", "Accent 5"),
    ("accent6", "Accent 6"),
    ("hlink", "Hyperlink"),
    ("folHlink", "Followed hyperlink"),
]

# EMU (English Metric Units) per inch -- PowerPoint's internal unit.
EMU_PER_INCH = 914400


def _q(ns, tag):
    return f"{{{ns}}}{tag}"


def _resolve_colour(slot_el):
    """Read a colour slot, which is either an explicit sRGB value or a system colour."""
    if slot_el is None:
        return None
    srgb = slot_el.find(_q(A, "srgbClr"))
    if srgb is not None:
        return "#" + srgb.get("val", "").upper()
    sysclr = slot_el.find(_q(A, "sysClr"))
    if sysclr is not None:
        # lastClr is the concrete value PowerPoint last resolved the system colour to.
        last = sysclr.get("lastClr")
        if last:
            return "#" + last.upper()
        return f"sys:{sysclr.get('val')}"
    return None


def _theme_part(zf):
    """Find the theme XML. Name varies (theme1.xml, theme2.xml) and .thmx differs."""
    names = [n for n in zf.namelist() if re.match(r"(ppt|word|xl)?/?theme/theme\d*\.xml$", n)]
    if not names:
        names = [n for n in zf.namelist() if n.endswith("theme1.xml")]
    if not names:
        raise SystemExit("No theme part found -- is this really a PowerPoint template?")
    return sorted(names)[0]


def extract_theme(zf):
    part = _theme_part(zf)
    root = ET.fromstring(zf.read(part))
    elements = root.find(_q(A, "themeElements"))

    colours = {}
    clr_scheme = elements.find(_q(A, "clrScheme")) if elements is not None else None
    scheme_name = clr_scheme.get("name") if clr_scheme is not None else None
    if clr_scheme is not None:
        for slot, label in SLOT_LABELS:
            colours[slot] = {
                "label": label,
                "value": _resolve_colour(clr_scheme.find(_q(A, slot))),
            }

    fonts = {}
    font_scheme = elements.find(_q(A, "fontScheme")) if elements is not None else None
    font_scheme_name = font_scheme.get("name") if font_scheme is not None else None
    if font_scheme is not None:
        for key, role in (("majorFont", "headings"), ("minorFont", "body")):
            fel = font_scheme.find(_q(A, key))
            if fel is None:
                continue
            latin = fel.find(_q(A, "latin"))
            fonts[role] = {
                "typeface": latin.get("typeface") if latin is not None else None,
                "panose": latin.get("panose") if latin is not None else None,
            }

    return {
        "theme_part": part,
        "colour_scheme_name": scheme_name,
        "font_scheme_name": font_scheme_name,
        "colours": colours,
        "fonts": fonts,
    }


def extract_geometry(zf):
    """Slide size, in EMU and inches, plus the aspect ratio."""
    if "ppt/presentation.xml" not in zf.namelist():
        return None
    root = ET.fromstring(zf.read("ppt/presentation.xml"))
    sz = root.find(_q(P, "sldSz"))
    if sz is None:
        return None
    cx, cy = int(sz.get("cx", 0)), int(sz.get("cy", 0))
    w_in, h_in = cx / EMU_PER_INCH, cy / EMU_PER_INCH
    ratio = "16:9" if abs(w_in / h_in - 16 / 9) < 0.02 else (
        "4:3" if abs(w_in / h_in - 4 / 3) < 0.02 else f"{w_in / h_in:.3f}:1")
    return {
        "cx_emu": cx, "cy_emu": cy,
        "width_in": round(w_in, 3), "height_in": round(h_in, 3),
        "width_px_at_96dpi": round(w_in * 96), "height_px_at_96dpi": round(h_in * 96),
        "aspect": ratio,
    }


def extract_layouts(zf):
    """The layout inventory -- the menu a deck author actually picks from."""
    layouts = []
    for name in sorted(n for n in zf.namelist()
                       if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", n)):
        root = ET.fromstring(zf.read(name))
        csld = root.find(_q(P, "cSld"))
        # Placeholder types tell you what the layout is FOR.
        holders = []
        for ph in root.iter(_q(P, "ph")):
            t = ph.get("type", "body")
            idx = ph.get("idx")
            holders.append(t if idx is None else f"{t}[{idx}]")
        layouts.append({
            "part": name,
            "name": csld.get("name") if csld is not None else None,
            "type": root.get("type"),
            "placeholders": holders,
        })
    return layouts


def extract_used_colours(zf, limit=25):
    """
    Every explicit sRGB value painted anywhere in the masters and layouts,
    by frequency. This is what catches colours that were hand-typed onto shapes
    instead of pulled from a theme slot -- the usual source of brand drift.
    """
    counter = collections.Counter()
    targets = [n for n in zf.namelist()
               if re.match(r"ppt/(slideMasters|slideLayouts|slides)/\w+\d+\.xml$", n)]
    for name in targets:
        for val in re.findall(rb'srgbClr val="([0-9A-Fa-f]{6})"', zf.read(name)):
            counter["#" + val.decode().upper()] += 1
    return counter.most_common(limit)


def extract_used_fonts(zf):
    """Typefaces named explicitly on runs, i.e. overriding the theme font pair."""
    counter = collections.Counter()
    targets = [n for n in zf.namelist()
               if re.match(r"ppt/(slideMasters|slideLayouts|slides)/\w+\d+\.xml$", n)]
    for name in targets:
        for val in re.findall(rb'typeface="([^"]+)"', zf.read(name)):
            face = val.decode()
            if face.startswith("+"):  # +mj-lt / +mn-lt are theme references, not overrides
                continue
            counter[face] += 1
    return counter.most_common()


def build(path):
    with zipfile.ZipFile(path) as zf:
        data = {
            "source_file": path,
            "theme": extract_theme(zf),
            "geometry": extract_geometry(zf),
            "layouts": extract_layouts(zf),
            "used_colours": extract_used_colours(zf),
            "used_fonts": extract_used_fonts(zf),
        }
    return data


def render_md(d):
    t, g = d["theme"], d["geometry"]
    out = []
    out.append("# Align HCM PowerPoint template - extracted tokens\n")
    out.append(f"Extracted from `{d['source_file']}` by "
               "`scripts/extract_pptx_theme.py`. Regenerate rather than hand-edit.\n")

    out.append("\n## Theme colour slots\n")
    out.append(f"Colour scheme: **{t['colour_scheme_name'] or 'unnamed'}**\n")
    out.append("\n| Slot | PowerPoint label | Hex |")
    out.append("\n|---|---|---|")
    for slot, label in SLOT_LABELS:
        v = t["colours"].get(slot, {}).get("value")
        out.append(f"\n| `{slot}` | {label} | `{v or '-'}` |")

    out.append("\n\n## Theme fonts\n")
    out.append(f"Font scheme: **{t['font_scheme_name'] or 'unnamed'}**\n")
    out.append("\n| Role | Typeface |")
    out.append("\n|---|---|")
    for role in ("headings", "body"):
        f = t["fonts"].get(role, {})
        out.append(f"\n| {role} (`{'major' if role == 'headings' else 'minor'}`) "
                   f"| {f.get('typeface') or '-'} |")

    if g:
        out.append("\n\n## Slide geometry\n")
        out.append(f"\n- {g['width_in']} x {g['height_in']} in ({g['aspect']})")
        out.append(f"\n- {g['width_px_at_96dpi']} x {g['height_px_at_96dpi']} px at 96 DPI")
        out.append(f"\n- {g['cx_emu']} x {g['cy_emu']} EMU\n")

    out.append("\n\n## Layout inventory\n")
    out.append("\nUse these layout names verbatim when building a deck.\n")
    out.append("\n| # | Layout name | Placeholders |")
    out.append("\n|---|---|---|")
    for i, l in enumerate(d["layouts"], 1):
        ph = ", ".join(l["placeholders"][:8]) or "-"
        out.append(f"\n| {i} | {l['name'] or '-'} | {ph} |")

    out.append("\n\n## Colours actually painted in the file\n")
    out.append("\nBy frequency. Anything here that is NOT a theme slot above was "
               "hand-applied to a shape and is a drift risk.\n")
    out.append("\n| Hex | Count |")
    out.append("\n|---|---|")
    for hexv, n in d["used_colours"]:
        out.append(f"\n| `{hexv}` | {n} |")

    if d["used_fonts"]:
        out.append("\n\n## Explicit font overrides\n")
        out.append("\nTypefaces named directly on runs instead of via `+mj-lt` / `+mn-lt`.\n")
        out.append("\n| Typeface | Count |")
        out.append("\n|---|---|")
        for face, n in d["used_fonts"]:
            out.append(f"\n| {face} | {n} |")

    out.append("\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template", help="path to .pptx / .potx / .thmx")
    ap.add_argument("--json", help="write raw extraction to this path")
    ap.add_argument("--md", help="write the markdown token reference to this path")
    args = ap.parse_args()

    try:
        data = build(args.template)
    except zipfile.BadZipFile:
        sys.exit(f"{args.template} is not a valid Office file (not a zip container).")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(data, fh, indent=2)
        print(f"wrote {args.json}")
    md = render_md(data)
    if args.md:
        with open(args.md, "w") as fh:
            fh.write(md)
        print(f"wrote {args.md}")
    if not args.json and not args.md:
        print(md)


if __name__ == "__main__":
    main()
