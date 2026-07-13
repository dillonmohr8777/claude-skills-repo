# The Ironic Ineptocracy — Site Build

Source files for the rebuild of **ironicineptocracy.com**, injected into WordPress.com via Customizer Additional CSS and per-section Custom HTML blocks.

---

## Status

| Step | Deliverable | State |
|---|---|---|
| 1 | Brand system + design tokens | **Done** |
| 2 | Site architecture (URL map, internal linking) | Next |
| 3 | Bleeding flag Three.js hero block | Pending |
| 4 | Homepage sections 2–7 | Pending |
| 5 | "Enter the World" surveillance page | Pending |
| 6 | Book / Author / Dispatches pages | Pending |
| 7 | A11y + perf audit pass | Pending |

---

## Step 1 — What was produced

**Files:**

- `styles/tokens.css` — paste into WordPress.
- `brand/brand-guidelines.md` — the spec.

**What `tokens.css` contains:**

- The 8-anchor color palette plus blood / brass / parchment / terminal-green scales
- Semantic role variables (`--ii-text`, `--ii-accent`, `--ii-danger`)
- Four font families loaded from Google Fonts in one `@import`
- Fluid type scale via `clamp()` from 12px caption to 160px hero display
- 8pt grid spacing tokens
- Section rhythm, content width, prose width
- Borders, radii (mostly sharp — distressed-document aesthetic)
- Atmospheric shadows (blood glow, brass glow, terminal glow, vignette)
- Motion tokens mapped to GSAP eases (`power3.out`, `expo.out`)
- Z-index layer system
- `.ii-display`, `.ii-quote`, `.ii-redacted`, `.ii-prose`, `.ii-cta`, `.ii-section` baseline classes
- `.ii-scanlines`, `.ii-grain`, `.ii-vignette` overlay hooks
- `prefers-reduced-motion` kill-switch that nukes durations to 0
- Focus ring (brass, 9.4:1 contrast on black)
- `::selection` color (blood)

---

## How to install (one-time, ~2 minutes)

1. Log in to **dillonmohr8777-mtapu.wordpress.com** (or whatever the active admin URL is for ironicineptocracy.com).
2. Go to **Appearance → Customize → Additional CSS**.
3. Open `styles/tokens.css` from this repo.
4. Copy the **entire file** and paste it into the Additional CSS panel.
5. Click **Publish**.
6. Verify: load the homepage. The page background should now be near-black (`#0A0A0A`) and body text should be parchment. If it's still the theme default, the active theme is overriding `body` — wrap pages in `<div class="ii-root">` instead (the same baseline rules apply to that class).

---

## How per-section blocks reference the tokens

Each upcoming Custom HTML block uses CSS variables, never raw hex. Example skeleton for any future section:

```html
<section class="ii-section" id="ii-section-name">
  <div class="ii-container">
    <h2 class="ii-display" style="font-size: var(--ii-fs-2xl);">Section heading</h2>
    <p class="ii-prose">Body paragraph in parchment serif.</p>
    <a href="#" class="ii-cta">Call to action</a>
  </div>
</section>

<style>
  /* Block-scoped overrides only. Never redefine tokens here. */
  #ii-section-name { background: var(--ii-bg-deep); }
</style>
```

---

## Branch & commit hygiene

All work is on `claude/book-documentation-0FjSm`. Each step ships as its own commit so installation can be staged page-by-page.

---

## Reference

- `brand/brand-guidelines.md` — voice rules, contrast pairings, audit checklist
- Brief: see the original prompt (kept out of repo for length)
