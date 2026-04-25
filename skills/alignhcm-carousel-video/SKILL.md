---
name: alignhcm-carousel-video
description: Produce SmartCare / Align HCM LinkedIn carousel videos using the canonical 8-slide template (1080×1350 portrait, vanilla HTML+CSS+JS, Inter font, orange #FF6B2B accent). Use when Dillon asks for a new LinkedIn carousel, carousel video, slide deck animation, or post-and-MP4 asset for Align HCM or SmartCare. Loads the production template (hero → transition → problem → principle → solution → support → value → CTA) and brand tokens so new carousels match the May-6 standard without re-deriving structure. Not for short-form motion graphics (use smartcare-motion.html as reference) or for general decks.
---

# SmartCare LinkedIn Carousel Skill

## What this skill does

Produces new LinkedIn carousels that match the production May-6 standard — same 8-slide arc, same brand tokens, same animation patterns — without re-deriving the system each time. Dillon has already shipped multiple carousels in this format; this skill is the reusable mold.

## When to invoke

Fire on any of these:

- "Make a SmartCare carousel"
- "New LinkedIn carousel for Align"
- "Carousel video for [topic]"
- Any request that mentions LinkedIn carousel + Align HCM or SmartCare
- Requests for the "post + video" combo Dillon ships to LinkedIn

Do NOT fire for:
- Short motion-graphics loops (16:9, 24s) — those use `smartcare-motion.html` as reference, not the carousel template
- Full-deck presentations (`.pptx`) — separate skill (pending)
- Text-only LinkedIn posts — no carousel needed

## How to use it

1. **Always read both context files first:**
   - `C:\Users\DillonMohr\.claude\clients\align-hcm\smartcare-carousel-template.md` (the 8-slide spec)
   - `C:\Users\DillonMohr\.claude\clients\align-hcm\brand.md` (tokens)

2. **Fork, don't rebuild.** Use `C:\Users\DillonMohr\Downloads\may-6-smartcare-carousel.html` as the starting HTML. Swap copy, don't restructure.

3. **Keep the 8-slide arc** unless Dillon says otherwise:
   - Slide 1: Hero (big affirming statement)
   - Slide 2: Transition (the reframing "but...")
   - Slide 3: Problem (3 bullet items with orange-bar accents)
   - Slide 4: Principle (best-practice reframe)
   - Slide 5: Solution (SmartCare intro + 5-feature grid)
   - Slide 6: Support model (3-chip differentiator row)
   - Slide 7: Value close (glass panel reinforcement)
   - Slide 8: CTA (dark, two-line hero, URL)

4. **Voice rules** (from `brand.md`):
   - Headlines: 8–15 words, direct, one accent word per headline gets the underline
   - Keep recurring phrases: "Go-live," "proactive," "no queue no chatbot," "stabilize → optimize → accelerate → transform"
   - Never default letter-spacing — always `-0.01em` to `-0.045em`

5. **Brand rules** (from `brand.md`):
   - Orange `#FF6B2B` primary
   - Font: Inter (standard) or DM Sans + Syne (premium variant)
   - CTA gradient: `linear-gradient(135deg, #F05A28 0%, #FF6B35 100%)`
   - Signature effects: CTA shimmer, arrow nudge, text underline animation, ambient glow blobs

6. **Output format:** single standalone HTML file that Dillon can open in Chrome and screen-record at 1080×1350 for LinkedIn upload. No build step, no framework, no external dependencies beyond Google Fonts.

## What to ask Dillon if missing

Before writing, confirm:
- **Topic / angle** — what's this carousel about? (e.g. "manufacturing HCM challenges")
- **Accent word per slide** — or let you pick and confirm
- **Standard or premium aesthetic** — Inter + light, or DM Sans/Syne + dark glows
- **CTA destination URL** — defaults to `alignhcm.com` SmartCare page if not specified

## What's NOT in this skill

- The MP4 render step — Dillon screen-records the HTML manually. Do not try to generate video directly.
- The copy-only LinkedIn post that ships with the carousel — that's a content task, separate.
- Motion graphics (16:9 looping ads) — different format, different source file.

## Rule of thumb

Structure is fixed. Copy is variable. Brand tokens are non-negotiable. If you're restructuring the slide arc or inventing a new color, stop and confirm with Dillon.
