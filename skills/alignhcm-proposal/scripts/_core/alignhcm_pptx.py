"""
Write a branded Align 16:9 deck from a slide spec.

The brand system clones a supplied seven-slide master, which is exact but
fixed. A proposal or a partner introduction has a variable number of sections,
so those decks are generated instead, using the same measured tokens as the
master. Anything produced here should sit next to a master-cloned deck without
looking like a different company made it.

No python-pptx. A .pptx is a zip of XML.

Units are EMU. 914400 per inch. The canvas is 13.333 x 7.5 in.
"""

import zipfile

import alignhcm_media as media

EMU = 914400
SLIDE_W = 12192000
SLIDE_H = 6858000

NAVY = "232E3E"
NAVY_CARD = "2B3849"
DEEP_NAVY = "1D2735"
ORANGE = "E97722"
CONTRAST_ORANGE = "B05512"
PAPER = "F6F8FA"
WHITE = "FFFFFF"
LIGHT_TEXT = "E3E8EE"
MUTED_LIGHT = "C5CEDA"
RULE = "C7D2DF"
MUTED = "4A5563"

HEADING_FONT = "Cambria"
BODY_FONT = "Calibri"

MARGIN = round(0.75 * EMU)
CONTENT_W = SLIDE_W - 2 * MARGIN


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Shapes
# ---------------------------------------------------------------------------

_ID = [1]


def _next_id():
    _ID[0] += 1
    return _ID[0]


def _sp_pr(x, y, cx, cy, geom="rect"):
    return (f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>')


def rect(x, y, cx, cy, fill, *, radius=False, line=None, line_w=12700):
    geom = "roundRect" if radius else "rect"
    body = _sp_pr(x, y, cx, cy, geom)
    body += f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    if line:
        body += (f'<a:ln w="{line_w}"><a:solidFill>'
                 f'<a:srgbClr val="{line}"/></a:solidFill></a:ln>')
    else:
        body += '<a:ln><a:noFill/></a:ln>'
    body += "</p:spPr>"
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_next_id()}" name="Rect"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>{body}'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')


def _run(text, *, size, color, bold=False, font=BODY_FONT, spacing=None,
         caps=False, italic=False):
    props = [f'sz="{int(size * 100)}"']
    if bold:
        props.append('b="1"')
    if italic:
        props.append('i="1"')
    if spacing is not None:
        props.append(f'spc="{int(spacing * 100)}"')
    if caps:
        props.append('cap="all"')
    return (f'<a:r><a:rPr lang="en-US" {" ".join(props)} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr>'
            f'<a:t>{esc(text)}</a:t></a:r>')


def picture(source, x, y, box_w, box_h, *, name="Picture", align="left",
            valign="middle"):
    """
    Place a PNG inside a box without distorting it.

    The box is a bounding box, not a target size. The mark is scaled to fit and
    then positioned inside it, because a stretched logo is both ugly and, for a
    client's mark, a trademark problem.
    """
    digest = media.register(source)
    cx, cy = media.fit(digest, box_w, box_h)
    if align == "center":
        x = x + (box_w - cx) // 2
    elif align == "right":
        x = x + (box_w - cx)
    if valign == "middle":
        y = y + (box_h - cy) // 2
    elif valign == "bottom":
        y = y + (box_h - cy)
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{_next_id()}" name="{esc(name)}"/>'
            '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/>'
            '</p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{media.token(digest)}"/>'
            '<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def textbox(x, y, cx, cy, paragraphs, *, anchor="t", wrap=True):
    """`paragraphs` is a list of (runs_html, space_before_pt, line_spacing_pct)."""
    body = "".join(
        f'<a:p><a:pPr><a:lnSpc><a:spcPct val="{int(ls * 1000)}"/></a:lnSpc>'
        f'<a:spcBef><a:spcPts val="{int(sb * 100)}"/></a:spcBef></a:pPr>{runs}</a:p>'
        for runs, sb, ls in paragraphs)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{_next_id()}" name="Text"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'{_sp_pr(x, y, cx, cy)}<a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="{"square" if wrap else "none"}" '
            f'anchor="{anchor}"><a:normAutofit/></a:bodyPr>'
            f'<a:lstStyle/>{body}</p:txBody></p:sp>')


def para(runs, before=0, line=100):
    return (runs, before, line)


# ---------------------------------------------------------------------------
# Slide chrome
# ---------------------------------------------------------------------------

def _footer(number, dark, right_label="Align HCM"):
    color = MUTED_LIGHT if dark else MUTED
    y = SLIDE_H - round(0.55 * EMU)
    third = round(CONTENT_W / 3)
    return (
        textbox(MARGIN, y, third, round(0.3 * EMU),
                [para(_run("alignhcm.com", size=8, color=color, caps=True,
                           spacing=1.6))])
        + textbox(MARGIN + third, y, third, round(0.3 * EMU),
                  [para(_run("Confidential", size=8, color=color, caps=True,
                             spacing=1.6))])
        + textbox(MARGIN + 2 * third, y, third, round(0.3 * EMU),
                  [para(_run(f"{right_label}  ·  {number:02d}", size=8,
                             color=color, caps=True, spacing=1.6))]))


def _eyebrow(text, y, dark, x=MARGIN):
    colour = ORANGE if dark else CONTRAST_ORANGE
    return textbox(x, y, CONTENT_W - (x - MARGIN), round(0.3 * EMU),
                   [para(_run(text, size=10, color=colour, bold=True,
                              caps=True, spacing=2.2))])


# ---------------------------------------------------------------------------
# Slide kinds
# ---------------------------------------------------------------------------

def cover(title_text, subtitle, eyebrow, meta_lines, *, lockup=None,
          client_logo=None):
    """
    Navy split cover.

    `lockup` is the Align mark and goes at the master's AlignHCM_Logo geometry.
    `client_logo` is the prospect's, cleaned and plated by the brand system, and
    goes in the right panel at the master's CLIENT_LOGO geometry. Both are
    fitted, never stretched.
    """
    split = round(SLIDE_W * 0.66)
    out = [rect(0, 0, SLIDE_W, SLIDE_H, NAVY),
           rect(split, 0, SLIDE_W - split, SLIDE_H, DEEP_NAVY),
           rect(split - 12700, 0, 25400, SLIDE_H, ORANGE)]
    if lockup:
        x, y, w, h = media.box_emu(media.ALIGN_LOGO_BOX)
        out.append(picture(lockup, x, y, w, h, name="AlignHCM_Logo",
                           align="left", valign="top"))
    if client_logo:
        x, y, w, h = media.box_emu(media.CLIENT_LOGO_BOX)
        out.append(picture(client_logo, x, y, w, h, name="CLIENT_LOGO",
                           align="center", valign="middle"))
    out.append(_eyebrow(eyebrow, round(3.2 * EMU), True))
    out.append(textbox(MARGIN, round(3.6 * EMU), split - MARGIN - round(0.5 * EMU),
                       round(1.3 * EMU),
                       [para(_run(title_text, size=40, color=WHITE, bold=True,
                                  font=HEADING_FONT))]))
    out.append(textbox(MARGIN, round(4.95 * EMU), split - MARGIN - round(0.5 * EMU),
                       round(0.6 * EMU),
                       [para(_run(subtitle, size=18, color=LIGHT_TEXT))]))
    out.append(rect(MARGIN, round(5.68 * EMU), round(0.9 * EMU), 38100, ORANGE))
    y = round(5.95 * EMU)
    for i, line in enumerate(meta_lines):
        out.append(textbox(MARGIN, y + i * round(0.32 * EMU), round(5 * EMU),
                           round(0.3 * EMU),
                           [para(_run(line, size=11, color=MUTED_LIGHT,
                                      bold=(i == 0)))]))
    out.append(textbox(split + round(0.4 * EMU), round(3.0 * EMU),
                       SLIDE_W - split - round(0.8 * EMU), round(0.3 * EMU),
                       [para(_run("Prepared for", size=9, color=MUTED_LIGHT,
                                  caps=True, spacing=2.0))]))
    return "".join(out)


def section(number, title_text, framing):
    """Paper divider with the orange numbered disc."""
    out = [rect(0, 0, SLIDE_W, SLIDE_H, PAPER)]
    d = round(1.15 * EMU)
    out.append(rect(MARGIN, round(2.9 * EMU), d, d, ORANGE, radius=True))
    out.append(textbox(MARGIN, round(3.2 * EMU), d, round(0.7 * EMU),
                       [para(_run(f"{number}", size=34, color=WHITE, bold=True,
                                  font=HEADING_FONT))]))
    left = MARGIN + d + round(0.5 * EMU)
    out.append(_eyebrow("Section", round(2.95 * EMU), False, x=left))
    out.append(textbox(left, round(3.25 * EMU), CONTENT_W - d - round(0.5 * EMU),
                       round(0.8 * EMU),
                       [para(_run(title_text, size=30, color=NAVY, bold=True,
                                  font=HEADING_FONT))]))
    out.append(textbox(left, round(4.1 * EMU), CONTENT_W - d - round(0.5 * EMU),
                       round(0.8 * EMU),
                       [para(_run(framing, size=13, color=MUTED))]))
    out.append(rect(0, SLIDE_H - round(0.75 * EMU), SLIDE_W, round(0.75 * EMU), NAVY))
    return "".join(out)


def statement(eyebrow, title_text, body, dark=False):
    """A light or navy field with a title and one paragraph."""
    ground, title_c, body_c = ((NAVY, WHITE, LIGHT_TEXT) if dark
                               else (PAPER, NAVY, MUTED))
    out = [rect(0, 0, SLIDE_W, SLIDE_H, ground), _eyebrow(eyebrow, MARGIN, dark)]
    out.append(textbox(MARGIN, round(1.15 * EMU), CONTENT_W, round(0.9 * EMU),
                       [para(_run(title_text, size=28, color=title_c, bold=True,
                                  font=HEADING_FONT))]))
    out.append(rect(MARGIN, round(2.05 * EMU), round(0.9 * EMU), 38100, ORANGE))
    out.append(textbox(MARGIN, round(2.35 * EMU), CONTENT_W, round(1.2 * EMU),
                       [para(_run(body, size=13, color=body_c), line=130)]))
    return "".join(out)


def cards(eyebrow, title_text, items, *, dark=True, columns=2):
    """A grid of navy cards. `items` is a list of (heading, body)."""
    ground = PAPER
    out = [rect(0, 0, SLIDE_W, SLIDE_H, ground), _eyebrow(eyebrow, MARGIN, False)]
    out.append(textbox(MARGIN, round(1.05 * EMU), CONTENT_W, round(0.8 * EMU),
                       [para(_run(title_text, size=26, color=NAVY, bold=True,
                                  font=HEADING_FONT))]))
    out.append(rect(MARGIN, round(1.9 * EMU), round(0.9 * EMU), 38100, ORANGE))

    gap = round(0.28 * EMU)
    rows = (len(items) + columns - 1) // columns
    card_w = round((CONTENT_W - gap * (columns - 1)) / columns)
    top = round(2.35 * EMU)
    avail = SLIDE_H - top - round(0.95 * EMU)
    card_h = round((avail - gap * (rows - 1)) / max(1, rows))

    for i, (head, body) in enumerate(items):
        col, row = i % columns, i // columns
        x = MARGIN + col * (card_w + gap)
        y = top + row * (card_h + gap)
        out.append(rect(x, y, card_w, card_h, NAVY_CARD if dark else WHITE,
                        radius=True, line=None if dark else RULE))
        out.append(rect(x, y, round(0.06 * EMU), card_h, ORANGE))
        pad = round(0.28 * EMU)
        out.append(textbox(x + pad, y + round(0.2 * EMU), card_w - 2 * pad,
                           round(0.5 * EMU),
                           [para(_run(head, size=13, bold=True,
                                      color=WHITE if dark else NAVY))]))
        out.append(textbox(x + pad, y + round(0.72 * EMU), card_w - 2 * pad,
                           card_h - round(0.9 * EMU),
                           [para(_run(body, size=10.5,
                                      color=LIGHT_TEXT if dark else MUTED),
                                 line=128)]))
    return "".join(out)


def phases(eyebrow, title_text, steps, marker_index=None):
    """A horizontal phase band, optionally with one orange milestone marker."""
    out = [rect(0, 0, SLIDE_W, SLIDE_H, PAPER), _eyebrow(eyebrow, MARGIN, False)]
    out.append(textbox(MARGIN, round(1.05 * EMU), CONTENT_W, round(0.8 * EMU),
                       [para(_run(title_text, size=26, color=NAVY, bold=True,
                                  font=HEADING_FONT))]))
    out.append(rect(MARGIN, round(1.9 * EMU), round(0.9 * EMU), 38100, ORANGE))

    n = max(1, len(steps))
    gap = round(0.12 * EMU)
    w = round((CONTENT_W - gap * (n - 1)) / n)
    y = round(3.0 * EMU)
    h = round(1.6 * EMU)
    shades = [NAVY, "26334A", "2F4059", "3A4E6B", "465C7E", "55606E"]

    for i, (label, detail) in enumerate(steps):
        x = MARGIN + i * (w + gap)
        out.append(rect(x, y, w, h, shades[i % len(shades)]))
        out.append(textbox(x + round(0.16 * EMU), y + round(0.22 * EMU),
                           w - round(0.32 * EMU), round(0.7 * EMU),
                           [para(_run(label, size=11.5, bold=True, color=WHITE))]))
        out.append(textbox(x + round(0.16 * EMU), y + round(1.0 * EMU),
                           w - round(0.32 * EMU), round(0.45 * EMU),
                           [para(_run(detail, size=9.5, color=MUTED_LIGHT))]))
        if marker_index is not None and i == marker_index:
            out.append(rect(x + w - 12700, y - round(0.45 * EMU), 25400,
                            h + round(0.45 * EMU), ORANGE))
    return "".join(out)


SMARTCARE_ASSET = "smartcare-lockup.png"


def smartcare_lockup(x, y, *, dark=False, asset=None, height_in=0.44):
    """
    The SmartCare mark.

    Align has no SmartCare logo. Not in the master deck, not in SharePoint, not
    in any reachable brand kit. Rather than invent artwork and pass it off as a
    logo, this draws the typographic lockup the client decks already use:
    "Smart" in the document's ink, "Care" in Align orange, with a short orange
    rule. It is type, not a trademark someone made up this afternoon.

    Drop a real `smartcare-lockup.png` into `scripts/_core/` and pass it as
    `asset` and that is used instead, with no other change.
    """
    if asset:
        return picture(asset, x, y, round(3.2 * EMU), round(height_in * EMU),
                       name="SmartCare_Lockup", align="left", valign="middle")

    ink = WHITE if dark else NAVY
    h = round(height_in * EMU)
    return "".join([
        textbox(x, y, round(2.6 * EMU), h,
                [para([_run("Smart", size=20, color=ink, bold=True,
                            font=HEADING_FONT, spacing=-0.3),
                       _run("Care", size=20, color=ORANGE, bold=True,
                            font=HEADING_FONT, spacing=-0.3)])]),
        rect(x + 25400, y + h - 12700, round(0.62 * EMU), 25400, ORANGE),
    ])


def data_table(eyebrow, title_text, headers, rows, widths=None, *,
               smartcare=False, smartcare_asset=None):
    """A light table with a navy header and alternating rows."""
    out = [rect(0, 0, SLIDE_W, SLIDE_H, PAPER), _eyebrow(eyebrow, MARGIN, False)]
    out.append(textbox(MARGIN, round(1.05 * EMU), CONTENT_W, round(0.8 * EMU),
                       [para(_run(title_text, size=26, color=NAVY, bold=True,
                                  font=HEADING_FONT))]))
    out.append(rect(MARGIN, round(1.9 * EMU), round(0.9 * EMU), 38100, ORANGE))
    if smartcare:
        # Right-aligned against the title, so it reads as a service mark on the
        # slide rather than competing with the Align lockup.
        out.append(smartcare_lockup(SLIDE_W - MARGIN - round(2.6 * EMU),
                                    round(1.05 * EMU), dark=False,
                                    asset=smartcare_asset))

    cols = len(headers)
    widths = widths or [1.0 / cols] * cols
    total = sum(widths)
    widths = [w / total for w in widths]
    y = round(2.45 * EMU)
    row_h = round(0.42 * EMU)

    out.append(rect(MARGIN, y, CONTENT_W, row_h, NAVY))
    x = MARGIN
    for i, head in enumerate(headers):
        cw = round(CONTENT_W * widths[i])
        out.append(textbox(x + round(0.12 * EMU), y + round(0.09 * EMU),
                           cw - round(0.2 * EMU), row_h,
                           [para(_run(head, size=10.5, bold=True, color=WHITE))]))
        x += cw

    for r, row in enumerate(rows):
        ry = y + row_h + r * row_h
        if r % 2 == 0:
            out.append(rect(MARGIN, ry, CONTENT_W, row_h, "EDF2F8"))
        x = MARGIN
        for i, val in enumerate(row):
            cw = round(CONTENT_W * widths[i])
            out.append(textbox(x + round(0.12 * EMU), ry + round(0.09 * EMU),
                               cw - round(0.2 * EMU), row_h,
                               [para(_run(val, size=10,
                                          bold=(i == 0),
                                          color=NAVY if i == 0 else "1F2937"))]))
            x += cw
    return "".join(out)


def closing(title_text, body, contact_lines):
    out = [rect(0, 0, SLIDE_W, SLIDE_H, NAVY)]
    out.append(_eyebrow("Next step", round(2.4 * EMU), True))
    out.append(textbox(MARGIN, round(2.85 * EMU), round(7.2 * EMU), round(1.2 * EMU),
                       [para(_run(title_text, size=32, color=WHITE, bold=True,
                                  font=HEADING_FONT))]))
    out.append(rect(MARGIN, round(4.2 * EMU), round(0.9 * EMU), 38100, ORANGE))
    out.append(textbox(MARGIN, round(4.5 * EMU), round(7.2 * EMU), round(0.9 * EMU),
                       [para(_run(body, size=13, color=LIGHT_TEXT), line=130)]))
    y = round(3.0 * EMU)
    for i, line in enumerate(contact_lines):
        out.append(textbox(round(8.3 * EMU), y + i * round(0.34 * EMU),
                           round(4.2 * EMU), round(0.32 * EMU),
                           [para(_run(line, size=11,
                                      color=WHITE if i == 0 else MUTED_LIGHT,
                                      bold=(i == 0)))]))
    return "".join(out)


# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

def _slide_xml(shapes):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + shapes +
            '</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping '
            'bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" '
            'accent2="accent2" accent3="accent3" accent4="accent4" '
            'accent5="accent5" accent6="accent6" hlink="hlink" '
            'folHlink="folHlink"/></p:clrMapOvr></p:sld>')


_MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr/></p:spTree></p:cSld>
<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>'''

_LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr/></p:spTree></p:cSld>
<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''

_THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Align HCM">
<a:themeElements>
<a:clrScheme name="Align HCM"><a:dk1><a:srgbClr val="232E3E"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
<a:dk2><a:srgbClr val="1D2735"/></a:dk2><a:lt2><a:srgbClr val="F6F8FA"/></a:lt2>
<a:accent1><a:srgbClr val="E97722"/></a:accent1><a:accent2><a:srgbClr val="B05512"/></a:accent2>
<a:accent3><a:srgbClr val="4A5C75"/></a:accent3><a:accent4><a:srgbClr val="C7D2DF"/></a:accent4>
<a:accent5><a:srgbClr val="2B3849"/></a:accent5><a:accent6><a:srgbClr val="55606E"/></a:accent6>
<a:hlink><a:srgbClr val="B05512"/></a:hlink><a:folHlink><a:srgbClr val="4A5563"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Align HCM"><a:majorFont><a:latin typeface="Cambria"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Align HCM">
<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
</a:fmtScheme></a:themeElements></a:theme>'''


def build(slides, path, *, title="Align HCM"):
    """`slides` is a list of shape-XML strings, one per slide, in order."""
    n = len(slides)
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Default Extension="png" ContentType="image/png"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>']
    for i in range(1, n + 1):
        ct.append(f'<Override PartName="/ppt/slides/slide{i}.xml" '
                  'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    ct.append("</Types>")

    sld_ids = "".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, n + 1))
    presentation = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{sld_ids}</p:sldIdLst>'
        f'<p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="screen16x9"/>'
        f'<p:notesSz cx="{SLIDE_H}" cy="{SLIDE_W}"/></p:presentation>')

    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(1, n + 1):
        pres_rels.append(f'<Relationship Id="rId{i + 1}" '
                         'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
                         f'Target="slides/slide{i}.xml"/>')
    pres_rels.append(f'<Relationship Id="rId{n + 2}" '
                     'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" '
                     'Target="theme/theme1.xml"/>')
    pres_rels.append("</Relationships>")

    # Pictures were emitted as {IMG:sha} tokens. Turn them into media parts and
    # per-slide relationships now that the whole deck is known.
    _, media_names = media.plan(slides)
    resolved, slide_rels = [], []
    for shapes in slides:
        digests = []
        for d in media.digests_in(shapes):
            if d not in digests:
                digests.append(d)
        mapping = {d: f"rId{i + 2}" for i, d in enumerate(digests)}
        resolved.append(media.substitute(shapes, mapping))
        rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" '
                'Target="../slideLayouts/slideLayout1.xml"/>']
        for d, rid in mapping.items():
            rels.append(f'<Relationship Id="{rid}" '
                        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                        f'Target="../media/{media_names[d]}"/>')
        rels.append("</Relationships>")
        slide_rels.append("".join(rels))
    slides = resolved

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                   '</Relationships>')
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", "".join(pres_rels))
        z.writestr("ppt/slideMasters/slideMaster1.xml", _MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
                   '</Relationships>')
        z.writestr("ppt/slideLayouts/slideLayout1.xml", _LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
                   '</Relationships>')
        z.writestr("ppt/theme/theme1.xml", _THEME)
        for digest, part in media_names.items():
            z.writestr(f"ppt/media/{part}", media.data_for(digest))
        for i, shapes in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", _slide_xml(shapes))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels[i - 1])
        z.writestr("docProps/core.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/">'
                   f'<dc:title>{esc(title)}</dc:title>'
                   '<dc:creator>Align HCM</dc:creator></cp:coreProperties>')
    return path


def with_footers(slides, dark_flags=None, right_label="Align HCM"):
    """Append the three-zone footer to each slide, numbered in order."""
    out = []
    for i, shapes in enumerate(slides, 1):
        dark = dark_flags[i - 1] if dark_flags else False
        out.append(shapes + _footer(i, dark, right_label))
    return out
