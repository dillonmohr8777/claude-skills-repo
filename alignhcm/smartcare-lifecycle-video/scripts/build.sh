#!/usr/bin/env bash
# Reproducible build for the SmartCare "Stabilize · Optimize · Thrive" sizzle.
# Renders audio + video, muxes the master, and writes delivery variants + poster.
#
#   scripts/build.sh            # full build (audio + 30fps render + master + poster)
#   scripts/build.sh --fast     # 24fps proof build
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
export SSL_CERT_FILE="${SSL_CERT_FILE:-/root/.ccr/ca-bundle.crt}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
FPS=30; [ "${1:-}" = "--fast" ] && FPS=24
NAME="smartcare-stabilize-optimize-thrive"
mkdir -p output dist

echo "==> 1/4  audio (bed + voiceover)"
python3 scripts/make_audio.py

echo "==> 2/4  render frames -> H.264 (${FPS}fps)"
node scripts/render.mjs --fps "$FPS" --jpeg 97 --out video_raw.mp4

echo "==> 3/4  mux master (delivery encode + AAC)"
"$FF" -y -hide_banner -loglevel error -i output/video_raw.mp4 -i output/mix.wav \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 256k -movflags +faststart -shortest "dist/${NAME}-1080p.mp4"

echo "==> 4/4  web-light (720p) + muted + poster"
"$FF" -y -hide_banner -loglevel error -i "dist/${NAME}-1080p.mp4" \
  -vf scale=1280:720 -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -movflags +faststart "dist/${NAME}-720p.mp4"
"$FF" -y -hide_banner -loglevel error -i "dist/${NAME}-1080p.mp4" \
  -an -c:v copy -movflags +faststart "dist/${NAME}-1080p-muted.mp4"
"$FF" -y -hide_banner -loglevel error -ss 9.6 -i "dist/${NAME}-1080p.mp4" \
  -vframes 1 -q:v 2 "dist/${NAME}-poster.jpg"

echo "==> done. deliverables:"
ls -la dist/
