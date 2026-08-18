"""
Minimal PNG read/write plus the cleanup a fetched logo needs.

Written on the standard library so the package keeps its no-install property.
Pillow is used only when it is already present, and only for the formats a
stdlib decoder cannot reach (JPEG, WebP) or for higher quality resampling.

Supported natively: PNG, bit depth 8, colour types 0/2/3/4/6, non-interlaced.
That covers essentially every logo served on the web. Anything else asks for
Pillow rather than guessing.
"""

import struct
import zlib

try:  # optional, never required
    from PIL import Image as _PILImage
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    _PILImage = None
    HAVE_PIL = False

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class Raster:
    """An RGBA image as a flat bytearray, 4 bytes per pixel."""

    __slots__ = ("w", "h", "px")

    def __init__(self, w, h, px=None):
        self.w = w
        self.h = h
        self.px = px if px is not None else bytearray(w * h * 4)

    def at(self, x, y):
        i = (y * self.w + x) * 4
        return self.px[i:i + 4]

    def set(self, x, y, rgba):
        i = (y * self.w + x) * 4
        self.px[i:i + 4] = rgba

    def alpha(self, x, y):
        return self.px[(y * self.w + x) * 4 + 3]

    def set_alpha(self, x, y, a):
        self.px[(y * self.w + x) * 4 + 3] = a


# ---------------------------------------------------------------------------
# PNG decode
# ---------------------------------------------------------------------------

def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _unfilter(data, w, h, bpp):
    """Undo the per-scanline PNG filters. Returns raw samples."""
    stride = w * bpp
    out = bytearray(stride * h)
    pos = 0
    prev = bytearray(stride)
    for y in range(h):
        ftype = data[pos]
        pos += 1
        line = bytearray(data[pos:pos + stride])
        pos += stride
        if ftype == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                upleft = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(left, prev[i], upleft)) & 0xFF
        elif ftype != 0:
            raise ValueError(f"unsupported PNG filter type {ftype}")
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out


def decode_png(data):
    """PNG bytes to Raster. Raises ValueError on anything unsupported."""
    if data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG")
    pos = 8
    idat = bytearray()
    palette = None
    trns = None
    w = h = depth = ctype = interlace = None

    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"PLTE":
            palette = body
        elif tag == b"tRNS":
            trns = body
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break

    if depth != 8:
        raise ValueError(f"unsupported PNG bit depth {depth}; needs Pillow")
    if interlace:
        raise ValueError("interlaced PNG; needs Pillow")

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if channels is None:
        raise ValueError(f"unsupported PNG colour type {ctype}")

    raw = _unfilter(zlib.decompress(bytes(idat)), w, h, channels)
    img = Raster(w, h)
    out = img.px

    for i in range(w * h):
        s = i * channels
        o = i * 4
        if ctype == 6:
            out[o:o + 4] = raw[s:s + 4]
        elif ctype == 2:
            out[o:o + 3] = raw[s:s + 3]
            out[o + 3] = 255
        elif ctype == 0:
            g = raw[s]
            out[o] = out[o + 1] = out[o + 2] = g
            out[o + 3] = 255
        elif ctype == 4:
            g = raw[s]
            out[o] = out[o + 1] = out[o + 2] = g
            out[o + 3] = raw[s + 1]
        elif ctype == 3:
            idx = raw[s]
            p = idx * 3
            out[o:o + 3] = palette[p:p + 3]
            out[o + 3] = trns[idx] if trns and idx < len(trns) else 255
    return img


def encode_png(img):
    """Raster to PNG bytes, RGBA, no interlacing."""
    stride = img.w * 4
    raw = bytearray()
    for y in range(img.h):
        raw.append(0)  # filter type none; logos compress fine without prediction
        raw += img.px[y * stride:(y + 1) * stride]

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))

    return (PNG_MAGIC
            + chunk(b"IHDR", struct.pack(">IIBBBBB", img.w, img.h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def load_any(data):
    """Decode any raster the environment can handle. PNG natively, rest via Pillow."""
    if data[:8] == PNG_MAGIC:
        try:
            return decode_png(data)
        except ValueError:
            if not HAVE_PIL:
                raise
    if not HAVE_PIL:
        raise ValueError(
            "only PNG is decodable without Pillow. Install Pillow, or supply the "
            "logo as a PNG or SVG.")
    import io
    pil = _PILImage.open(io.BytesIO(data)).convert("RGBA")
    return Raster(pil.width, pil.height, bytearray(pil.tobytes()))


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def has_real_alpha(img, threshold=250):
    """True when the image carries meaningful transparency, not a full opaque rect."""
    transparent = 0
    total = img.w * img.h
    for i in range(3, len(img.px), 4):
        if img.px[i] < threshold:
            transparent += 1
    return transparent > total * 0.02


def _close(a, b, tol):
    return (abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol
            and abs(a[2] - b[2]) <= tol)


def remove_background(img, tolerance=32):
    """
    Flood fill inward from the border, clearing pixels close to the corner colour.

    Deliberately conservative: it only removes background connected to the edge,
    so a white area enclosed by the mark (the counter of an O, a knockout) is
    preserved. It will not key out a photographic or gradient background, and
    reports how much it removed so the caller can judge.
    """
    corners = [img.at(0, 0), img.at(img.w - 1, 0),
               img.at(0, img.h - 1), img.at(img.w - 1, img.h - 1)]
    # Only treat as a flat background when the corners agree with each other.
    base = corners[0]
    if not all(_close(base, c, tolerance) for c in corners[1:]):
        return img, 0.0

    seen = bytearray(img.w * img.h)
    stack = []
    for x in range(img.w):
        stack.append((x, 0))
        stack.append((x, img.h - 1))
    for y in range(img.h):
        stack.append((0, y))
        stack.append((img.w - 1, y))

    cleared = 0
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= img.w or y >= img.h:
            continue
        k = y * img.w + x
        if seen[k]:
            continue
        seen[k] = 1
        px = img.at(x, y)
        if px[3] == 0:
            cleared += 1
            stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            continue
        if not _close(px, base, tolerance):
            continue
        img.set_alpha(x, y, 0)
        cleared += 1
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return img, cleared / float(img.w * img.h)


def defringe(img, tolerance=40):
    """
    Soften the halo left when a logo was flattened onto a light background.

    Pixels adjacent to transparency that are close to white get their alpha
    reduced in proportion to how close they are. Without this, a keyed logo
    shows a pale outline on the Align navy field.
    """
    w, h = img.w, img.h
    touched = 0
    for y in range(h):
        for x in range(w):
            if img.alpha(x, y) == 0:
                continue
            near_clear = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and img.alpha(nx, ny) == 0:
                    near_clear = True
                    break
            if not near_clear:
                continue
            r, g, b, a = img.at(x, y)
            lightness = (r + g + b) / 3.0
            if lightness > 255 - tolerance:
                scale = max(0.0, (255 - lightness) / float(tolerance))
                img.set_alpha(x, y, int(a * scale))
                touched += 1
    return img, touched


def trim(img, alpha_floor=8):
    """Crop transparent margins so the mark fills its box and centres predictably."""
    minx, miny, maxx, maxy = img.w, img.h, -1, -1
    for y in range(img.h):
        row = y * img.w
        for x in range(img.w):
            if img.px[(row + x) * 4 + 3] > alpha_floor:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return img, False
    if (minx, miny, maxx, maxy) == (0, 0, img.w - 1, img.h - 1):
        return img, False
    nw, nh = maxx - minx + 1, maxy - miny + 1
    out = Raster(nw, nh)
    for y in range(nh):
        src = ((y + miny) * img.w + minx) * 4
        out.px[y * nw * 4:(y + 1) * nw * 4] = img.px[src:src + nw * 4]
    return out, True


def scale_to_width(img, target_w):
    """
    Resample to a target width. Pillow does this with a proper filter; the
    stdlib path is nearest neighbour, which is only ever used to go smaller.
    """
    if img.w == target_w:
        return img
    target_h = max(1, round(img.h * target_w / img.w))
    if HAVE_PIL:
        import io
        pil = _PILImage.frombytes("RGBA", (img.w, img.h), bytes(img.px))
        pil = pil.resize((target_w, target_h), _PILImage.LANCZOS)
        return Raster(target_w, target_h, bytearray(pil.tobytes()))
    out = Raster(target_w, target_h)
    for y in range(target_h):
        sy = min(img.h - 1, y * img.h // target_h)
        for x in range(target_w):
            sx = min(img.w - 1, x * img.w // target_w)
            out.set(x, y, img.at(sx, sy))
    return out


# ---------------------------------------------------------------------------
# Legibility against the cover field
# ---------------------------------------------------------------------------

def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r, g, b):
    return (0.2126 * _srgb_to_linear(r)
            + 0.7152 * _srgb_to_linear(g)
            + 0.0722 * _srgb_to_linear(b))


def contrast_ratio(lum_a, lum_b):
    hi, lo = max(lum_a, lum_b), min(lum_a, lum_b)
    return (hi + 0.05) / (lo + 0.05)


def ink_analysis(img, background, alpha_floor=128):
    """
    How the visible mark reads against a given background colour.

    A dark logo keyed onto the navy cover field disappears, which is the most
    common way an auto-fetched mark fails in practice. This measures the mark's
    own ink rather than the whole bounding box, so transparent margins do not
    skew the result.

    Returns mean luminance of the ink, the contrast ratio against the
    background, and the share of ink pixels that individually fall below a
    readable contrast.
    """
    bg_lum = relative_luminance(*background)
    bins = 512
    hist = [0] * bins
    total = 0
    lum_sum = 0.0
    low = 0
    for i in range(0, len(img.px), 4):
        if img.px[i + 3] < alpha_floor:
            continue
        lum = relative_luminance(img.px[i], img.px[i + 1], img.px[i + 2])
        total += 1
        lum_sum += lum
        hist[min(bins - 1, int(lum * bins))] += 1
        if contrast_ratio(lum, bg_lum) < 3.0:
            low += 1
    if not total:
        return {"ink_pixels": 0, "mean_luminance": 0.0, "median_luminance": 0.0,
                "contrast": 0.0, "low_contrast_share": 1.0}

    # The headline figure is the median, not the mean. A mark that is mostly
    # dark brand colour with a light antialiased edge has a mean pulled well
    # above anything actually on the slide: measured on a real logo, the mean
    # said 6.7:1 while 62% of the ink was below 3:1. The median tracks the
    # colour a reader actually sees.
    half = total // 2
    seen = 0
    median = 0.0
    for idx, count in enumerate(hist):
        seen += count
        if seen > half:
            median = (idx + 0.5) / bins
            break

    return {
        "ink_pixels": total,
        "mean_luminance": lum_sum / total,
        "median_luminance": median,
        "contrast": contrast_ratio(median, bg_lum),
        "low_contrast_share": low / float(total),
    }
