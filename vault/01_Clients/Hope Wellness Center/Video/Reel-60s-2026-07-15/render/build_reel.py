#!/usr/bin/env python3
"""The Hope Wellness Center - 60 second vertical reel renderer.

Renders exactly 1,800 frames (60.00 s @ 30 fps, 1080x1920) following
../timeline.json and pipes them into ffmpeg (H.264, yuv420p).

Design system (from CLAUDE_VIDEO_PROMPT.md):
  - three depth planes per scene: blurred environmental plane, the exact
    illustration as the stable base, and a botanical foreground plane
  - organic transitions: breath rings, drifting leaves, ink-line wipe,
    curved path wipe, volleyball match cuts, particle converge into logo
  - Poppins primary type, Lora Italic emotional accent, brand palette
  - the supplied logo is composited untouched (uniform scale only)

Run:  python3 build_reel.py [--preview]   (preview writes sample PNGs only)
"""

import json
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- paths ----
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "out")
DERIVED = os.path.join(HERE, "derived")
os.makedirs(OUT, exist_ok=True)
os.makedirs(DERIVED, exist_ok=True)

W, H, FPS, TOTAL = 1080, 1920, 30, 1800

# safe margins from the brief
SAFE_L, SAFE_R, SAFE_T, SAFE_B = 90, 90, 140, 250

# brand palette
NAVY = (32, 64, 144)
GREEN = (112, 192, 80)
SOFTBLUE = (220, 234, 254)
WARMWHITE = (247, 250, 248)
DEEPNAVY = (24, 48, 110)

with open(os.path.join(ROOT, "timeline.json")) as fh:
    TIMELINE = json.load(fh)
SCENES = TIMELINE["scenes"]
STARTS = [s["start_frame"] for s in SCENES]          # 13 scenes
ENDS = [s["end_frame_exclusive"] for s in SCENES]

FONT_DIR = os.path.join(HERE, "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name + ".ttf"), size)


# --------------------------------------------------------------- easing ----
def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 3 * t * t - 2 * t * t * t


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t ** 3


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# -------------------------------------------------------------- helpers ----
def cover(img, tw, th):
    """Scale-to-cover + center crop."""
    w, h = img.size
    s = max(tw / w, th / h)
    img = img.resize((int(round(w * s)), int(round(h * s))), Image.LANCZOS)
    w, h = img.size
    x = (w - tw) // 2
    y = (h - th) // 2
    return img.crop((x, y, x + tw, y + th))


def make_leaf(length, width, color, alpha, angle=0.0, blur=0):
    """Simple organic leaf sprite: two quadratic arcs + a vein."""
    pad = 8
    im = Image.new("RGBA", (length + 2 * pad, width + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p0 = (pad, pad + width / 2)
    p2 = (pad + length, pad + width / 2)
    pts = []
    for i in range(25):
        t = i / 24
        cx, cy = pad + length / 2, pad
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t ** 2 * p2[1]
        pts.append((x, y))
    for i in range(25):
        t = 1 - i / 24
        cx, cy = pad + length / 2, pad + width
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t ** 2 * p2[1]
        pts.append((x, y))
    d.polygon(pts, fill=color + (alpha,))
    vein = tuple(int(c * 0.75) for c in color)
    d.line([p0, p2], fill=vein + (min(255, alpha + 25),), width=2)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def radial_grid():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return xx, yy


XX, YY = radial_grid()


def dist_from(cx, cy):
    return np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)


# a soft blue-noise-ish texture for organic dissolves
def build_noise():
    rng = np.random.default_rng(11)
    n = rng.random((H // 4, W // 4)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(18))
    a = np.asarray(im).astype(np.float32) / 255.0
    a = (a - a.min()) / (a.max() - a.min())
    return a


NOISE = build_noise()

# vertical warm-white feathering: keeps the top calm and the copy band
# readable on every scene without resorting to cards or plates
def build_vertical_light():
    y = np.arange(H, dtype=np.float32)
    top = 0.38 * smoothstep(0, 1, np.clip((560 - y) / 430.0, 0, 1))
    bot = 0.42 * smoothstep(0, 1, np.clip((y - 1230) / 430.0, 0, 1))
    return (top + bot)[:, None, None].astype(np.float32)


VERT_LIGHT = build_vertical_light()
WW = np.array(WARMWHITE, np.float32)

# -------------------------------------------------------- scene styling ----
# per-scene motion style: bg zoom travel, mid zoom travel, drift directions
STYLES = []
for i in range(13):
    rng = random.Random(100 + i)
    STYLES.append({
        "bg_z0": 1.10, "bg_z1": 1.16 if i % 2 == 0 else 1.105,
        "bg_dx": rng.choice([-26, 22, -18, 28]),
        "mid_z0": 1.005 if i % 2 == 0 else 1.05,
        "mid_z1": 1.05 if i % 2 == 0 else 1.005,
        "mid_dx": rng.choice([-14, 12, -10, 16]),
        "mid_dy": rng.choice([-12, 10, -14, 12]),
    })

MID_CY = 830  # vertical center of the illustration plane

# approximate volleyball canvas positions for the match cuts
BALL = {9: (540, 500), 10: (818, 488), 11: (688, 610)}


class Scene:
    """Pre-computed layers for one timeline entry."""

    def __init__(self, idx, spec):
        self.idx = idx
        self.spec = spec
        self.start = spec["start_frame"]
        self.end = spec["end_frame_exclusive"]
        self.dur = self.end - self.start
        self.is_logo = "00-hope" in spec["asset"]
        img = Image.open(os.path.join(ROOT, spec["asset"])).convert("RGBA")
        self.src = img
        st = STYLES[idx]
        if not self.is_logo:
            base = img.convert("RGB")
            # environmental plane: enlarged, blurred, lifted toward soft blue
            big = cover(base, int(W * 1.25), int(H * 1.25))
            big = big.filter(ImageFilter.GaussianBlur(26))
            arr = np.asarray(big).astype(np.float32)
            tint = np.array(SOFTBLUE, np.float32)
            arr = arr * 0.70 + tint * 0.11 + 255.0 * 0.19
            self.bg_big = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            # stable base plane: the untouched illustration, soft-feathered
            w0, h0 = base.size
            if abs(w0 - h0) < 8:            # square artwork
                mw = 950
            else:
                mw = 1060
            mh = int(round(mw * h0 / w0))
            # overscan so the plane can breathe without exposing edges
            ow = int(mw * 1.08)
            oh = int(round(ow * h0 / w0))
            mid = base.resize((ow, oh), Image.LANCZOS).convert("RGBA")
            mask = Image.new("L", (ow, oh), 0)
            md = ImageDraw.Draw(mask)
            inset = 56
            md.rounded_rectangle([inset, inset, ow - inset, oh - inset],
                                 radius=140, fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(48))
            mid.putalpha(mask)
            self.mid = mid
            self.mid_w = mw
            self.mid_h = mh
            # botanical foreground plane
            rng = random.Random(idx * 7 + 3)
            self.fg = []
            colmix = tuple(int(0.45 * a + 0.55 * b) for a, b in zip(NAVY, GREEN))
            leaf1 = make_leaf(360, 150, colmix, 46, angle=38, blur=9)
            leaf2 = make_leaf(300, 120, GREEN, 40, angle=205, blur=8)
            self.fg.append({"im": leaf1, "x": -70, "y": H - 400,
                            "amp": 16, "ph": rng.random() * 6.28})
            self.fg.append({"im": leaf2, "x": W - 220, "y": 210,
                            "amp": 13, "ph": rng.random() * 6.28})
            # small drifting leaves
            self.drift = []
            for k in range(6):
                c = GREEN if k % 2 else colmix
                self.drift.append({
                    "im": make_leaf(rng.randint(26, 44), rng.randint(12, 20),
                                    c, rng.randint(50, 85),
                                    angle=rng.randint(0, 359), blur=1),
                    "x0": rng.randint(40, W - 80),
                    "y0": rng.randint(240, H - 560),
                    "vx": rng.uniform(8, 30), "vy": -rng.uniform(14, 40),
                    "ph": rng.random() * 6.28,
                })
        else:
            self.logo = img  # exact logo, never redrawn

    # ------------------------------------------------------------------
    def frame(self, fl, pan=0.0):
        """Compose this scene at local frame fl -> PIL RGB."""
        if self.is_logo:
            return self._logo_frame(fl)
        st = STYLES[self.idx]
        p = ease_io(fl / max(self.dur - 1, 1))
        canvas = Image.new("RGBA", (W, H))

        # plane 1: environment
        zoom = st["bg_z0"] + (st["bg_z1"] - st["bg_z0"]) * p
        bw, bh = self.bg_big.size
        cw, ch = int(bw / zoom), int(bh / zoom)
        cx = (bw - cw) / 2 + st["bg_dx"] * (p - 0.5) * 2 + pan * 0.4
        cy = (bh - ch) / 2
        cx = min(max(cx, 0), bw - cw)
        crop = self.bg_big.crop((int(cx), int(cy), int(cx) + cw, int(cy) + ch))
        bg = np.asarray(crop.resize((W, H), Image.BILINEAR)).astype(np.float32)
        bg = bg * (1 - VERT_LIGHT) + WW * VERT_LIGHT
        canvas.paste(Image.fromarray(bg.astype(np.uint8)).convert("RGBA"))

        # breath rings on the meditation scene (and softly on balance)
        if self.idx in (1, 5):
            rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rd = ImageDraw.Draw(rings)
            cxr, cyr = (540, 810) if self.idx == 1 else (540, 790)
            cycle = 120.0  # 4 s breathing cycle
            for k in range(2):
                ph = ((fl + k * 60) % cycle) / cycle
                r = 90 + 420 * ph
                a = int(120 * (1 - ph) * (0.9 if self.idx == 1 else 0.45))
                if a > 2:
                    rd.ellipse([cxr - r, cyr - r, cxr + r, cyr + r],
                               outline=WARMWHITE + (a,), width=4)
            canvas = Image.alpha_composite(
                canvas, rings.filter(ImageFilter.GaussianBlur(3)))

        # plane 2: the illustration itself
        mz = st["mid_z0"] + (st["mid_z1"] - st["mid_z0"]) * p
        mw = int(self.mid_w * mz)
        mh = int(round(mw * self.mid.size[1] / self.mid.size[0]))
        mid = self.mid.resize((mw, mh), Image.LANCZOS)
        mx = int((W - mw) / 2 + st["mid_dx"] * (p - 0.5) * 2 + pan)
        my = int(MID_CY - mh / 2 + st["mid_dy"] * (p - 0.5) * 2)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(mid, (mx, my), mid)
        canvas = Image.alpha_composite(canvas, layer)

        # plane 3: botanical foreground
        fgl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for s in self.fg:
            dx = int(s["amp"] * math.sin(2 * math.pi * fl / 300 + s["ph"]) + pan * 1.6)
            dy = int(s["amp"] * 0.5 * math.cos(2 * math.pi * fl / 340 + s["ph"]))
            fgl.paste(s["im"], (s["x"] + dx, s["y"] + dy), s["im"])
        for s in self.drift:
            t = fl / self.dur
            x = int(s["x0"] + s["vx"] * t * 4 + 10 * math.sin(6 * t + s["ph"]))
            y = int(s["y0"] + s["vy"] * t * 4)
            fgl.paste(s["im"], (x, y), s["im"])
        canvas = Image.alpha_composite(canvas, fgl)
        return canvas.convert("RGB")

    # ------------------------------------------------------------------
    def _logo_frame(self, fl):
        """Opening (scene 0) and closing (scene 12) logo scenes."""
        opening = self.idx == 0
        # calm gradient field
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top = np.array(WARMWHITE, np.float32)
        bot = np.array(SOFTBLUE, np.float32)
        arr = np.repeat(top * (1 - g) + bot * g, W, axis=1)
        # soft radial center light
        d = dist_from(W / 2, 880) / 1200.0
        arr += (18 * np.exp(-d ** 2))[..., None]
        canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

        faint = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        l1 = make_leaf(430, 180, GREEN, 22, angle=32, blur=12)
        l2 = make_leaf(360, 150, NAVY, 16, angle=210, blur=12)
        faint.paste(l1, (-90, H - 470), l1)
        faint.paste(l2, (W - 300, 170), l2)
        canvas = Image.alpha_composite(canvas, faint)

        # exact logo, uniform scale only
        lw = 780
        lh = int(round(lw * self.logo.size[1] / self.logo.size[0]))
        settle = ease_out(fl / 60.0) if opening else ease_out(fl / 26.0)
        sc = (1.05 - 0.05 * settle) if opening else (1.04 - 0.04 * settle)
        lw2, lh2 = int(lw * sc), int(lh * sc)
        logo = self.logo.resize((lw2, lh2), Image.LANCZOS)
        lx, ly = (W - lw2) // 2, 880 - lh2 // 2

        if opening:
            # two interlocking curved masks open the mark, echoing the
            # brain-and-leaf circle; particles gather during the reveal
            rev = ease_io(fl / 55.0)
            mask = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mask)
            r = int(90 + 760 * rev)
            md.ellipse([lx + lw2 * 0.30 - r, 880 - r, lx + lw2 * 0.30 + r, 880 + r], fill=255)
            md.ellipse([lx + lw2 * 0.72 - r * 0.92, 880 - r * 0.92,
                        lx + lw2 * 0.72 + r * 0.92, 880 + r * 0.92], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(40))
            lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lo.paste(logo, (lx, ly), logo)
            a = np.asarray(lo).copy()
            a[..., 3] = (a[..., 3].astype(np.float32) *
                         (np.asarray(mask).astype(np.float32) / 255.0)).astype(np.uint8)
            canvas = Image.alpha_composite(canvas, Image.fromarray(a))
            if fl < 52:
                canvas = Image.alpha_composite(canvas, _particles(fl / 52.0,
                                               (W / 2, 880), converge=True, seed=5))
            # a single quiet breath ring after the mark settles
            if fl >= 56:
                ph = (fl - 56) / 34.0
                rr = 300 + 300 * ph
                ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ring).ellipse(
                    [W / 2 - rr, 880 - rr, W / 2 + rr, 880 + rr],
                    outline=NAVY + (int(60 * (1 - ph)),), width=3)
                canvas = Image.alpha_composite(canvas, ring.filter(ImageFilter.GaussianBlur(2)))
        else:
            # closing: center-out radial reveal as particles resolve back
            rev = ease_out(fl / 20.0)
            lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lo.paste(logo, (lx, ly), logo)
            if rev < 1.0:
                m = (smoothstep(0, 1, np.clip(
                    (1600 * rev - dist_from(W / 2, 880)) / 260.0, 0, 1)) * 255)
                a = np.asarray(lo).copy()
                a[..., 3] = (a[..., 3].astype(np.float32) * m / 255.0).astype(np.uint8)
                lo = Image.fromarray(a)
            canvas = Image.alpha_composite(canvas, lo)
        return canvas.convert("RGB")


def _particles(prog, center, converge=True, seed=7, n=54):
    """Leaves and pale dots that gather toward (or leave) a point."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        ang = rng.random() * 6.28318
        r0 = 260 + rng.random() * 780
        rr = r0 * (1 - ease_io(prog)) if converge else r0 * ease_io(prog)
        x = center[0] + rr * math.cos(ang)
        y = center[1] + rr * math.sin(ang) * 1.25
        size = rng.randint(3, 11)
        col = rng.choice([NAVY, GREEN, (168, 196, 240), WARMWHITE])
        fade = 1 - abs(prog - 0.5) * 1.6
        a = int(max(0.0, fade) * rng.randint(90, 170))
        if a <= 2:
            continue
        if i % 5 == 0:
            leaf = make_leaf(size * 3, size, col, a, angle=rng.randint(0, 359))
            layer.paste(leaf, (int(x), int(y)), leaf)
        else:
            d.ellipse([x - size / 2, y - size / 2, x + size / 2, y + size / 2],
                      fill=col + (a,))
    return layer.filter(ImageFilter.GaussianBlur(1))


# ---------------------------------------------------------- transitions ----
# boundary i sits between scene i-1 and scene i at frame STARTS[i]
TRANSITIONS = {
    1: {"kind": "rings", "center": (540, 820), "pre": 8, "post": 18},
    2: {"kind": "rings_leaves", "center": (540, 830), "pre": 6, "post": 18},
    3: {"kind": "dots", "pre": 6, "post": 18},
    4: {"kind": "ink", "pre": 6, "post": 18},
    5: {"kind": "leafwipe", "frm": "right", "pre": 6, "post": 18},
    6: {"kind": "leafdrift", "pre": 6, "post": 18},
    7: {"kind": "pathwipe", "pre": 6, "post": 18},
    8: {"kind": "pancross", "pre": 8, "post": 16},
    9: {"kind": "leafwipe", "frm": "left", "pre": 6, "post": 18},
    10: {"kind": "ballcut", "center": BALL[10], "pre": 5, "post": 9},
    11: {"kind": "ballcut", "center": BALL[11], "orbit": True, "pre": 4, "post": 8},
    12: {"kind": "converge", "center": (540, 880), "pre": 4, "post": 8},
}


def transition_mask(tr, prog):
    """Grayscale float mask (H,W): 0 -> scene A, 1 -> scene B."""
    k = tr["kind"]
    if k in ("rings", "rings_leaves"):
        cx, cy = tr["center"]
        rmax = 2300.0
        r = rmax * ease_io(prog)
        base = smoothstep(0, 1, np.clip((r - dist_from(cx, cy)) / 240.0, 0, 1))
        ripple = 0.10 * np.sin(dist_from(cx, cy) / 46.0 - prog * 16.0)
        return np.clip(base + ripple * base * (1 - base) * 4, 0, 1)
    if k == "dots":
        return smoothstep(0, 1, np.clip((prog * 1.25 - NOISE) / 0.16, 0, 1))
    if k == "ink":
        edge = -140 + (W + 320) * ease_io(prog)
        wav = 46 * np.sin(YY / 150.0 + prog * 5.0)
        return smoothstep(0, 1, np.clip((edge + wav - XX) / 110.0, 0, 1))
    if k == "leafwipe":
        sgn = 1.0 if tr.get("frm") == "left" else -1.0
        x0 = (-260 if sgn > 0 else W + 260) - sgn * 40
        edge = x0 + sgn * (W + 560) * ease_io(prog)
        wav = 70 * np.sin(YY / 210.0 + prog * 4.0) * np.sin(YY / 57.0)
        rel = (edge + wav - XX) * sgn
        return smoothstep(0, 1, np.clip(rel / 150.0, 0, 1))
    if k == "leafdrift":
        return smoothstep(0, 1, np.clip((prog * 1.3 - NOISE * 1.05) / 0.22, 0, 1))
    if k == "pathwipe":
        r = 3050.0 * ease_io(prog)
        return smoothstep(0, 1, np.clip((r - dist_from(-180, H + 160)) / 300.0, 0, 1))
    if k == "pancross":
        return np.full((H, W), ease_io(prog), np.float32)
    if k == "ballcut":
        cx, cy = tr["center"]
        r = 2350.0 * ease_in(prog) if prog < 0.5 else 2350.0 * ease_io(prog)
        return smoothstep(0, 1, np.clip((r - dist_from(cx, cy)) / 90.0, 0, 1))
    if k == "converge":
        r = 2300.0 * ease_io(prog)
        cx, cy = tr["center"]
        return smoothstep(0, 1, np.clip((r - dist_from(cx, cy)) / 220.0, 0, 1))
    raise ValueError(k)


def transition_fx(img, tr, prog, fabs):
    """Object overlays that motivate each transition."""
    k = tr["kind"]
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    fade = math.sin(min(max(prog, 0), 1) * math.pi)
    if k in ("rings", "rings_leaves"):
        cx, cy = tr["center"]
        for kk in range(3):
            r = (2300 * ease_io(prog)) * (0.72 + 0.14 * kk)
            a = int(70 * fade)
            if 40 < r < 2400 and a > 2:
                d.ellipse([cx - r, cy - r, cx + r, cy + r],
                          outline=WARMWHITE + (a,), width=4)
        if k == "rings_leaves":
            rng = random.Random(21)
            for i in range(9):
                ang = rng.random() * 6.283
                rr = 2300 * ease_io(prog) * (0.55 + 0.4 * rng.random())
                x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 1.3
                lf = make_leaf(rng.randint(24, 42), rng.randint(11, 18), GREEN,
                               int(150 * fade), angle=rng.randint(0, 359))
                over.paste(lf, (int(x), int(y)), lf)
    elif k == "dots":
        rng = random.Random(31)
        for i in range(14):
            x = rng.randint(120, W - 120)
            y = rng.randint(320, H - 620) - int(120 * prog)
            s = rng.randint(4, 9)
            a = int(120 * fade)
            d.ellipse([x - s, y - s, x + s, y + s], fill=NAVY + (a,))
    elif k == "ink":
        edge = -140 + (W + 320) * ease_io(prog)
        pts = [(edge + 46 * math.sin(y / 150.0 + prog * 5.0), y)
               for y in range(0, H + 1, 24)]
        d.line(pts, fill=DEEPNAVY + (int(200 * fade),), width=5, joint="curve")
    elif k == "leafwipe":
        sgn = 1.0 if tr.get("frm") == "left" else -1.0
        x0 = (-260 if sgn > 0 else W + 260)
        edge = x0 + sgn * (W + 560) * ease_io(prog)
        rng = random.Random(41)
        for i in range(4):
            L = rng.randint(340, 520)
            lf = make_leaf(L, int(L * 0.42), GREEN if i % 2 else
                           tuple(int(0.5 * a + 0.5 * b) for a, b in zip(NAVY, GREEN)),
                           int(120 * fade), angle=rng.randint(-30, 30) + (0 if sgn > 0 else 180),
                           blur=6)
            over.paste(lf, (int(edge - sgn * (120 + i * 90) - L / 2),
                            int(i * H / 4 + 60 * math.sin(prog * 6 + i))), lf)
    elif k == "leafdrift":
        rng = random.Random(51)
        for i in range(12):
            x = rng.randint(40, W - 80) + int(70 * prog * (1 if i % 2 else -1))
            y = rng.randint(200, H - 400) - int(190 * prog)
            lf = make_leaf(rng.randint(26, 46), rng.randint(12, 20), GREEN,
                           int(140 * fade), angle=rng.randint(0, 359))
            over.paste(lf, (x, y), lf)
    elif k == "pathwipe":
        r = 3050.0 * ease_io(prog)
        a = int(90 * fade)
        if a > 2:
            d.arc([-180 - r, H + 160 - r, -180 + r, H + 160 + r],
                  start=270, end=360, fill=WARMWHITE + (a,), width=6)
    elif k == "converge":
        over = Image.alpha_composite(over, _particles(prog, tr["center"],
                                                      converge=True, seed=9, n=70))
    if k == "ballcut":
        cx, cy = tr["center"]
        r = 90 + 60 * fade
        a = int(60 * fade)
        if a > 2:
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=WARMWHITE + (a,), width=3)
    over = over.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


# ----------------------------------------------------------- typography ----
def fit_font(name, size, text, max_w):
    while size > 24:
        f = font(name, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return font(name, size)


def render_line(text, fname, size, color, tracking=0.0, glow=True,
                max_w=W - SAFE_L - SAFE_R - 20):
    """Rasterize one line (optionally letter-spaced) with a soft glow."""
    f = fit_font(fname, size, text, max_w - tracking * max(len(text) - 1, 0))
    if tracking:
        widths = [f.getlength(ch) for ch in text]
        tw = int(sum(widths) + tracking * (len(text) - 1))
    else:
        tw = int(f.getlength(text))
    asc, desc = f.getmetrics()
    th = asc + desc
    pad = 90
    im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    if glow:
        # soft warm light so copy stays readable over artwork (no card shapes)
        gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse(
            [pad - 70, pad - 26, pad + tw + 70, pad + th + 30],
            fill=WARMWHITE + (165,))
        gl = gl.filter(ImageFilter.GaussianBlur(46))
        im = Image.alpha_composite(im, gl)
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, wch in zip(text, widths):
            d.text((x, pad), ch, font=f, fill=color + (255,))
            x += wch + tracking
    else:
        d.text((pad, pad), text, font=f, fill=color + (255,))
    return im, tw, th, pad


class TextBlock:
    def __init__(self, f0, f1, lines, hold_out=False, glow=True):
        """lines: list of (text, fontname, size, color, y_center, tracking)."""
        self.f0, self.f1 = f0, f1
        self.hold_out = hold_out
        self.lines = []
        for (txt, fn, sz, col, yc, trk) in lines:
            im, tw, th, pad = render_line(txt, fn, sz, col, tracking=trk, glow=glow)
            x = (W - tw) // 2 - pad
            y = int(yc - th / 2) - pad
            self.lines.append({"im": im, "x": x, "y": y, "h": im.size[1], "pad": pad})

    def draw(self, canvas, f):
        if not (self.f0 <= f < self.f1):
            return canvas
        rel = f - self.f0
        out_len = 14
        canvas = canvas.convert("RGBA")
        for i, ln in enumerate(self.lines):
            t_in = ease_out((rel - i * 7) / 20.0)
            if t_in <= 0:
                continue
            a = t_in
            dy = int((1 - t_in) * 34)
            if not self.hold_out:
                t_out = (self.f1 - f) / out_len
                if t_out < 1:
                    a *= max(t_out, 0.0)
                    dy -= int((1 - max(t_out, 0.0)) * 20)
            if a <= 0.01:
                continue
            im = ln["im"]
            # masked reveal: the line rises behind a static soft clip band
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lay.paste(im, (ln["x"], ln["y"] + dy), im)
            band = Image.new("L", (W, H), 0)
            bd = ImageDraw.Draw(band)
            bd.rectangle([0, ln["y"] - 10, W, ln["y"] + ln["h"] + 6], fill=255)
            band = band.filter(ImageFilter.GaussianBlur(8))
            arr = np.asarray(lay).copy()
            arr[..., 3] = (arr[..., 3].astype(np.float32) *
                           (np.asarray(band).astype(np.float32) / 255.0) *
                           a).astype(np.uint8)
            canvas = Image.alpha_composite(canvas, Image.fromarray(arr))
        return canvas.convert("RGB")


def build_text_blocks():
    P_SB, P_MD, P_RG, LORA = ("Poppins-SemiBold", "Poppins-Medium",
                              "Poppins-Regular", "Lora-Italic")
    blocks = [
        TextBlock(12, 90, [("A gentler way forward", LORA, 60, DEEPNAVY, 1185, 0)],
                  glow=False),
        TextBlock(104, 388, [
            ("Breathe.", P_SB, 62, DEEPNAVY, 1392, 0),
            ("Begin where you are.", P_MD, 44, DEEPNAVY, 1478, 0)]),
        TextBlock(404, 688, [("Care that makes room for you.", P_SB, 50, DEEPNAVY, 1430, 0)]),
        TextBlock(704, 988, [("Balance. Rest. Reconnect.", P_SB, 54, DEEPNAVY, 1430, 0)]),
        TextBlock(1004, 1288, [("Small steps still move you forward.", P_SB, 47, DEEPNAVY, 1430, 0)]),
        TextBlock(1304, 1588, [("Personalized mental health care", P_SB, 49, DEEPNAVY, 1430, 0)]),
        TextBlock(1600, 1678, [
            ("Telehealth across", P_MD, 40, DEEPNAVY, 1372, 0),
            ("MA • RI • NY • CO • AZ", P_SB, 52, DEEPNAVY, 1448, 6)]),
        TextBlock(1700, 1800, [
            ("Helping you find comfort,", LORA, 50, DEEPNAVY, 1150, 0),
            ("peace of mind, and hope.", LORA, 50, DEEPNAVY, 1226, 0),
            ("thehopewellnesscenter.com", P_SB, 44, NAVY, 1372, 1)],
            hold_out=True, glow=False),
    ]
    return blocks


# -------------------------------------------------------------- grading ----
def build_vignette():
    d = dist_from(W / 2, H / 2)
    v = 1.0 - 0.10 * smoothstep(0.55, 1.25, d / (0.5 * math.hypot(W, H)))
    return v[..., None].astype(np.float32)


VIGNETTE = build_vignette()


def grade(arr):
    a = arr.astype(np.float32) * VIGNETTE
    a = a * 0.995 + 4.0  # gentle warm lift
    return np.clip(a, 0, 255).astype(np.uint8)


# ------------------------------------------------------------ main loop ----
def scene_at(f):
    for i, s in enumerate(SCENES):
        if s["start_frame"] <= f < s["end_frame_exclusive"]:
            return i
    return len(SCENES) - 1


def compose_frame(f, scenes, blocks):
    idx = scene_at(f)
    # active transition window?
    active = None
    for b, tr in TRANSITIONS.items():
        fb = STARTS[b]
        if fb - tr["pre"] <= f < fb + tr["post"]:
            active = (b, tr, (f - (fb - tr["pre"])) / (tr["pre"] + tr["post"]))
            break
    if active is None:
        img = scenes[idx].frame(f - scenes[idx].start)
    else:
        b, tr, prog = active
        sA, sB = scenes[b - 1], scenes[b]
        panA = panB = 0.0
        if tr["kind"] == "pancross":
            panA = -70.0 * ease_io(prog)
            panB = 70.0 * (1 - ease_io(prog))
        if tr.get("orbit"):
            panB = 26.0 * math.sin(math.pi * (1 - prog))
        fA = min(f - sA.start, sA.dur - 1)
        fB = max(f - sB.start, 0)
        a = np.asarray(sA.frame(fA, pan=panA), np.float32)
        bimg = np.asarray(sB.frame(fB, pan=panB), np.float32)
        m = transition_mask(tr, prog)[..., None]
        img = Image.fromarray(np.clip(a * (1 - m) + bimg * m, 0, 255).astype(np.uint8))
        img = transition_fx(img, tr, prog, f)
    for blk in blocks:
        img = blk.draw(img, f)
    return grade(np.asarray(img))


def save_derived_samples(scenes):
    """Retain a few generated derivative masks/sprites beside the source."""
    scenes[1].mid.split()[3].save(os.path.join(DERIVED, "midplane-feather-mask.png"))
    Image.fromarray((NOISE * 255).astype(np.uint8)).save(
        os.path.join(DERIVED, "organic-dissolve-noise.png"))
    make_leaf(360, 150, GREEN, 200, angle=30).save(
        os.path.join(DERIVED, "leaf-sprite-sample.png"))
    m = transition_mask(TRANSITIONS[1], 0.5)
    Image.fromarray((m * 255).astype(np.uint8)).save(
        os.path.join(DERIVED, "breath-ring-mask-sample.png"))


def main():
    preview = "--preview" in sys.argv
    scenes = [Scene(i, s) for i, s in enumerate(SCENES)]
    blocks = build_text_blocks()
    save_derived_samples(scenes)

    if preview:
        picks = [0, 30, 70, 96, 160, 300, 400, 470, 545, 620, 760, 910, 1000,
                 1060, 1150, 1360, 1444, 1520, 1592, 1640, 1684, 1710, 1780]
        for f in picks:
            Image.fromarray(compose_frame(f, scenes, blocks)).save(
                os.path.join(OUT, f"preview_{f:04d}.png"))
        print("previews written to", OUT)
        return

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    vpath = os.path.join(OUT, "reel-video.mp4")
    cmd = [ff, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", vpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time
    t0 = time.time()
    for f in range(TOTAL):
        proc.stdin.write(compose_frame(f, scenes, blocks).tobytes())
        if f % 150 == 0:
            el = time.time() - t0
            print(f"frame {f}/{TOTAL}  ({el:.0f}s elapsed)", flush=True)
    proc.stdin.close()
    proc.wait()
    print("video written:", vpath, "rc:", proc.returncode)


if __name__ == "__main__":
    main()
