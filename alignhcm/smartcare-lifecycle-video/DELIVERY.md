# Delivery — SmartCare "Stabilize · Optimize · Thrive"

Status: **complete** · 1920×1080 · 30 fps · ~45.6 s · H.264 High · **silent (no audio track)**

## Files (`dist/`)
| File | What |
|---|---|
| `smartcare-stabilize-optimize-thrive-1080p.mp4` | **Primary master** — 1080p, silent |
| `smartcare-stabilize-optimize-thrive-720p.mp4` | Web-light 720p, silent |
| `smartcare-stabilize-optimize-thrive-poster.jpg` | Poster / thumbnail (intro card) |

## What it is
A five-slide sizzle for Align HCM's SmartCare post-go-live lifecycle, built by animating the
finished SmartCare frames — slow dimensional camera, staged glass-panel illumination,
selective icon activation, orange energy-path light trails, accent-underline draws,
seamless light-trail transitions, and a CTA finish. Compositions preserved, not redesigned.

**5 unique slides:** Intro (SmartCare logo on a white card) → Overview (Stabilize · Optimize
· Thrive model) → Optimize (clean panel) → Thrive (clean panel) → CTA (logo card + alignhcm.com).

## Source of truth
The supplied SmartCare frames in `assets/plates/`. The edit uses the clean stage plates
(`s2`, `s4`); the data-viz variants (`s3` 87% dashboard, `s5` growth chart) are present but
unused, per direction. Brand marks (Align wordmark, SmartCare heart, and the hi-res SmartCare
logo for the white card) come from the supplied art — no external assets.

## Rebuild
```bash
scripts/build.sh          # 30fps render + silent master + 720p + poster
```
See `README.md` for the editable knobs (scene timing, camera, illumination cues).

## Notes
- Audio: **none — silent** (no music, no voiceover, per direction). The optional cinematic-bed
  generator (`make_audio.py`) remains in the repo but is not muxed by `build.sh`.
- Intro + CTA show the real SmartCare logo on a **white card** with a thick orange+white gradient
  outline, so the logo's charcoal wordmark reads (it disappears on black).
- Every camera move is full-frame (≤1.03×) so no composition is cropped.
- Rendered deterministically (Playwright drives `seek(t)`, frames piped to ffmpeg), so the
  build is exactly reproducible.
