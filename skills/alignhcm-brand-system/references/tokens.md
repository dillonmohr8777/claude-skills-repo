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

Observed from live alignhcm.com CSS on 2026-07-15.

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

## Never use

| Hex | Why |
|---|---|
| `#E8760A` | Appears in zero production files across the eight Align repositories; came from an unreconciled generic skill. |
| `#414042` | Same origin. Align's dark family is navy, not neutral gray. |
| `#E8832A` | Historical documentation evidence only; no shipped file in the audited repositories uses it. Owner verdict 2026-08-13: not approved for new work on any surface. |

All three are errors in `brand_lint.py` and `validate_client_deck.py`. `#E8832A`
may still be read in old documentation as evidence of what was once written
down; it may not be painted into anything new.
