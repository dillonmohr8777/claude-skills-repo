# Delivery — Picking Up My Notepad v2

Status: **complete**

## Masters (cloud artifacts)

| File | Size | Role |
|---|---|---|
| `picking-up-my-notepad-v2-web.mp4` | 172MB | **Site drop-in** — 1080p @ ~8 Mbps |
| `picking-up-my-notepad-v2-preview.mp4` | 82MB | Review cut (720p) |
| `picking-up-my-notepad-v2-teaser30.mp4` | 30MB | First 30s for email gate / social |

Audio: full 2:52 mix extracted from the live Netlify MV (Gmail MCP was unavailable in this run).

## Netlify drop-in

1. Download `picking-up-my-notepad-v2-web.mp4`
2. Rename → `picking-up-my-notepad.mp4`
3. Replace `public/video/picking-up-my-notepad.mp4` in the Immortal site repo
4. Optional: refresh `public/video/notepad-poster.jpg` from a strong frame (~5s title card)
5. Redeploy Netlify — keep the existing 30s email gate

## Rebuild later

```bash
cd immohrtal/picking-up-my-notepad-v2
python3 scripts/build_v2.py
```

Requires: `ffmpeg`, `pillow`, `numpy`, stills in `stills/`, and `picking-up-my-notepad.mp3`.
