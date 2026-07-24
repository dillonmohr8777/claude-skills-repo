# Align HCM — SmartCare · "Stabilize · Optimize · Thrive"

**Format:** 1920×1080, 16:9, 30 fps · **Runtime:** ~46 s · **Audio:** none — silent (no music, no voiceover)
**Use:** Website hero, LinkedIn (feed + Sales Nav), sales-enablement, event loop.
**Bookends:** intro + CTA present the real SmartCare logo on a **white card** with a thick orange+white gradient outline + glow (the logo's charcoal text needs a light ground).

Motion **preserves** the five finished SmartCare compositions — it does not redesign them.
Applied in order: **alignhcm-brand** (navy/black + orange glow system, logo, expert tone) ·
**video-content-strategist** (≈60 s narrative, 8–11 s chapters, blueprint→outcomes progression) ·
**epic-design** (asset inspection, depth layers, dimensional camera, directional reveals, light trails,
animated typography, inter-section transitions — ignoring its website-scroll parts) ·
**alignhcm-carousel-video** (shipped Align animation language: glass-panel reveals, icon sequencing,
accent lighting, CTA shimmer, headline treatment — 16:9, not the 8-slide portrait format) ·
**demo-video** (owns the editable project, audio, scene timing, transitions, ffmpeg render, MP4 validation) ·
**code-reviewer** (engineering QA of the JS source after build).

## Slides (5 unique — every slide distinct, no duplicates)

The supplied set had two Optimize variants and two Thrive variants. To keep every slide
unique — and to keep the frames clean (no dashboard/chart graphics, per direction) — the
film uses the clean-statement variant of each stage. The data-viz variants
(`s3-optimize-proof` with the 87% dashboard, `s5-thrive-proof` with the growth chart) are
held in `assets/plates/` but not used in the edit.

| # | Slide | File | Focus |
|---|-------|------|-------|
| 1 | Intro | — | SmartCare logo on a white card + "keeps HCM moving after go-live" |
| 2 | Overview | `s1-overview` (5/5) | the model: Stabilize · Optimize · Thrive + coverage |
| 3 | Optimize | `s2-optimize-statement` | "Optimize the system you already own" + panel + icon row |
| 4 | Thrive | `s4-thrive-statement` | "Thrive beyond support" + panel + icon row |
| 5 | CTA | — | SmartCare logo (white card) + ALIGNHCM.COM |

## Timeline (master clock · 0.45 s crossfades — never a black frame)

```
S0 Intro     0.00 → 5.60    SmartCare logo (white card) forms + tagline
S1 Overview  5.15 → 15.90   s1 · 01→02→03 cards illuminate, connector arrows energize
S2 Optimize  15.45 → 26.40  s2 · panel + checklist + icon row activate, accent underline draws
S3 Thrive    25.95 → 36.90  s4 · panel + checklist + icon row activate, accent underline draws
S4 CTA       36.45 → 45.60  SmartCare logo (white card) + Stabilize·Optimize·Thrive + ALIGNHCM.COM
```

## Audio

None — the deliverable is **silent** (no music, no voiceover, per direction). The frames
carry the piece. The cinematic-bed generator (`scripts/make_audio.py`) stays in the repo if
an audio version is ever wanted, but `scripts/build.sh` no longer muxes any audio track.

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
