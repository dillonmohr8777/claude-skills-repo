#!/usr/bin/env python3
"""Build IMMOHRTAL — My Own Way (official video), the Star Room cut.

Sources:
  boards/sheet1-master40.png  7x6 grid — the 40-panel narrative backbone
  boards/sheet2-heroes10.png  5x2 grid — 10 tall hero panels
  boards/sheet3-alt36.png     7x6 grid — alternate takes (fill pool)
  clips/clip_a.mp4            rooftop skyline sit (motion)
  clips/clip_b.mp4            studio notebook + mic (motion)
  my-own-way.mp3              full mix (3:12)

Grammar per ../reference/star-room-study.md, adapted to the boards'
ink-and-gold zine palette: violet-ink shadows, warm amber highlights
(so the 412 gold survives the night), cross-dissolves, ghost heroes,
escalation ramp, cold open, dissolve out. Motion clips are spliced
throughout on a steady cadence with staggered in-points.
"""
from __future__ import annotations

import json
import math
import random
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "boards"
PANELS = ROOT / "panels"
CLIPS = ROOT / "clips"
OUT = ROOT / "output"
FRAMES = OUT / "frames"
CLIPFRAMES = OUT / "clipframes"
EDIT = ROOT / "scripts" / "edit.json"
AUDIO = ROOT / "my-own-way.mp3"

W, H, FPS = 1920, 1080, 24
CW, CH = 2112, 1188            # clip plate size (pan headroom)
SEED = 412
DISSOLVE = 0.8
PLATE_SCALE = 1.07

END_TAG = ("MY OWN WAY", "IMMOHRTAL  ·  DANCE WITH THE DELUSIONAL")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:9]), "..." if len(cmd) > 9 else "")
    subprocess.check_call(cmd)


def audio_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)])
    return float(out.strip())


# ---------------------------------------------------------------- slice

def _light_bands(profile: np.ndarray, thresh: float, min_size: int) -> list[tuple[int, int]]:
    lit = profile > thresh
    bands, start = [], None
    for i, v in enumerate(lit):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_size:
                bands.append((start, i))
            start = None
    if start is not None and len(lit) - start >= min_size:
        bands.append((start, len(lit)))
    return bands


def slice_sheet(sheet: Path, cols: int, rows: int, prefix: str,
                label_crop: float, inset: float,
                rows_uniform: bool = False) -> list[Path]:
    """Cut a storyboard grid into panels by detecting the black gutters
    (labels live in the dark gutter strips, so they fall away too).
    Columns via 90th-percentile brightness (gutters stay black even where
    dark night panels sit); rows via near-black fraction (caption text in
    a gutter only lifts a few pixels). Falls back to a uniform grid if
    detection finds the wrong counts."""
    img = Image.open(sheet).convert("RGB")
    gray = np.asarray(ImageOps.grayscale(img)).astype(np.float32)
    colp = np.percentile(gray, 90, axis=0)
    rowdark = (gray < 30).mean(axis=1)
    col_bands = _light_bands(colp, 60.0, int(img.width / cols * 0.5))
    if rows_uniform:
        ch = img.height / rows
        row_bands = [(int(r * ch + 4), int((r + 1) * ch - 4)) for r in range(rows)]
    else:
        row_bands = _light_bands((rowdark < 0.82).astype(np.float32), 0.5,
                                 int(img.height / rows * 0.35))
    detected = len(col_bands) == cols and len(row_bands) == rows
    print(f"{sheet.name}: gutter detect cols={len(col_bands)} rows={len(row_bands)}"
          f" -> {'ok' if detected else 'FALLBACK uniform'}")
    out: list[Path] = []
    if detected:
        for ri, (y0, y1) in enumerate(row_bands):
            for ci, (x0, x1) in enumerate(col_bands):
                w, h = x1 - x0, y1 - y0
                # labels live in the gutters, so no label_crop here
                cell = img.crop((int(x0 + w * inset), int(y0 + h * inset),
                                 int(x1 - w * inset), int(y1 - h * inset)))
                p = PANELS / f"{prefix}_{ri * cols + ci:02d}.png"
                cell.save(p)
                out.append(p)
        return out
    cw, ch = img.width / cols, img.height / rows
    for r in range(rows):
        for c in range(cols):
            cell = img.crop((int(c * cw + cw * inset), int(r * ch + ch * inset),
                             int((c + 1) * cw - cw * inset),
                             int((r + 1) * ch - ch * (inset + label_crop))))
            p = PANELS / f"{prefix}_{r * cols + c:02d}.png"
            cell.save(p)
            out.append(p)
    return out


# ---------------------------------------------------------------- grade

def night_gold(img: Image.Image) -> Image.Image:
    """Violet-ink shadows -> warm amber highlights. Keeps the boards'
    gold 412 alive inside the Star Room night."""
    gray = np.asarray(ImageOps.grayscale(img)).astype(np.float32) / 255.0
    g = np.clip((gray - 0.05) / 0.95, 0, 1) ** 1.18
    # shadows (12,8,28) -> mids (88,62,104) -> highs (250,206,150)
    r = np.where(g < 0.5, 12 + (88 - 12) * (g / 0.5), 88 + (250 - 88) * ((g - 0.5) / 0.5))
    gg = np.where(g < 0.5, 8 + (62 - 8) * (g / 0.5), 62 + (206 - 62) * ((g - 0.5) / 0.5))
    b = np.where(g < 0.5, 28 + (104 - 28) * (g / 0.5), 104 + (150 - 104) * ((g - 0.5) / 0.5))
    toned = Image.fromarray(np.stack([r, gg, b], axis=2).astype(np.uint8))
    out = Image.blend(img.convert("RGB"), toned, 0.45)
    return ImageEnhance.Color(out).enhance(1.18)


def bloom(img: Image.Image, strength: float = 0.5) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    small = img.resize((img.width // 4, img.height // 4), Image.Resampling.BILINEAR)
    blur = small.filter(ImageFilter.GaussianBlur(10)).resize(img.size, Image.Resampling.BILINEAR)
    barr = np.asarray(blur).astype(np.float32)
    screened = 255 - (255 - arr) * (255 - barr * strength) / 255
    return Image.fromarray(np.clip(screened, 0, 255).astype(np.uint8))


def chroma_bleed(img: Image.Image, px: int) -> Image.Image:
    if px <= 0:
        return img
    r, g, b = img.split()
    r = r.transform(r.size, Image.AFFINE, (1, 0, -px, 0, 1, 0))
    b = b.transform(b.size, Image.AFFINE, (1, 0, px, 0, 1, 0))
    return Image.merge("RGB", (r, g, b))


def grade_plate(img: Image.Image, escalate: float) -> Image.Image:
    img = night_gold(img)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = bloom(img, 0.42 + 0.24 * escalate)
    img = chroma_bleed(img, int(round(1 + 3 * escalate)))
    return img


def upscale_sharp(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Panels are ~210-500px; two-stage lanczos with unsharp at each stage
    plus autocontrast keeps the ink lines and halftone punch alive."""
    img = ImageOps.autocontrast(img, cutoff=1)
    mid = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
    mid = mid.filter(ImageFilter.UnsharpMask(radius=1.6, percent=120, threshold=2))
    up = mid.resize(size, Image.Resampling.LANCZOS)
    return up.filter(ImageFilter.UnsharpMask(radius=2.6, percent=150, threshold=2))


# ------------------------------------------------------------- segments

class Seg:
    """One timeline segment: a panel plate, a tall hero, or a motion clip."""

    def __init__(self, kind: str, start: float, end: float, escalate: float,
                 rng: random.Random, *, plate: Image.Image | None = None,
                 ghost: Image.Image | None = None,
                 clip_dir: Path | None = None, clip_in: float = 0.0,
                 clip_len: float = 10.0):
        self.kind, self.start, self.end, self.escalate = kind, start, end, escalate
        self.plate, self.ghost = plate, ghost
        self.clip_dir, self.clip_in, self.clip_len = clip_dir, clip_in, clip_len
        if kind == "panel":
            max_x = plate.width - W
            max_y = plate.height - H
            self.x0 = rng.uniform(0.15, 0.85) * max_x
            self.y0 = rng.uniform(0.1, 0.6) * max_y
            self.x1 = min(max(self.x0 + rng.uniform(-0.2, 0.2) * max_x, 0), max_x)
            self.y1 = min(max(self.y0 + rng.uniform(-0.15, 0.15) * max_y, 0), max_y)
            self.zoom_in = 0.035 + 0.035 * rng.random()
        elif kind == "vert":
            self.y0 = 0.0
            self.y1 = plate.height - H
            if rng.random() < 0.5:
                self.y0, self.y1 = self.y1, self.y0
        else:  # clip
            self.x0 = rng.uniform(0, CW - W)
            self.x1 = min(max(self.x0 + rng.uniform(-120, 120), 0), CW - W)
            self.y0 = rng.uniform(0, CH - H)
            self.y1 = min(max(self.y0 + rng.uniform(-50, 50), 0), CH - H)
        # ghosts read clean over motion clips; over busy ink panels they mud —
        # only allow them there deep into the escalation, and lighter
        if kind == "clip":
            self.ghost_on = ghost is not None and rng.random() < 0.35 + 0.4 * escalate
            self.ghost_peak = 0.20 + 0.24 * escalate
        else:
            self.ghost_on = ghost is not None and escalate > 0.45 and rng.random() < 0.30
            self.ghost_peak = 0.14 + 0.14 * escalate
        self.ghost_mirror = rng.random() < 0.5
        self.double = kind != "clip" and rng.random() < 0.18 + 0.25 * escalate

    def frame_at(self, t: float) -> Image.Image:
        u = (t - self.start) / max(0.04, self.end - self.start)
        u = min(max(u, 0.0), 1.0)
        e = u * u * (3 - 2 * u)
        if self.kind == "clip":
            n = int(round(self.clip_len * FPS))
            fi = int(round((self.clip_in + (t - self.start)) * FPS))
            k = fi % (2 * n - 2) if n > 1 else 0            # ping-pong loop
            if k >= n:
                k = 2 * n - 2 - k
            src = Image.open(self.clip_dir / f"c{k:04d}.jpg")
            x = int(self.x0 + (self.x1 - self.x0) * e)
            y = int(self.y0 + (self.y1 - self.y0) * e)
            crop = src.crop((x, y, x + W, y + H))
        elif self.kind == "vert":
            y = int(self.y0 + (self.y1 - self.y0) * e)
            crop = self.plate.crop((0, y, W, y + H))
        else:
            shed = self.zoom_in * e
            cw, ch = int(W * (1 - shed)), int(H * (1 - shed))
            x = int(self.x0 + (self.x1 - self.x0) * e + (W - cw) / 2)
            y = int(self.y0 + (self.y1 - self.y0) * e + (H - ch) / 2)
            x = min(max(x, 0), self.plate.width - cw)
            y = min(max(y, 0), self.plate.height - ch)
            crop = self.plate.crop((x, y, x + cw, y + ch))
            if (cw, ch) != (W, H):
                crop = crop.resize((W, H), Image.Resampling.BILINEAR)

        out = np.asarray(crop).astype(np.float32)
        if self.double:
            flip = np.asarray(crop.transpose(Image.FLIP_LEFT_RIGHT)).astype(np.float32)
            a = 0.12 + 0.10 * self.escalate
            out = out * (1 - a) + flip * a
        if self.ghost_on:
            ga = self.ghost_peak * math.sin(math.pi * u) ** 2
            if ga > 0.01:
                g = self.ghost
                gy = int((g.height - H) * 0.4)
                gx = int((g.width - W) * (0.25 + 0.5 * u)) if g.width > W else 0
                gcrop = g.crop((gx, gy, gx + W, gy + H))
                if self.ghost_mirror:
                    gcrop = gcrop.transpose(Image.FLIP_LEFT_RIGHT)
                out = out * (1 - ga) + np.asarray(gcrop).astype(np.float32) * ga
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------ overlays

def get_font(size: int, bold: bool = True):
    import os
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def vignette_mask() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (1.0 - 0.50 * np.clip((r - 0.34) / 0.95, 0, 1) ** 1.5)[..., None].astype(np.float32)


def draw_centered(img: Image.Image, title: str, sub: str | None, alpha: float,
                  size: int = 110) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    a = int(255 * alpha)
    f = get_font(size)
    tb = d.textbbox((0, 0), title, font=f)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rectangle([0, 0, W, H], fill=(6, 4, 12, int(120 * alpha)))
    d.text(((W - tw) / 2, (H - th) / 2 - 20), title, font=f, fill=(250, 226, 180, a))
    if sub:
        sf = get_font(30, bold=False)
        sb = d.textbbox((0, 0), sub, font=sf)
        d.text(((W - (sb[2] - sb[0])) / 2, (H + th) / 2 + 36), sub, font=sf,
               fill=(200, 175, 150, int(220 * alpha)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


# ------------------------------------------------------------ clip prep

def prep_clip(src: Path, name: str, escalate_mid: float) -> Path:
    """Extract, cover-scale to the pan plate size, grade every frame once."""
    d = CLIPFRAMES / name
    if d.exists() and any(d.iterdir()):
        return d
    d.mkdir(parents=True, exist_ok=True)
    raw = d / "raw"
    raw.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-vf", f"scale={CW}:-2,crop={CW}:{CH}", "-r", str(FPS),
         str(raw / "r%04d.jpg")])
    for i, f in enumerate(sorted(raw.iterdir())):
        img = Image.open(f).convert("RGB")
        grade_plate(img, escalate_mid).save(d / f"c{i:04d}.jpg", quality=92)
    shutil.rmtree(raw)
    return d


# ---------------------------------------------------------------- main

def main() -> None:
    rng = random.Random(SEED)
    np.random.seed(SEED)
    duration = audio_duration(AUDIO)
    print(f"duration={duration:.2f}s")

    if PANELS.exists():
        shutil.rmtree(PANELS)
    PANELS.mkdir(parents=True)
    backbone = slice_sheet(BOARDS / "sheet1-master40.png", 7, 6, "s1", 0.17, 0.025)
    heroes = slice_sheet(BOARDS / "sheet2-heroes10.png", 5, 2, "s2", 0.0, 0.02,
                         rows_uniform=True)
    alts = slice_sheet(BOARDS / "sheet3-alt36.png", 7, 6, "s3", 0.15, 0.025)
    title_panel, end_panel = backbone[0], backbone[41]
    story = backbone[1:41]                      # panels 1..40 in narrative order
    print(f"panels: story={len(story)} heroes={len(heroes)} alts={len(alts)}")

    clip_a = prep_clip(CLIPS / "clip_a.mp4", "a", 0.5)
    clip_b = prep_clip(CLIPS / "clip_b.mp4", "b", 0.5)
    clip_len_a = len(list(clip_a.glob("c*.jpg"))) / FPS
    clip_len_b = len(list(clip_b.glob("c*.jpg"))) / FPS

    # ---- shot list: title, then story backbone with heroes + clips woven in
    shots: list[dict] = [{"kind": "panel", "src": title_panel, "d": 3.4}]
    clip_toggle = True
    ci = 0
    for i, p in enumerate(story):
        shots.append({"kind": "panel", "src": p, "d": rng.uniform(2.5, 3.6)})
        if (i + 1) % 3 == 0:                     # splice motion throughout
            src, clen = (clip_a, clip_len_a) if clip_toggle else (clip_b, clip_len_b)
            shots.append({"kind": "clip", "src": src, "d": rng.uniform(2.8, 3.8),
                          "in": (ci * 2.3) % max(0.5, clen - 4.0), "len": clen})
            clip_toggle = not clip_toggle
            ci += 1
        if (i + 1) % 4 == 0:
            shots.append({"kind": "vert", "src": heroes[(i // 4) % len(heroes)],
                          "d": rng.uniform(2.8, 3.8)})
    ai = 0
    while sum(s["d"] for s in shots) < duration - 3.0 and ai < len(alts):
        shots.append({"kind": "panel", "src": alts[ai], "d": rng.uniform(2.5, 3.4)})
        if ai % 3 == 2:
            src, clen = (clip_a, clip_len_a) if clip_toggle else (clip_b, clip_len_b)
            shots.append({"kind": "clip", "src": src, "d": rng.uniform(2.8, 3.6),
                          "in": (ci * 2.3) % max(0.5, clen - 4.0), "len": clen})
            clip_toggle = not clip_toggle
            ci += 1
        ai += 1
    shots.append({"kind": "panel", "src": end_panel, "d": 4.0})

    # scale durations to hit the track length exactly
    total = sum(s["d"] for s in shots)
    for s in shots:
        s["d"] *= duration / total

    # ---- build segments
    segs: list[Seg] = []
    t = 0.0
    hero_imgs = [grade_plate(upscale_sharp(Image.open(h), (W + 260, int((W + 260) * Image.open(h).height / Image.open(h).width))), 0.4) for h in heroes]
    for si, s in enumerate(shots):
        esc = t / duration
        ghost = hero_imgs[si % len(hero_imgs)]
        if s["kind"] == "panel":
            img = Image.open(s["src"])
            plate = grade_plate(upscale_sharp(img, (int(W * PLATE_SCALE), int(H * PLATE_SCALE))), esc)
            seg = Seg("panel", t, t + s["d"], esc, rng, plate=plate, ghost=ghost)
        elif s["kind"] == "vert":
            img = Image.open(s["src"])
            ph = int(H * 1.35)
            pw = max(W, int(ph * img.width / img.height))
            plate = grade_plate(ImageOps.fit(upscale_sharp(img, (pw, ph)), (max(W, pw), ph)), esc)
            seg = Seg("vert", t, t + s["d"], esc, rng, plate=plate, ghost=ghost)
        else:
            seg = Seg("clip", t, t + s["d"], esc, rng, ghost=ghost,
                      clip_dir=s["src"], clip_in=s["in"], clip_len=s["len"])
        segs.append(seg)
        print(f"  seg {si:02d} {t:6.2f}-{t + s['d']:6.2f} {s['kind']:5s}")
        t += s["d"]

    vmask = vignette_mask()
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)

    end_fade = 2.4
    nframes = int(round(duration * FPS))
    for fi in range(nframes):
        tt = fi / FPS
        si = next((k for k in range(len(segs)) if tt < segs[k].end), len(segs) - 1)
        cur = segs[si]
        frame = cur.frame_at(tt)
        into = tt - cur.start
        if si > 0 and into < DISSOLVE:
            a = into / DISSOLVE
            a = a * a * (3 - 2 * a)
            frame = Image.blend(segs[si - 1].frame_at(tt), frame, a)
        arr = np.asarray(frame).astype(np.float32) * vmask
        esc = tt / duration
        g = int(7 + 13 * esc)
        arr = np.clip(arr + np.random.randint(-g, g + 1, arr.shape, dtype=np.int16), 0, 255)
        if tt < 1.3:
            arr *= tt / 1.3
        if tt > duration - end_fade:
            arr *= max(0.0, (duration - tt) / end_fade)
        frame = Image.fromarray(arr.astype(np.uint8))
        if tt > duration - end_fade - 1.6 and tt < duration - 0.3:
            u = (tt - (duration - end_fade - 1.6)) / (end_fade + 1.3)
            fade = min(1.0, u / 0.25) * max(0.0, (1 - u) / 0.3 + 0.35)
            frame = draw_centered(frame, END_TAG[0], END_TAG[1], min(1.0, max(0.0, fade)))
        frame.save(FRAMES / f"f{fi:06d}.jpg", quality=92)
        if fi % 240 == 0:
            print(f"frame {fi}/{nframes} t={tt:.1f}s seg={si}/{len(segs)}")

    final = OUT / "my-own-way-night-full.mp4"
    web = OUT / "my-own-way-night-full-web.mp4"
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%06d.jpg"),
         "-i", str(AUDIO), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", str(final)])
    run(["ffmpeg", "-y", "-i", str(final),
         "-c:v", "libx264", "-preset", "medium", "-b:v", "8M", "-maxrate", "10M",
         "-bufsize", "16M", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(web)])

    EDIT.write_text(json.dumps({
        "track": "My Own Way",
        "duration": duration,
        "segments": [{"t": round(s.start, 2), "kind": s.kind} for s in segs],
        "n_segments": len(segs),
        "dissolve": DISSOLVE,
        "grammar": "star-room-study.md (ink+gold adaptation)",
        "sources": {"boards": 3, "clips": 2, "panels": len(list(PANELS.iterdir()))},
        "resolution": f"{W}x{H}", "fps": FPS,
        "audio_source": AUDIO.name,
    }, indent=2))
    print("DONE", web, web.stat().st_size)


if __name__ == "__main__":
    main()
