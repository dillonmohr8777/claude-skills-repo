# Align HCM token ledger

Align does not have a single interchangeable orange. It has distinct
surface-specific systems. Select the surface before selecting tokens.

## Precedence

1. Bundled primary PowerPoint reference for decks and formal documents. Its
   rendered slides and explicit painted values outrank its stock Office theme.
2. Current live alignhcm.com CSS for web and HubSpot.
3. Verified `SOURCE-NOTES.md` typography rulings.
4. `gfx3.html` motion master for video and motion.
5. Shipped production carousel and editorial files for their own surfaces.
6. Legacy skill lists only where a higher source does not exist.

## Web and HubSpot

Observed from live alignhcm.com CSS on 2026-07-15. **Review due 2027-01-15**, or
sooner if the production theme changes. Re-observe the live CSS and update this
table plus the `web` palette in `scripts/brand_lint.py`.

| Role | Hex | Use |
|---|---|---|
| Slate | `#2C3C4C` | Primary text and dark fields |
| Deep navy | `#1A334E` | Cover and section fields |
| Ink navy | `#041424` | Deepest background and footer |
| Align orange | `#FF9902` | Hero figures, proof, CTAs |
| Warm orange | `#F79A20` | Secondary glow and chart tint |
| Coral | `#EF6936`, `#EF6B51` | Evidence and highlight rules |
| Muted slate | `#546474` | Support copy and labels |
| Paper | `#F8FAFC` | Light background |
| White | `#FFFFFF` | Cards and reverse type |

Type: Inter, then Segoe UI, Arial, sans-serif.

## LinkedIn carousel and social

| Role | Hex | Use |
|---|---|---|
| Gradient start | `#F05A28` | Primary social accent |
| Gradient end | `#FF6B35` | Hot gradient stop |
| Ink navy | `#0A1628` | Ground |
| Navy mid | `#2D3748` | Panels |
| Teal | `#2BB5A0` | Secondary accent |
| White | `#FFFFFF` | Reverse type |

Type: Inter, or DM Sans plus Syne for the premium variant. Do not combine the
two systems.

## Video and motion

| Role | Hex |
|---|---|
| Motion orange | `#F47A25` |
| Orange hot | `#FF9A4D` |
| Orange tint | `#F4A96A` |
| Steel blue | `#7FA9F0` |
| Steel blue deep | `#3D6DB5` |
| Ink 1 and 2 | `#0A1424`, `#0E1A2B` |
| Navy lift | `#14305A` |
| Cream | `#F7F4EE` |
| Steel labels | `#8FA3BC`, `#7E93AE` |
| Positive | `#5CDB95` |

Type: Gelasio for display and Inter for support.

## Blog and editorial HTML

| Role | Hex |
|---|---|
| Navy deep | `#0A1628` |
| Ink and ink soft | `#2D3748`, `#4A5568` |
| Muted | `#7A8699` |
| Warm paper | `#FBF9F6` |
| Card | `#FFFFFF` |
| Rules | `#E9E4DC`, `#D8D2C7` |
| Article orange | `#FF6B2B` |
| Gradient | `#F05A28` to `#FF6B35` |
| Teal | `#2BB5A0` |

Type: Plus Jakarta Sans display and DM Sans body.

## PowerPoint decks

Measured from `assets/templates/Align-HCM-Primary-Deck-Reference.pptx`, supplied
on 2026-08-13. The file's theme is stock Office. These explicit painted values,
not `accent1` through `accent6`, define the deck.

| Role | Hex | Use |
|---|---|---|
| Primary navy | `#232E3E` | Cover, close, proof and investment fields |
| Navy card | `#2B3849` | Secondary dark cards |
| Deep navy | `#1D2735` | Darkest timeline and card state |
| Navy sequence | `#26334A`, `#2F4059`, `#3A4E6B`, `#465C7E` | Ordered timeline phases only |
| Primary orange | `#E97722` | Rules, icons, markers on navy |
| Contrast orange | `#B05512` | Eyebrows and emphasis on light fields |
| Dark orange | `#94480F` | Small high-contrast orange text |
| Paper | `#F6F8FA` | Light slide field |
| Pale row | `#EDF2F8` | Alternating table row |
| White | `#FFFFFF` | Cards and reverse type |
| Light type | `#E3E8EE` | Reverse support text |
| Muted light | `#C5CEDA` | Footer and secondary reverse text |
| Rule | `#C7D2DF` | Tables and light-field borders |
| Muted slate | `#4A5563`, `#55606E` | Supporting text |
| Dark border | `#4A5C75` | Dark-card outlines |

Type: Cambria display, Calibri body and support, with limited Arial overrides
in the supplied file.

## Formal documents

Word reports, one-pagers, and sales collateral use the deck navy, orange,
paper, rule, and type family unless a newer approved document template is
supplied. Use the bundled exact Align lockup. This closes the prior gap that
allowed `cool-data-elements` to generate unverified gray/orange documents.

## Surface ruling and evidence

Each orange family is evidenced by shipped production files. The families are
not interchangeable, which is why `brand_lint.py` requires a surface.

| Surface | Approved family | Evidence |
|---|---|---|
| Web and HubSpot | `#FF9902`, `#F79A20`, `#EF6936`, `#EF6B51` | Observed production CSS |
| Social carousel | `#F05A28` to `#FF6B35` | Shipped carousel system |
| Motion | `#F47A25`, `#FF9A4D`, `#F4A96A` | `gfx3.html` and derived engine |
| Editorial HTML | `#FF6B2B`, with the social gradient for CTA blocks | Ten shipped article builds |
| PowerPoint and formal documents | `#E97722`, `#B05512`, `#94480F` | Supplied primary deck |

## Typography ruling

| Surface | Type system |
|---|---|
| Web | Inter in observed production CSS. Plus Jakarta Sans and DM Sans remain the verified broader web/editorial pair from `SOURCE-NOTES.md` |
| Editorial | Plus Jakarta Sans display, DM Sans body |
| Social | Inter, or DM Sans plus Syne for the premium variant |
| Motion | Gelasio display, Inter support |
| PowerPoint and formal documents | Cambria display, Calibri body and support, limited Arial overrides |

Do not mix the systems inside one artifact.

## Never use

| Hex | Why |
|---|---|
| `#E8760A` | Not present in any audited Align production file. |
| `#414042` | Not present in any audited Align production file. Align's dark family is navy, not neutral gray. |
| `#E8832A` | Retired 2026-08-17. Appeared only in historical brand documentation and files copied from it, never in a shipped asset. |
| `#F5A623` | Not present in any audited Align production file. Hardcoded as "Align orange" in the `rfp-responder` skill. Unverified. |
| `#404040` | Not present in any audited Align production file. Hardcoded as "Align dark gray" in the `rfp-responder` skill. Align's dark family is navy. |

The general rule these come from: never take a color or typeface from a generic
design skill, a preset theme, or any source that does not name the shipped file
it was measured from. If a value cannot be traced to production evidence, it is
not an Align token.

To reinstate `#E8832A`, the brand owner names the surface it applies to and adds
it to that surface's table above and to `scripts/brand_lint.py`.
