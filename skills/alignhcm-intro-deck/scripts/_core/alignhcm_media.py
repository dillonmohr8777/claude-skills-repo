"""
Image embedding for the Align document writers.

Both writers emit XML as plain strings, which is why they had no pictures: a
picture needs a media part and a relationship, and those live in the package
rather than in the shape. Rather than thread an image list through every call
site, a picture emits a token and `resolve()` turns the tokens into real parts
at package time. Slides and paragraphs stay strings.

Only PNG is handled on purpose. The Align lockup is a PNG, `fetch_client_logo`
writes PNG, and the whole point of that pipeline is a cleaned raster with a
known alpha channel.
"""

import hashlib
import os
import re
import struct

TOKEN_RE = re.compile(r"\{IMG:([0-9a-f]{64})\}")

EMU_PER_INCH = 914400

_BANK = {}


class ImageError(ValueError):
    pass


def register(source):
    """
    Take a path or raw bytes, return the sha256 that identifies it.

    Registration is content-addressed, so the same logo used on six slides is
    stored once and referenced six times.
    """
    if isinstance(source, (bytes, bytearray)):
        data = bytes(source)
    else:
        if not os.path.exists(source):
            raise ImageError(f"image not found: {source}")
        with open(source, "rb") as fh:
            data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ImageError("only PNG is supported; got something else")
    digest = hashlib.sha256(data).hexdigest()
    _BANK[digest] = data
    return digest


def token(digest):
    return "{IMG:" + digest + "}"


def size(digest):
    """(width, height) in pixels, read from the PNG IHDR."""
    data = _BANK[digest]
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def fit(digest, box_w_emu, box_h_emu):
    """
    Largest (cx, cy) preserving aspect that fits the box.

    A logo stretched to fill a box is the single most common way a co-branded
    deck looks amateur, and it is also a trademark problem: a distorted mark is
    not the client's mark.
    """
    w, h = size(digest)
    if w <= 0 or h <= 0:
        raise ImageError("image reports a zero dimension")
    scale = min(box_w_emu / w, box_h_emu / h)
    return int(round(w * scale)), int(round(h * scale))


def digests_in(xml):
    return TOKEN_RE.findall(xml)


def data_for(digest):
    return _BANK[digest]


def substitute(xml, mapping):
    """Replace {IMG:sha} with whatever the package assigned, usually an rId."""
    return TOKEN_RE.sub(lambda m: mapping[m.group(1)], xml)


def plan(xml_parts):
    """
    Work out the media parts for a package.

    Returns (ordered_digests, media_names) where media_names maps a digest to
    its part name under the package's media folder.
    """
    ordered = []
    for xml in xml_parts:
        for digest in digests_in(xml):
            if digest not in ordered:
                ordered.append(digest)
    names = {d: f"image{i}.png" for i, d in enumerate(ordered, 1)}
    return ordered, names


def reset():
    """Drop the bank. Used by tests that build several documents in a row."""
    _BANK.clear()


# ---------------------------------------------------------------------------
# The Align lockup
# ---------------------------------------------------------------------------

LOCKUP_NAME = "align-hcm-deck-lockup.png"

# The exact mark, taken from ppt/media/image1.png of the Align master deck.
# Pinned so a swapped or re-exported file is caught rather than shipped.
LOCKUP_SHA = "3a0340d27bfe44b21277f4a689796b1c31338f5fd74134786209f5b736d22a07"

# Geometry from the master's named picture zones, in inches.
ALIGN_LOGO_BOX = (0.900, 0.780, 2.750, 1.275)   # AlignHCM_Logo
CLIENT_LOGO_BOX = (9.667, 3.475, 2.900, 0.967)  # CLIENT_LOGO


def align_lockup(core_dir):
    """Path to the vendored lockup, refusing anything that is not the real one."""
    path = os.path.join(core_dir, LOCKUP_NAME)
    if not os.path.exists(path):
        raise ImageError(f"the Align lockup is missing from {core_dir}")
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != LOCKUP_SHA:
        raise ImageError(
            f"{LOCKUP_NAME} is not the approved Align mark "
            f"(sha256 {digest[:16]}, expected {LOCKUP_SHA[:16]})")
    return path


def box_emu(box):
    """Convert an inches 4-tuple to EMU."""
    return tuple(int(round(v * EMU_PER_INCH)) for v in box)
