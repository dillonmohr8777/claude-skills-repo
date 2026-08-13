# Align HCM — carousel and motion systems

Two animated surfaces with different token sets. Consolidated from the legacy
`alignhcm-carousel-video` skill and from `gfx3.html` / `deck8.html`.

---

# LinkedIn carousel (1080 × 1350 portrait)

The May-6 production standard. Multiple carousels have shipped in this format.
**Structure is fixed. Copy is variable. Tokens are non-negotiable.**

## The 8-slide arc

| # | Slide | Content |
|---|---|---|
| 1 | Hero | Big affirming statement |
| 2 | Transition | The reframing "but…" |
| 3 | Problem | 3 bullet items with orange-bar accents |
| 4 | Principle | Best-practice reframe |
| 5 | Solution | SmartCare intro + 5-feature grid |
| 6 | Support model | 3-chip differentiator row |
| 7 | Value close | Glass panel reinforcement |
| 8 | CTA | Dark ground, two-line hero, URL |

Do not restructure the arc without confirming first.

## Tokens

- CTA gradient: `linear-gradient(135deg, #F05A28 0%, #FF6B35 100%)` + shimmer loop
- Ground: `#0A1628`, panels `#2D3748`, secondary accent `#2BB5A0`
- Type: Inter (standard) **or** DM Sans + Syne (premium). Not both systems.
- Letter-spacing `-0.01em` to `-0.045em`, never default

## Signature effects

- **CTA shimmer** — looping sheen across the gradient button
- **Arrow nudge** — small horizontal drift on the CTA arrow
- **Text underline** — accent word animates `scaleX(0) → scaleX(1)`, 0.6s,
  `transform-origin: left`
- **Glass panels** — `backdrop-filter: blur(20–24px)`
- **Ambient glow** — 120px blur blob, top or bottom corner, low opacity

## Output format

A single standalone HTML file, openable in Chrome and screen-recorded at
1080 × 1350. No build step, no framework, no external dependencies beyond
Google Fonts.

**Do not attempt to render MP4 directly.** The video is produced by screen
recording the HTML.

## Confirm before writing

- Topic and angle
- Accent word per slide (or propose and confirm)
- Standard or premium aesthetic
- CTA destination URL (defaults to the SmartCare page on alignhcm.com)

> The original template spec and starting HTML
> (`smartcare-carousel-template.md`, `may-6-smartcare-carousel.html`) are **not
> in any repository** — verified missing as of 2026-07-16. The structure above
> is what survived in the skill prose. Ask for the source HTML if an exact fork
> is needed.

---

# Motion graphics (1920 × 1080)

The verified motion master is `gfx3.html`, from the Align HCM Maher/Brent ROI
video. A reusable engine derived from it lives at
`align-hcm-public-content/video-production/source-package/deliverables/_engine/deck8.html`.

## Environment

```css
background:
  radial-gradient(140% 110% at 82% 8%, rgba(53,118,201,.34) 0%, rgba(53,118,201,0) 46%),
  radial-gradient(90% 80% at 12% 88%, rgba(198,90,28,.22) 0%, rgba(198,90,28,0) 52%),
  radial-gradient(70% 60% at 20% 12%, rgba(198,90,28,.15) 0%, rgba(198,90,28,0) 55%),
  linear-gradient(118deg,#0A1424 0%,#0E1A2B 38%,#14305A 74%,#0B1A30 100%);
```

Plus a 96px data grid at 5.5% opacity and a radial vignette.

## Tokens

```css
--orange:#F47A25; --orange-hot:#FF9A4D; --cream:#F7F4EE;
--blue:#7FA9F0; --ink1:#0A1424; --ink2:#0E1A2B;
--steel:#8FA3BC; --steel2:#7E93AE;
```

Editorial display type is **Gelasio**; support type is **Inter**. This pair is
specific to motion — `SOURCE-NOTES.md` is explicit that these are not the
current website fonts.

## Signature elements

- **Glass diamonds** — 45°-rotated squares, 20% border radius,
  `backdrop-filter: blur(12px) saturate(135%)`, warm inner shadow, orange
  elliptical ground shadow
- **Data chips** — blurred navy pills, wide-tracked Inter 700, green for
  positive delta, orange for the highlighted value
- **Spark/bar boxes** — blurred navy cards; bars use a blue gradient, with the
  emphasis bar in `#FF9A4D → #F47A25`
- **Orbs** — thin steel-blue rings with a glowing orange node on the perimeter
- **Ghost type** — oversized Gelasio, transparent fill, 2px steel stroke at
  10% opacity, `letter-spacing: -4px`
- **Top bar** — 6px, `linear-gradient(90deg, #F47A25 0%, #F47A25 60%, #7FA9F0 100%)`
- **Footer** — 48px, `rgba(7,12,22,.90)`, orange dot + orange brand word,
  wide-tracked steel support text
- **Eyebrow** — 34×4px orange bar, then caps text in `#F4A96A` at `0.34em`

## Discipline

Restrained camera movement, kinetic headings, dimensional data elements, and
minimal end-card branding. The look is expensive because it is controlled — do
not add motion for its own sake.
