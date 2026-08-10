---
name: alignhcm-brand
description: Load Align HCM / SmartCare brand tokens — exact hex codes, Google Fonts stack (Inter + DM Sans + Syne), signature visual effects (orange-to-red gradient CTAs, backdrop-blur glass panels, text-underline accent animation, ambient glow blobs), typography scale, and voice/tone rules. Use ANY time you're designing, coding, or writing visual content for Align HCM or SmartCare — LinkedIn graphics, email headers, landing pages, HubSpot modules, decks, carousels, motion graphics, ad creative, social posts. Skip if the work is non-visual copy only.
---

# Align HCM / SmartCare Brand Loader

## What this skill does

Loads the canonical brand token reference so you don't re-derive colors, fonts, or signature effects every session. The tokens come from real production files (May-6 carousel, motion graphics, premium variant) — they're already shipped and in-market.

## When to invoke

Fire this whenever Dillon asks for Align HCM or SmartCare:

- Graphics, icons, illustrations, or image generation
- Landing pages, HubSpot CMS modules, web page code
- LinkedIn carousel videos, motion graphics, animated videos
- Decks, slides, one-pagers
- Email templates, ad creative, social post graphics
- Any CSS / HTML / JSX / SVG work

Also fire whenever Dillon mentions brand, colors, fonts, logos, or visual consistency for these clients.

## How to use it

1. **Read the brand reference first:**
   `C:\Users\DillonMohr\.claude\clients\align-hcm\brand.md`
   Remote/cloud sessions can't reach that path — use the canonical token table
   below (verified 2026-08-10 against the shipped Aug 2026 editorial PDFs) and
   the vault page `dillon-os/02_FullTimeJob/AlignHCM/brand-guidelines.md`.

2. **Use exact hex codes and exact font names.** Don't paraphrase. `#FF6B2B` not "orange". `Inter` not "a sans-serif."

3. **Pair with the carousel template skill** (`alignhcm-carousel-video`) when the work is a LinkedIn carousel specifically.

4. **Pair with the SmartCare GTM skill** (`alignhcm-smartcare`) when positioning/copy also needs to match.

5. **When generating new assets**, always apply the signature effects where relevant:
   - CTA buttons → orange-to-red gradient `linear-gradient(135deg, #F05A28 0%, #FF6B35 100%)` + shimmer loop
   - Accent word in headline → text-underline animation (`scaleX(0)→scaleX(1)`, 0.6s, transform-origin left)
   - Depth panels → `backdrop-filter: blur(20–24px)` glass
   - Ambient background → 120px blur glow blob, top/bottom corner, low opacity

## What's NOT in this skill

- Messaging / positioning / pricing — that's `alignhcm-smartcare`
- Deck structure — separate skill to be built from the `.pptx` source (pending)
- Final MP4 video outputs — this skill references the HTML sources, not rendered video

## Canonical tokens (remote-safe copy, verified 2026-08-10)

Extracted from the shipped Align editorial PDF set (Aug 2026) plus the
production carousel/motion files. Exact values; do not paraphrase.

- Navy ink / masthead `#0A1628` · slate body `#2D3748` / `#4A5568` · muted `#646E7C`
- Steel blue `#1B4F72` (tint `#EDF3F8`) · muted blue on navy `#B9C6D8`
- Orange primary `#F05A28` · bright `#FF6B2B` · legacy `#E8832A` · rust kickers `#AD3D1B` (tint `#FDF1EA`)
- Teal chips `#136E61` (tint `#E9F7F4`) · product teal `#2BB5A0`
- Paper `#FCFAF7` · panel `#F5F1EA` · hairlines `#E9E4DC` · sheet total cream `#F4EFE7` · editable yellow `#FFF2CC`
- Fonts: Inter + DM Sans + Syne (web/motion); Arial in Office docs
- Exact logo (reverse, transparent 268x108):
  `dillon-os/02_FullTimeJob/AlignHCM/assets/align-hcm-logo-reverse.png` — place big, on navy

## Rule of thumb

If this skill fires, every color, font, and effect in your output should trace back to a token in `brand.md` (or the canonical table above when remote). No "close enough."
