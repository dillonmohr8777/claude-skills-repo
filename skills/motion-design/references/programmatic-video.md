# Programmatic Video Ads with Remotion

Write video as React → render to MP4 → parametrize + batch for A/B variations. Perfect for scaling ad creative from one composition.

## Setup

```bash
npm create video@latest       # scaffold a Remotion project
npm i                          # then edit src/
npx remotion studio            # live preview in browser
npx remotion render <Comp> out/ad.mp4
```

## A parametrized ad composition

One composition, many variants — pass copy/colors/product as `props`.

```tsx
// src/Ad.tsx
import { AbsoluteFill, Img, interpolate, spring,
  useCurrentFrame, useVideoConfig, Sequence } from "remotion";

export type AdProps = {
  headline: string; cta: string; product: string;
  bg: string; accent: string;
};

export const Ad: React.FC<AdProps> = ({ headline, cta, product, bg, accent }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  // Product pops in with a spring (frames 0–20)
  const pop = spring({ frame, fps, config: { damping: 14 } });
  // Headline rises + fades in (frames 15–35)
  const hOpacity = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: "clamp" });
  const hY = interpolate(frame, [15, 35], [40, 0], { extrapolateRight: "clamp" });
  // CTA pulses near the end
  const pulse = 1 + 0.05 * Math.sin(frame / 4);

  return (
    <AbsoluteFill style={{ background: bg, justifyContent: "center", alignItems: "center", fontFamily: "Inter, sans-serif" }}>
      <Sequence from={0}>
        <Img src={product} style={{ width: width * 0.5, transform: `scale(${pop})` }} />
      </Sequence>
      <h1 style={{ color: "#fff", fontSize: 72, opacity: hOpacity, transform: `translateY(${hY}px)`, textAlign: "center", padding: "0 60px" }}>
        {headline}
      </h1>
      <Sequence from={60}>
        <div style={{ background: accent, color: "#000", fontSize: 40, fontWeight: 700,
          padding: "20px 48px", borderRadius: 999, transform: `scale(${pulse})` }}>
          {cta}
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};
```

```tsx
// src/Root.tsx — register sizes; reuse one component
import { Composition } from "remotion";
import { Ad } from "./Ad";

const defaults = { headline: "New Drop", cta: "Shop Now",
  product: "/product.png", bg: "#0b0b0b", accent: "#7CFC00" };

export const Root = () => (
  <>
    <Composition id="Square"    component={Ad} durationInFrames={90} fps={30} width={1080} height={1080} defaultProps={defaults} />
    <Composition id="Story"     component={Ad} durationInFrames={90} fps={30} width={1080} height={1920} defaultProps={defaults} />
    <Composition id="Landscape" component={Ad} durationInFrames={90} fps={30} width={1920} height={1080} defaultProps={defaults} />
  </>
);
```

## Batch-render variants (A/B at scale)

```bash
# One variant with overridden props
npx remotion render Square out/spring-drop.mp4 \
  --props='{"headline":"20% Off Today","cta":"Claim Deal","accent":"#FF4D4D"}'
```

```js
// scripts/batch.mjs — render a matrix of variants
import { execSync } from "node:child_process";
const variants = [
  { headline: "New Drop",       cta: "Shop Now",   accent: "#7CFC00" },
  { headline: "20% Off Today",  cta: "Claim Deal", accent: "#FF4D4D" },
  { headline: "Back in Stock",  cta: "Get Yours",  accent: "#00B4FF" },
];
variants.forEach((v, i) => {
  const props = JSON.stringify(v).replace(/"/g, '\\"');
  execSync(`npx remotion render Square out/ad-${i}.mp4 --props="${props}"`, { stdio: "inherit" });
});
```

## Ad craft that converts

- **Hook in 0–2s.** Motion or bold claim in the first frames or viewers scroll past.
- **Sound-off default.** Burn in captions; don't rely on audio.
- **Brand + CTA at the end**, held long enough to read (~1s+).
- **Safe zones** for story/reel (keep text off the top/bottom ~15% where UI overlays sit).
- **Vertical first** for reels/stories/TikTok; render square + landscape from the same comp.
- Pair with `ad-creative` for the copy matrix and (for cannabis) `cannabis-compliance` to filter claims before rendering.

## Alternatives

- **Motion Canvas** — timeline-first, great for explainer/tech animations.
- **FFmpeg** — stitch/overlay/transcode finished frames or clips.
- **Lottie → video** — export designer animations, composite in Remotion.
