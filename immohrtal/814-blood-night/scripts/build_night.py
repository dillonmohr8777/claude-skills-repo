#!/usr/bin/env python3
"""Build IMMOHRTAL — 814 Blood (ft. King Keev), the Star Room cut.

Grammar per ../reference/star-room-study.md — the night-side inversion of
the Notepad v2 newsprint chop:

  * long segments (1.5–2.5 bars at 123 BPM), cross-DISSOLVED, not cut
  * night duotone grade (ink black -> violet -> magenta), bloom, chroma bleed
  * ghost figures that fade in and out mid-segment
  * one text declaration ("I'M NOT REAL" register): THE CMO ISN'T REAL
  * bad-trip escalation — grain/ghosting/bleed ramp with t/duration
  * cold open from black, long dissolve out

Audio: uses 814-blood.mp3 (full mix) if present, else falls back to the
30s preview so the teaser can ship before the full mix lands.
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
STILLS = ROOT / "stills"
OUT = ROOT / "output"
FRAMES = OUT / "frames"
EDIT = ROOT / "scripts" / "edit.json"
FULL_AUDIO = ROOT / "814-blood.mp3"
PREVIEW_AUDIO = ROOT / "814-blood-preview30.mp3"

W, H, FPS = 1920, 1080, 24
SEED = 814
BPM = 123.0
BEAT = 60.0 / BPM          # 0.4878s
BAR = 4 * BEAT             # 1.9512s
DISSOLVE = 0.8             # seconds of overlap between segments
PLATE_SCALE = 1.22         # oversize for the slow push-in

HEROES = [
    "artist.jpg",
    "portrait-bw.png",
    "collage-814-lighthouse.jpeg",
    "lotus-erie-pittsburgh.png",
    "cover.jpg",
]

# The single Star Room-style declaration ("I'M NOT REAL" register).
# Placed at ~45% of runtime, held ~3.2s.
DECLARATION = "THE CMO ISN'T REAL"
END_TAG = ("814 BLOOD", "IMMOHRTAL  FT. KING KEEV  ·  DANCE WITH THE DELUSIONAL")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:9]), "..." if len(cmd) > 9 else "")
    subprocess.check_call(cmd)


def audio_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)]
    )
    return float(out.strip())


def plan_segments(duration: float, rng: random.Random) -> list[float]:
    """Phrase-level boundaries on the bar grid: 1.5–2.5 bars per segment."""
    bounds = [0.0]
    t = 0.0
    while t < duration - BAR:
        bars = rng.choice([1.5, 2.0, 2.0, 2.5])
        t = min(duration, t + bars * BAR)
        bounds.append(round(t, 3))
    if bounds[-1] < duration:
        bounds[-1] = duration
    return bounds


# ---------------------------------------------------------------- grade

def night_duotone(img: Image.Image) -> Image.Image:
    """Crushed ink blacks -> violet mids -> magenta/pink highlights."""
    gray = np.asarray(ImageOps.grayscale(img)).astype(np.float32) / 255.0
    g = np.clip((gray - 0.06) / 0.94, 0, 1) ** 1.25       # crush the toe
    # channel curves: shadows (8,6,20) mids (96,40,140) highs (255,170,225)
    r = np.where(g < 0.5, 8 + (96 - 8) * (g / 0.5), 96 + (255 - 96) * ((g - 0.5) / 0.5))
    gg = np.where(g < 0.5, 6 + (40 - 6) * (g / 0.5), 40 + (170 - 40) * ((g - 0.5) / 0.5))
    b = np.where(g < 0.5, 20 + (140 - 20) * (g / 0.5), 140 + (225 - 140) * ((g - 0.5) / 0.5))
    toned = np.stack([r, gg, b], axis=2).astype(np.uint8)
    toned_img = Image.fromarray(toned)
    # keep a whisper of the original color underneath so faces stay human
    return Image.blend(img.convert("RGB"), toned_img, 0.82)


def bloom(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Screen-blend a blurred bright pass — the hanging-lights haze."""
    arr = np.asarray(img).astype(np.float32)
    small = img.resize((img.width // 4, img.height // 4), Image.Resampling.BILINEAR)
    blur = small.filter(ImageFilter.GaussianBlur(10)).resize(img.size, Image.Resampling.BILINEAR)
    barr = np.asarray(blur).astype(np.float32)
    screened = 255 - (255 - arr) * (255 - barr * strength) / 255
    return Image.fromarray(np.clip(screened, 0, 255).astype(np.uint8))


def chroma_bleed(img: Image.Image, px: int) -> Image.Image:
    """VHS-ish RGB mis-registration; px grows with the escalation ramp."""
    if px <= 0:
        return img
    r, g, b = img.split()
    r = r.transform(r.size, Image.AFFINE, (1, 0, -px, 0, 1, 0))
    b = b.transform(b.size, Image.AFFINE, (1, 0, px, 0, 1, 0))
    return Image.merge("RGB", (r, g, b))


def make_plate(path: Path, escalate: float, rng: random.Random) -> Image.Image:
    """Oversized, fully graded source plate for one segment."""
    src = Image.open(path).convert("RGB")
    plate = ImageOps.fit(
        src, (int(W * PLATE_SCALE), int(H * PLATE_SCALE)),
        method=Image.Resampling.LANCZOS, centering=(0.5, 0.42),
    )
    plate = night_duotone(plate)
    plate = ImageEnhance.Contrast(plate).enhance(1.10)
    plate = bloom(plate, 0.45 + 0.25 * escalate)
    plate = chroma_bleed(plate, int(round(1 + 3 * escalate)))
    if rng.random() < 0.35 + 0.3 * escalate:
        plate = plate.filter(ImageFilter.GaussianBlur(0.6 + 1.2 * escalate))
    return plate


# ------------------------------------------------------------- segments

class Segment:
    def __init__(self, i: int, start: float, end: float, still: Path,
                 ghost: Path | None, escalate: float, rng: random.Random):
        self.start, self.end = start, end
        self.plate = make_plate(still, escalate, rng)
        self.escalate = escalate
        max_x = self.plate.width - W
        max_y = self.plate.height - H
        # slow push-in: start wide-ish, drift toward a point, zoom handled
        # by cropping progressively less border
        self.x0 = rng.uniform(0.2, 0.8) * max_x
        self.y0 = rng.uniform(0.1, 0.6) * max_y
        self.x1 = self.x0 + rng.uniform(-0.18, 0.18) * max_x
        self.y1 = self.y0 + rng.uniform(-0.12, 0.12) * max_y
        self.x1 = min(max(self.x1, 0), max_x)
        self.y1 = min(max(self.y1, 0), max_y)
        self.zoom_in = 0.06 + 0.05 * rng.random()   # fraction of border shed
        # ghost figure that appears and disappears mid-segment
        self.ghost = None
        if ghost is not None and rng.random() < 0.35 + 0.45 * escalate:
            self.ghost = make_plate(ghost, escalate, rng)
            self.ghost_mirror = rng.random() < 0.5
            self.ghost_peak = 0.22 + 0.28 * escalate
        # alter-ego doubling: re-composite the SAME plate mirrored + offset
        self.double = rng.random() < 0.25 + 0.35 * escalate

    def frame_at(self, t: float) -> Image.Image:
        u = (t - self.start) / max(0.04, self.end - self.start)
        u = min(max(u, 0.0), 1.0)
        e = u * u * (3 - 2 * u)
        # push-in: shrink the crop window as e grows, then upscale
        shed = self.zoom_in * e
        cw = int(W * (1 - shed))
        ch = int(H * (1 - shed))
        x = int(self.x0 + (self.x1 - self.x0) * e + (W - cw) / 2)
        y = int(self.y0 + (self.y1 - self.y0) * e + (H - ch) / 2)
        x = min(max(x, 0), self.plate.width - cw)
        y = min(max(y, 0), self.plate.height - ch)
        crop = self.plate.crop((x, y, x + cw, y + ch))
        if (cw, ch) != (W, H):
            crop = crop.resize((W, H), Image.Resampling.BILINEAR)
        out = np.asarray(crop).astype(np.float32)

        if self.double:
            flipped = np.asarray(crop.transpose(Image.FLIP_LEFT_RIGHT)).astype(np.float32)
            a = 0.14 + 0.10 * self.escalate
            out = out * (1 - a) + flipped * a

        if self.ghost is not None:
            # sin envelope: nothing -> apparition -> gone
            ga = self.ghost_peak * math.sin(math.pi * u) ** 2
            if ga > 0.01:
                gimg = self.ghost
                gx = int((gimg.width - W) * (0.3 + 0.4 * u))
                gy = int((gimg.height - H) * 0.35)
                gcrop = gimg.crop((gx, gy, gx + W, gy + H))
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
    return (1.0 - 0.62 * np.clip((r - 0.32) / 0.95, 0, 1) ** 1.5)[..., None].astype(np.float32)


def draw_centered(img: Image.Image, title: str, sub: str | None,
                  alpha: float, size: int = 92) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    a = int(255 * alpha)
    f = get_font(size)
    tb = d.textbbox((0, 0), title, font=f)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    # dim the room behind the words, Star Room style — words own the frame
    d.rectangle([0, 0, W, H], fill=(4, 2, 10, int(120 * alpha)))
    d.text(((W - tw) / 2, (H - th) / 2 - 20), title, font=f,
           fill=(240, 225, 240, a))
    if sub:
        sf = get_font(30, bold=False)
        sb = d.textbbox((0, 0), sub, font=sf)
        d.text(((W - (sb[2] - sb[0])) / 2, (H + th) / 2 + 36), sub, font=sf,
               fill=(190, 160, 200, int(220 * alpha)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


# ---------------------------------------------------------------- main

def main() -> None:
    rng = random.Random(SEED)
    np.random.seed(SEED)

    audio = FULL_AUDIO if FULL_AUDIO.exists() else PREVIEW_AUDIO
    is_preview = audio == PREVIEW_AUDIO
    duration = audio_duration(audio)
    tag = "teaser30" if is_preview else "full"
    print(f"audio={audio.name} duration={duration:.2f}s mode={tag}")

    bounds = plan_segments(duration, rng)
    stills = sorted(
        p for p in STILLS.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        and p.stat().st_size > 30_000
    )
    heroes = [STILLS / h for h in HEROES if (STILLS / h).exists()]
    pool = [p for p in stills if p not in heroes]
    rng.shuffle(pool)

    segs: list[Segment] = []
    for i in range(len(bounds) - 1):
        esc = bounds[i] / duration                       # escalation ramp
        if i == 0 or i == len(bounds) - 2:
            still = heroes[0] if heroes else pool[0]     # artist owns open/close
        elif i % 5 == 0 and heroes:
            still = heroes[(i // 5) % len(heroes)]
        else:
            still = pool[i % len(pool)]
        ghost = heroes[(i + 1) % len(heroes)] if heroes else None
        segs.append(Segment(i, bounds[i], bounds[i + 1], still, ghost, esc, rng))
        print(f"  seg {i:02d} {bounds[i]:6.2f}-{bounds[i+1]:6.2f} {still.name}")

    decl_t = duration * 0.45
    decl_dur = 3.2
    end_fade = 2.2                                        # dissolve out
    vmask = vignette_mask()

    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)

    nframes = int(round(duration * FPS))
    for fi in range(nframes):
        t = fi / FPS
        # active segment + dissolve partner
        si = max(0, min(len(segs) - 1,
                        next((k for k in range(len(segs)) if t < segs[k].end), len(segs) - 1)))
        cur = segs[si]
        frame_img = cur.frame_at(t)
        into = t - cur.start
        if si > 0 and into < DISSOLVE:
            prev = segs[si - 1].frame_at(t)               # prev keeps drifting
            a = into / DISSOLVE
            a = a * a * (3 - 2 * a)
            frame_img = Image.blend(prev, frame_img, a)

        arr = np.asarray(frame_img).astype(np.float32) * vmask
        esc = t / duration
        grain = np.random.randint(-int(8 + 14 * esc), int(8 + 14 * esc) + 1,
                                  arr.shape, dtype=np.int16)
        arr = np.clip(arr + grain, 0, 255)
        # cold open / dissolve out
        if t < 1.2:
            arr *= t / 1.2
        if t > duration - end_fade:
            arr *= max(0.0, (duration - t) / end_fade)
        frame_img = Image.fromarray(arr.astype(np.uint8))

        # the one declaration
        if decl_t <= t < decl_t + decl_dur:
            u = (t - decl_t) / decl_dur
            fade = min(1.0, u / 0.18, (1 - u) / 0.22)
            frame_img = draw_centered(frame_img, DECLARATION, None, max(0.0, fade))
        # end tag rides the dissolve-out
        if t > duration - end_fade - 1.4 and t < duration - 0.3:
            u = (t - (duration - end_fade - 1.4)) / (end_fade + 1.1)
            fade = min(1.0, u / 0.25) * max(0.0, (1 - u) / 0.3 + 0.35)
            frame_img = draw_centered(frame_img, END_TAG[0], END_TAG[1],
                                      min(1.0, max(0.0, fade)), size=110)

        frame_img.save(FRAMES / f"f{fi:06d}.jpg", quality=92)
        if fi % 120 == 0:
            print(f"frame {fi}/{nframes} t={t:.1f}s")

    final = OUT / f"814-blood-night-{tag}.mp4"
    web = OUT / f"814-blood-night-{tag}-web.mp4"
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%06d.jpg"),
         "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart",
         str(final)])
    run(["ffmpeg", "-y", "-i", str(final),
         "-c:v", "libx264", "-preset", "medium", "-b:v", "8M", "-maxrate", "10M",
         "-bufsize", "16M", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(web)])

    EDIT.write_text(json.dumps({
        "track": "814 Blood (ft. King Keev)",
        "mode": tag,
        "duration": duration,
        "bpm": BPM,
        "segments": bounds,
        "n_segments": len(bounds) - 1,
        "dissolve": DISSOLVE,
        "declaration": {"t": round(decl_t, 2), "text": DECLARATION},
        "grammar": "star-room-study.md",
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "audio_source": audio.name,
    }, indent=2))
    print("DONE", web, web.stat().st_size)


if __name__ == "__main__":
    main()
