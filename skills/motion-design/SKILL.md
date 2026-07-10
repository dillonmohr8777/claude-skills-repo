---
name: "motion-design"
description: "Motion and animation for web UI and programmatic video ads. Use when building UI micro-interactions, page transitions, scroll/hero animations, loading states, or generating animated video ads/social clips in code (Remotion), plus Lottie and CSS/SVG animation. Trigger on 'animate', 'animation', 'motion', 'micro-interaction', 'transition', 'scroll effect', 'Framer Motion', 'Lottie', 'Remotion', 'animated ad', 'video ad', 'hero animation', or 'make it feel alive'."
license: MIT
metadata:
  version: 1.0.0
  author: dillonmohr8777
  category: engineering
  updated: 2026-07-10
---

# Motion Design

You design motion that feels intentional, fast, and premium — for product UI and for video ads generated in code. Motion should guide attention and reinforce brand, never decorate for its own sake. Every animation earns its place or gets cut.

## First: pick the right tool for the job

| Need | Reach for | Why |
|---|---|---|
| UI micro-interactions, gestures, layout transitions (React) | **Framer Motion** | Declarative, spring physics, `layout`, `AnimatePresence` |
| Simple hovers, fades, keyframes, loaders | **CSS / Tailwind** | Zero JS, GPU-friendly, cheapest option — try this first (ponytail) |
| Complex timelines, scroll-scrub, SVG morph | **GSAP** (+ ScrollTrigger) | Best-in-class sequencing when Framer/CSS can't |
| Designer-made vector animations (illustrations, icons) | **Lottie** (`lottie-react`) | Play After Effects/JSON; tiny, scalable |
| **Programmatic video ads / social clips** rendered to MP4 | **Remotion** | Write video as React; parametrize + batch-render variations |
| One-off shape/path animation | **SVG SMIL / CSS** | No dependency |

Default to the **cheapest tool that works** — CSS before a library, one library before three. See `references/web-animation.md` and `references/programmatic-video.md`.

## Motion principles (apply to everything)

1. **Purpose** — Motion communicates: state change, spatial relationship, hierarchy, feedback. No motion without meaning.
2. **Speed** — UI feels instant. Micro-interactions **100–200ms**, transitions **200–400ms**, big/hero moments **400–600ms**. When in doubt, faster.
3. **Easing** — Almost never linear (except continuous loops/spinners). Use ease-out for entrances (fast→settle), ease-in for exits, spring for anything that should feel physical. Good default cubic-bezier: `cubic-bezier(0.4, 0, 0.2, 1)`.
4. **Choreography** — Stagger related elements (~30–60ms apart); don't animate everything at once. Lead the eye.
5. **Restraint** — One or two hero moments per screen. If everything moves, nothing stands out.
6. **Performance** — Animate only `transform` and `opacity` (GPU-composited). Avoid animating `width/height/top/left/box-shadow` — they trigger layout/paint. Use `will-change` sparingly.
7. **Accessibility** — ALWAYS honor `prefers-reduced-motion`: reduce/replace movement with fades or none. This is non-negotiable.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Workflow

1. **Clarify intent** — Which surface (UI vs. video ad)? What should the motion *say*? Brand tone (playful / premium / techy)?
2. **Choose the tool** from the table. Justify anything heavier than CSS.
3. **Spec the motion** — trigger, duration, easing, properties, choreography — before coding.
4. **Implement** minimally; reuse a shared `transition`/variants object so timing is consistent across the app.
5. **Verify** — smooth at 60fps, respects reduced-motion, no layout thrash, degrades gracefully.

## For video ads specifically (Remotion)

- Parametrize copy, colors, logo, product shot as `props` → render N variants for A/B testing from one composition (pairs well with the `ad-creative` skill).
- Standard sizes: 1080×1080 (square), 1080×1920 (story/reel), 1920×1080 (landscape), 1200×628 (static). Build one composition, resize via config.
- Keep hooks in the **first 1–2 seconds**; captions on (sound-off viewing); brand + CTA in the last frames.
- Render with `npx remotion render`; batch via a props matrix.
- See `references/programmatic-video.md`.

## References

- `references/web-animation.md` — Framer Motion + CSS + GSAP + Lottie patterns (copy-paste)
- `references/programmatic-video.md` — Remotion setup, a parametrized ad composition, batch rendering
- `references/easing-cheatsheet.md` — durations, easing curves, spring configs
