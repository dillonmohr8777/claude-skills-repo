# Align HCM — SmartCare · "Stabilize · Optimize · Thrive"

**Format:** 1920×1080, 16:9, 30 fps · **Runtime:** ~60 s · **Audio:** cinematic bed + AI voiceover (ducked)
**Use:** Website hero, LinkedIn (feed + Sales Nav), sales-enablement, event loop.

Motion **preserves** the five finished SmartCare compositions — it does not redesign them.
Applied in order: **alignhcm-brand** (navy/black + orange glow system, logo, expert tone) ·
**video-content-strategist** (≈60 s narrative, 8–11 s chapters, blueprint→outcomes progression) ·
**epic-design** (asset inspection, depth layers, dimensional camera, directional reveals, light trails,
animated typography, inter-section transitions — ignoring its website-scroll parts) ·
**alignhcm-carousel-video** (shipped Align animation language: glass-panel reveals, icon sequencing,
accent lighting, CTA shimmer, headline treatment — 16:9, not the 8-slide portrait format) ·
**demo-video** (owns the editable project, audio, scene timing, transitions, ffmpeg render, MP4 validation) ·
**code-reviewer** (engineering QA of the JS source after build).

## Source frames (the visual source of truth — only these five)

| Role in film | File | Composition |
|---|---|---|
| Overview | `s1-overview` (5/5) | Stabilize · Optimize · Thrive + 01/02/03 cards + "What SmartCare covers" |
| Optimize · statement | `s2-optimize-statement` | "Optimize the system you already own" (clean variant) |
| Optimize · proof | `s3-optimize-proof` | same, **with** 87% System-Health ring + Performance chart |
| Thrive · statement | `s4-thrive-statement` | "Thrive beyond support" (growth-icon variant) |
| Thrive · proof | `s5-thrive-proof` | same, **with** rising bar chart + trend line |

The two variant-pairs are edited as **wide statement → detail proof**, so each stage reads as
"claim, then evidence" — never a repeat.

## Timeline (master clock · 0.45 s crossfades — never a black frame)

```
S0 Intro       0.00 → 6.40    SmartCare logo forms + "the work that keeps HCM moving after go-live"
S1 Overview    5.95 → 16.60   s1 · 01→02→03 cards illuminate, connector arrows energize
S2 Optimize    16.15 → 25.60  s2 · panel + checklist + icon row illuminate, accent underline draws
S3 Optimize·pf 25.15 → 34.10  s3 · punch to 87% System-Health ring (fills), Performance
S4 Thrive      33.65 → 43.10  s4 · checklist + icon row illuminate, growth arrows energize
S5 Thrive·pf   42.65 → 51.30  s5 · punch to rising chart (bars + trend draw on)
S6 CTA         50.85 → 59.80  SmartCare logo + Stabilize·Optimize·Thrive + ALIGNHCM.COM (shimmer)
```

## Voiceover  (warm-confident enterprise; leaves air for the bed)

- **S0:** "Go-live is only the beginning. SmartCare keeps your HCM moving — every day after."
- **S1:** "Stabilize. Optimize. Thrive. One support model for the work that never really stops."
- **S2:** "Optimize the system you already own — sharper workflows, cleaner reporting, less friction."
- **S3:** "As configuration gets dialed in, system health climbs toward optimal."
- **S4:** "Then thrive beyond support — continuous improvement, stronger decisions, room to grow."
- **S5:** "Insights compound, performance rises, and your platform keeps paying you back."
- **S6:** "SmartCare, from Align. Stabilize, optimize, and thrive. Align H-C-M dot com."

## Brand tokens  (sampled from the SmartCare plates — exact)

```
--bg       #030303   true black field (plates are black, not navy)
--ink      #FCFCFC   headline white
--muted    #A9AEBB   body / labels
--orange   #FF8500   primary accent      (hot #FFA23A · deep #F0560E)
--orange-d #C24E00   trail shadow
CTA grad   linear-gradient(135deg,#F0560E,#FFA23A)
```

**Type:** Playfair Display (headlines/accent italics — matches the plates) · Inter (labels/body/UI/numerals).
**Marks:** Align wordmark + SmartCare heart logo, extracted from the plates themselves (no external assets).
**Signature motion:** slow dimensional camera · orange energy-path light-trails · staged glass-panel illumination ·
selective icon activation · restrained headline reveal (materialize sweep) · accent-underline draw ·
count-up 87% ring · seamless light-trail transitions · CTA shimmer.
**Non-negotiables (epic-design):** ≥3 depth layers/scene · GPU-safe props only · `prefers-reduced-motion` fallback · one focus per scene.
