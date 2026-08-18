---
name: alignhcm-brand-system
description: Exact, portable Align HCM and SmartCare brand production system with the bundled primary PowerPoint reference, exact Align deck logo, deterministic client-logo placement, surface-specific color and type tokens, deck layouts, web/editorial/data-visualization rules, LinkedIn carousel and motion systems, accessibility checks, and voice/copy guidance. Use for any Align HCM or SmartCare deck, proposal, presentation, Word document, report, one-pager, HubSpot page, landing page, email, ad, social graphic, carousel, video, or brand review. Use especially when a deck must identify the client from its brief, source and verify that client's logo, and render in the exact Align master style. Co-branding a client's logo onto an Align deck is exactly what this skill is for. Do not use it to produce a non-Align company's own brand system.
---

# Align HCM brand system

Use this package as the execution authority for Align-branded work. It contains
the production assets, not pointers to a missing machine folder.

## Ownership

| Role | Who | Responsibility |
|---|---|---|
| Brand owner | Align HCM marketing lead | Approves the deck master, token changes, and any new surface palette |
| Contributor | Anyone producing Align work | Uses this package as-is and reports drift |

Practical rules for anyone outside the brand owner's team:

- **Do not replace `assets/templates/Align-HCM-Primary-Deck-Reference.pptx`
  yourself.** Submit a proposed master to the brand owner. On approval they
  replace the file, re-run `extract_pptx_theme.py`, and update the SHA-256 in
  `references/powerpoint-deck-system.md` and `CHANGELOG.md`.
- **Do not add a color or typeface** without production evidence naming the
  shipped file it came from. See the rule at the end of `references/tokens.md`.
- **If a token looks wrong**, raise it with the brand owner rather than editing
  locally. Local edits silently fork the standard.

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
scrubbed clone of the exact seven-slide authority supplied by the brand owner:
geometry, styles, colors, type, icons, and Align artwork are preserved, while
the prior client's logo, contacts, pricing, and engagement data are removed. The
Align lockup is also bundled at `assets/logos/align-hcm-deck-lockup.png`.

### The template carries 15 placeholders

All 15 must be filled or `validate_client_deck.py` fails. Five are covered by
named flags; the other ten need `--replace`. Run
`python scripts/prepare_client_deck.py --list-placeholders ...` to print this
inventory from the file itself.

| Placeholder | Slides | How to fill |
|---|---|---|
| `{{CLIENT}}` | 1, 2, 4, 5, 6 | `--client-name` |
| `{{ENGAGEMENT}}` | 1, 2 | `--engagement-title` |
| `{{DECK_TYPE}}` | 1 | `--deck-type` |
| `{{DATE}}` | 1 | `--date` |
| `{{ALIGN_CONTACT}}` | 7 | `--replace` |
| `{{CONTACT_EMAIL}}` | 7 | `--replace` |
| `{{CONTACT_PHONE}}` | 7 | `--replace` |
| `{{COUNT}}` | 2, 5 | `--replace` |
| `{{FEE}}` | 5 | `--replace` |
| `{{GO_LIVE}}` | 2, 3, 5 | `--replace` |
| `{{PHASE_2_SCOPE}}` | 5 | `--replace` |
| `{{PRICE}}` | 5 | `--replace` |
| `{{SOURCE_PLATFORM}}` | 2, 4 | `--replace` |
| `{{TARGET_PLATFORM}}` | 2, 4, 5 | `--replace` |
| `{{WORKSTREAM}}` | 2, 4, 5 | `--replace` |

`prepare_client_deck.py` reports any placeholder you miss, grouped by slide, and
exits non-zero. Pass `--allow-unresolved` only when you intend to fill the rest
by hand in PowerPoint.

1. Read the current deck brief and supporting source files. State the resolved
   client, engagement, audience, deck type, and date.
2. Obtain the client's official logo from, in order: an attached approved
   asset, the client's canonical project assets, the client's official brand
   kit, or its official website. Prefer a transparent PNG or convert an official
   SVG without modifying the artwork. Record the source locator.
3. Start from the bundled reference, filling all 15 placeholders. A complete
   worked example:

   ```bash
   python scripts/prepare_client_deck.py \
     --output acme-ukg.pptx \
     --client-name "Acme Foods" \
     --client-logo acme-logo.png \
     --engagement-title "UKG Pro Implementation" \
     --deck-type "Client Presentation" \
     --date "September 2026" \
     --replace '{{ALIGN_CONTACT}}=Jordan Reyes' \
     --replace '{{CONTACT_EMAIL}}=jordan.reyes@alignhcm.com' \
     --replace '{{CONTACT_PHONE}}=(555) 010-4477' \
     --replace '{{COUNT}}=1,200' \
     --replace '{{FEE}}=$18,000' \
     --replace '{{GO_LIVE}}=January 2027' \
     --replace '{{PHASE_2_SCOPE}}=Benefits and Recruiting' \
     --replace '{{PRICE}}=$142,000' \
     --replace '{{SOURCE_PLATFORM}}=ADP Workforce Now' \
     --replace '{{TARGET_PLATFORM}}=UKG Pro' \
     --replace '{{WORKSTREAM}}=Core HR and Payroll'
   ```

   Every value above is a placeholder for real engagement data. Take them from
   the current brief, never from this example and never from the reference deck.

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

Extraction is an onboarding and drift-audit tool, not a runtime dependency. Run
`extract_pptx_theme.py` when the brand owner has approved and installed a new
master, or when auditing whether the bundled reference has drifted. Producing a
deck never requires it.

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
| `references/powerpoint-tokens.json` | Machine-readable form of the generated measurements |
| `CHANGELOG.md` | Revision history, repository audit, and known limitations |
| `INTEGRATION.md` | Cross-references owed by downstream Align document skills |
| `RELEASE-READINESS.md` | What must be true before sharing this skill, and who can do each part |
| `scripts/selftest.py` | 22 checks proving the documented workflow runs. Run before publishing any edit |

## Two surfaces produce net-new copy

The historical SmartCare GTM document and the original LinkedIn carousel source
HTML are unavailable and cannot be recovered from any repository. Structure and
messaging for those two surfaces survived only as summaries.

**SmartCare copy and new carousels produced from this skill are net-new and
require review before publishing.** Say so when you deliver them. Do not present
reconstructed wording as approved copy.

## Composition with other skills

Any Align skill that produces a client-facing file must load this package
before building. Wired up today:

| Skill | What it builds | Status |
|---|---|---|
| `rfp-responder` | RFP and RFI responses | Loads the formal-document tokens at Step 0 |

It loads `references/tokens.md` (formal documents section) plus the bundled
Align lockup, and gates on `brand_lint.py --surface document`.

`INTEGRATION.md` carries the paste-in block for wiring up any further document
skill, and records which previously-named skills could not be found.

General composition:

- Use a PowerPoint file-manipulation skill for mechanics, but always begin from
  the bundled Align reference and keep this skill's validation gate.
- Use presentation strategy skills to shape the narrative before applying the
  visual system.
- **Never take colors or type from a generic design skill, a preset theme
  library, or any source that does not name the shipped Align file it was
  measured from.** Generic skills carry their own palettes and will silently
  override Align tokens. If a value cannot be traced to production evidence, it
  is not an Align token.

This is a standard `SKILL.md` package with relative assets and stdlib scripts.
It is usable by Claude Code and Codex without machine-specific source pointers.
