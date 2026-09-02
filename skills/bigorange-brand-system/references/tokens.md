# BigOrange.Marketing token ledger

One brand, several surfaces, and the approved set differs per surface. The
linter (`scripts/brand_lint.py`) mirrors this file; keep them in step.

## Precedence

1. The exact logo PNGs in `assets/logos/` (SHA-256 pinned in `assets/SHA256SUMS`). Never redraw, retype, recolor, or image-generate the logo.
2. The live WordPress theme for anything that ships into bigorange.marketing (web, editorial).
3. The deck reference `assets/templates/BigOrange-Primary-Deck-Reference.pptx` and `lib/doc-kit/theme.css` for everything BigOrange presents or hands over (deck, document, social).

When two ledgers disagree, the surface decides. Do not "fix" the site orange in a deck or the deck orange on the site.

## Colours

| Token | Hex | Deck | Document | Web / editorial | Social | Role |
|---|---|---|---|---|---|---|
| orange | `#FF7C00` | yes | yes | logo only | yes | Sampled from the logo PNG. Blocks, numerals, eyebrows, CTAs. |
| orange-deep | `#D96400` | yes | yes | no | no | Small orange text on light fields, links in PDFs. |
| theme-orange | `#F68326` | no | no | yes | no | Beaver Builder accent, primary CTA fill (observed 2026-09-02). |
| theme-orange-border | `#D66509` | no | no | yes | no | CTA border on the live site. |
| theme-orange-old | `#FF7700` | no | no | yes | no | Painted in older theme CSS (observed 2026-07-16). |
| theme-blue | `#428BCA` | no | no | yes | no | Link and nav blue on the live site. Never in decks. |
| ink | `#121212` | yes | yes | no | yes | Dark grounds, titles. |
| ink-2 | `#2B2B2B` | yes | yes | no | no | Secondary dark card. |
| theme-text | `#333333` | no | no | yes | no | Body text on the live site. |
| mute | `#6E6A66` | yes | yes | no | no | Footers, captions. |
| pith | `#F6F1EA` | yes | yes | editorial only | yes | Light card ground. |
| peel | `#FFF3E8` | yes | yes | editorial only | yes | Warm tint, direct-answer callout. |
| theme-light | `#F2F2F2` | no | no | yes | no | Theme light background. |
| line | `#E4DDD4` | yes | yes | no | no | Hairlines. |
| soft | `#CFC8C0` | yes | yes | no | no | Muted reverse text. |
| reverse | `#EDE7E0` | yes | yes | no | no | Body text on dark. |
| leaf | `#1E6B3C` | charts only | charts only | no | no | Sparse positive accent. Nod to the logo leaves. |
| white | `#FFFFFF` | yes | yes | yes | yes | |

Never use (linter errors): Align HCM `#232E3E` `#E97722` `#FF9902` `#1A334E`, Momentum `#2A80C2` `#2456C4`, and the retired v0 brown `#2B1A10`.

## Type

| Surface | Display | Body | Data / tables | Notes |
|---|---|---|---|---|
| Deck (.pptx) | Montserrat 800/700 | Arial | Arial | Montserrat matches the wordmark. Arial is metric-safe on every machine; do not use Calibri or Aptos. |
| Document (PDF) | Montserrat | Source Serif 4 | Inter | Fonts are embedded by Chromium at render time from `assets/fonts/` (see `assets/fonts/README.md`). |
| Web / editorial | Raleway | Open Sans | Open Sans | The live theme's stack. Poppins 300 appears inside Beaver Builder rich-text blocks; treat it as inherited, never add it. |
| Social | Montserrat | Arial | | |

## Sizes and rhythm (deck)

Canvas 13.333 x 7.5 in. Margin 0.6 in. Logo 1.24 x 0.42 in at (0.6, 0.42). Eyebrow 9 pt Montserrat bold, 3 pt tracking, orange. Title 30 pt Montserrat bold. Body 11.5 to 14 pt Arial. Stat values 26 to 40 pt. Footer 7 pt, slide number 10 pt bottom right with the 0.11 in orange square.

## Motif

The square block from the logo (the "crate") and oversized numerals. Use one or two orange squares per slide or page, never stripes, bars under titles, or gradients.

## Provenance

Logo PNGs: `https://bigorange.marketing/wp-content/uploads/2025/05/BOM-logo-orange.png` and `.../2023/09/BOM-logo-white.png`, captured 2026-07-16. Orange sampled from the orange PNG's dominant opaque pixel (67,049 of 70,338 opaque pixels are `#FF7C00`). Theme colours and fonts: `references/brand-research-2026-09.md`.
