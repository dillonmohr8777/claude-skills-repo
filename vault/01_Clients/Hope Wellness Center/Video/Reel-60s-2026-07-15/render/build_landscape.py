#!/usr/bin/env python3
"""The Hope Wellness Center - 60 second LANDSCAPE brand film (1920x1080).

Cooler cut: the supplied illustrations are background-removed to clean figure
cutouts (see make_cutouts.py) and re-composited into a designed, parallaxed
brand environment — layered gradient depth, soft botanical planes, drifting
light and pollen, editorial split-screen typography, and object-motivated
transitions (particle handoffs, light sweeps, volleyball match cuts).

Timeline, durations and copy schedule match the approved 60 s structure, so the
existing score (reel-audio.wav, breath swells on the scene changes) still syncs.

Run:  python3 build_landscape.py [--preview]
"""
import json
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CUTS = os.path.join(HERE, "cutouts")
OUT = os.path.join(HERE, "out")
FONT_DIR = os.path.join(HERE, "fonts")
os.makedirs(OUT, exist_ok=True)

W, H, FPS, TOTAL = 1920, 1080, 30, 1800
OW, OH = 2200, 1240                     # oversized env canvas for camera drift
MX, MY = (OW - W) // 2, (OH - H) // 2   # base crop origin
SAFE = 96

# brand palette
NAVY = (32, 64, 144)
GREEN = (112, 192, 80)
SOFTBLUE = (220, 234, 254)
WARMWHITE = (247, 250, 248)
DEEPNAVY = (24, 48, 110)
INK = (22, 40, 92)

with open(os.path.join(ROOT, "timeline.json")) as fh:
    SCENES_T = json.load(fh)["scenes"]
STARTS = [s["start_frame"] for s in SCENES_T]
ENDS = [s["end_frame_exclusive"] for s in SCENES_T]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name + ".ttf"), size)


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 3 * t * t - 2 * t * t * t


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t ** 3


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


# ------------------------------------------------------------ botanicals ----
def make_leaf(length, width, color, alpha, angle=0.0, blur=0):
    pad = 10
    im = Image.new("RGBA", (length + 2 * pad, width + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p0 = (pad, pad + width / 2)
    p2 = (pad + length, pad + width / 2)
    pts = []
    for i in range(26):
        t = i / 25
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * (pad + length / 2) + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * pad + t ** 2 * p2[1]
        pts.append((x, y))
    for i in range(26):
        t = 1 - i / 25
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * (pad + length / 2) + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * (pad + width) + t ** 2 * p2[1]
        pts.append((x, y))
    d.polygon(pts, fill=color + (alpha,))
    vein = tuple(int(c * 0.72) for c in color)
    d.line([p0, p2], fill=vein + (min(255, alpha + 20),), width=2)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def make_ball(r=52):
    """Minimalist volleyball sprite (brand navy seams on warm white)."""
    im = Image.new("RGBA", (2 * r + 8, 2 * r + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = r + 4
    d.ellipse([4, 4, 4 + 2 * r, 4 + 2 * r], fill=WARMWHITE + (255,),
              outline=NAVY + (255,), width=4)
    for a0 in (0, 120, 240):
        a = math.radians(a0)
        d.arc([c - r * 1.6 + r * math.cos(a), c - r * 1.6 + r * math.sin(a),
               c + r * 0.6 + r * math.cos(a), c + r * 0.6 + r * math.sin(a)],
              0, 360, fill=NAVY + (180,), width=3)
    d.ellipse([c - 7, c - 7, c + 7, c + 7], fill=NAVY + (60,))
    return im


NOISE = None
def build_noise():
    rng = np.random.default_rng(7)
    n = rng.random((OH // 5, OW // 5)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((OW, OH), Image.BILINEAR)
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(20))).astype(np.float32) / 255
    return (a - a.min()) / (a.max() - a.min())
NOISE = build_noise()

XX, YY = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))


# ------------------------------------------------------------- grade prep ----
def build_vignette():
    d = np.sqrt((XX[MY:MY + H, MX:MX + W] - W / 2 - MX) ** 2 +
                (YY[MY:MY + H, MX:MX + W] - H / 2 - MY) ** 2)
    dn = d / (0.5 * math.hypot(W, H))
    v = 1.0 - 0.16 * np.clip((dn - 0.55) / 0.7, 0, 1) ** 2
    return v[..., None].astype(np.float32)
VIGNETTE = build_vignette()

GRAIN = (np.random.default_rng(3).standard_normal((H, W, 1)).astype(np.float32) * 2.4)


def grade(arr):
    a = arr.astype(np.float32) * VIGNETTE + GRAIN
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------- environment -----
def env_base(progress, seed, glow_x=0.5):
    """Oversized gradient + radial glow + far blurred brand blobs."""
    top = lerp((228, 238, 250), WARMWHITE, ease_io(progress))
    bot = lerp((196, 214, 244), (214, 230, 250), ease_io(progress))
    g = np.linspace(0, 1, OH, dtype=np.float32)[:, None, None]
    arr = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    arr = np.repeat(arr, OW, axis=1)
    # warm radial glow behind the subject (halos the figure, calms the copy side)
    gx, gy = OW * glow_x, OH * 0.46
    d2 = (XX - gx) ** 2 + (YY - gy) ** 2
    glow = np.exp(-d2 / (2 * (OW * 0.34) ** 2))
    warm = np.array(lerp(SOFTBLUE, WARMWHITE, 0.5 + 0.4 * progress), np.float32)
    arr += (glow[..., None] * (warm - arr) * 0.35)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    # far blurred brand blobs
    rng = random.Random(seed)
    far = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    fd = ImageDraw.Draw(far)
    for _ in range(3):
        cx, cy = rng.randint(200, OW - 200), rng.randint(200, OH - 200)
        rr = rng.randint(320, 520)
        col = rng.choice([NAVY, GREEN, (150, 180, 230)])
        fd.ellipse([cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7],
                   fill=col + (14,))
    far = far.filter(ImageFilter.GaussianBlur(70))
    im = Image.alpha_composite(im, far)
    return im


def env_mid(seed, text_side="L"):
    """Oversized transparent plane of big soft botanical silhouettes, with a
    larger cluster biased to the copy side to balance the negative space."""
    rng = random.Random(seed * 3 + 1)
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    for _ in range(5):
        L = rng.randint(360, 620)
        col = rng.choice([GREEN, NAVY, (120, 160, 210)])
        leaf = make_leaf(L, int(L * 0.42), col, rng.randint(20, 34),
                         angle=rng.randint(0, 359), blur=10)
        x = rng.choice([rng.randint(-120, 260), rng.randint(OW - 500, OW - 120)])
        y = rng.randint(-80, OH - 200)
        im.alpha_composite(leaf, (x, y))
    # soft botanical accent behind the copy third
    cx = OW * (0.24 if text_side == "L" else 0.76 if text_side == "R" else 0.5)
    for k in range(3):
        L = rng.randint(300, 460)
        leaf = make_leaf(L, int(L * 0.4), GREEN if k % 2 else NAVY,
                         rng.randint(16, 26), angle=rng.randint(-40, 40) + 200,
                         blur=14)
        im.alpha_composite(leaf, (int(cx - L / 2 + rng.randint(-60, 60)),
                                  int(OH * 0.30 + k * 150)))
    return im


# --------------------------------------------------------------- figures ----
NAMES = [
    "01-meditation-and-breathing", "02-self-compassion",
    "03-reflection-and-journaling", "04-gentle-stretch",
    "05-balance-and-mindfulness", "06-rest-and-recovery",
    "07-movement-and-mood", "08-daily-routine", "09-active-wellness",
    "10-focus-and-drive", "11-playful-confidence",
]

# Each line of copy spans a PAIR of scenes (10 s), so the figure holds one side
# for the whole line and the copy lives opposite it; the side flips per pair.
LAYOUT = {1: "R", 2: "R", 3: "L", 4: "L", 5: "R", 6: "R",
          7: "L", 8: "L", 9: "R", 10: "R", 11: "R"}
ANCHOR_X = {"R": 1380, "L": 540, "C": 960}
GLOW_X = {"R": 0.66, "L": 0.34, "C": 0.5}
TEXT_SIDE = {"R": "L", "L": "R", "C": "C"}


def load_figure(name):
    im = Image.open(os.path.join(CUTS, name + ".png")).convert("RGBA")
    bb = im.getbbox()
    im = im.crop(bb)
    return im


class Scene:
    def __init__(self, idx):
        self.idx = idx
        self.start = STARTS[idx]
        self.end = ENDS[idx]
        self.dur = self.end - self.start
        self.mid_prog = (self.start + self.dur / 2) / TOTAL
        self.is_logo = idx in (0, 12)
        self.layout = LAYOUT.get(idx, "C")
        tside = TEXT_SIDE[self.layout]
        self.env = env_base(self.mid_prog, seed=100 + idx,
                            glow_x=GLOW_X[self.layout])
        self.mid = env_mid(seed=100 + idx, text_side=tside)
        if self.is_logo:
            self.logo = Image.open(os.path.join(ROOT, "assets",
                                    "00-hope-wellness-logo.png")).convert("RGBA")
            return
        fig = load_figure(NAMES[idx - 1])
        fw, fh = fig.size
        tall = fh >= 1.15 * fw
        target_h = int(H * (0.82 if tall else 0.66))
        sc = target_h / fh
        self.fig = fig.resize((max(1, int(fw * sc)), target_h), Image.LANCZOS)
        self.fw, self.fh = self.fig.size
        # contact shadow sized to figure footprint
        shw = int(self.fw * 0.92)
        shh = int(self.fw * 0.20)
        sh = Image.new("RGBA", (shw, shh), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([0, 0, shw, shh], fill=INK + (70,))
        self.shadow = sh.filter(ImageFilter.GaussianBlur(18))
        # foreground drifting leaves for this scene
        rng = random.Random(idx * 5 + 2)
        self.fg_leaves = []
        for _ in range(5):
            c = GREEN if rng.random() < 0.5 else NAVY
            self.fg_leaves.append({
                "im": make_leaf(rng.randint(50, 120), rng.randint(22, 48), c,
                                rng.randint(60, 120), angle=rng.randint(0, 359),
                                blur=2),
                "x0": rng.uniform(0, W), "y0": rng.uniform(H * 0.15, H * 0.95),
                "vx": rng.uniform(-24, 30), "vy": rng.uniform(-16, 12),
                "ph": rng.random() * 6.28,
            })

    # ------------------------------------------------------------------
    def frame(self, fl, cam=0.0):
        p = fl / max(self.dur - 1, 1)
        # camera drift: far slow, mid faster (parallax)
        off_far = int(10 * math.sin(math.pi * p) + cam * 0.5)
        off_mid = int(26 * ease_io(p) - 13 + cam)
        base = self.env.crop((MX + off_far, MY, MX + off_far + W, MY + H)).copy()
        midc = self.mid.crop((MX + off_mid, MY - 6, MX + off_mid + W, MY - 6 + H))
        base = Image.alpha_composite(base, midc)

        if self.is_logo:
            return self._logo(base, fl).convert("RGB")

        # figure entrance: rise + settle + gentle float
        ent = ease_out(fl / 22.0)
        floaty = 6 * math.sin(2 * math.pi * (fl / 150.0) + self.idx)
        breath = 1.0 + 0.012 * math.sin(2 * math.pi * (fl / 120.0))
        fw = int(self.fw * breath)
        fh = int(self.fh * breath)
        fig = self.fig.resize((fw, fh), Image.LANCZOS) if breath != 1.0 else self.fig
        ax = ANCHOR_X[self.layout] + int(cam * 1.4)
        base_y = int(H * 0.965)
        fx = int(ax - fw / 2)
        fy = int(base_y - fh - (1 - ent) * 46 + floaty)
        # shadow
        shx = int(ax - self.shadow.size[0] / 2)
        shy = int(base_y - self.shadow.size[1] / 2 - 6 + floaty * 0.3)
        sh = self.shadow.copy()
        sh.putalpha(sh.getchannel("A").point(lambda v: int(v * (0.5 + 0.5 * ent))))
        base.alpha_composite(sh, (shx, shy))
        # figure with entrance fade
        if ent < 1.0:
            fig = fig.copy()
            fig.putalpha(fig.getchannel("A").point(lambda v: int(v * ent)))
        base.alpha_composite(fig, (fx, fy))

        # foreground drifting leaves (higher parallax)
        fgl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for s in self.fg_leaves:
            t = fl / FPS
            x = (s["x0"] + s["vx"] * t + 14 * math.sin(0.7 * t + s["ph"])) % (W + 240) - 120
            y = s["y0"] + s["vy"] * t + 10 * math.cos(0.6 * t + s["ph"])
            fgl.alpha_composite(s["im"], (int(x + cam * 2.1), int(y)))
        base = Image.alpha_composite(base, fgl)
        return base.convert("RGB")

    # ------------------------------------------------------------------
    def _logo(self, base, fl):
        opening = self.idx == 0
        lw = 860
        lh = int(round(lw * self.logo.size[1] / self.logo.size[0]))
        settle = ease_out(fl / (58.0 if opening else 26.0))
        sc = (1.06 - 0.06 * settle) if opening else (1.04 - 0.04 * settle)
        lw2, lh2 = int(lw * sc), int(lh * sc)
        logo = self.logo.resize((lw2, lh2), Image.LANCZOS)
        cy_frac = 0.42 if opening else 0.34
        lx, ly = (W - lw2) // 2, int(H * cy_frac) - lh2 // 2
        if opening:
            rev = ease_io(fl / 52.0)
            mask = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mask)
            r = int(70 + 720 * rev)
            md.ellipse([lx + lw2 * 0.28 - r, ly + lh2 / 2 - r,
                        lx + lw2 * 0.28 + r, ly + lh2 / 2 + r], fill=255)
            md.ellipse([lx + lw2 * 0.66 - r * 0.9, ly + lh2 / 2 - r * 0.9,
                        lx + lw2 * 0.66 + r * 0.9, ly + lh2 / 2 + r * 0.9], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(46))
            lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lo.alpha_composite(logo, (lx, ly))
            a = np.asarray(lo).copy()
            a[..., 3] = (a[..., 3] * (np.asarray(mask) / 255.0)).astype(np.uint8)
            base = Image.alpha_composite(base, Image.fromarray(a))
            if fl < 50:
                base = Image.alpha_composite(base, particles(fl / 50.0,
                                    (W / 2, ly + lh2 / 2), converge=True, seed=5, n=64))
        else:
            rev = ease_out(fl / 18.0)
            lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lo.alpha_composite(logo, (lx, ly))
            if rev < 1.0:
                dd = np.sqrt((XX[MY:MY + H, MX:MX + W] - W / 2 - MX) ** 2 +
                             (YY[MY:MY + H, MX:MX + W] - (ly + lh2 / 2) - MY) ** 2)
                m = np.clip((1500 * rev - dd) / 240.0, 0, 1)
                a = np.asarray(lo).copy()
                a[..., 3] = (a[..., 3] * m).astype(np.uint8)
                lo = Image.fromarray(a)
            base = Image.alpha_composite(base, lo)
        return base


def particles(prog, center, converge=True, seed=7, n=60):
    rng = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        ang = rng.random() * 6.28318
        r0 = 220 + rng.random() * 900
        rr = r0 * (1 - ease_io(prog)) if converge else r0 * ease_io(prog)
        x = center[0] + rr * math.cos(ang)
        y = center[1] + rr * math.sin(ang) * 0.8
        size = rng.randint(3, 10)
        col = rng.choice([NAVY, GREEN, (170, 198, 240), WARMWHITE])
        fade = 1 - abs(prog - 0.5) * 1.7
        a = int(max(0.0, fade) * rng.randint(90, 175))
        if a <= 2:
            continue
        if i % 5 == 0:
            leaf = make_leaf(size * 3, size, col, a, angle=rng.randint(0, 359))
            layer.alpha_composite(leaf, (int(x), int(y)))
        else:
            d.ellipse([x - size / 2, y - size / 2, x + size / 2, y + size / 2],
                      fill=col + (a,))
    return layer.filter(ImageFilter.GaussianBlur(0.8))


def light_sweep(prog, warm=True):
    """Diagonal soft light band crossing the frame."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xc = -400 + (W + 800) * ease_io(prog)
    band = np.clip(1 - np.abs((np.arange(W) - xc) / 240.0), 0, 1) ** 2
    a = (band * 90 * math.sin(min(max(prog, 0), 1) * math.pi)).astype(np.uint8)
    col = np.array(WARMWHITE if warm else SOFTBLUE, np.uint8)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., :3] = col
    arr[..., 3] = np.tile(a, (H, 1))
    return Image.alpha_composite(layer, Image.fromarray(arr, "RGBA"))


# ----------------------------------------------------------- typography -----
def fit_font(name, size, text, max_w):
    while size > 26:
        f = font(name, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return font(name, size)


def render_line(text, fname, size, color, tracking=0.0, max_w=760):
    f = fit_font(fname, size, text, max_w - tracking * max(len(text) - 1, 0))
    widths = [f.getlength(ch) for ch in text]
    tw = int(sum(widths) + tracking * (len(text) - 1))
    asc, desc = f.getmetrics()
    th = asc + desc
    im = Image.new("RGBA", (tw + 8, th + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 4
    for ch, wch in zip(text, widths):
        d.text((x, 4), ch, font=f, fill=color + (255,))
        x += wch + tracking
    return im, tw, th


class TextBlock:
    """Editorial type anchored in the empty third; masked line reveals."""
    def __init__(self, f0, f1, side, lines, hold_out=False, cy=None):
        self.f0, self.f1, self.side = f0, f1, side
        self.hold_out = hold_out
        cx = {"L": SAFE + 380, "R": W - SAFE - 380, "C": W / 2}[side]
        total_h = sum(sz for (_, _, sz, _, _) in lines) + 24 * (len(lines) - 1)
        y = (cy if cy is not None else H / 2) - total_h / 2
        self.items = []
        for (txt, fn, sz, col, trk) in lines:
            im, tw, th = render_line(txt, fn, sz, col, tracking=trk)
            self.items.append({"im": im, "x": int(cx - tw / 2), "y": int(y),
                               "h": th, "w": tw})
            y += sz + 24

    def draw(self, canvas, f):
        if not (self.f0 <= f < self.f1):
            return canvas
        rel = f - self.f0
        canvas = canvas.convert("RGBA")
        for i, it in enumerate(self.items):
            t_in = ease_out((rel - i * 6) / 18.0)
            if t_in <= 0:
                continue
            a = t_in
            dy = int((1 - t_in) * 26)
            if not self.hold_out:
                t_out = (self.f1 - f) / 12.0
                if t_out < 1:
                    a *= max(t_out, 0.0)
            if a <= 0.02:
                continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lay.alpha_composite(it["im"], (it["x"], it["y"] + dy))
            band = Image.new("L", (W, H), 0)
            ImageDraw.Draw(band).rectangle(
                [0, it["y"] - 8, W, it["y"] + it["h"] + 6], fill=255)
            band = band.filter(ImageFilter.GaussianBlur(6))
            arr = np.asarray(lay).copy()
            arr[..., 3] = (arr[..., 3] * (np.asarray(band) / 255.0) * a).astype(np.uint8)
            canvas = Image.alpha_composite(canvas, Image.fromarray(arr))
        return canvas.convert("RGB")


def build_text():
    SB, MD, RG, LO = ("Poppins-SemiBold", "Poppins-Medium", "Poppins-Regular",
                      "Lora-Italic")
    # copy side = opposite the figure for that pair of scenes
    return [
        TextBlock(14, 90, "C", [("A gentler way forward", LO, 74, DEEPNAVY, 0)],
                  cy=H * 0.80),
        TextBlock(104, 388, TEXT_SIDE[LAYOUT[1]], [       # scenes 1-2 fig R
            ("Breathe.", SB, 92, DEEPNAVY, 0),
            ("Begin where you are.", MD, 46, DEEPNAVY, 0)]),
        TextBlock(404, 688, TEXT_SIDE[LAYOUT[3]], [       # scenes 3-4 fig L
            ("Care that makes", SB, 64, DEEPNAVY, 0),
            ("room for you.", SB, 64, DEEPNAVY, 0)]),
        TextBlock(704, 988, TEXT_SIDE[LAYOUT[5]], [       # scenes 5-6 fig R
            ("Balance.", SB, 72, DEEPNAVY, 0),
            ("Rest. Reconnect.", SB, 56, DEEPNAVY, 0)]),
        TextBlock(1004, 1288, TEXT_SIDE[LAYOUT[7]], [     # scenes 7-8 fig L
            ("Small steps still", SB, 60, DEEPNAVY, 0),
            ("move you forward.", SB, 60, DEEPNAVY, 0)]),
        TextBlock(1304, 1588, TEXT_SIDE[LAYOUT[9]], [     # scenes 9-10 fig R
            ("Personalized", SB, 66, DEEPNAVY, 0),
            ("mental health care", SB, 66, DEEPNAVY, 0)]),
        TextBlock(1600, 1678, TEXT_SIDE[LAYOUT[11]], [    # scene 11 fig R
            ("Telehealth across", MD, 44, DEEPNAVY, 0),
            ("MA • RI • NY", SB, 58, DEEPNAVY, 4),
            ("CO • AZ", SB, 58, DEEPNAVY, 4)]),
        TextBlock(1690, 1800, "C", [                      # closing, below logo
            ("Helping you find comfort,", LO, 54, DEEPNAVY, 0),
            ("peace of mind, and hope.", LO, 54, DEEPNAVY, 0),
            ("thehopewellnesscenter.com", SB, 44, NAVY, 2)],
            hold_out=True, cy=H * 0.70),
    ]


# ------------------------------------------------------------ transitions ---
# boundary b (frame STARTS[b]) between scene b-1 and b
TRANS = {
    1: ("particles", 8, 16), 2: ("sweep", 6, 14), 3: ("particles", 6, 14),
    4: ("sweep", 6, 14), 5: ("particles", 6, 14), 6: ("sweep", 6, 14),
    7: ("particles", 6, 14), 8: ("sweep", 6, 14), 9: ("ball", 5, 12),
    10: ("ball", 5, 12), 11: ("particles", 5, 12), 12: ("converge", 5, 12),
}


def scene_index(f):
    for i, s in enumerate(SCENES_T):
        if s["start_frame"] <= f < s["end_frame_exclusive"]:
            return i
    return len(SCENES_T) - 1


BALL = make_ball(50)


def compose(f, scenes, blocks):
    idx = scene_index(f)
    active = None
    for b, (kind, pre, post) in TRANS.items():
        fb = STARTS[b]
        if fb - pre <= f < fb + post:
            active = (b, kind, pre, post, (f - (fb - pre)) / (pre + post))
            break
    if active is None:
        img = scenes[idx].frame(f - scenes[idx].start)
    else:
        b, kind, pre, post, prog = active
        A, B = scenes[b - 1], scenes[b]
        camA = 24 * ease_io(prog)
        camB = -20 * (1 - ease_io(prog))
        fa = np.asarray(A.frame(min(f - A.start, A.dur - 1), cam=camA), np.float32)
        fbimg = np.asarray(B.frame(max(f - B.start, 0), cam=camB), np.float32)
        m = ease_io((prog - 0.15) / 0.7)
        img = Image.fromarray(np.clip(fa * (1 - m) + fbimg * m, 0, 255).astype(np.uint8))
        if kind in ("particles", "converge"):
            c = (W / 2, H * 0.5)
            img = Image.alpha_composite(img.convert("RGBA"),
                    particles(prog, c, converge=(kind == "converge"),
                              seed=b, n=70)).convert("RGB")
        elif kind == "sweep":
            img = Image.alpha_composite(img.convert("RGBA"),
                    light_sweep(prog)).convert("RGB")
        elif kind == "ball":
            img = img.convert("RGBA")
            x = -120 + (W + 240) * ease_io(prog)
            y = H * 0.62 - 260 * math.sin(math.pi * prog)
            rot = BALL.rotate(-360 * prog, resample=Image.BICUBIC)
            img.alpha_composite(rot, (int(x - rot.size[0] / 2), int(y - rot.size[1] / 2)))
            img = Image.alpha_composite(img, light_sweep(prog)).convert("RGB")
    for blk in blocks:
        img = blk.draw(img, f)
    return grade(np.asarray(img))


def main():
    preview = "--preview" in sys.argv
    scenes = [Scene(i) for i in range(13)]
    blocks = build_text()
    if preview:
        for f in [1, 40, 70, 120, 260, 470, 620, 760, 930, 1060, 1210, 1360,
                  1470, 1560, 1630, 1700, 1770]:
            Image.fromarray(compose(f, scenes, blocks)).save(
                os.path.join(OUT, f"lp_{f:04d}.png"))
        print("previews ->", OUT)
        return
    import imageio_ffmpeg
    import time
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    vpath = os.path.join(OUT, "landscape-video.mp4")
    cmd = [ff, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset",
           "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags",
           "+faststart", vpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    for f in range(TOTAL):
        proc.stdin.write(compose(f, scenes, blocks).tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{TOTAL} ({time.time()-t0:.0f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    print("video ->", vpath, "rc", proc.returncode)


if __name__ == "__main__":
    main()
