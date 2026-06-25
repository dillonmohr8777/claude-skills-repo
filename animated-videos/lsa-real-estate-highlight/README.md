# LSA & SEO for Real Estate — 60s Animated Highlight

An animated ~60-second highlight built with [Remotion](https://remotion.dev),
based on the video **"Google Local Service Ads (LSA) & SEO for Real Estate
Agents"** by Mac Frederick / Momentum Digital
([source short](https://youtu.be/18aAUyyFYjY)).

The original is a vertical YouTube Short, so this highlight is rendered
vertical (1080×1920, 30fps) for Shorts / Reels / TikTok.

## Motion-design stack

This is not a slideshow — it leans on the Remotion plugin ecosystem:

- **`@remotion/google-fonts`** — Poppins (display) + Inter (body) typography
- **`@remotion/transitions`** — slide / wipe / clock-wipe / fade between scenes
- **`@remotion/noise`** — Perlin-noise-driven animated gradient mesh background
- **`@remotion/paths`** — draw-on underlines + animated check ticks
- **`@remotion/shapes`** — rotating decorative star / triangle outlines

Plus kinetic word-by-word headline reveals (blur → sharp, scale overshoot),
fake-glass cards, glowing count-up stat bars, and a vignette.

> Performance note: the mesh background and "glass" cards are built from
> stacked radial-gradients rather than `blur()` / `backdrop-filter`, which
> software-render ~20× faster. The full 60s renders in ~2 minutes at
> `--concurrency=4`.

## Output

The rendered video lives at `out/lsa-real-estate-highlight.mp4`.

## Scenes

1. **Intro** — Local Service Ads + SEO for Realtors
2. **The hook** — high-intent "realtor near me" searches
3. **Why LSAs win** — they appear above standard ads and organic results
4. **Built for trust** — Google Guaranteed badge, pay-per-lead, ready buyers
5. **The long game** — LSAs win today, SEO compounds over time
6. **Your playbook** — 3 moves: verify profile, run LSAs, invest in local SEO
7. **CTA outro** — Get found locally · Momentum Digital

## Develop / preview

```bash
npm install
npm start          # opens the Remotion Studio for live editing
```

## Render the MP4

```bash
npm run render
```

In a headless/CI environment without a bundled Chrome, point Remotion at an
existing Chromium **headless shell**:

```bash
npx remotion render Highlight out/lsa-real-estate-highlight.mp4 \
  --browser-executable=/path/to/chrome-headless-shell \
  --concurrency=4
```

If `@remotion/google-fonts` can't reach `fonts.gstatic.com` because you're
behind a TLS-intercepting proxy, add `--ignore-certificate-errors` (only
needed in such sandboxes; normal machines load the fonts fine).

## Editing the content

All copy, timing, colors, and animation live in `src/Highlight.tsx`. Each scene
is its own component; the master timeline at the bottom controls scene order and
duration (frames = seconds × 30).
