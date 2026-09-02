# BigOrange document system (PDF)

`lib/doc-kit/` renders branded PDFs from HTML with Chromium (Playwright) and
stamps the footer and page numbers with pdf-lib. Letter, portrait.

## Files

| File | Purpose |
|---|---|
| `theme.css` | Tokens, type, cover, article body, tables, FAQ, close block |
| `plan.css` | Report additions: dark cover, section heads with big numerals, stat tiles, layers, timeline, chain, decisions |
| `voice.css` | Brand voice guide additions: orange cover, pillar cards, before/after, prompt block |
| `render.js` | `node render.js in.html out.pdf "Footer label"`: cover pass (no margins) + body pass (0.85 in margins, 1.05 in bottom), merged, footer stamped in Montserrat |
| `build-voice.py` | Converts `brand-voice-guide.md` to `voice.html` using the voice components |

Fonts load from `assets/fonts/*.ttf` (Montserrat, Source Serif 4, Inter; all
OFL). Fetch them with the commands in `assets/fonts/README.md` before rendering.
Chromium must also see them as system fonts for the footer stamp: copy them to
`~/.fonts` and run `fc-cache -f`.

## Page components

| Component | Class | Notes |
|---|---|---|
| Article cover | `.page.cover` | White page, outlined numeral, title, orange band with the spec sheet |
| Report cover | `.page.pcover` | Ink page, orange corner square, stat strip |
| Guide cover | `.page.vcover` | Orange page, ink corner square |
| Section head | `.sechead` | Big orange numeral, kicker, title, rule |
| Purpose block | `.purpose` | Peel tint |
| Direct answer | `.answer` | Peel tint, orange left rule |
| Stat tiles | `.stats .stat[.hot]` | 4 across |
| Layers | `.layers .layer` | 2-column numbered list |
| Timeline | `.timeline .tl` | 4 phases, first orange |
| Chain | `.chain .c` | 6 dark cells, fifth orange |
| Decisions | `.decisions .dec[.wide]` | 2-column, wide dark |
| Tables | `table.t` | Orange caps header, ink rules |
| FAQ | `.faq .qa` | Orange Q, pith card |
| Close | `.close` | Ink block, white logo, CTA links |
| Legal | `.legal` | Small data-font line; wrap close and legal in `.endwrap` |

## Rules

- Cover markup carries `cover-only`; everything else sits in one `.body-only` container.
- Never put a `@page` margin in the HTML; `render.js` owns margins.
- Numbered `h2.n` headings use the `.idx` orange numeral; the rail sits inside the text column.
- Links in body copy are orange-deep with a light underline.
- Every PDF ends with the private-review legal line until release is approved.
- Run `python3 scripts/brand_lint.py --surface document theme.css plan.css voice.css` after any CSS change.
