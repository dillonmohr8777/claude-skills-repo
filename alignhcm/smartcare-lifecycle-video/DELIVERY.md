# Delivery — SmartCare "Stabilize · Optimize · Thrive"

Status: **complete** · 1920×1080 · 30 fps · ~59.8 s · H.264 + AAC (faststart)

## Files (`dist/`)
| File | What |
|---|---|
| `smartcare-stabilize-optimize-thrive-1080p.mp4` | **Primary master** — bed + voiceover |
| `smartcare-stabilize-optimize-thrive-720p.mp4` | Web-light 720p (email / embeds) |
| `smartcare-stabilize-optimize-thrive-1080p-muted.mp4` | Muted 1080p (silent-autoplay feeds) |
| `smartcare-stabilize-optimize-thrive-poster.jpg` | Poster / thumbnail (overview frame) |

## What it is
A six-chapter sizzle for Align HCM's SmartCare post-go-live lifecycle, built by
animating the five finished SmartCare frames — dimensional camera, staged glass-panel
illumination, selective icon activation, orange energy-path light trails, restrained
headline reveals, seamless light-trail transitions, and a confident CTA finish.
The compositions are **preserved, not redesigned.**

Arc: Intro → the model (Stabilize·Optimize·Thrive) → Optimize (statement → 87% proof)
→ Thrive (statement → growth-chart proof) → CTA (alignhcm.com).

## Source of truth
The five supplied SmartCare frames in `assets/plates/`. All brand marks (Align wordmark,
SmartCare heart) were extracted from those frames — no external assets. Brand tokens
(orange `#FF8500` on true black, Playfair Display + Inter) were sampled from the frames.

## Rebuild
```bash
scripts/build.sh          # audio + 30fps render + master + variants + poster
```
See `README.md` for the editable knobs (scene timing, camera, illumination cues, VO copy).

## Notes
- Voiceover: edge-tts `en-US-AndrewMultilingualNeural`, ducked ~11 dB under a synthesized
  cinematic bed whose chord changes land on the scene cuts.
- Rendered deterministically (Playwright drives `seek(t)`, frames piped to ffmpeg), so the
  build is exactly reproducible.
