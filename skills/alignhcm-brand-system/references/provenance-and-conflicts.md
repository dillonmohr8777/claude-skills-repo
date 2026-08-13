# Align HCM brand provenance and conflict rulings

Audit refreshed 2026-08-13 against all 32 repositories on the
`dillonmohr8777` account and the primary PowerPoint file supplied directly by
Dillon.

## Repository scope

Eight repositories contain Align material:

1. `align-hcm-august-2026-content`
2. `align-hcm-lead-intelligence`
3. `align-hcm-maher-brent-chatcut`
4. `align-hcm-public-content`
5. `claude-skills-repo`
6. `client-operations-canonical`
7. `dillon-os`
8. `mohr-vault`

`alignhcm-ai-marketing-skills` is named as though it contains Align work, but
its current tree contains Momentum 360 transfer material and no Align or
SmartCare path. It is not one of the eight evidence repositories. The other 23
repositories contain no Align material in their current trees.

## Broken legacy skills

The three earlier skills existed in `claude-skills-repo` but pointed to missing
machine-local files:

| Skill | Missing pointer |
|---|---|
| `alignhcm-brand` | `C:\Users\DillonMohr\.claude\clients\align-hcm\brand.md` |
| `alignhcm-smartcare` | `C:\Users\DillonMohr\.claude\clients\align-hcm\smartcare-gtm-strategy.md` |
| `alignhcm-carousel-video` | `smartcare-carousel-template.md` and a Downloads HTML file |

`SOURCE-NOTES.md` independently recorded the same missing paths on 2026-07-16.
The redirect stubs remain temporarily so old prompts route to this package.

## Sources consolidated

| Source | Repository or origin | Contribution |
|---|---|---|
| `master-template-reference/SOURCE-NOTES.md` | `align-hcm-august-2026-content` | Source verification and typography boundaries |
| `master-template-reference/brand-guidelines.md` | `align-hcm-august-2026-content` | Historical palette, voice, writing rules |
| `master-template-reference/gfx3.html` | `align-hcm-august-2026-content` | Motion master |
| `assets/source/website-brand-tokens.md` | `align-hcm-lead-intelligence` | Observed live web tokens |
| `presentation/DESIGN_SYSTEM.md` | `align-hcm-lead-intelligence` | Logo, photography, chart, layout, and accessibility rules |
| `references/align-brand-system-reference.jpg` | `align-hcm-maher-brent-chatcut` | Earlier visual screenshot of the deck style |
| `_engine/deck8.html` | `align-hcm-public-content` | Motion-derived reusable engine |
| `vendor-intent-blog-batch/**/*.html` | `align-hcm-august-2026-content` | Shipped editorial system |
| `02_FullTimeJob/AlignHCM/*` | `dillon-os` | Brand, SmartCare, audience, and deliverable context |
| `AlignHCM Monthly LinkedIn Calendar.md` | `mohr-vault` | Cross-agent brand workflow references |
| `1-Primary-align-template-.pptx` | Dillon attachment, 2026-08-13 | Exact primary deck reference and exact embedded Align lockup |

The attachment itself contained prior-client branding, contact data, pricing,
and engagement facts, so the original binary is not published. A privacy-
scrubbed visual clone is bundled as
`assets/templates/Align-HCM-Primary-Deck-Reference.pptx`; geometry, styles,
colors, type, icons, Align artwork, and the client-logo zone are preserved. The
exact Align deck lockup is bundled separately at
`assets/logos/align-hcm-deck-lockup.png`.

## Deck correction

The earlier draft assumed the PowerPoint theme slots would become the deck
authority after extraction. The supplied file disproves that assumption:

- color scheme: stock `Office`
- font scheme: stock `Office`
- actual design: explicit painted slide colors and direct font overrides
- measured primary navy: `#232E3E`
- measured primary orange: `#E97722`
- measured light-field orange: `#B05512`
- measured type overrides: Calibri 131, Arial 9, Cambria 8

The correct runtime model is to clone and edit the designed slides. Office
`accent1` through `accent6` are not Align tokens. The extractor now reports
`painted-slide-system` and inventories named picture zones instead of treating
all hand-painted values as drift.

## Surface-specific orange ruling

| Surface | Approved family | Evidence |
|---|---|---|
| Web and HubSpot | `#FF9902`, `#F79A20`, `#EF6936`, `#EF6B51` | Observed production CSS |
| Social carousel | `#F05A28` to `#FF6B35` | Shipped carousel system |
| Motion | `#F47A25`, `#FF9A4D`, `#F4A96A` | `gfx3.html` and derived engine |
| Editorial HTML | `#FF6B2B`, with the social gradient for CTA blocks | Ten shipped article builds |
| PowerPoint and formal documents | `#E97722`, `#B05512`, `#94480F` | Supplied primary deck |

These values are not interchangeable. `brand_lint.py` requires a surface.

`#E8832A` is documented but does not ship in the audited repository files, so
it remains historical and unapproved for new work. `#E8760A` and `#414042`
appear only in the generic `cool-data-elements` skill and are rejected for
Align.

## Typography ruling

| Surface | Type system |
|---|---|
| Web | Inter in observed production CSS; Plus Jakarta Sans and DM Sans remain the verified broader web/editorial pair from `SOURCE-NOTES.md` |
| Editorial | Plus Jakarta Sans display, DM Sans body |
| Social | Inter, or DM Sans plus Syne for the premium variant |
| Motion | Gelasio display, Inter support |
| PowerPoint and formal documents | Cambria display, Calibri body/support, limited Arial overrides |

Do not mix the systems inside one artifact.

## Missing capabilities found in the earlier package draft

The first draft contained colors, voice, carousel, motion, and an extractor but
still lacked:

- the actual master deck and exact Align deck lockup
- deterministic client-logo sourcing, containment, and validation
- the first-party logo, photography, chart, and accessibility rules from
  `presentation/DESIGN_SYSTEM.md`
- a populated deck and formal-document palette
- residue checks that prevent sample-client names, contacts, prices, and dates
  from leaking into a new deck
- Claude marketplace registration, Codex interface metadata, and portable
  relative resources

Those gaps are addressed in this package revision.

## Remaining open items

1. The supplied deck is a painted reference on the stock Office theme, not a
   normalized `.potx`. Clone-based production is exact; a future approved
   custom theme could improve maintainability but must be visually compared
   before replacing this authority.
2. The full historical SmartCare GTM document and old carousel source HTML are
   still unavailable. Do not present reconstructed wording as approved copy.
3. `#E8832A` still needs an explicit owner verdict before any new use.
4. Web tokens were observed on 2026-07-15 and should be refreshed when the live
   production theme changes.
5. A client logo is intentionally resolved per deck from current official
   evidence. Never bundle or reuse one client's logo as another client's.
