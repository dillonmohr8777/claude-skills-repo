# Web Animation Patterns

Copy-paste patterns. Reach for CSS first; use a library only when CSS can't.

## CSS — cheapest wins

```css
/* Fade + rise on mount (add .in when visible, e.g. via IntersectionObserver) */
.reveal { opacity: 0; transform: translateY(16px);
  transition: opacity .4s cubic-bezier(.4,0,.2,1), transform .4s cubic-bezier(.4,0,.2,1); }
.reveal.in { opacity: 1; transform: none; }

/* Button press feedback */
.btn { transition: transform .12s ease-out; }
.btn:active { transform: scale(.96); }

/* Skeleton shimmer loader */
@keyframes shimmer { 100% { background-position: -200% 0; } }
.skeleton { background: linear-gradient(90deg,#eee 25%,#f5f5f5 50%,#eee 75%);
  background-size: 200% 100%; animation: shimmer 1.2s linear infinite; }
```

## Scroll reveal without a library

```js
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => e.isIntersecting && e.target.classList.add("in"));
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach(el => io.observe(el));
```

## Framer Motion (React) — UI motion

```tsx
import { motion, AnimatePresence } from "framer-motion";

// Shared timing so the whole app feels consistent
export const t = { duration: 0.3, ease: [0.4, 0, 0.2, 1] };

// Staggered list entrance
const list = { show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: t } };

export function Cards({ items }: { items: string[] }) {
  return (
    <motion.ul variants={list} initial="hidden" animate="show">
      {items.map((x) => <motion.li key={x} variants={item}>{x}</motion.li>)}
    </motion.ul>
  );
}

// Enter/exit (modals, toasts)
<AnimatePresence>
  {open && (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={t}
    />
  )}
</AnimatePresence>

// Shared-layout magic (auto-animate position/size changes)
<motion.div layout transition={{ type: "spring", stiffness: 400, damping: 30 }} />
```

## GSAP — timelines & scroll-scrub (only when Framer/CSS fall short)

```js
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

gsap.timeline({ scrollTrigger: { trigger: ".hero", start: "top top",
  end: "+=100%", scrub: true, pin: true } })
  .to(".hero h1", { y: -80, opacity: 0 })
  .from(".hero img", { scale: 1.2 }, 0);
```

## Lottie — designer vector animations

```tsx
import Lottie from "lottie-react";
import success from "./success.json";
<Lottie animationData={success} loop={false} style={{ width: 120 }} />
```

## Always

- Animate `transform` + `opacity` only for smoothness.
- Wrap non-essential motion in a reduced-motion guard.
- Keep a single source of truth for durations/easing (`t` above) so nothing drifts.
