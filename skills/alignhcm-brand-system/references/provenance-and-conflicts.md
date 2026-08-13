# Provenance and conflicts — the Align brand audit

Every Align HCM branding asset reachable from the account, where it lives, what
it claims, and how the contradictions were resolved. This is the audit trail
behind `tokens.md`.

Audit date: 2026-08-13. Repositories searched: 8 (of 32 on the account; the
other 24 contain no Align material — see § Scope).

---

## What was consolidated

### Skills folded into this package

| Skill | Location | Status |
|---|---|---|
| `alignhcm-brand` | `claude-skills-repo/skills/alignhcm-brand/` | Folded in. Was pointer-only. |
| `alignhcm-smartcare` | `claude-skills-repo/skills/alignhcm-smartcare/` | Folded in. Was pointer-only. |
| `alignhcm-carousel-video` | `claude-skills-repo/skills/alignhcm-carousel-video/` | Folded in. Was pointer-only. |

All three were **broken before this consolidation**. Each instructed the reader
to load a file under `C:\Users\DillonMohr\.claude\clients\align-hcm\`:

- `brand.md`
- `smartcare-gtm-strategy.md`
- `smartcare-carousel-template.md`
- `C:\Users\DillonMohr\Downloads\may-6-smartcare-carousel.html`

None of those files exist in any repository, and `SOURCE-NOTES.md` independently
recorded them as **already missing on 2026-07-16**. The skills carried usable
inline tokens in their prose, which is what has been salvaged here; the
documents they pointed at are gone.

Two of the three also stated that a deck skill was still to be built:

> "Deck structure — separate skill to be built from the `.pptx` source (pending)"
> — `alignhcm-brand`
>
> "Full-deck presentations (`.pptx`) — separate skill (pending)"
> — `alignhcm-carousel-video`

This package closes that gap.

### Source documents folded in

| Source | Repo | Contributes |
|---|---|---|
| `master-template-reference/SOURCE-NOTES.md` | align-hcm-august-2026-content | Typography ruling, verification discipline |
| `master-template-reference/brand-guidelines.md` | align-hcm-august-2026-content | Palette, tone, writing rules |
| `master-template-reference/gfx3.html` | align-hcm-august-2026-content | Motion master tokens (1,000+ lines) |
| `02_FullTimeJob/AlignHCM/brand-guidelines.md` | dillon-os | Byte-identical duplicate of the above |
| `assets/source/website-brand-tokens.md` | align-hcm-lead-intelligence | Live site CSS tokens, 2026-07-15 |
| `references/align-brand-system-reference.jpg` | align-hcm-maher-brent-chatcut | Screenshot of the PowerPoint master |
| `_engine/deck8.html` | align-hcm-public-content | Deck engine built on motion tokens |
| 10 × `vendor-intent-blog-batch/**/*.html` | align-hcm-august-2026-content | Article accent in production |

---

## The orange problem

Five oranges are in active production use. Counts are occurrences across all
eight repositories.

| Hex | Count | Where it lives | Ruling |
|---|---|---|---|
| `#F05A28` | 133 | Carousels, blog CTAs, gradient origin | **Keep** — social + editorial gradient start |
| `#FF6B35` | 104 | Gradient terminus | **Keep** — pairs with the above |
| `#F47A25` | 60 | `gfx3.html` motion master, `deck8.html` | **Keep** — motion only |
| `#FF6B2B` | 13 | 10 production blog files + 2 skill files | **Keep** — article accent |
| `#E8832A` | 9 | `brand-guidelines.md` and derivatives | **Demote** — documented but never shipped |
| `#FF9902` | live CSS | alignhcm.com production | **Keep** — web only |
| `#E8760A` | 0 | `cool-data-elements` skill only | **Reject** |

### How this was resolved

The instinct is to declare one winner. That would be wrong. Reading the actual
usage, these are not five competing answers to one question — they are four
distinct surface systems that were each developed correctly and simply never
written down together:

- **Web** runs `#FF9902` / `#EF6936`, straight from the live stylesheet.
- **Motion** runs `#F47A25`, consistently, across the master and the deck engine.
- **Social** runs the `#F05A28 → #FF6B35` gradient across every shipped carousel.
- **Editorial** runs `#FF6B2B` across all ten blog builds.

Each is internally consistent. The failure was never having a document that said
which applies where — so `tokens.md` is organised by surface, and `brand_lint.py`
takes `--surface` as a required argument rather than checking one flat list.

Two genuine errors did surface:

1. **`#E8832A` is documented but unshipped.** It appears only in
   `brand-guidelines.md` and files that copy from it. No production asset uses
   it. Demoted, not deleted — it may be a legacy print value worth confirming.

2. **`#E8760A` and `#414042` are unsupported.** Zero occurrences across every
   repository. They come from the `cool-data-elements` account skill. Rejected.

---

## The typography problem

| Source | Claims | Ruling |
|---|---|---|
| Live site CSS | Inter, sans-serif | Web body/UI |
| `SOURCE-NOTES.md` | Plus Jakarta Sans (headings) + DM Sans (body) | **Authoritative for web/editorial** |
| `brand-guidelines.md` | Plus Jakarta Sans, DM Sans, Poppins, Barlow | Menu, not a stack |
| `alignhcm-brand` skill | Inter + DM Sans + Syne | Social variants |
| `gfx3.html` | Gelasio + Inter | Motion only |
| PowerPoint master (screenshot) | Serif display + sans body | Deck — needs measurement |

`SOURCE-NOTES.md` wins on typography because it is the only source that states
its method, its date, and its own caveats. It resolves the Inter-vs-Plus-Jakarta
tension directly:

> "The current page also contains a legacy or component-level Inter declaration.
> The production default is: Plus Jakarta Sans for primary sans headings and UI,
> DM Sans for body and support copy, Gelasio plus Inter only when intentionally
> inheriting the verified editorial motion-master system."

And it sets the rule that matters most:

> "Do not mix all four fonts in one asset."

The `brand-guidelines.md` list of four is a menu of approved faces, not a stack
to be used simultaneously. That misreading is the likeliest cause of drift.

The deck's serif display face is **unresolved** — the screenshot shows a serif
headline that is not Gelasio-obvious at that resolution, and no deck file exists
to measure. It comes out of the `.potx` theme's `majorFont`.

---

## Adjacent skills — deliberately not folded in

| Skill | Why not |
|---|---|
| `cool-data-elements` | Word-document data callouts. Genuinely useful, but its palette is wrong (see above). Needs a token fix, not absorption. |
| `rfp-responder` | Carries Align company boilerplate — brand *voice*, not visual identity. Different lifecycle. |
| `slide-polish`, `presentation-design-master` | Generic deck craft, brand-neutral. Compose with this skill; do not merge. |
| `brand-guidelines` (Anthropic) | **Anthropic's** brand. Never use for Align. Name collision only. |
| `theme-factory`, `dataviz` | Generic systems that accept a brand palette. Feed them `tokens.md`. |
| `brand-voice` plugin, `marketing:brand-review`, `canva:brand-check` | Generic enforcement machinery, client-agnostic. Point them at this package. |
| `nimble:brand-mention-monitor`, `brightdata-plugin:brand-listening` | External monitoring. Not identity. |

---

## Scope

Searched all 32 repositories on the account by name and metadata; cloned and
full-text searched the 8 carrying Align material:

`dillon-os` · `claude-skills-repo` · `client-operations-canonical` ·
`alignhcm-ai-marketing-skills` · `align-hcm-august-2026-content` ·
`align-hcm-public-content` · `align-hcm-lead-intelligence` ·
`align-hcm-maher-brent-chatcut`

`alignhcm-ai-marketing-skills` is named as if it holds Align skills but
contains a Momentum 360 agent suite transfer and one CrewAI note. No Align
branding.

The remaining 24 are client sites, prospect batches, forks, and unrelated
tooling. No Align brand tokens or skills in any of them.

---

## Open items

1. **No PowerPoint template exists in any repository.** The package is built to
   ingest one; until a `.potx` lands in `assets/templates/`, the deck ledger is
   empty by design rather than guessed.
2. **`cool-data-elements` ships off-brand colour.** It hardcodes `#E8760A` and
   `#414042`. Every Word document it has produced carries those. Fixing it is a
   one-line change per token once the correct Word-surface palette is agreed.
3. **`#E8832A` needs a verdict** — legacy print value, or a stale draft?
4. **The deck serif is unidentified** pending the template.
5. **Three legacy skills remain as redirect stubs.** Delete them once nothing
   references the old names.
