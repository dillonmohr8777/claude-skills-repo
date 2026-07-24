#!/usr/bin/env bash
# Reproducible build for the SmartCare "Stabilize · Optimize · Thrive" sizzle.
# Renders the frames and writes the delivery variants + poster.
#
# Audio is intentionally omitted — the deliverable is SILENT (no music, no VO).
# To restore an audio bed: set INCLUDE_VO in scripts/make_audio.py as desired,
# run `python3 scripts/make_audio.py`, then mux output/mix.wav into the master
# (add `-i output/mix.wav -map 0:v:0 -map 1:a:0 -c:a aac -b:a 256k -shortest`).
#
#   scripts/build.sh            # full build (30fps render + silent master + poster)
#   scripts/build.sh --fast     # 24fps proof build
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
FPS=30; [ "${1:-}" = "--fast" ] && FPS=24
NAME="smartcare-stabilize-optimize-thrive"
mkdir -p output dist

echo "==> 1/3  render frames -> H.264 (${FPS}fps)"
node scripts/render.mjs --fps "$FPS" --jpeg 97 --out video_raw.mp4

echo "==> 2/3  encode master (silent — no audio track)"
"$FF" -y -hide_banner -loglevel error -i output/video_raw.mp4 \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -an -movflags +faststart "dist/${NAME}-1080p.mp4"

echo "==> 3/3  web-light (720p, silent) + poster"
"$FF" -y -hide_banner -loglevel error -i "dist/${NAME}-1080p.mp4" \
  -vf scale=1280:720 -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
  -an -movflags +faststart "dist/${NAME}-720p.mp4"
"$FF" -y -hide_banner -loglevel error -ss 3.0 -i "dist/${NAME}-1080p.mp4" \
  -vframes 1 -q:v 2 "dist/${NAME}-poster.jpg"

echo "==> done. deliverables:"
ls -la dist/
