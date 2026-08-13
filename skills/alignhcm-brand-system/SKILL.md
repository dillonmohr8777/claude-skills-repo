---
name: alignhcm-brand-system
description: The single source of truth for Align HCM and SmartCare brand identity — exact per-surface color tokens, font stacks, the PowerPoint master template system, LinkedIn carousel structure, motion-graphics tokens, and voice/copy rules. Use ANY time you design, build, write, or review something branded for Align HCM or SmartCare — PowerPoint decks, slides, presentations, Word documents, LinkedIn carousels, motion graphics, video, landing pages, HubSpot CMS modules, email templates, ad creative, social graphics, blog HTML, reports, or one-pagers. Also use when asked about Align brand colors, the Align orange, Align fonts, logo usage, deck templates, or whether an asset is on-brand. Replaces the older alignhcm-brand, alignhcm-carousel-video, and alignhcm-smartcare skills. Do NOT use for Anthropic's own brand (that is `brand-guidelines`) or for other clients.
---

# Align HCM / SmartCare — brand system

Consolidates every Align branding asset found across the account into one
package, and makes the PowerPoint master template the authority for deck work.

## The one thing to get right

**Align does not have a single orange.** It has four in active production use,
one per surface, and they are not interchangeable:

| Surface | Orange |
|---|---|
| Web / HubSpot | `#FF9902` |
| PowerPoint decks | *from the template* — see below |
| LinkedIn carousel / social | `#F05A28` → `#FF6B35` gradient |
| Video / motion | `#F47A25` |
| Blog / long-form | `#FF6B2B` |

Using the web orange in a deck is the most common way Align work goes off-brand.
**Identify the surface before picking any token.**

Never use `#E8760A` or `#414042`. They appear in zero production files.

## How to use this skill

1. **Identify the surface.** Deck, web, social, motion, editorial, or document.
2. **Load the token table for that surface** from `references/tokens.md`.
3. **For decks, ingest the template first** (below). It outranks everything else.
4. **Apply voice rules** from `references/voice-and-copy.md` to any copy —
   especially the no-em-dashes rule, which is absolute.
5. **Lint before shipping:**
   ```bash
   python3 scripts/brand_lint.py --surface <surface> <files>
   ```

## PowerPoint decks — start here

Put the master template in `assets/templates/`, then run:

```bash
python3 scripts/extract_pptx_theme.py assets/templates/<file>.potx \
  --md references/powerpoint-tokens.md \
  --json references/powerpoint-tokens.json
```

Stdlib only — no `python-pptx` required. This pulls the exact theme colour
slots, the major/minor font pair, slide geometry, the full layout inventory, and
every colour actually painted on the masters. The generated
`references/powerpoint-tokens.md` then becomes authoritative for all deck work.

Build on the **named layouts** the extractor reports. Reference colours as theme
slots (`accent1`), not literals, and fonts as `+mj-lt` / `+mn-lt` — that is what
survives a template update.

Full deck spec, structure, and shipping checks: `references/powerpoint-deck-system.md`.

> **Status: no Align `.potx` exists in any of the eight repositories searched.**
> The deck ledger in `tokens.md` is intentionally empty rather than guessed.
> What is currently known about the master comes from a screenshot at
> `align-hcm-maher-brent-chatcut/references/align-brand-system-reference.jpg`
> — reliable for design intent, not for measurement.

## Files

| File | What's in it |
|---|---|
| `references/tokens.md` | Per-surface colour and type ledger, with precedence rules |
| `references/powerpoint-deck-system.md` | Deck structure, type hierarchy, colour discipline, checks |
| `references/voice-and-copy.md` | Tone, hard writing rules, SmartCare messaging |
| `references/carousel-and-motion.md` | 8-slide carousel arc, motion-master tokens and effects |
| `references/provenance-and-conflicts.md` | Full audit: every source, every conflict, how each was resolved |
| `scripts/extract_pptx_theme.py` | `.potx`/`.pptx`/`.thmx` → exact tokens |
| `scripts/brand_lint.py` | Surface-aware colour and font check; `--list` prints the ledger |
| `assets/templates/` | Drop the master template here |

## Composing with other skills

- **`pptx`** — the mechanics of writing `.pptx` files. This skill supplies tokens.
- **`slide-polish`** — run after building; brand-neutral, won't fight these tokens.
- **`presentation-design-master`** — narrative shaping; run on content first.
- **`docx`** — Word deliverables. Apply the token table manually.
- **`cool-data-elements`** — ⚠️ hardcodes `#E8760A` / `#414042`. **Off-brand for
  Align.** Do not use until its tokens are corrected.
- **`brand-guidelines`** — ⚠️ Anthropic's brand, not Align's. Never use here.
- **`theme-factory`, `dataviz`** — feed them `references/tokens.md`.

## Rules of thumb

- Every colour and font in your output should trace to a token in this package.
  No "close enough."
- Orange is an accent: eyebrows, rules, numerals, one KPI. Never body copy,
  never a field behind a text block. One accent per slide.
- Don't mix font systems. `SOURCE-NOTES.md` is explicit: do not use all four
  approved faces in one asset.
- If something isn't here — exact approved page copy, email subject lines — say
  so and mark anything you write as net-new. Don't fabricate approved copy.
