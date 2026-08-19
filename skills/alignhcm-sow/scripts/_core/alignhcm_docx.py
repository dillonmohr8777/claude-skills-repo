"""
Write a branded Align Word document from a simple block spec.

There is no python-docx here and there will not be one, so this emits
WordprocessingML directly. It supports exactly what an Align SOW, status
report, or one-pager needs and nothing else: headings, paragraphs, bullets,
tables, a title block, page breaks, and a footer.

Colours and fonts come from the measured Align deck master, so a document this
produces passes the same brand gate a deck does.

Sizes are in half-points (Word's unit), so 22 is 11pt.
"""

import datetime
import re
import zipfile

import alignhcm_media as media

NAVY = "232E3E"
ORANGE = "E97722"
CONTRAST_ORANGE = "B05512"
RULE = "C7D2DF"
MUTED = "4A5563"
PAPER_ROW = "EDF2F8"

HEADING_FONT = "Cambria"
BODY_FONT = "Calibri"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Block constructors. A document is a list of these.
# ---------------------------------------------------------------------------

def title(text, subtitle=None, meta=None, *, suppress_eyebrow=False):
    """`suppress_eyebrow` drops the typographic ALIGN HCM line, which is
    redundant and looks like a second logo once a masthead is present."""
    return {"type": "title", "text": text, "subtitle": subtitle, "meta": meta,
            "suppress_eyebrow": suppress_eyebrow}


def masthead(source, width_in=1.9, *, fill=None):
    """
    The Align lockup on a navy band across the top of the page.

    The bundled lockup is a reverse mark: the wordmark is light grey, built for
    dark backgrounds. Dropped straight onto white paper it is washed out and
    off-brand. The band is not decoration, it is what makes the supplied
    artwork legible without altering it.
    """
    return {"type": "masthead", "source": source, "width_in": width_in,
            "fill": fill or NAVY}


def logo(source, width_in=1.9, *, name="AlignHCM_Logo", after=120):
    """An inline image, scaled to `width_in` inches with aspect preserved."""
    return {"type": "logo", "source": source, "width_in": width_in,
            "name": name, "after": after}


def heading(text, level=1):
    return {"type": "heading", "text": text, "level": level}


def para(text, bold=False, color=None, size=22):
    return {"type": "para", "text": text, "bold": bold, "color": color, "size": size}


def bullets(items):
    return {"type": "bullets", "items": list(items)}


def numbered(items):
    return {"type": "numbered", "items": list(items)}


def table(headers, rows, widths=None):
    return {"type": "table", "headers": list(headers),
            "rows": [list(r) for r in rows], "widths": widths}


def rule():
    return {"type": "rule"}


def page_break():
    return {"type": "page_break"}


def signature_block(labels):
    return {"type": "signature", "labels": list(labels)}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _run(text, *, bold=False, color=None, size=22, font=BODY_FONT, caps=False,
         spacing=None, italic=False):
    props = [f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>']
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if caps:
        props.append("<w:caps/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if spacing:
        props.append(f'<w:spacing w:val="{spacing}"/>')
    props.append(f'<w:sz w:val="{size}"/>')
    return (f'<w:r><w:rPr>{"".join(props)}</w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r>')


def _para(runs, *, before=0, after=120, border_bottom=None, indent=None,
          align=None, numbering=None):
    props = ["<w:pPr>"]
    if numbering is not None:
        props.append(f'<w:numPr><w:ilvl w:val="0"/>'
                     f'<w:numId w:val="{numbering}"/></w:numPr>')
    if indent:
        props.append(f'<w:ind w:left="{indent}"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    props.append(f'<w:spacing w:before="{before}" w:after="{after}"/>')
    if border_bottom:
        props.append(f'<w:pBdr><w:bottom w:val="single" w:sz="{border_bottom[1]}" '
                     f'w:space="4" w:color="{border_bottom[0]}"/></w:pBdr>')
    props.append("</w:pPr>")
    return f'<w:p>{"".join(props)}{"".join(runs)}</w:p>'


DRAWING_NS = ('xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/'
              'wordprocessingDrawing"')
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"


def _drawing(digest, cx, cy, name):
    ident = media.size(digest)[0]  # any stable int is fine for docPr
    return (
        f'<w:p><w:pPr><w:spacing w:after="0"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0" {DRAWING_NS}>'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{ident}" name="{esc(name)}"/>'
        f'<a:graphic xmlns:a="{A_NS}"><a:graphicData uri="{PIC_NS}">'
        f'<pic:pic xmlns:pic="{PIC_NS}">'
        f'<pic:nvPicPr><pic:cNvPr id="{ident}" name="{esc(name)}"/>'
        '<pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{media.token(digest)}"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/>'
        '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline>'
        '</w:drawing></w:r></w:p>')


def _render_block(block):
    kind = block["type"]

    if kind == "masthead":
        digest = media.register(block["source"])
        box = int(block["width_in"] * media.EMU_PER_INCH)
        cx, cy = media.fit(digest, box, box * 4)
        inner = _drawing(digest, cx, cy, "AlignHCM_Logo")
        return (
            '<w:tbl><w:tblPr>'
            '<w:tblW w:w="9360" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar>'
            '<w:top w:w="220" w:type="dxa"/><w:left w:w="260" w:type="dxa"/>'
            '<w:bottom w:w="220" w:type="dxa"/><w:right w:w="260" w:type="dxa"/>'
            '</w:tblCellMar></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="9360"/></w:tblGrid>'
            '<w:tr><w:tc><w:tcPr><w:tcW w:w="9360" w:type="dxa"/>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="{block["fill"]}"/>'
            '</w:tcPr>' + inner + '</w:tc></w:tr></w:tbl>'
            + _para([], after=200))

    if kind == "logo":
        digest = media.register(block["source"])
        box = int(block["width_in"] * media.EMU_PER_INCH)
        cx, cy = media.fit(digest, box, box * 4)
        return _drawing(digest, cx, cy, block["name"])

    if kind == "title":
        out = []
        if not block.get("suppress_eyebrow"):
            out.append(_para([_run("ALIGN HCM", bold=True, color=ORANGE, size=18,
                                   caps=True, spacing=60)], after=60))
        out.append(_para([_run(block["text"], bold=True, color=NAVY, size=52,
                               font=HEADING_FONT)], after=80))
        if block.get("subtitle"):
            out.append(_para([_run(block["subtitle"], color=MUTED, size=26)],
                             after=80))
        out.append(_para([], border_bottom=(ORANGE, 18), after=160))
        if block.get("meta"):
            for label, value in block["meta"]:
                out.append(_para([
                    _run(f"{label}   ", bold=True, color=NAVY, size=20),
                    _run(value, color=MUTED, size=20)], after=40))
        return "".join(out)

    if kind == "heading":
        level = block.get("level", 1)
        if level == 1:
            return _para([_run(block["text"], bold=True, color=NAVY, size=32,
                               font=HEADING_FONT)],
                         before=280, after=100, border_bottom=(RULE, 6))
        return _para([_run(block["text"], bold=True, color=CONTRAST_ORANGE,
                           size=22, caps=True, spacing=40)],
                     before=200, after=80)

    if kind == "para":
        return _para([_run(block["text"], bold=block.get("bold", False),
                           color=block.get("color") or "1F2937",
                           size=block.get("size", 22))])

    if kind == "bullets":
        return "".join(
            _para([_run("•   ", color=ORANGE, bold=True),
                   _run(item)], indent=284, after=60)
            for item in block["items"])

    if kind == "numbered":
        return "".join(
            _para([_run(f"{i}.   ", color=ORANGE, bold=True),
                   _run(item)], indent=284, after=60)
            for i, item in enumerate(block["items"], 1))

    if kind == "rule":
        return _para([], border_bottom=(RULE, 6), after=160)

    if kind == "page_break":
        return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

    if kind == "table":
        return _render_table(block)

    if kind == "signature":
        cells = []
        for label in block["labels"]:
            cells.append(
                '<w:tc><w:tcPr><w:tcW w:w="4600" w:type="dxa"/>'
                '<w:tcBorders><w:top w:val="single" w:sz="6" w:color="' + NAVY
                + '"/></w:tcBorders></w:tcPr>'
                + _para([_run(label, size=18, color=MUTED)], before=60, after=0)
                + "</w:tc>")
        return ('<w:tbl><w:tblPr><w:tblW w:w="9200" w:type="dxa"/>'
                '<w:tblCellMar><w:top w:w="120" w:type="dxa"/>'
                '<w:left w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>'
                '<w:tr><w:trPr><w:trHeight w:val="900"/></w:trPr>'
                + "".join(cells) + "</w:tr></w:tbl>")

    raise ValueError(f"unknown block type {kind!r}")


def _cell(text, *, bold=False, color="1F2937", fill=None, width=None,
          size=20, align=None):
    props = ["<w:tcPr>"]
    if width:
        props.append(f'<w:tcW w:w="{width}" w:type="dxa"/>')
    if fill:
        props.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>')
    props.append('<w:tcBorders>'
                 f'<w:bottom w:val="single" w:sz="4" w:color="{RULE}"/>'
                 '</w:tcBorders>')
    props.append('<w:vAlign w:val="center"/>')
    props.append("</w:tcPr>")
    body = _para([_run(text, bold=bold, color=color, size=size)],
                 before=60, after=60, align=align)
    return f'<w:tc>{"".join(props)}{body}</w:tc>'


def _render_table(block):
    headers, rows = block["headers"], block["rows"]
    widths = block.get("widths") or [round(9200 / max(1, len(headers)))] * len(headers)

    head = "".join(_cell(h, bold=True, color="FFFFFF", fill=NAVY,
                         width=widths[i], size=19)
                   for i, h in enumerate(headers))
    body = []
    for r, row in enumerate(rows):
        fill = PAPER_ROW if r % 2 else None
        body.append("<w:tr>" + "".join(
            _cell(str(v), fill=fill, width=widths[i],
                  bold=(i == 0), color=NAVY if i == 0 else "1F2937")
            for i, v in enumerate(row)) + "</w:tr>")
    return ('<w:tbl><w:tblPr><w:tblW w:w="9200" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:left w:w="110" w:type="dxa"/>'
            '<w:right w:w="110" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tr><w:trPr><w:tblHeader/></w:trPr>{head}</w:tr>'
            + "".join(body) + "</w:tbl>")


# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''

STYLES = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="{BODY_FONT}" w:hAnsi="{BODY_FONT}"/>
<w:sz w:val="22"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/>
</w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/></w:style>
</w:styles>'''


def _footer(text):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:ftr xmlns:w="{W_NS}">'
            + _para([_run(text, size=16, color=MUTED, caps=True, spacing=40)],
                    after=0, border_bottom=None)
            + "</w:ftr>")


def build(blocks, path, *, footer_text="alignhcm.com  ·  Confidential",
          doc_title="Align HCM"):
    """Render blocks to a .docx at `path`."""
    body = "".join(_render_block(b) for b in blocks)
    document = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<w:body>{body}'
        '<w:sectPr>'
        '<w:footerReference w:type="default" r:id="rId2"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/>'
        '</w:sectPr></w:body></w:document>')

    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f'<dc:title>{esc(doc_title)}</dc:title>'
            '<dc:creator>Align HCM</dc:creator>'
            '</cp:coreProperties>')

    # Pictures were emitted as {IMG:sha} tokens; bind them to relationships.
    _, media_names = media.plan([document])
    mapping, rels = {}, [DOC_RELS.replace("</Relationships>", "")]
    for i, digest in enumerate(media_names, 3):
        mapping[digest] = f"rId{i}"
        rels.append(f'<Relationship Id="rId{i}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                    f'Target="media/{media_names[digest]}"/>')
    rels.append("</Relationships>")
    document = media.substitute(document, mapping)
    content_types = CONTENT_TYPES
    if media_names:
        content_types = CONTENT_TYPES.replace(
            '<Default Extension="xml" ContentType="application/xml"/>',
            '<Default Extension="xml" ContentType="application/xml"/>\n'
            '<Default Extension="png" ContentType="image/png"/>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", "".join(rels))
        for digest, part in media_names.items():
            z.writestr(f"word/media/{part}", media.data_for(digest))
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/footer1.xml", _footer(footer_text))
        z.writestr("docProps/core.xml", core)
    return path
