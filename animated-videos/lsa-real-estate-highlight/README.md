# LSA & SEO for Real Estate — 3D Animated Highlight

A ~60-second **fully 3D (WebGL)** animated highlight built with
[Remotion](https://remotion.dev) + [Three.js](https://threejs.org), based on
the video **"Google Local Service Ads (LSA) & SEO for Real Estate Agents"** by
Mac Frederick / Momentum Digital ([source short](https://youtu.be/18aAUyyFYjY)).

Rendered vertical (1080×1920, 30fps) for Shorts / Reels / TikTok. Opens with the
**Momentum logo as a 3D metallic medallion**.

## What makes it 3D

Real WebGL via `@remotion/three` + `@react-three/fiber`, composited under crisp
DOM typography:

- **Logo medallion** — your logo on a spinning metallic coin (front + back),
  polished rim, glow ring (`src/three/objects.tsx` → `Medallion`)
- **3D SERP stack** — the "LSAs sit above everything" cards are real extruded
  boxes in perspective, with text rendered onto their faces via `CanvasTexture`
- **3D bar chart** — extruded, glowing bars growing on a reflective floor
- **3D trust badge** — a green Google-Guaranteed coin with a check
- **Living 3D world** — a deterministic particle field, floating wireframe
  shapes, and a noise-driven camera dolly behind every scene

Supporting motion: `@remotion/transitions` (slide/wipe/clock-wipe/fade),
`@remotion/google-fonts` (Poppins + Inter), kinetic headline reveals, count-up
stats, and faux-extruded 3D text via layered shadows.

### Skills consulted

Built using guidance from the repo's skills: **`demo-video`** (producer mindset
— every scene has one job; hook → proof → logo arc), **`video-content-strategist`**
(hook/messaging), and brand discipline from **`alignhcm-carousel-video`**. Note:
this reel's brand is **Momentum (blue)** to match the logo + content, not the
AlignHCM orange.

## Output & compositions

- `out/lsa-real-estate-highlight.mp4` — the rendered 3D video
- Remotion comps: **`Highlight`** (3D, main) and **`Highlight2D`** (the earlier
  flat motion-graphics version, kept for reference)

## Develop / preview

```bash
npm install --legacy-peer-deps   # r3f v9 peer ranges
npm start                        # Remotion Studio
```

## Render

```bash
npm run render     # 3D version  (Highlight)
npm run render2d   # 2D version  (Highlight2D)
```

WebGL must render in your environment. On a machine with a GPU the default works;
**headless / CI** needs software GL — this is why the script passes `--gl=angle`.
Also point Remotion at a Chromium **headless shell**:

```bash
npx remotion render Highlight out/lsa-real-estate-highlight.mp4 \
  --gl=angle --concurrency=4 \
  --browser-executable=/path/to/chrome-headless-shell
```

If `@remotion/google-fonts` can't reach `fonts.gstatic.com` because you're behind
a TLS-intercepting proxy, add `--ignore-certificate-errors` (sandbox-only).

## Editing

- 2D layout / copy / timing: `src/Highlight3D.tsx` (scenes + master timeline)
- 3D objects: `src/three/objects.tsx`; world/lighting/camera: `src/three/world.tsx`
- Brand colors + fonts: `src/theme.ts`
- Swap the logo: replace `public/logo.png` (square; the medallion crops it to a circle)
