---
name: alignhcm-brand-system
description: Exact, portable Align HCM and SmartCare brand production system with the bundled primary PowerPoint reference, exact Align deck logo, deterministic client-logo placement, surface-specific color and type tokens, deck layouts, web/editorial/data-visualization rules, LinkedIn carousel and motion systems, accessibility checks, and voice/copy guidance. Use for any Align HCM or SmartCare deck, proposal, presentation, Word document, report, one-pager, HubSpot page, landing page, email, ad, social graphic, carousel, video, or brand review. Use especially when a deck must identify the client from its brief, source and verify that client's logo, and render in the exact Align master style. Do not use for Anthropic's brand or another client.
---

# Align HCM brand system

Use this package as the execution authority for Align-branded work. It contains
the production assets, not pointers to a missing machine folder.

## Non-negotiable contract

1. Identify the output surface before selecting tokens.
2. Load only the reference files required for that surface.
3. Use bundled artwork. Never redraw, typeset, trace, or image-generate a logo.
4. Resolve the exact client and logo from the current brief or source material.
   Do not infer a client from an old filename or the bundled reference content.
5. Fail closed when the client identity, logo provenance, or approved copy is
   ambiguous.
6. Run the surface linter and the output-specific validation before delivery.

## Surface selector

| Work | Required references | Gate |
|---|---|---|
| PowerPoint or sales deck | `powerpoint-deck-system.md`, `powerpoint-tokens.md`, `logo-imagery-data-visualization.md` | `validate_client_deck.py` plus rendered-slide review |
| Word document, report, one-pager | `tokens.md`, `logo-imagery-data-visualization.md`, `voice-and-copy.md` | `brand_lint.py --surface document` plus PDF review |
| Web or HubSpot | `tokens.md`, `logo-imagery-data-visualization.md`, `voice-and-copy.md` | `brand_lint.py --surface web` plus responsive/accessibility review |
| LinkedIn or static social | `carousel-and-motion.md`, `tokens.md`, `voice-and-copy.md` | `brand_lint.py --surface social` |
| Video or motion | `carousel-and-motion.md`, `tokens.md`, `voice-and-copy.md` | `brand_lint.py --surface motion` plus frame review |
| Blog or editorial HTML | `tokens.md`, `logo-imagery-data-visualization.md`, `voice-and-copy.md` | `brand_lint.py --surface editorial` |

## Exact deck workflow

The bundled reference is
`assets/templates/Align-HCM-Primary-Deck-Reference.pptx`. It is a privacy-
scrubbed clone of the exact seven-slide authority supplied by Dillon: geometry,
styles, colors, type, icons, and Align artwork are preserved, while the prior
client's logo, contacts, pricing, and engagement data are removed. The Align
lockup is also bundled at `assets/logos/align-hcm-deck-lockup.png`.

1. Read the current deck brief and supporting source files. State the resolved
   client, engagement, audience, deck type, and date.
2. Obtain the client's official logo from, in order: an attached approved
   asset, the client's canonical project assets, the client's official brand
   kit, or its official website. Prefer a transparent PNG or convert an official
   SVG without modifying the artwork. Record the source locator.
3. Start from the bundled reference:

   ```bash
   python scripts/prepare_client_deck.py \
     --output <working-deck>.pptx \
     --client-name "<verified client>" \
     --client-logo <verified-logo>.png \
     --engagement-title "<engagement>" \
     --deck-type "<deck type>" \
     --date "<month year>"
   ```

4. Rewrite every reference-specific body value from the current brief. Never
   carry the sample client, people, price, dates, scope, or timeline forward.
5. Preserve the template's fields, grid, footer rhythm, and named logo zones.
   Clone the closest designed slide instead of rebuilding from a blank layout.
6. Validate the editable deck:

   ```bash
   python scripts/validate_client_deck.py <working-deck>.pptx \
     --client-name "<verified client>" \
     --client-logo <verified-logo>.png
   ```

7. Render every slide and compare it with the bundled reference. Check client
   logo aspect ratio and optical size, Align logo fidelity, overflow, contrast,
   table legibility, footer sequence, and source notes.

Extraction is an onboarding and drift-audit tool, not a runtime dependency.
Run `extract_pptx_theme.py` only when Dillon supplies a newer master or when the
bundled reference may have changed.

## Assets and references

| Path | Purpose |
|---|---|
| `assets/templates/Align-HCM-Primary-Deck-Reference.pptx` | Exact primary deck visual authority |
| `assets/logos/align-hcm-deck-lockup.png` | Exact deck lockup extracted once from that authority |
| `references/powerpoint-deck-system.md` | Slide recipes, client co-branding, and deck QA |
| `references/powerpoint-tokens.md` | Generated measurements, painted colors, fonts, and picture zones |
| `references/tokens.md` | Surface-specific token ledger and precedence |
| `references/logo-imagery-data-visualization.md` | Logo, imagery, chart, and accessibility rules |
| `references/carousel-and-motion.md` | Social carousel and motion systems |
| `references/voice-and-copy.md` | Align voice and SmartCare messaging |
| `references/provenance-and-conflicts.md` | Repository audit and conflict rulings |

## Composition with other skills

- Use a PowerPoint file-manipulation skill for mechanics, but always begin from
  the bundled Align reference and keep this skill's validation gate.
- Use presentation strategy skills to shape the narrative before applying the
  visual system.
- Do not use `cool-data-elements` for Align. It hardcodes unverified colors.
- Do not use Anthropic's `brand-guidelines` skill for Align.

This is a standard `SKILL.md` package with relative assets and stdlib scripts.
It is usable by Claude Code and Codex without machine-specific source pointers.
