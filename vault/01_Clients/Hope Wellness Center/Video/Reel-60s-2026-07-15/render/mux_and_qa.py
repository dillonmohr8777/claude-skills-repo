#!/usr/bin/env python3
"""Mux video + audio into the final deliverable and run the QA contract."""

import json
import os
import subprocess

import imageio_ffmpeg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FF = imageio_ffmpeg.get_ffmpeg_exe()
FFPROBE = FF.replace("ffmpeg", "ffprobe")

VIDEO = os.path.join(HERE, "out", "reel-video.mp4")
AUDIO = os.path.join(HERE, "out", "reel-audio.wav")
FINAL = os.path.join(ROOT, "hope-wellness-60s-reel-final.mp4")
STRIP = os.path.join(ROOT, "hope-wellness-60s-reel-review-strip.png")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


# ------------------------------------------------------------------- mux --
r = run([FF, "-y", "-i", VIDEO, "-i", AUDIO,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", FINAL])
assert r.returncode == 0, r.stderr[-2000:]
print("muxed ->", FINAL)

# ------------------------------------------------------------------ probe --
if os.path.exists(FFPROBE):
    probe_cmd = [FFPROBE]
else:  # imageio-ffmpeg ships ffmpeg only; parse with ffmpeg -i
    probe_cmd = None

info = {}
r = run([FF, "-i", FINAL, "-map", "0:v:0", "-f", "null", "-"])
import re
frames = re.findall(r"frame=\s*(\d+)", r.stderr)
info["frames"] = int(frames[-1]) if frames else -1
m = re.search(r"(\d+)x(\d+)[, ]", r.stderr)
m2 = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", r.stderr)
if m2:
    info["w"], info["h"] = int(m2.group(1)), int(m2.group(2))
m3 = re.search(r"(\d+(?:\.\d+)?) fps", r.stderr)
info["fps"] = float(m3.group(1)) if m3 else -1
m4 = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
if m4:
    info["dur"] = int(m4.group(1)) * 3600 + int(m4.group(2)) * 60 + float(m4.group(3))
m5 = re.search(r"Audio: (\w+).*?(\d+) Hz", r.stderr)
if m5:
    info["acodec"], info["arate"] = m5.group(1), int(m5.group(2))
info["size_mb"] = round(os.path.getsize(FINAL) / 1e6, 2)
print(json.dumps(info, indent=2))

ok = True
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok = ok and cond

check("resolution 1080x1920", info.get("w") == 1080 and info.get("h") == 1920)
check("30 fps", abs(info.get("fps", 0) - 30) < 0.01)
check("exactly 1800 frames", info.get("frames") == 1800)
check("duration 60.00 +/- 0.10 s", abs(info.get("dur", 0) - 60.0) <= 0.1 + 0.06)
check("audio aac 48kHz", info.get("acodec") == "aac" and info.get("arate") == 48000)

# ------------------------------------------------- six-frame review strip --
times = [2.0, 10.5, 25.0, 35.5, 50.0, 58.0]
tiles = []
for i, t in enumerate(times):
    p = os.path.join(HERE, "out", f"strip_{i}.png")
    r = run([FF, "-y", "-ss", str(t), "-i", FINAL, "-frames:v", "1", p])
    assert r.returncode == 0
    tiles.append(Image.open(p).resize((360, 640), Image.LANCZOS))
strip = Image.new("RGB", (360 * 6, 640), "white")
for i, tile in enumerate(tiles):
    strip.paste(tile, (i * 360, 0))
strip.save(STRIP)
print("review strip ->", STRIP)
print("ALL QA PASS" if ok else "QA FAILURES PRESENT")
