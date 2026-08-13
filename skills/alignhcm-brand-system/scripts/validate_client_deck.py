#!/usr/bin/env python3
"""Validate an Align HCM client deck before delivery."""

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
EXPECTED_GEOMETRY = (12191969, 6858000)
CLIENT_LOGO_ZONE_EMU = (8839184, 3163824, 2651760, 912070)
REQUIRED_DECK_COLOURS = {"#232E3E", "#E97722"}
BANNED_COLOURS = {"#E8760A", "#414042"}


def q(ns, tag):
    return f"{{{ns}}}{tag}"


def sha256(data):
    return hashlib.sha256(data).hexdigest().upper()


def png_size_bytes(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def picture_targets(parts):
    pictures = []
    slide_names = sorted(n for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    for slide_name in slide_names:
        rels_name = slide_name.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
        if rels_name not in parts:
            continue
        slide = ET.fromstring(parts[slide_name])
        rels = ET.fromstring(parts[rels_name])
        rel_map = {rel.get("Id"): rel.get("Target") for rel in rels.findall(q(PKG_R, "Relationship"))}
        for pic in slide.iter(q(P, "pic")):
            props = pic.find(f"./{q(P, 'nvPicPr')}/{q(P, 'cNvPr')}")
            blip = pic.find(f"./{q(P, 'blipFill')}/{q(A, 'blip')}")
            xfrm = pic.find(f"./{q(P, 'spPr')}/{q(A, 'xfrm')}")
            if props is None or blip is None:
                continue
            target = rel_map.get(blip.get(q(R, "embed")), "")
            media = "ppt/" + target.replace("../", "").replace("\\", "/")
            ext = xfrm.find(q(A, "ext")) if xfrm is not None else None
            off = xfrm.find(q(A, "off")) if xfrm is not None else None
            pictures.append({
                "slide": slide_name,
                "name": props.get("name", ""),
                "media": media,
                "x": int(off.get("x")) if off is not None else 0,
                "y": int(off.get("y")) if off is not None else 0,
                "cx": int(ext.get("cx")) if ext is not None else 0,
                "cy": int(ext.get("cy")) if ext is not None else 0,
            })
    return pictures


def validate(args):
    findings = []
    with zipfile.ZipFile(args.deck) as zf:
        parts = {name: zf.read(name) for name in zf.namelist()}

    presentation = ET.fromstring(parts.get("ppt/presentation.xml", b"<x/>"))
    size = presentation.find(q(P, "sldSz"))
    geometry = (int(size.get("cx", 0)), int(size.get("cy", 0))) if size is not None else None
    if geometry != EXPECTED_GEOMETRY:
        findings.append(("error", f"wrong slide geometry: {geometry}; expected {EXPECTED_GEOMETRY}"))

    slide_parts = [parts[n] for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    texts = []
    for slide_bytes in slide_parts:
        root = ET.fromstring(slide_bytes)
        texts.extend(node.text or "" for node in root.iter(q(A, "t")))
    plain_text = " ".join(texts).lower()
    if "{{" in plain_text or "}}" in plain_text:
        findings.append(("error", "unresolved template placeholder remains"))
    if args.client_name and args.client_name.lower() not in plain_text:
        findings.append(("error", f"client name not found in deck text: {args.client_name}"))

    colours = {"#" + value.decode().upper() for value in re.findall(rb'srgbClr val="([0-9A-Fa-f]{6})"', b"\n".join(slide_parts))}
    for colour in sorted(BANNED_COLOURS & colours):
        findings.append(("error", f"banned Align colour present: {colour}"))
    missing = REQUIRED_DECK_COLOURS - colours
    if missing:
        findings.append(("error", f"deck no longer carries primary master colours: {', '.join(sorted(missing))}"))

    pictures = picture_targets(parts)
    align = [p for p in pictures if p["name"] in {"AlignHCM_Logo", "ALIGN_HCM_LOGO"}]
    client = [p for p in pictures if p["name"] == "CLIENT_LOGO"]
    if not align:
        findings.append(("error", "named Align HCM logo is missing"))
    else:
        skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(skill_root, "assets", "logos", "align-hcm-deck-lockup.png")
        with open(logo_path, "rb") as fh:
            expected_align_hash = sha256(fh.read())
        for picture in align:
            if picture["media"] not in parts or sha256(parts[picture["media"]]) != expected_align_hash:
                findings.append(("error", "Align HCM logo does not match the bundled master artwork"))
                break
    if not client:
        findings.append(("error", "named CLIENT_LOGO picture is missing from the cover"))
    elif args.client_logo:
        with open(args.client_logo, "rb") as fh:
            expected_client = sha256(fh.read())
        picture = client[0]
        actual = parts.get(picture["media"], b"")
        if sha256(actual) != expected_client:
            findings.append(("error", "cover client logo does not match the verified input asset"))
        dims = png_size_bytes(actual)
        if dims and picture["cy"]:
            image_ratio = dims[0] / dims[1]
            placed_ratio = picture["cx"] / picture["cy"]
            if abs(image_ratio / placed_ratio - 1) > 0.01:
                findings.append(("error", "client logo is stretched or compressed"))
        zone_x, zone_y, zone_w, zone_h = CLIENT_LOGO_ZONE_EMU
        if not (
            picture["x"] >= zone_x
            and picture["y"] >= zone_y
            and picture["x"] + picture["cx"] <= zone_x + zone_w + 1
            and picture["y"] + picture["cy"] <= zone_y + zone_h + 1
        ):
            findings.append(("error", "client logo escapes the approved cover zone"))
        picture_cx = picture["x"] + picture["cx"] / 2
        picture_cy = picture["y"] + picture["cy"] / 2
        zone_cx = zone_x + zone_w / 2
        zone_cy = zone_y + zone_h / 2
        if abs(picture_cx - zone_cx) > 2 or abs(picture_cy - zone_cy) > 2:
            findings.append(("error", "client logo is not centered in the approved cover zone"))

    errors = sum(1 for level, _ in findings if level == "error")
    return {
        "deck": args.deck,
        "passed": errors == 0,
        "slide_count": len(slide_parts),
        "geometry": geometry,
        "colours": sorted(colours),
        "findings": [{"level": level, "message": message} for level, message in findings],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck")
    ap.add_argument("--client-name")
    ap.add_argument("--client-logo")
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
        for finding in result["findings"]:
            print(f"{finding['level']}: {finding['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
