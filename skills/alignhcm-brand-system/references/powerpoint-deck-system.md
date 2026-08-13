# Align HCM PowerPoint deck system

How to build an Align deck that matches the master template, and how to make the
template itself the authority instead of a hand-copied hex list.

---

## Step 1 — ingest the template (do this first, every time)

```bash
python3 scripts/extract_pptx_theme.py assets/templates/Align_HCM_Master_Template.potx \
  --md references/powerpoint-tokens.md \
  --json references/powerpoint-tokens.json
```

This reads the OPC container directly — no `python-pptx` needed — and pulls:

- the **12 theme colour slots** (`dk1`, `lt1`, `dk2`, `lt2`, `accent1–6`,
  `hlink`, `folHlink`) with exact hex
- the **major/minor font pair** (headings and body) as PowerPoint resolves them
- **slide geometry** in inches, pixels at 96 DPI, and EMU
- the **layout inventory** with each layout's name and placeholder types
- **every hex actually painted** on masters and layouts, by frequency
- **font overrides** applied directly to runs instead of via `+mj-lt` / `+mn-lt`

The last two are the drift detectors. A colour that appears in "painted" but is
not a theme slot was typed onto a shape by hand and will not follow a theme
change.

Once `powerpoint-tokens.md` exists, **it outranks every other source for deck
work**, including `tokens.md`.

---

## Step 2 — build on the layouts, not on rectangles

Use the layout names exactly as the extractor reports them. Never rebuild a
cover by drawing shapes onto a blank slide — it breaks theme inheritance, the
footer chrome, and every subsequent template update.

Colours go in as **theme references** (`accent1`), not literals (`#F05A28`).
Fonts go in as `+mj-lt` / `+mn-lt`. That is what makes a deck survive a rebrand.

---

## Structure observed on the master

From `Align_HCM_Master_Template_9…`, read off
`align-hcm-maher-brent-chatcut/references/align-brand-system-reference.jpg`.
Design intent is reliable here; measurements are not — take those from Step 1.

### Cover
- Navy ground, full bleed
- Logo lock top-left: `Align` wordmark with the orange chevron/dot mark and
  `HUMAN CAPITAL MANAGEMENT` beneath in small caps
- Orange eyebrow, caps, wide tracking: `PRESENTATION CATEGORY · EYEBROW`
- Serif display title, sentence case, large
- One-line descriptor in light sans below
- Thin orange rule
- `Client or Audience Name` bold, `Engagement or Date · Month YYYY` muted
- Decorative: soft darker-navy quarter circle upper right, small orange dot
- Footer: `alignhcm.com` · `Confidential` · `Align HCM · 01`

### Brand at a Glance (slide 2)
Three cards on paper ground, each with a thin orange top rule:
- **LOGO** — primary lock on light, reversed lock on navy
- **COLOR** — four swatches labelled Base (navy), Card (white), Accent (orange),
  Surface (off-white)
- **TYPE** — serif `Headline` "Display weight for titles"; sans `Body copy`
  "easy, light and readable"; orange `EYEBROW · LABEL` "Slip line, eyebrow, footnote"

Keep this slide in client-facing decks. It is doing brand-standards work.

### Section divider
Paper ground · large solid orange circle with the section number reversed out ·
orange `SECTION OVERVIEW` eyebrow · serif section title · one framing sentence ·
navy footer bar.

### Footer chrome
Present on every slide. Three zones: `alignhcm.com` left, `Confidential` centre,
`Align HCM · NN` right. Zero-padded slide number.

---

## Type hierarchy

| Level | Face | Treatment |
|---|---|---|
| Display title | Theme major (serif) | Sentence case, tight tracking |
| Section title | Theme major (serif) | Sentence case |
| Eyebrow / label | Theme minor (sans) | Caps, orange, wide tracking (~0.16–0.34em) |
| Body | Theme minor (sans) | Light weight, generous leading |
| Footer | Theme minor (sans) | Small, caps, wide tracking, muted |

The eyebrow is the signature move — an orange caps line above nearly every
title. Do not drop it.

---

## Colour discipline

- Navy and paper alternate as grounds. Orange is **accent only** — eyebrows,
  rules, the section numeral, one KPI figure per slide.
- Never set body copy in orange.
- Never put an orange field behind a large text block; orange is a stroke, a
  dot, a numeral, or a thin rule.
- One accent per slide. Two oranges competing reads as a template failure.

---

## Composing with other skills

- `pptx` — the file-manipulation layer. Use it to actually write the `.pptx`.
  This skill supplies the tokens; that one supplies the mechanics.
- `slide-polish` — run **after** the deck is built, for alignment and spacing.
  It is brand-neutral, so it will not fight these tokens.
- `presentation-design-master` — narrative and condensation. Run it on content
  before applying this system, not after.
- `cool-data-elements` — **has the wrong Align palette** (`#E8760A`, `#414042`).
  Do not use for Align until its tokens are corrected.

---

## Checks before shipping

1. Every slide uses a named layout — none built freehand on Blank.
2. Colours reference theme slots, not literals.
3. Fonts resolve through `+mj-lt` / `+mn-lt`.
4. Eyebrow present and orange on every title slide.
5. Footer chrome intact, slide numbers zero-padded and sequential.
6. One orange accent per slide.
7. Re-run the extractor on the finished deck and diff its "painted colours"
   against the template's. New hexes mean drift.
