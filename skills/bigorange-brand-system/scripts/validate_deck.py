#!/usr/bin/env python3
"""Validate a BigOrange.Marketing deck before delivery.

Checks: 16:9 wide geometry, bundled BigOrange logo present on every slide and
byte-identical to the skill asset, no unresolved [[slot]] placeholders, brand
orange present, banned Align/Momentum colours absent, draft banner present when
--draft is passed, client name present when --client-name is passed, and the
CLIENT_LOGO picture (if any) not stretched.

Usage:
    python3 validate_deck.py deck.pptx [--client-name "X"] [--client-logo x.png] [--draft] [--json]
Exit 1 on any error.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"
EXPECTED_GEOMETRY = (12192000, 6858000)  # 13.333 x 7.5 in (pptxgenjs LAYOUT_WIDE)
REQUIRED_COLOURS = {"FF7C00"}
BANNED_COLOURS = {"232E3E", "E97722", "FF9902", "1A334E", "2A80C2", "2456C4", "2B1A10"}
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS = {
    "orange": os.path.join(SKILL_ROOT, "assets", "logos", "bigorange-logo-orange.png"),
    "white": os.path.join(SKILL_ROOT, "assets", "logos", "bigorange-logo-white.png"),
}


def q(ns, tag):
    return f"{{{ns}}}{tag}"


def sha256(b):
    return hashlib.sha256(b).hexdigest().upper()


def png_size(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def pictures(parts):
    out = []
    for slide_name in sorted(n for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)):
        rels_name = slide_name.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
        if rels_name not in parts:
            continue
        slide = ET.fromstring(parts[slide_name])
        rels = ET.fromstring(parts[rels_name])
        rel_map = {r.get("Id"): r.get("Target") for r in rels.findall(q(PKG_R, "Relationship"))}
        for pic in slide.iter(q(P, "pic")):
            props = pic.find(f"./{q(P, 'nvPicPr')}/{q(P, 'cNvPr')}")
            blip = pic.find(f"./{q(P, 'blipFill')}/{q(A, 'blip')}")
            xfrm = pic.find(f"./{q(P, 'spPr')}/{q(A, 'xfrm')}")
            if props is None or blip is None:
                continue
            target = rel_map.get(blip.get(q(R, "embed")), "")
            media = "ppt/" + target.replace("../", "").replace("\\", "/")
            ext = xfrm.find(q(A, "ext")) if xfrm is not None else None
            out.append({"slide": slide_name, "name": props.get("name", ""), "descr": props.get("descr", ""), "media": media,
                        "cx": int(ext.get("cx")) if ext is not None else 0, "cy": int(ext.get("cy")) if ext is not None else 0})
    return out


def validate(args):
    findings = []
    with zipfile.ZipFile(args.deck) as zf:
        parts = {n: zf.read(n) for n in zf.namelist()}
    pres = ET.fromstring(parts.get("ppt/presentation.xml", b"<x/>"))
    size = pres.find(q(P, "sldSz"))
    geometry = (int(size.get("cx", 0)), int(size.get("cy", 0))) if size is not None else None
    if geometry is None or abs(geometry[0] - EXPECTED_GEOMETRY[0]) > 100 or geometry[1] != EXPECTED_GEOMETRY[1]:
        findings.append(("error", f"wrong slide geometry: {geometry}; expected {EXPECTED_GEOMETRY}"))

    slide_names = sorted(n for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    all_text = []
    per_slide_text = {}
    for n in slide_names:
        root = ET.fromstring(parts[n])
        t = " ".join(node.text or "" for node in root.iter(q(A, "t")))
        per_slide_text[n] = t
        all_text.append(t)
    plain = " ".join(all_text)
    unresolved = sorted(set(re.findall(r"\[\[[^\]]+\]\]", plain)))
    if unresolved:
        findings.append(("error", f"unresolved slot placeholders remain: {', '.join(unresolved[:8])}"))
    if args.client_name and args.client_name.lower() not in plain.lower():
        findings.append(("error", f"client name not found in deck text: {args.client_name}"))
    if args.draft:
        missing = [n for n, t in per_slide_text.items() if "DRAFT" not in t.upper()]
        if missing:
            findings.append(("error", f"draft banner missing on {len(missing)} slide(s): {', '.join(os.path.basename(m) for m in missing[:5])}"))

    colours = {v.decode().upper() for v in re.findall(rb'srgbClr val="([0-9A-Fa-f]{6})"', b"\n".join(parts[n] for n in slide_names))}
    for c in sorted(BANNED_COLOURS & colours):
        findings.append(("error", f"banned non-BigOrange colour present: #{c}"))
    if REQUIRED_COLOURS - colours:
        findings.append(("error", "brand orange #FF7C00 is not painted anywhere in the deck"))

    pics = pictures(parts)
    logo_hashes = {k: sha256(open(p, "rb").read()) for k, p in LOGOS.items() if os.path.exists(p)}
    slides_with_logo = set()
    for p in pics:
        h = sha256(parts.get(p["media"], b""))
        if h in logo_hashes.values():
            slides_with_logo.add(p["slide"])
    without = [n for n in slide_names if n not in slides_with_logo]
    if without:
        findings.append(("error", f"BigOrange logo missing or altered on {len(without)} slide(s): {', '.join(os.path.basename(w) for w in without[:5])}"))

    client = [p for p in pics if p["descr"] == "CLIENT_LOGO" or p["name"] == "CLIENT_LOGO"]
    if args.client_logo:
        if not client:
            findings.append(("error", "no CLIENT_LOGO picture found although a client logo was supplied"))
        else:
            expected = sha256(open(args.client_logo, "rb").read())
            actual = parts.get(client[0]["media"], b"")
            if sha256(actual) != expected:
                findings.append(("error", "CLIENT_LOGO does not match the verified input asset"))
            dims = png_size(actual)
            if dims and client[0]["cy"]:
                placed = client[0]["cx"] / client[0]["cy"]
                ratio = dims[0] / dims[1]
                if abs(ratio / placed - 1) > 0.02:
                    findings.append(("warn", "CLIENT_LOGO frame ratio differs from image ratio (pptxgenjs contain-sizing may pad; check render)"))

    errors = sum(1 for lvl, _ in findings if lvl == "error")
    return {"deck": args.deck, "passed": errors == 0, "slide_count": len(slide_names), "geometry": geometry,
            "colours": sorted("#" + c for c in colours), "findings": [{"level": l, "message": m} for l, m in findings]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--client-name")
    ap.add_argument("--client-logo")
    ap.add_argument("--draft", action="store_true", help="require the draft banner on every slide")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        result = validate(args)
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        sys.exit(f"error: {exc}")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"passed={result['passed']} slides={result['slide_count']} deck={result['deck']}")
        for f in result["findings"]:
            print(f"{f['level']}: {f['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
