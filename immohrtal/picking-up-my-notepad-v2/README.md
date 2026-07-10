# IMMOHRTAL — Picking Up My Notepad (Official Video v2)

Beat-synced 1080p newsprint-collage cut for [immohrtal-site.netlify.app/video.html](https://immohrtal-site.netlify.app/video.html).

## What changed vs live v1

| | Live v1 | This v2 |
|---|---|---|
| Resolution | 1280×720 | **1920×1080** |
| Edit | Soft still drift | **Beat-led cuts** (~0.5–1.4s) |
| Type | Sparse titles | Chapter stamps: Erie → Burg → Split → Family |
| Grade | Native | Sepia wash, grain, vignette, torn-paper edges |
| Audio | Embedded AAC | Same full track (extracted from live MV) |

## Audio source

Gmail MCP is not connected in this cloud agent run. The full mix was extracted from the public Netlify file:

`https://immohrtal-site.netlify.app/video/picking-up-my-notepad.mp4` (2:52)

## Build

```bash
# stills/ should contain collage frames (harvested from v1 + site assets)
# picking-up-my-notepad.mp3 should sit in this folder
python3 scripts/build_v2.py
```

Outputs:

- `output/picking-up-my-notepad-v2-web.mp4` — **drop-in master** (1080p @ ~8 Mbps)
- `output/picking-up-my-notepad-v2-preview.mp4` — 720p preview
- `output/picking-up-my-notepad-v2-teaser30.mp4` — first 30s for the email gate
- `output/picking-up-my-notepad-v2.mp4` — lossless-ish CRF18 working master (large)

## Drop-in on the site

Replace `public/video/picking-up-my-notepad.mp4` with `picking-up-my-notepad-v2-web.mp4` (and refresh `notepad-poster.jpg` from a strong frame) then redeploy Netlify. Keep the 30s email gate.
