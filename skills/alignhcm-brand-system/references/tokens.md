# Align HCM — token ledger

One table per surface. **Align does not have a single orange.** It has five in
active production use, and they are not interchangeable. Picking the wrong one
is the single most common way Align work goes off-brand, so the ledger is
organised by surface rather than by colour.

Provenance and the reasoning behind each ruling: `provenance-and-conflicts.md`.

---

## Precedence

When two sources disagree, the higher rung wins:

1. **The attached `.potx` / `.pptx` master** — authoritative for decks, and only
   for decks. Extracted by `scripts/extract_pptx_theme.py`.
2. **Live production CSS** on alignhcm.com — authoritative for web and HubSpot.
3. **`SOURCE-NOTES.md`** in `align-hcm-august-2026-content/master-template-reference/`
   — the only document that verified its own sources. Authoritative on typography.
4. **The motion master** `gfx3.html` — authoritative for video and motion.
5. **Shipped production files** — carousels, blog HTML. Authoritative for their own surface.
6. **Legacy skill token lists** — historical. Superseded wherever they conflict.

---

## Web / HubSpot CMS

Observed from live alignhcm.com CSS on 2026-07-15.

| Role | Hex | Use |
|---|---|---|
| Slate | `#2C3C4C` | Primary text, dark fields |
| Deep navy | `#1A334E` | Cover, section breaks, emphasis |
| Ink navy | `#041424` | Deepest background, footer |
| Align orange | `#FF9902` | Hero figures, proof points, CTAs |
| Warm orange | `#F79A20` | Secondary glow, chart tint |
| Coral | `#EF6936` / `#EF6B51` | Evidence, highlight rules |
| Muted slate | `#546474` | Supporting copy, labels |
| Paper | `#F8FAFC` | Light page background |
| White | `#FFFFFF` | Cards, reverse type |

**Type:** Inter, falling back to Segoe UI then Arial. A restrained editorial
serif is allowed as an accent, never for numeric KPIs.

---

## LinkedIn carousel / social

The May-6 production standard. Multiple carousels have shipped in this system.

| Role | Hex | Use |
|---|---|---|
| Gradient start | `#F05A28` | CTA gradient origin, primary accent |
| Gradient end | `#FF6B35` | CTA gradient terminus |
| Ink navy | `#0A1628` | Ground |
| Navy mid | `#2D3748` | Panels |
| Teal | `#2BB5A0` | Secondary accent |

**Signature CTA:** `linear-gradient(135deg, #F05A28 0%, #FF6B35 100%)` plus a
shimmer loop.

**Type:** Inter (standard variant) or DM Sans + Syne (premium variant).
Letter-spacing is never left at default — always `-0.01em` to `-0.045em`.

---

## Video / motion

From `gfx3.html`, the verified motion master (Maher/Brent ROI video).

| Role | Hex | Use |
|---|---|---|
| Motion orange | `#F47A25` | Primary accent, chrome, glow |
| Orange hot | `#FF9A4D` | Bar tops, gradient lift |
| Orange tint | `#F4A96A` | Eyebrow type |
| Steel blue | `#7FA9F0` | Data elements, secondary |
| Steel blue deep | `#3D6DB5` | Bar bases |
| Ink 1 / 2 | `#0A1424` / `#0E1A2B` | Stage base, stage mid |
| Navy lift | `#14305A` | Stage highlight |
| Cream | `#F7F4EE` | Editorial display type |
| Steel / Steel 2 | `#8FA3BC` / `#7E93AE` | Support type, labels |
| Positive | `#5CDB95` | Upward delta |

**Type:** Gelasio for editorial display, Inter for support. This pair is
specific to motion — do not carry it to web.

**Environment:** deep navy stage, 96px data grid at 5.5% opacity, glass
diamonds with `backdrop-filter: blur(12px) saturate(135%)`, vignette,
6px top bar gradient orange→steel blue.

---

## Blog / long-form article

The `:root` block shipped in all ten vendor-intent blog builds. This is the
complete production set, not an abridged one.

| CSS var | Hex | Use |
|---|---|---|
| `--navy-deep` | `#0A1628` | Headings, dark grounds |
| `--ink` | `#2D3748` | Body text |
| `--ink-soft` | `#4A5568` | Secondary text |
| `--muted` | `#7A8699` | Labels, captions |
| `--paper` | `#FBF9F6` | Page ground |
| `--card` | `#FFFFFF` | Cards |
| `--line` | `#E9E4DC` | Hairlines |
| `--line-strong` | `#D8D2C7` | Emphasised rules |
| `--orange` | `#FF6B2B` | Article accent |
| `--orange-deep` | `#F05A28` | Gradient start |
| `--grad` | `#F05A28` → `#FF6B35` | CTA blocks (135deg) |
| `--teal` | `#2BB5A0` | Secondary accent |

**Type:** `--display` = Plus Jakarta Sans; `--body` = DM Sans. Both fall back to
`system-ui, sans-serif`.

Note the paper here (`#FBF9F6`) differs from the web paper (`#F8FAFC`) — warm
versus cool. That is deliberate in the editorial system; do not cross them.

---

## PowerPoint decks

> **Ledger empty pending template ingestion.** No `.potx`, `.pptx`, or `.thmx`
> Align template exists in any of the eight repositories searched. The only
> PowerPoint file present anywhere is a Replenish/7-Eleven client deck on the
> stock Office theme, which is unrelated.

What is known, read off a screenshot of `Align_HCM_Master_Template_9…` found at
`align-hcm-maher-brent-chatcut/references/align-brand-system-reference.jpg`:

- **Cover:** navy ground, logo top-left, orange eyebrow in caps with wide
  tracking, serif display title, thin orange rule, audience/date block.
  Footer: `alignhcm.com` · `Confidential` · `Align HCM · 01`.
- **Palette named on the "Brand at a Glance" slide:** Base (navy), Card (white),
  Accent (orange), Surface (off-white//paper).
- **Type system named on that slide:** serif Headline at display weight, sans
  Body copy, orange `EYEBROW · LABEL` in caps.
- **Section divider:** paper ground, large orange numbered circle, orange
  eyebrow, serif section title, one framing sentence.
- **Logo:** two locks — primary on light, reversed for dark grounds.

This is design intent read from a phone screenshot. **It is not measured.** Exact
hex values, the theme font pair, slide dimensions, and layout names come from the
file itself. Run:

```bash
python3 scripts/extract_pptx_theme.py assets/templates/<file>.potx \
  --md references/powerpoint-tokens.md \
  --json references/powerpoint-tokens.json
```

That writes `powerpoint-tokens.md`, which then outranks everything above for
deck work.

---

## Never use

| Hex | Why |
|---|---|
| `#E8760A` | Appears in **zero** files across all eight repositories. Originates in the `cool-data-elements` account skill, which was never reconciled against production. |
| `#414042` | Same origin. Align's dark family is navy, not neutral grey. |

Both are hardcoded in the `cool-data-elements` skill, so any Word document it
produces is currently off-brand. See `provenance-and-conflicts.md` § Open items.
