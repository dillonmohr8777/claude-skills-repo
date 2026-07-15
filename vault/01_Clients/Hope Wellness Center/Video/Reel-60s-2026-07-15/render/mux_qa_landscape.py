#!/usr/bin/env python3
"""Mux the landscape reel with the score and run the QA contract."""
import json
import os
import re
import subprocess

import imageio_ffmpeg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FF = imageio_ffmpeg.get_ffmpeg_exe()

# The landscape cut is now THE deliverable (canonical name); it replaces the
# earlier box-treatment vertical, which remains in git history.
VIDEO = os.path.join(HERE, "out", "landscape-video.mp4")
AUDIO = os.path.join(HERE, "out", "reel-audio.wav")
FINAL = os.path.join(ROOT, "hope-wellness-60s-reel-final.mp4")
STRIP = os.path.join(ROOT, "hope-wellness-60s-reel-review-strip.png")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


r = run([FF, "-y", "-i", VIDEO, "-i", AUDIO, "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
         "-shortest", FINAL])
assert r.returncode == 0, r.stderr[-2000:]
print("muxed ->", FINAL)

info = {}
r = run([FF, "-i", FINAL, "-map", "0:v:0", "-f", "null", "-"])
frames = re.findall(r"frame=\s*(\d+)", r.stderr)
info["frames"] = int(frames[-1]) if frames else -1
m = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", r.stderr)
if m:
    info["w"], info["h"] = int(m.group(1)), int(m.group(2))
m = re.search(r"(\d+(?:\.\d+)?) fps", r.stderr)
info["fps"] = float(m.group(1)) if m else -1
m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
if m:
    info["dur"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
m = re.search(r"Audio: (\w+).*?(\d+) Hz", r.stderr)
if m:
    info["acodec"], info["arate"] = m.group(1), int(m.group(2))
info["size_mb"] = round(os.path.getsize(FINAL) / 1e6, 2)
print(json.dumps(info, indent=2))

ok = True
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok = ok and cond

check("resolution 1920x1080", info.get("w") == 1920 and info.get("h") == 1080)
check("30 fps", abs(info.get("fps", 0) - 30) < 0.01)
check("exactly 1800 frames", info.get("frames") == 1800)
check("duration 60.00 +/- 0.10 s", abs(info.get("dur", 0) - 60.0) <= 0.16)
check("audio aac 48kHz", info.get("acodec") == "aac" and info.get("arate") == 48000)

# six-frame review strip (landscape tiles)
times = [2.0, 11.0, 21.0, 35.0, 50.0, 58.5]
tiles = []
for i, t in enumerate(times):
    p = os.path.join(HERE, "out", f"lstrip_{i}.png")
    run([FF, "-y", "-ss", str(t), "-i", FINAL, "-frames:v", "1", p])
    tiles.append(Image.open(p).resize((640, 360), Image.LANCZOS))
strip = Image.new("RGB", (640 * 3, 360 * 2), "white")
for i, tile in enumerate(tiles):
    strip.paste(tile, ((i % 3) * 640, (i // 3) * 360))
strip.save(STRIP)
print("review strip ->", STRIP)
print("ALL QA PASS" if ok else "QA FAILURES PRESENT")
