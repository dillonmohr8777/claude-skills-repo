#!/usr/bin/env python3
"""Build IMMOHRTAL — Picking Up My Notepad (official video v2).

1080p collage cut: Ken Burns stills on beat, chapter type, grain/vignette,
muxed with the real track audio extracted from the live Netlify MV.
"""
from __future__ import annotations

import json
import math
import os
import random
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
STILLS = ROOT / "stills"
OUT = ROOT / "output"
CLIPS = OUT / "clips"
FRAMES = OUT / "frames"
EDIT = ROOT / "scripts" / "edit.json"
AUDIO = ROOT / "picking-up-my-notepad.mp3"
WAV = Path("/tmp/picking-up-my-notepad.wav")
FINAL = OUT / "picking-up-my-notepad-v2.mp4"
WEB = OUT / "picking-up-my-notepad-v2-web.mp4"
PREVIEW = OUT / "picking-up-my-notepad-v2-preview.mp4"
TEASER = OUT / "picking-up-my-notepad-v2-teaser30.mp4"
W, H, FPS = 1920, 1080, 24
SEED = 814


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:8]), "..." if len(cmd) > 8 else "")
    subprocess.check_call(cmd)


def detect_cuts(duration: float) -> list[float]:
    wav = wave.open(str(WAV), "rb")
    sr = wav.getframerate()
    nch = wav.getnchannels()
    raw = wav.readframes(wav.getnframes())
    wav.close()
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if nch == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    hop = 1024
    frames = 1 + (len(data) - hop) // hop
    env = np.array(
        [np.sqrt(np.mean(data[i * hop : i * hop + hop] ** 2)) for i in range(frames)]
    )
    smooth = np.convolve(env, np.ones(7) / 7, mode="same")
    diff = np.diff(smooth, prepend=smooth[0])
    thr = np.percentile(diff, 90)
    min_gap = int(0.30 * sr / hop)
    beats: list[float] = []
    last = -999
    for i, v in enumerate(diff):
        if v > thr and i - last >= min_gap:
            beats.append(i * hop / sr)
            last = i

    # Force visual pacing in quiet intro / outro
    forced = list(np.arange(0, 28, 1.6)) + list(np.arange(155, duration, 1.8))
    raw_cuts = sorted(set([0.0] + beats + forced + [duration]))
    cuts = [raw_cuts[0]]
    for t in raw_cuts[1:]:
        want = 0.55 if 28 < t < 155 else 1.35
        if t - cuts[-1] >= want:
            cuts.append(float(round(t, 3)))
    if cuts[-1] < duration - 0.05:
        cuts.append(duration)
    return cuts


CHAPTERS = [
    (0.0, "PICKING UP MY NOTEPAD", "IMMOHRTAL  ·  OFFICIAL VIDEO"),
    (8.0, "ERIE, PA", "814  ·  LAKE EFFECT"),
    (30.0, "FROM THE LAND OF THE SNOW", "HOLD YOUR HANDS IF THEY COLD"),
    (58.0, "PITTSBURGH", "STEEL CITY  ·  CITY OF BRIDGES"),
    (88.0, "THE SPLIT", "CMO DISCIPLINE  /  ARTIST INSTINCT"),
    (118.0, "NO WAY OUT", "SAME BLOOD  ·  SAME FIRE"),
    (148.0, "FAMILY", "YOU'RE THE REASON I FOUND MY FIRE AGAIN"),
    (165.0, "IMMOHRTAL", "SESSION 001  ·  DANCE WITH THE DELUSIONAL"),
]


def load_stills() -> list[Path]:
    files = sorted(
        [
            p
            for p in STILLS.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
            and p.stat().st_size > 40_000
        ]
    )
    if not files:
        raise SystemExit(f"No stills in {STILLS}")
    # Prefer photographic collage frames over tiny assets
    ranked = sorted(files, key=lambda p: p.stat().st_size, reverse=True)
    return ranked


def cover_crop(img: Image.Image, tw: int, th: int) -> Image.Image:
    return ImageOps.fit(img, (tw, th), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))


def sepia(img: Image.Image, amount: float = 0.55) -> Image.Image:
    gray = ImageOps.grayscale(img).convert("RGB")
    arr = np.asarray(gray).astype(np.float32)
    r = np.clip(arr[:, :, 0] * 1.05 + 18, 0, 255)
    g = np.clip(arr[:, :, 1] * 0.92 + 8, 0, 255)
    b = np.clip(arr[:, :, 2] * 0.72, 0, 255)
    toned = np.stack([r, g, b], axis=2).astype(np.uint8)
    toned_img = Image.fromarray(toned)
    return Image.blend(img.convert("RGB"), toned_img, amount)


def add_grain(img: Image.Image, strength: float = 18.0) -> Image.Image:
    arr = np.asarray(img).astype(np.int16)
    noise = np.random.randint(-int(strength), int(strength) + 1, arr.shape, dtype=np.int16)
    out = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    factor = 1.0 - strength * np.clip((r - 0.35) / 0.9, 0, 1) ** 1.6
    arr = np.asarray(img).astype(np.float32)
    arr *= factor[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def torn_edge_mask(size: tuple[int, int], rng: random.Random) -> Image.Image:
    w, h = size
    mask = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(mask)
    # jagged border
    for side in ("top", "bottom", "left", "right"):
        pts = []
        if side in ("top", "bottom"):
            y0 = 0 if side == "top" else h - 1
            x = 0
            while x < w:
                jag = rng.randint(4, 28)
                y = y0 + (jag if side == "top" else -jag)
                pts.append((x, y))
                x += rng.randint(18, 55)
            pts.append((w, y0 + (20 if side == "top" else -20)))
            if side == "top":
                poly = [(0, 0), *pts, (w, 0)]
            else:
                poly = [(0, h), *pts, (w, h)]
            draw.polygon(poly, fill=0)
        else:
            x0 = 0 if side == "left" else w - 1
            y = 0
            while y < h:
                jag = rng.randint(4, 28)
                x = x0 + (jag if side == "left" else -jag)
                pts.append((x, y))
                y += rng.randint(18, 55)
            pts.append((x0 + (20 if side == "left" else -20), h))
            if side == "left":
                poly = [(0, 0), *pts, (0, h)]
            else:
                poly = [(w, 0), *pts, (w, h)]
            draw.polygon(poly, fill=0)
    return mask.filter(ImageFilter.GaussianBlur(1.2))


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def draw_type(
    base: Image.Image,
    title: str,
    subtitle: str,
    t_in_seg: float,
    seg_dur: float,
    rng: random.Random,
) -> Image.Image:
    img = base.copy()
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # fade in/out within segment
    fade = min(1.0, t_in_seg / 0.25, max(0.0, (seg_dur - t_in_seg) / 0.35))
    alpha = int(230 * fade)

    title_font = get_font(74 if len(title) < 28 else 56)
    sub_font = get_font(28, bold=False)

    # stamp block
    pad_x, pad_y = 64, 70
    # measure
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    sb = draw.textbbox((0, 0), subtitle, font=sub_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    box_w = max(tw, sw) + 56
    box_h = th + sh + 48
    x0 = pad_x
    y0 = H - pad_y - box_h
    # slight jitter for zine feel
    x0 += rng.randint(-4, 4)
    y0 += rng.randint(-3, 3)

    draw.rectangle(
        [x0, y0, x0 + box_w, y0 + box_h],
        fill=(12, 14, 18, int(170 * fade)),
    )
    # accent bar
    draw.rectangle([x0, y0, x0 + 10, y0 + box_h], fill=(200, 170, 90, alpha))
    draw.text((x0 + 28, y0 + 14), title, font=title_font, fill=(245, 240, 230, alpha))
    draw.text(
        (x0 + 28, y0 + 18 + th + 6),
        subtitle,
        font=sub_font,
        fill=(200, 190, 170, int(200 * fade)),
    )

    # corner 814 mark
    mark_font = get_font(42)
    draw.text((W - 160, 48), "814", font=mark_font, fill=(235, 230, 220, int(160 * fade)))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def chapter_at(t: float) -> tuple[str, str]:
    cur = CHAPTERS[0]
    for ch in CHAPTERS:
        if t >= ch[0]:
            cur = ch
        else:
            break
    return cur[1], cur[2]


def render_segment_frames(
    still: Path,
    start: float,
    end: float,
    frame_dir: Path,
    frame_offset: int,
    rng: random.Random,
) -> int:
    dur = max(0.04, end - start)
    nframes = max(1, int(round(dur * FPS)))
    src = Image.open(still).convert("RGB")
    # oversize for Ken Burns
    scale = 1.18 + rng.random() * 0.12
    big = cover_crop(src, int(W * scale), int(H * scale))
    big = sepia(big, 0.42 + rng.random() * 0.2)
    big = ImageEnhance.Contrast(big).enhance(1.08)
    big = ImageEnhance.Color(big).enhance(0.85)

    # pan direction
    max_x = big.width - W
    max_y = big.height - H
    x0 = rng.uniform(0, max_x) if max_x > 0 else 0
    y0 = rng.uniform(0, max_y * 0.4) if max_y > 0 else 0
    x1 = rng.uniform(0, max_x) if max_x > 0 else 0
    y1 = rng.uniform(0, max_y * 0.5) if max_y > 0 else 0
    # prefer readable motion
    if abs(x1 - x0) < max_x * 0.15 and max_x > 0:
        x1 = 0 if x0 > max_x / 2 else max_x

    paper = Image.new("RGB", (W, H), (232, 224, 210))
    title, subtitle = chapter_at(start + dur * 0.2)
    use_torn = rng.random() < 0.55

    for i in range(nframes):
        u = i / max(1, nframes - 1)
        # ease
        e = u * u * (3 - 2 * u)
        x = int(x0 + (x1 - x0) * e)
        y = int(y0 + (y1 - y0) * e)
        crop = big.crop((x, y, x + W, y + H))
        if use_torn:
            mask = torn_edge_mask((W, H), rng)
            frame = paper.copy()
            frame.paste(crop, (0, 0), mask)
        else:
            frame = crop
        frame = vignette(frame, 0.48 + 0.1 * math.sin(u * math.pi))
        frame = add_grain(frame, 12 + 8 * (0.5 + 0.5 * math.sin(start)))
        # type on most segments, denser in hooks
        if dur >= 0.7 or (start > 28 and rng.random() < 0.7):
            frame = draw_type(frame, title, subtitle, i / FPS, dur, rng)
        out_path = frame_dir / f"f{frame_offset + i:06d}.jpg"
        frame.save(out_path, quality=92, optimize=True)
    return nframes


def encode(frame_dir: Path, nframes: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # full quality
    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frame_dir / "f%06d.jpg"),
            "-i",
            str(AUDIO),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "320k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(FINAL),
        ]
    )
    # web delivery master (~8 Mbps 1080p)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(FINAL),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-b:v",
            "8M",
            "-maxrate",
            "10M",
            "-bufsize",
            "16M",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-movflags",
            "+faststart",
            str(WEB),
        ]
    )
    # compact 720p preview
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(WEB),
            "-vf",
            "scale=1280:-2",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            str(PREVIEW),
        ]
    )
    # 30s gate teaser
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(WEB),
            "-t",
            "30",
            "-c",
            "copy",
            str(TEASER),
        ]
    )


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    stills = load_stills()
    duration = 172.29
    if WAV.exists():
        wav = wave.open(str(WAV), "rb")
        duration = wav.getnframes() / float(wav.getframerate())
        wav.close()
    cuts = detect_cuts(duration)
    edit = {
        "duration": duration,
        "cuts": cuts,
        "n_cuts": len(cuts) - 1,
        "chapters": [
            {"t": t, "title": title, "subtitle": sub} for t, title, sub in CHAPTERS
        ],
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "audio_source": "Extracted from https://immohrtal-site.netlify.app/video/picking-up-my-notepad.mp4 (Gmail MCP unavailable in this cloud run)",
    }
    EDIT.write_text(json.dumps(edit, indent=2))
    print(f"stills={len(stills)} segments={len(cuts)-1} duration={duration:.2f}s")

    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)

    rng = random.Random(SEED)
    # shuffle still order but keep largest/most iconic early
    pool = stills[:]
    rng.shuffle(pool)
    # bias: put biggest stills more often
    weighted = pool[:40] * 2 + pool

    frame_offset = 0
    for i in range(len(cuts) - 1):
        start, end = cuts[i], cuts[i + 1]
        still = weighted[i % len(weighted)]
        # every ~8 segments, force a high-signal still (poster/cover/daughter)
        if i % 8 == 0:
            heroes = [p for p in stills if p.name in {"notepad-poster.jpg", "cover.jpg", "daughter.jpg", "artist.jpg"} or p.name.startswith("cut_")]
            if heroes:
                still = heroes[i % len(heroes)]
        n = render_segment_frames(still, start, end, FRAMES, frame_offset, random.Random(SEED + i))
        frame_offset += n
        if i % 10 == 0:
            print(f"segment {i}/{len(cuts)-1} frames={frame_offset} t={start:.1f}-{end:.1f} still={still.name}")

    print(f"encoding {frame_offset} frames...")
    encode(FRAMES, frame_offset)
    # copy artifacts
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    for path in (FINAL, WEB, PREVIEW, TEASER):
        if path.exists():
            shutil.copy2(path, art / path.name)
            print(path.name, path.stat().st_size)
    print("DONE", WEB)


if __name__ == "__main__":
    main()
