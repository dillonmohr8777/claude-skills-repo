# SmartCare — "Stabilize · Optimize · Thrive" (editable motion project)

A ~60-second, 1920×1080 brand sizzle for **Align HCM · SmartCare** (post-go-live
lifecycle), built by animating the five finished SmartCare carousel frames with a
dimensional camera, staged illumination, energy-path light trails, and crisp vector
overlays — **preserving the compositions, not redesigning them.**

**Deliverables** live in [`dist/`](dist/) · treatment in [`TREATMENT.md`](TREATMENT.md) · delivery notes in [`DELIVERY.md`](DELIVERY.md).

## Skills applied (in order)
`alignhcm-brand` → `video-content-strategist` → `epic-design` → `alignhcm-carousel-video`
→ `demo-video` (owns the editable project + render + MP4 QA) → `code-reviewer` (engineering QA).

## How it works
- **`src/video.html`** — the whole film. A self-contained 1920×1080 stage driven by a
  deterministic timeline: `window.seek(t)` positions every element for time `t` (no
  wall-clock, no RAF timing) so frame capture is exact and repeatable. Fonts
  (`fonts.css`) and brand marks (`assets.css`) are embedded as data-URIs; the five
  source plates load from `assets/plates/`. Open it in Chrome and press **space** to preview.
- **`scripts/render.mjs`** — Playwright drives `seek(t)` frame-by-frame and pipes frames
  straight into ffmpeg (`image2pipe`) → H.264. No multi-GB frame dump on disk.
- **`scripts/make_audio.py`** — synthesizes the cinematic bed (pad + sub pulse + shimmer +
  transition risers, chord changes on the scene cuts) and renders the 7 edge-tts VO lines,
  ducking the bed ~6 dB under the voice.
- **`scripts/build.sh`** — one command: audio → render → mux master → 720p/muted/poster.

## Edit it
Everything creative is data at the top of `src/video.html`:
- **`SCENES[]`** — per-scene timing, camera move (`push`/`punch`), and the illumination /
  activation / overlay cues (all positions in source-plate pixels).
- Brand tokens are CSS variables in the `<style>` block (`--orange #FF8500`, etc.).
- VO copy + timing and the music design live in `scripts/make_audio.py`.
Change copy or timing, then rerun `scripts/build.sh`.

## Rebuild
```bash
scripts/build.sh          # full 30 fps master   (~8 min render in this env)
scripts/build.sh --fast   # 24 fps proof
```
**Requires:** Node + Playwright (Chromium), Python (`numpy`, `Pillow`, `imageio-ffmpeg`,
`edge-tts`). In this cloud env, set `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` and
`SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` (edge-tts trust); `build.sh` sets sane defaults.

## Regenerate embedded assets (only if you swap plates/fonts)
`fonts.css`, `assets.css`, and the extracted logos are produced from `assets/` by the
one-off snippets documented in `DELIVERY.md`.
