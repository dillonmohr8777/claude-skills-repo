---
name: bigorange-brand-system
description: Exact, portable BigOrange.Marketing brand production system: the bundled logo PNGs, per-surface colour and type tokens (deck, PDF document, web/editorial, social), a pptxgenjs deck kit with the BigOrange slide blocks, a Playwright PDF document kit, a brand linter and a deck validator. Use for any BigOrange deck, proposal, client kickoff, monthly review, leadership review, PDF plan, blog PDF, guide, one-pager, or brand review, and whenever a BigOrange deck must identify the client from its brief, verify the client's logo, and render in the exact BigOrange style. Do not use for Align HCM, Momentum 360, or any other brand.
---

# BigOrange.Marketing brand system

Use this package as the execution authority for BigOrange-branded work. It
carries the production assets and code, not pointers to a machine folder.

## Non-negotiable contract

1. Identify the output surface first (deck, document, web, editorial, social). Load only the references that surface needs.
2. Use the bundled logo PNGs in `assets/logos/`. Never redraw, retype, recolor, trace, or image-generate the logo. Hashes are pinned in `assets/SHA256SUMS`.
3. Resolve the exact client and logo from the current brief. A client deck without `logo.path`, `logo.source` and `logo.verified: true` renders a placeholder and fails validation. Never guess a logo from a filename or an old deck.
4. Fail closed on ambiguity: unknown client, unverified stat, missing source, or copy that promises results.
5. Every generated deck defaults to `sampleData: true` and carries the draft banner until every figure has a granted, dated source.
6. Run the linter and the validator before delivery, then look at every rendered slide or page.

## Surface selector

| Work | Read | Build with | Gate |
|---|---|---|---|
| Deck (.pptx) | `references/deck-system.md`, `references/tokens.md`, `references/voice-and-copy.md` | `scripts/build_deck.js` with a recipe from `bigorange-client-decks` | `scripts/validate_deck.py` + rendered-slide review |
| PDF document | `references/document-system.md`, `tokens.md`, `voice-and-copy.md` | `lib/doc-kit/render.js` | `scripts/brand_lint.py --surface document` + rendered-page review |
| Web / WordPress page | `tokens.md` (web column), `brand-research-2026-09.md` | the live theme's own styles | `brand_lint.py --surface web` + responsive and accessibility check |
| Blog HTML into WordPress | `tokens.md` (editorial), `voice-and-copy.md` | theme styles only | `brand_lint.py --surface editorial` |
| Social graphic | `tokens.md` (social), `voice-and-copy.md` | doc-kit or deck-kit exports | `brand_lint.py --surface social` |

## Deck workflow

```bash
cd skills/bigorange-brand-system
npm install                        # once; see package.json
node scripts/build_deck.js ../bigorange-client-decks/briefs/examples/leadership-review-thursday-2026-09-03.json out.pptx
python3 scripts/validate_deck.py out.pptx [--client-name "X" --client-logo x.png] [--draft]
```

Recipes live in `bigorange-client-decks/recipes/`. Blocks and data shapes are
listed in `references/deck-system.md`. The kit API is `lib/deck-kit.js`.

## Document workflow

```bash
# fonts once: see assets/fonts/README.md
node lib/doc-kit/render.js article.html article.pdf "Blog 01 · Private review draft · BigOrange.Marketing"
python3 scripts/brand_lint.py --surface document lib/doc-kit/theme.css
```

Author the HTML with the components in `references/document-system.md`. Worked
examples (five blog PDFs, the growth plan, the brand voice guide) are in
`client-operations-canonical/clients/bigorange-marketing/deliverables/2026-09-02-wordpress-growth-package-redesign/src/`.

## Assets and references

| Path | Purpose |
|---|---|
| `assets/logos/bigorange-logo-orange.png`, `-white.png` | Exact logo artwork, SHA pinned |
| `assets/templates/BigOrange-Primary-Deck-Reference.pptx` | Rendered proof of the kit (15-slide Thursday review, 2026-09-03) |
| `assets/fonts/README.md` | OFL font fetch instructions (fonts are not committed) |
| `lib/deck-kit.js` | pptxgenjs house library: cover, chrome, stats, cards, grid, flow, timeline, chart, table, decisions, close |
| `lib/doc-kit/` | `theme.css`, `plan.css`, `voice.css`, `render.js`, `build-voice.py` |
| `scripts/build_deck.js` | brief + recipe to .pptx, runs the validator |
| `scripts/validate_deck.py` | geometry, logo hash on every slide, orange present, banned colours, `[[slot]]` leftovers, draft banner, client logo |
| `scripts/brand_lint.py` | per-surface colour and font ledger; exit 1 on errors |
| `scripts/extract_pptx_theme.py` | drift audit when BigOrange supplies a new master |
| `references/tokens.md` | the ledger, with precedence and provenance |
| `references/deck-system.md` | slide grammar, blocks, logo rules, QA gate |
| `references/document-system.md` | PDF components and render rules |
| `references/voice-and-copy.md` | short-form voice rules; the full guide is the Brand Voice Guide PDF |
| `references/brand-research-2026-09.md` | dated public research (expires 2026-12-01) |
| `references/powerpoint-tokens.md`, `.json` | generated measurement of the deck reference |
| `references/provenance.md` | where every token came from and how conflicts were ruled |

## Composition with other skills

- `bigorange-client-decks` supplies recipes and briefs; this skill renders and validates.
- `bigorange-client-radar` supplies the client roster and evidence that a client deck may cite.
- `bigorange-vertical-*` supply industry briefs and deck narratives that fill `industry-pitch` briefs.
- Use the `pptx` skill for file mechanics and visual QA, and the `pdf` skill for merges. Never start from `alignhcm-brand-system` or Momentum templates.

This is a standard `SKILL.md` package with relative assets and stdlib Python plus a small Node dependency set. It is usable by Claude Code and Codex without machine-specific paths.
