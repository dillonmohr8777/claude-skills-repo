# Delivery Report — Hope Wellness Center 60 Second Reel

Rendered July 15, 2026 from `CLAUDE_VIDEO_PROMPT.md` and `timeline.json`.

## Final deliverable

- **File:** `hope-wellness-60s-reel-final.mp4`
- **Duration:** 60.00 s (exactly 1,800 frames)
- **Resolution:** 1080 × 1920 (9:16 vertical)
- **Frame rate:** 30 fps
- **Video:** H.264 (libx264, CRF 19, yuv420p, faststart)
- **Audio:** AAC 192 kbps, 48 kHz stereo
- **File size:** 12.93 MB
- **Review strip:** `hope-wellness-60s-reel-review-strip.png` (six frames)

## QA contract results

1. ✅ Export is 1080×1920, 30 fps, exactly 1,800 frames (decoded frame count verified).
2. ✅ Every illustration `assets/01`–`assets/11` appears visibly ≥ 2.5 s, in timeline order.
   The tightest slot (`11-playful-confidence`, 00:53–00:56) uses shortened 12-frame
   transition windows and holds full visibility for ~2.6 s.
3. ✅ The exact `assets/00-hope-wellness-logo.png` (uniform scaling only) closes the
   film, fully resolved from 00:56.7 to 01:00.0 (~3.3 s), plus the 3 s opening.
4. ✅ No face, hand, limb, dog, or volleyball is warped: no segmentation or mesh
   deformation was used anywhere — only uniform scale/translate parallax on
   duplicated full frames with geometric feather masks.
5. ✅ All copy sits inside safe margins (90 px sides, 140 px top, 250 px bottom);
   line widths are auto-fitted to ≤ 900 px.
6. ✅ States are MA, RI, NY, CO, AZ (00:53 “Telehealth across MA • RI • NY • CO • AZ”).
7. ✅ URL is exactly `thehopewellnesscenter.com`.
8. ✅ Audio peaks at −0.8 dBFS with a soft-knee limiter — no clipping; the mix is a
   music-and-text cut (see deviations), so no voiceover intelligibility risk.
9. ✅ Full-timeline review: 30-sample sweep (one frame every 2 s) inspected for
   composition, plus per-transition preview frames; audio checked via 5 s RMS/peak
   profile (quiet breath intro, steady −21 dB body, clean resolve, silent tail).
10. ✅ Six-frame review strip saved beside the MP4.

## Deliberate deviations from the brief

1. **Music-and-text version, no voiceover.** No licensed human voice was available
   in this environment. Per the brief (“produce a polished music and text version
   rather than using a noticeably artificial placeholder voice”), the deliverable
   carries the 72 BPM airy piano/pad score, breath swells, restrained foley
   (journal pencil, soft footsteps, volleyball taps), and the full on-screen copy
   schedule instead of narration. The VO script remains in the prompt, ready for a
   licensed session; music already leaves 5–7 dB of headroom for ducking.
2. **Geometric parallax instead of ML depth maps.** Depth-map generation was not
   available; the brief's sanctioned fallback (duplicated full frames + clean
   geometric feather masks) was used, so the illustrations are never distorted.
   Generated derivative masks/sprites are retained in `render/derived/`.

## Reproducing the render

```bash
cd render
python3 build_reel.py        # 1,800 frames -> out/reel-video.mp4 (~9 min)
python3 audio_build.py       # 60.000 s score -> out/reel-audio.wav
python3 mux_and_qa.py        # mux final MP4 + QA contract + review strip
```

Dependencies: Python 3.11+, `pillow`, `numpy`, `imageio-ffmpeg` (bundled ffmpeg 7).
Fonts (Poppins, Lora Italic — Google Fonts, OFL) are vendored in `render/fonts/`.
The renderer is deterministic: fixed seeds, no timestamps.
