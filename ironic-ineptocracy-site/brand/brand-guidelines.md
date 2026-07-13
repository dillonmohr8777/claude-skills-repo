# The Ironic Ineptocracy — Brand Guidelines

**Version:** 1.0  ·  **Owner:** Dillon Mohr  ·  **Site:** ironicineptocracy.com

This is the spec a contractor could build from with no other context. Every visual and copy decision on the site routes through it. If a section breaks one of these rules, the section is wrong, not the rule.

---

## 1. Foundation

**What it is.** The marketing site for *The Ironic Ineptocracy*, a debut dark political thriller by Dillon Mohr. The site exists to make a reader feel like they're already inside the story before they've read a sentence of the book.

**Premise of the book.** An ineptocracy is a system where the least capable hold power and the productive fund the unproductive. The "ironic" layer: everyone inside it is either blind to it or complicit in it. Two Harvard students figure out the system built to reward them and the system built to destroy them are the same system.

**The question the brand asks.** *What happens when the people the system was built to control figure out how the system actually works?*

**What the brand is not.**
- A traditional author website.
- A clean, minimal, "literary" aesthetic.
- Comfortable. Reassuring. Polite.

**What the brand is.**
- HBO prestige drama title sequence.
- Surveillance briefing room.
- Cracked seal, bleeding flag, redacted document.
- Confident, dangerous, ironic. Not loud. Not edgy for its own sake.

---

## 2. Color System

All colors live in `styles/tokens.css` as `--ii-*` variables. Reference variables, never raw hex.

### Anchor palette

| Role | Token | Hex | Notes |
|------|-------|-----|-------|
| Base black | `--ii-black` / `--ii-surface-1` | `#0A0A0A` | Page base. Default canvas. |
| Atmospheric navy | `--ii-navy` / `--ii-bg-deep` | `#0A0F1E` | Hero sky, surveillance backdrop. |
| Blood red (primary) | `--ii-blood-500` | `#9B2020` | Threat panels, conspiracy section. Headlines only on dark — fails AA at small sizes. |
| Crimson (secondary) | `--ii-blood-400` | `#C9384A` | Body-safe red. Subhead callouts, "ACTIVE SURVEILLANCE" indicators. |
| Glitch crimson | `--ii-blood-glitch` | `#8B0000` | Glitch flash, corruption. Animation only, never static. |
| Aged brass | `--ii-brass-500` | `#C9A84C` | The CTA color. Patriotic decay. Highlight rim. |
| Off-white parchment | `--ii-parch-100` | `#EBEBEB` | Default body text on dark. ~17:1 contrast on `#0A0A0A`. |
| Aged parchment | `--ii-parch-200` | `#D0C8BC` | Editorial body, longer reads. Aged-paper feel. |

### Contrast pairings (WCAG AA / AAA)

| Foreground | Background | Ratio | Verdict |
|------------|------------|-------|---------|
| `--ii-parch-100` | `--ii-surface-1` | ~17.3 : 1 | AAA — default body |
| `--ii-parch-200` | `--ii-surface-1` | ~13.6 : 1 | AAA — editorial body |
| `--ii-brass-500` | `--ii-surface-1` | ~9.4 : 1 | AAA — CTA, highlights |
| `--ii-blood-400` | `--ii-surface-1` | ~5.0 : 1 | AA normal — safe for subheads |
| `--ii-blood-500` | `--ii-surface-1` | ~3.0 : 1 | AA large only — headlines ≥24pt |
| `--ii-parch-300` | `--ii-surface-1` | ~7.2 : 1 | AAA — captions, meta |

**Rule.** Body copy is always parchment on dark. Blood is for headlines and accents, never paragraphs.

### Surveillance / "Enter the World" sub-palette

The surveillance briefing page (`/enter-the-world/`) uses a tighter sub-system. Black canvas. Terminal green primary. Blood red as alarm only.

| Role | Token | Use |
|------|-------|-----|
| Terminal green | `--ii-term-green` `#00FF66` | Document chrome, scan reveals, countdown |
| Dim green | `--ii-term-green-dim` `#1ABC55` | Static metadata |
| Glow | `--ii-term-green-glow` | Box-shadow on active surveillance dots |

### Prohibited

- No gradients on type. Glitch effects only via clip-path / blend modes.
- No blue. No "social media blue." No "trust blue." This brand has none.
- No saturated full red `#FF0000`. Always `--ii-blood-*` (deeper, oxidized).
- No pure white. Use `--ii-parch-50` (`#F5F4EE`) at most.
- No drop shadows in default neutral grey. Atmospheric (red glow, brass glow, deep black) only.

---

## 3. Typography

| Role | Family | Token | When |
|------|--------|-------|------|
| Display | Bebas Neue | `--ii-font-display` | Hero title, section heads, CTA labels. All-caps, wide tracking. |
| Editorial quote | Playfair Display Italic | `--ii-font-quote` | The Question. Pull quotes. Author bio statement. |
| Redacted / surveillance | Special Elite | `--ii-font-redacted` | "SUBJECT 001 // THREAT CLASSIFICATION". Case file metadata. Countdown. |
| Body / essay | Source Serif 4 | `--ii-font-body` | Paragraphs. Dispatches blog. About page. |

### Fluid scale

| Size | Token | Range | Use |
|------|-------|-------|-----|
| Display | `--ii-fs-display` | 64–160px | `THE IRONIC INEPTOCRACY` hero |
| 3xl | `--ii-fs-3xl` | 48–80px | Section anchor lines |
| 2xl | `--ii-fs-2xl` | 32–48px | Section heads |
| xl | `--ii-fs-xl` | 24–32px | Subheads, character names |
| lg | `--ii-fs-lg` | 20px | Lede, CTA |
| base | `--ii-fs-base` | 17px | Body |
| sm | `--ii-fs-sm` | 14px | Meta, redacted labels |
| xs | `--ii-fs-xs` | 12px | Fine print, footer |

**Rule.** No section uses more than three sizes. Hierarchy through size + family + color, not through three different display fonts.

---

## 4. Imagery & Visual Language

**Allowed.**
- Distressed Americana. Bleeding flag. Cracked Capitol seal. Burned edges.
- Redacted government documents. Scan lines. Coordinate overlays.
- Silhouettes with red rim light. Pixel-noise photo placeholders.
- Campaign-night atmosphere — podium lights, blurred crowds, patriotic decay.
- Glitch on key words: `INEPTOCRACY`, `WATCH`, `CONTROL`, `CLASSIFIED`.

**Forbidden.**
- Stock photography of people smiling.
- Soft gradients, lens flares, Apple-style depth-of-field portraits.
- Trendy 3D blob illustrations. Memphis shapes. Brutalist parody.
- Clean unfaded American flags. Whole, intact institutional logos.

**Texture rule.** Every full-bleed surface should have one of: grain overlay, scan lines, vignette, or all three. Never a flat clean black. The site should never look like a SaaS product.

---

## 5. Voice & Tone

### Voice attributes (always on)

1. **Cinematic** — every paragraph could be a title card.
2. **Punchy** — short sentences dominate. Long ones earn their length.
3. **Slightly dangerous** — implies more than it says.
4. **Ironic** — aware of the absurdity it's describing.
5. **Confident, not loud** — the brand never has to convince. It states.

### Tone matrix

| Context | Tone dial | Example |
|---------|-----------|---------|
| Homepage hero | Cold, declarative, cinematic | "The system isn't broken. It's working exactly as designed." |
| The Question section | Editorial, slow, italic | "What happens when the people the system was built to control figure out how the system actually works?" |
| Character HUD cards | Surveillance file, dispassionate | "SUBJECT 001 // THREAT CLASSIFICATION: EXCEPTIONAL" |
| Conspiracy / tension | Staccato, hard cuts | "False flags. Blackmailed senators. Manufactured wars." |
| Author bio | First-person, quiet, confident | "I wrote this book because I needed someone to ask the question out loud." |
| Email capture | Direct, conspiratorial | "Read it before the world does." |
| Surveillance page | Bureaucratic menace | "FILE SELF-DESTRUCTS IN: 01:30" |
| Dispatches (blog) | Essayistic, sharp, first-person | Personal observation paired with systemic claim. |

---

## 6. Writing Rules (hard-enforced)

**Style violations block ship.** These come from the author and are non-negotiable.

- **No em dashes anywhere.** Use a period, comma, colon, or restructure the sentence.
- **No sentence starters of:** "Do not", "That is", "This is", "It is", "And", "But", "Or".
- **Always use contractions:** it's, don't, won't, can't, isn't.
- **No corporate language.** No "leverage," "solutions," "unlock," "empower," "seamless," "robust."
- **No AI tells.** No "delve," "tapestry," "in today's fast-paced world," "in conclusion," "navigate the landscape," "unlock the power of."
- **Short sentences dominate.** One occasional long cinematic sentence per paragraph for rhythm. Not three.
- **Bullets use the `•` character**, not `-` or `*`.
- **No exclamation points.** The brand never raises its voice.
- **No questions in headlines** except The Question itself (Section 2 of the homepage).

---

## 7. Logo & Title Treatment

The book has no logomark, only a wordmark.

- Wordmark: `THE IRONIC INEPTOCRACY` set in Bebas Neue, all-caps, `--ii-ls-display` tracking.
- Always parchment (`--ii-parch-50`) on dark. Never inverted on light.
- Minimum size: 200px wide. Below that, use shortened `IRONIC INEPTOCRACY`.
- Clear space: at least 1 character height of clear space on all sides.
- Forbidden: outline-only, gradient fill, drop shadow, tilt, italicize, color the letters individually.

---

## 8. Quick Audit Checklist

Run before any section ships.

- [ ] Every color is a `--ii-*` variable, no raw hex in markup
- [ ] Every font size is a `--ii-fs-*` token
- [ ] Body copy uses `--ii-parch-100` or `--ii-parch-200` only
- [ ] Blood red is on a headline or accent, never on a paragraph
- [ ] No em dashes in any string
- [ ] No banned sentence starters
- [ ] Contractions used everywhere
- [ ] Background has grain, scan lines, or vignette — not flat black
- [ ] Any motion is gated by `prefers-reduced-motion`
- [ ] Focus ring visible on every interactive element
- [ ] Mobile checked at 390px wide
- [ ] CTA uses `.ii-cta` class, no other button style

---

## 9. Related Files

- `styles/tokens.css` — canonical CSS variables (the executable form of this doc)
- `brand/tone-matrix.md` *(future)* — expanded examples per surface
- `README.md` — paste instructions and build order
