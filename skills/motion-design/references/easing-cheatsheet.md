# Easing & Timing Cheatsheet

## Durations (UI)

| Motion | Duration |
|---|---|
| Micro-interaction (hover, press, toggle) | 100–200ms |
| Standard transition (fade, slide, expand) | 200–400ms |
| Hero / page transition | 400–600ms |
| Large full-screen / onboarding | 600–800ms (rare) |

Faster feels more responsive. If unsure, cut 100ms.

## Easing curves (cubic-bezier)

| Use | Curve | Feel |
|---|---|---|
| Entrance (element appears) | `cubic-bezier(0, 0, 0.2, 1)` (ease-out) | fast in, gentle settle |
| Exit (element leaves) | `cubic-bezier(0.4, 0, 1, 1)` (ease-in) | eases away |
| Move on screen (both ends visible) | `cubic-bezier(0.4, 0, 0.2, 1)` (standard) | balanced |
| Emphasis / playful | `cubic-bezier(0.34, 1.56, 0.64, 1)` | slight overshoot |
| Continuous (spinner, marquee) | `linear` | constant |

**Rule:** never `linear` except for continuous loops.

## Spring configs (Framer Motion / Remotion)

```js
// Snappy UI (buttons, toggles)
{ type: "spring", stiffness: 400, damping: 30 }
// Smooth layout shifts
{ type: "spring", stiffness: 260, damping: 26 }
// Bouncy / playful
{ type: "spring", stiffness: 300, damping: 12 }
// Remotion spring
spring({ frame, fps, config: { damping: 14, stiffness: 100 } })
```

## Video (frames)

- 30fps standard for social; 60fps for ultra-smooth UI capture.
- Hook: land the first beat by frame ~15 (0.5s @30fps).
- Hold CTA ≥ 30 frames (1s) so it's readable.
- Total ad length: 6–15s (180–450 frames @30fps) for paid social.

## Stagger

- Related items: 30–60ms apart.
- Lists: cap total stagger ~300ms so the last item isn't slow.

## Reduce motion

Always ship the `prefers-reduced-motion: reduce` guard — replace movement with instant/opacity-only. See SKILL.md.
