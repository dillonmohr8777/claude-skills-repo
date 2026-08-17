#!/usr/bin/env python3
"""Create an Align HCM client deck from the bundled visual reference.

The agent using this script must first resolve the client from the current
brief and obtain a verified PNG logo. This script performs the deterministic
part: copy the exact reference deck, replace the cover metadata, replace the
client logo without distortion, and preserve the bundled Align artwork.
"""

import argparse
import io
import os
import re
import struct
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"
CLIENT_LOGO_ZONE_EMU = (8839184, 3163824, 2651760, 912070)


def q(ns, tag):
    return f"{{{ns}}}{tag}"


def register_namespaces(xml_bytes):
    for _, pair in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
        prefix, uri = pair
        try:
            ET.register_namespace(prefix or "", uri)
        except ValueError:
            pass


def png_size(path):
    with open(path, "rb") as fh:
        header = fh.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("client logo must be a valid PNG")
    width, height = struct.unpack(">II", header[16:24])
    if width < 16 or height < 16:
        raise ValueError("client logo is too small; use a verified source asset")
    return width, height


PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


def _apply(text, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def replace_text(xml_bytes, replacements):
    """Substitute placeholders, tolerating tokens split across runs.

    PowerPoint may split a single token across several `a:t` runs when the text
    was edited in place. Per-run replacement alone would silently miss those, so
    each paragraph is also checked as a whole: if joining its runs yields a
    different result than replacing run by run, the token spanned runs and the
    paragraph is collapsed into its first run. The per-run path is preferred
    because it preserves mixed formatting inside a paragraph.
    """
    register_namespaces(xml_bytes)
    root = ET.fromstring(xml_bytes)
    changed = False

    for para in root.iter(q(A, "p")):
        nodes = [n for n in para.iter(q(A, "t"))]
        if not nodes:
            continue
        originals = [n.text or "" for n in nodes]
        joined = "".join(originals)
        if "{{" not in joined:
            continue

        per_run = [_apply(t, replacements) for t in originals]
        whole = _apply(joined, replacements)

        if "".join(per_run) == whole:
            for node, updated, original in zip(nodes, per_run, originals):
                if updated != original:
                    node.text = updated
                    changed = True
        else:
            # A token straddled a run boundary. Collapse into the first run.
            nodes[0].text = whole
            for node in nodes[1:]:
                node.text = ""
            changed = True

    return ET.tostring(root, encoding="utf-8", xml_declaration=True) if changed else xml_bytes


def slide_number(part_name):
    match = re.search(r"slide(\d+)\.xml$", part_name)
    return int(match.group(1)) if match else 0


def discover_placeholders(parts):
    """Every `{{TOKEN}}` in the deck, mapped to the slides it appears on.

    Runs are joined per paragraph before matching so a token split across runs
    is still found. Tokens may contain digits and underscores, so the pattern
    is deliberately broad rather than a fixed list.
    """
    found = {}
    for name in sorted(parts, key=slide_number):
        if not re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
            continue
        try:
            root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        number = slide_number(name)
        for para in root.iter(q(A, "p")):
            joined = "".join(n.text or "" for n in para.iter(q(A, "t")))
            for token in PLACEHOLDER_RE.findall(joined):
                found.setdefault(token, set()).add(number)
    return {token: sorted(slides) for token, slides in found.items()}


def replace_client_logo(slide_bytes, rels_bytes, logo_bytes, logo_width, logo_height):
    register_namespaces(slide_bytes)
    register_namespaces(rels_bytes)
    slide = ET.fromstring(slide_bytes)
    rels = ET.fromstring(rels_bytes)

    client_pic = None
    for pic in slide.iter(q(P, "pic")):
        props = pic.find(f"./{q(P, 'nvPicPr')}/{q(P, 'cNvPr')}")
        if props is not None and props.get("name") == "CLIENT_LOGO":
            client_pic = pic
            props.set("name", "CLIENT_LOGO")
            props.set("descr", "Verified client logo")
            break
    if client_pic is None:
        raise ValueError("template does not contain the named client-logo picture")

    blip = client_pic.find(f"./{q(P, 'blipFill')}/{q(A, 'blip')}")
    if blip is None or not blip.get(q(R, "embed")):
        raise ValueError("client-logo picture has no embedded image relationship")
    rel_id = blip.get(q(R, "embed"))

    relationship = None
    for rel in rels.findall(q(PKG_R, "Relationship")):
        if rel.get("Id") == rel_id:
            relationship = rel
            break
    if relationship is None:
        raise ValueError("client-logo relationship is missing")
    target = relationship.get("Target", "")
    media_part = "ppt/" + target.replace("../", "").replace("\\", "/")

    # The client logo is written as PNG bytes straight over this part. If a
    # future template revision points the client zone at a .jpeg, writing PNG
    # bytes into it produces a file PowerPoint cannot open, with no error here.
    if not media_part.lower().endswith(".png"):
        raise ValueError(
            f"client-logo media part is {media_part!r}, not a .png. This script "
            "writes PNG bytes and would corrupt it. Update the template so the "
            "client-logo zone uses a PNG part, or extend this script to convert.")

    xfrm = client_pic.find(f"./{q(P, 'spPr')}/{q(A, 'xfrm')}")
    off = xfrm.find(q(A, "off")) if xfrm is not None else None
    ext = xfrm.find(q(A, "ext")) if xfrm is not None else None
    if off is None or ext is None:
        raise ValueError("client-logo picture has no placement transform")

    box_x, box_y, box_w, box_h = CLIENT_LOGO_ZONE_EMU
    logo_ratio = logo_width / logo_height
    box_ratio = box_w / box_h
    if logo_ratio >= box_ratio:
        new_w = box_w
        new_h = round(box_w / logo_ratio)
    else:
        new_h = box_h
        new_w = round(box_h * logo_ratio)
    off.set("x", str(box_x + (box_w - new_w) // 2))
    off.set("y", str(box_y + (box_h - new_h) // 2))
    ext.set("cx", str(new_w))
    ext.set("cy", str(new_h))

    src_rect = client_pic.find(f"./{q(P, 'blipFill')}/{q(A, 'srcRect')}")
    if src_rect is not None:
        for attr in ("l", "t", "r", "b"):
            src_rect.attrib.pop(attr, None)

    return (
        ET.tostring(slide, encoding="utf-8", xml_declaration=True),
        ET.tostring(rels, encoding="utf-8", xml_declaration=True),
        media_part,
        logo_bytes,
    )


def parse_replacements(args):
    replacements = [
        ("{{CLIENT}}", args.client_name),
        ("{{ENGAGEMENT}}", args.engagement_title),
        ("{{DECK_TYPE}}", args.deck_type.upper()),
        ("{{DATE}}", args.date),
    ]
    for item in args.replace:
        if "=" not in item:
            raise ValueError(f"invalid --replace value: {item!r}; expected OLD=NEW")
        old, new = item.split("=", 1)
        if not old:
            raise ValueError("--replace OLD may not be empty")
        replacements.append((old, new))
    return replacements


def build(args):
    logo_width, logo_height = png_size(args.client_logo)
    with open(args.client_logo, "rb") as fh:
        logo_bytes = fh.read()
    replacements = parse_replacements(args)

    with zipfile.ZipFile(args.template) as source:
        parts = {name: source.read(name) for name in source.namelist()}
    slide_name = "ppt/slides/slide1.xml"
    rels_name = "ppt/slides/_rels/slide1.xml.rels"
    if slide_name not in parts or rels_name not in parts:
        raise ValueError("template is missing cover-slide parts")

    cover, rels, media_part, media_bytes = replace_client_logo(
        parts[slide_name], parts[rels_name], logo_bytes, logo_width, logo_height
    )
    parts[slide_name] = cover
    parts[rels_name] = rels
    parts[media_part] = media_bytes

    for name in list(parts):
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
            parts[name] = replace_text(parts[name], replacements)

    out_dir = os.path.dirname(os.path.abspath(args.output)) or "."
    os.makedirs(out_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix="align-deck-", suffix=".pptx", dir=out_dir)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as dest:
            for name, data in parts.items():
                dest.writestr(name, data)
        os.replace(temp_path, args.output)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    return discover_placeholders(parts)


def report_unresolved(remaining, allow):
    """Print what is still unfilled, grouped by slide, and say how to fill it.

    validate_client_deck.py hard-errors on any surviving `{{`, so leaving this
    silent would mean the documented workflow always fails one step later with
    no indication of which token was missed.
    """
    if not remaining:
        print("all placeholders resolved")
        return 0

    by_slide = {}
    for token, slides in remaining.items():
        for slide in slides:
            by_slide.setdefault(slide, []).append(token)

    print(f"\n{len(remaining)} unresolved placeholder(s):")
    for slide in sorted(by_slide):
        print(f"  slide {slide}: {' '.join(sorted(by_slide[slide]))}")
    print("\nSupply each with --replace, for example:")
    example = sorted(remaining)[0]
    print(f"  --replace '{example}=<value>'")

    if allow:
        print("\n--allow-unresolved set: continuing despite the above.")
        return 0
    print("\nThe deck was written but will fail validate_client_deck.py until "
          "these are filled. Re-run with the missing --replace values, or pass "
          "--allow-unresolved to accept a partial deck.")
    return 1


def main():
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_template = os.path.join(
        skill_root, "assets", "templates", "Align-HCM-Primary-Deck-Reference.pptx"
    )
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", default=default_template)
    ap.add_argument("--output", required=True)
    ap.add_argument("--client-name", required=True)
    ap.add_argument("--client-logo", required=True)
    ap.add_argument("--engagement-title", required=True)
    ap.add_argument("--deck-type", default="Client Presentation")
    ap.add_argument("--date", required=True)
    ap.add_argument("--replace", action="append", default=[], metavar="OLD=NEW")
    ap.add_argument("--allow-unresolved", action="store_true",
                    help="write the deck and exit 0 even if placeholders remain")
    ap.add_argument("--list-placeholders", action="store_true",
                    help="print every placeholder in the template and exit")
    args = ap.parse_args()

    if args.list_placeholders:
        try:
            with zipfile.ZipFile(args.template) as source:
                parts = {name: source.read(name) for name in source.namelist()}
        except (OSError, zipfile.BadZipFile) as exc:
            sys.exit(f"error: {exc}")
        inventory = discover_placeholders(parts)
        print(f"{len(inventory)} placeholder(s) in {args.template}:")
        for token in sorted(inventory):
            slides = ", ".join(str(n) for n in inventory[token])
            print(f"  {token:24} slides {slides}")
        return 0

    try:
        remaining = build(args)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        sys.exit(f"error: {exc}")
    print(f"wrote {args.output}")
    print("starter only: rewrite every reference-specific body value, then run validate_client_deck.py")
    return report_unresolved(remaining, args.allow_unresolved)


if __name__ == "__main__":
    sys.exit(main())
