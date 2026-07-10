# Delivery — Picking Up My Notepad v2

Status: **complete**

## The MP4 (in this repo)

**[`dist/picking-up-my-notepad.mp4`](dist/picking-up-my-notepad.mp4)** — 1080p @ ~8 Mbps, full 2:52 track (Git LFS)

Audio: full mix extracted from the live Netlify MV (Gmail MCP unavailable in this run).

## Netlify drop-in

1. Take `immohrtal/picking-up-my-notepad-v2/dist/picking-up-my-notepad.mp4`
2. Replace `public/video/picking-up-my-notepad.mp4` in the Immortal site repo
3. Optional: refresh `public/video/notepad-poster.jpg` from a strong frame (~5s title card)
4. Redeploy Netlify — keep the existing 30s email gate

## Rebuild later

```bash
cd immohrtal/picking-up-my-notepad-v2
python3 scripts/build_v2.py
```

Requires: `ffmpeg`, `pillow`, `numpy`, stills in `stills/`, and `picking-up-my-notepad.mp3`.
