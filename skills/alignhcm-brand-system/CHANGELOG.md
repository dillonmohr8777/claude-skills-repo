# Changelog

History and audit trail for `alignhcm-brand-system`. Nothing here is needed to
produce a deliverable. The operative rulings live in `references/tokens.md`.

## 2026-08-17 org-readiness review

Fixes from a pre-rollout review. Four blockers and ten smaller items.

### Blockers

1. **The documented deck workflow always failed validation.** The bundled
   reference carries 15 placeholder tokens; `prepare_client_deck.py` substituted
   4, and `validate_client_deck.py` hard-errors on any survivor, so the happy
   path exited 1. The script now discovers placeholders itself, joins runs per
   paragraph so a token split across runs is still found and still replaced,
   reports what is unresolved grouped by slide, and exits non-zero unless
   `--allow-unresolved` is passed. A `--list-placeholders` mode prints the
   inventory. `SKILL.md` carries the full table and a worked command.
2. **`brand_lint.py` silently passed every Word and PowerPoint file.** It read
   files as text and matched CSS-form hex, but an Office file is a compressed
   zip, so nothing matched and the documented Word gate returned exit 0 on a
   document containing both banned colors. The linter now detects the OPC magic
   bytes, opens the package, and lints the XML parts using the attribute forms
   Office writes. Findings report the part name.
3. **The skill depended on a named individual in nine places**, including two
   instructions and three unreachable `C:\Users\...` paths. Replaced with the
   "brand owner" role and an ownership block in `SKILL.md`.
4. **Nothing connected this skill to the six skills that produce client-facing
   files.** Each now instructs the agent to load this package before building.

### Also changed

- Split this changelog out of `references/provenance-and-conflicts.md`, which
  was mostly history. The three operative rulings (surface orange table,
  typography table, never-use list) moved into `references/tokens.md`; the file
  was removed.
- Removed every em dash from the reference prose. The voice rules forbid them,
  and an agent reads the prose as a style exemplar.
- Replaced the rules naming specific unavailable skills with one durable rule:
  never take color or type from a generic design skill or any source that does
  not name its evidence.
- **`#E8832A` retired.** It appeared only in historical brand documentation and
  files copied from it, never in a shipped asset. Reinstating it requires the
  brand owner to name a surface. Recorded so users stop re-asking.
- Web tokens now carry a review date rather than only an observation date.
- `references/powerpoint-tokens.json` had a Windows `source_file` path; now
  repo-relative, and the file is listed in the assets table.
- Geometry validation now compares within 500 EMU. The reference is 31 EMU under
  a nominal 13.333in canvas, so an otherwise identical deck rebuilt at nominal
  size was being rejected.
- `prepare_client_deck.py` now fails clearly if the client-logo media part is not
  a `.png`, instead of writing PNG bytes into a `.jpeg` part and producing a
  corrupt file.
- Icon pictures on slides 2, 3, 5, 6, and 7 were unnamed (`Picture 8`,
  `Picture 13`). They are now `ALIGN_ICON_S<slide>_<n>` and are hash-verified
  against the bundled reference, so a swapped or recolored icon is caught.
- Slide 5 hardcoded a possessive after the client token and rendered
  "Acme Foods's 1200 employees". Restructured to read correctly for any client.
- `sldSz` declared `type="screen4x3"` while the dimensions are 16:9. Corrected
  to `screen16x9`.

### Hashes

The bundled PNG lockup is unchanged:
`3A0340D27BFE44B21277F4A689796B1C31338F5FD74134786209F5B736D22A07`.

The reference deck changed, because the slide 5 possessive fix, the `sldSz`
correction, and the icon naming are all edits inside it:

- was `1BE9BDEE225E53C4F4E5F17B7D92CE5E98C15AE0709C10B9F61C331F3287A722`
- then `42DD524F303AA0CB4FFCCCABD94B4311A31CFD4C808A0DC8C84573A7DEA2938C` (slide 5 only)
- now `BA3CD30112BC9EFB2A9D18483A2188559FD97BCD08CF47E02B0C9BEA675F18EA` (slides 2, 4, 6 possessives also fixed after visual render)

Only six XML parts differ (`ppt/presentation.xml` and slides 2, 3, 5, 6, 7). All
nine `ppt/media/*` artwork parts are byte-identical, so no artwork was altered.

## 2026-08-18 automated client logo sourcing

The deck workflow required a logo file already found by hand. It now fetches one.

`scripts/fetch_client_logo.py` reads the company's own site, ranks every logo
candidate, takes the best, and cleans it. `scripts/logo_image.py` carries the
imaging: a stdlib PNG codec, edge-connected background removal, defringing,
trimming, resampling, and legibility analysis. Pillow is used when already
installed for JPEG and WebP sources and better resampling, and is never
required, which the suite now asserts.

Ranking prefers assets needing no modification: SVG, then a transparent site
logo, then og:image, then apple-touch-icon, then favicon. A URL naming a
reverse, white, or knockout variant is scored higher, because the Align cover is
navy and that is the variant that belongs on it.

The quality gate is the substance. The script exits non-zero rather than
returning a poor mark, on any of:

- narrower than 600px after trimming, so it would be soft in the 2.9in zone
- still fully opaque, so it would show as a rectangle on navy
- an extreme aspect ratio, so it is probably not the mark
- **under 3:1 contrast against the cover navy**

That last one was found by rendering. A dark logo keyed to transparency looks
correct in isolation and on a white page, then vanishes on the navy cover panel.
Neither the structural checks nor a look at the PNG would catch it; only
measuring the ink against the field it lands on does.

Background removal is deliberately conservative. It floods inward from the
border, so enclosed light areas such as the counter of a letter survive, and it
declines entirely when the corners disagree, which is the signal for a
photographic or gradient background.

Every fetched logo gets a `.source.json` recording the source URL, the original
and final dimensions, every processing step, the measured contrast, and whether
a human still needs to look at it. That satisfies the existing source-locator
rule, which was previously left to the operator.

Five checks added, and check registration is now explicit rather than discovered
by name so helpers cannot be mistaken for tests. Suite is 30 checks. The logo
tests run against a local fixture site, so they work offline and do not depend
on any third party's markup.

## 2026-08-18 real-company validation

The logo fetcher was built against synthetic fixtures and passed. Running it
against real brand artwork found two defects the fixtures could not.

**Every vector candidate scored identically.** A 32px favicon served as SVG tied
with the 512px header logo, and ties broke on discovery order, so the favicon
won. It happened on all five real brands tried. The synthetic fixture missed it
because its favicon was a PNG, which scored lower for an unrelated reason. Role
now dominates scoring: a favicon is a favicon whether or not it is vector.

**Vectors rasterised at intrinsic size.** Only rsvg-convert and inkscape accept
a width flag; LibreOffice uses the file's own dimensions, so a 32px favicon
stayed 32px and the reason for preferring vector was lost. The requested size is
now written into the SVG before conversion, which every backend honours.

**The reported contrast figure was misleading.** It was a mean, and a mark that
is mostly dark brand colour with a light antialiased edge gets a flattering
mean: real measurement showed 6.70:1 while 62% of the ink sat below 3:1. The
headline number is now the median, computed from a histogram, which tracks the
colour a reader actually sees. On the same logo it reports 2.60:1, matching the
verdict and the eye.

Results against real brand colours, with the mark on the navy cover field:

| Company | Brand | Contrast | Verdict |
|---|---|---|---|
| SAP | `#0FAAFF` | 5.36:1 | accepted |
| Siemens | `#009999` | 3.93:1 | accepted |
| ADP | `#D0271D` | 2.60:1 | rejected |
| Paychex | `#004B8D` | 1.56:1 | rejected |
| FedEx | `#4D148C` | 1.18:1 | rejected |

The rejections are correct. Dark blue, dark purple, and mid red on a navy field
are genuinely hard to read, and each of those companies publishes a reverse
lockup for exactly this case. The gate errs conservative and names the remedy.

Two regression checks added, so the suite is 32.

## 2026-08-18 universal client logo plate

Contrast rejection was the wrong end of the problem. A prospect's mark is
designed for their own background, so measuring it against Align navy and
refusing it just moved the work back to a person. Every client mark now goes on
a plate instead.

| Mark | Plate fill | Border |
|---|---|---|
| Dark | White `#FFFFFF` | Thick, sampled from the mark |
| Light or white | Near-black `#0B0E12` | Thick, sampled from the mark |

Polarity is chosen by measuring the mark against both candidate fills and taking
the one it reads better on, rather than a fixed luminance cutoff that would be
wrong near the middle. The border colour comes from `dominant_colour`, which
buckets ink in a coarse RGB cube and prefers saturated buckets, so grey
supporting text cannot outvote the brand hue. On real artwork it recovers
`#0FAAFF` for SAP, `#4D148C` for FedEx, and `#009999` for Siemens exactly. If
that colour would vanish into the plate fill, its lightness is nudged until it
separates, and its hue is left alone.

The plate is drawn with an antialiased rounded rectangle computed from the
signed distance to the shape, so no supersampling is needed. Border width, pad,
and corner radius all scale from the mark's short edge.

All five real brands that previously failed now pass:

| Company | Bare on navy | Plate | Mark on plate |
|---|---|---|---|
| ADP | 2.60:1 | white, `#D0271D` border | 5.27:1 |
| Paychex | 1.56:1 | white, `#004B8D` border | 8.80:1 |
| FedEx | 1.18:1 | white, `#4D148C` border | 11.66:1 |
| SAP | 5.36:1 | near-black, `#0FAAFF` border | 7.56:1 |
| Siemens | 3.93:1 | near-black, `#009999` border | 5.54:1 |

`--plate` takes `always` (default), `auto`, or `never`. The contrast gate still
bites under `never`, and the size, aspect, and unkeyable-background gates apply
in every mode.

This supersedes the earlier rule in `powerpoint-deck-system.md` that a client
mark went on a card only when it was otherwise unreadable. Both reference files
are updated.

Fixed while testing: the fully-opaque check ran after trimming, and trimming
crops to the mark's bounding box, so any transparent logo whose ink filled that
box was reported as still having a background plate. It now runs before the trim
and only fires when keying was actually attempted and failed.

Four checks added, so the suite is 36.

## 2026-08-13 exact-authority revision

The primary PowerPoint file was supplied directly and became the deck authority.

### Repository audit

Refreshed against all 32 repositories on the account. Eight contain Align
material:

`align-hcm-august-2026-content`, `align-hcm-lead-intelligence`,
`align-hcm-maher-brent-chatcut`, `align-hcm-public-content`,
`claude-skills-repo`, `client-operations-canonical`, `dillon-os`, `mohr-vault`

`alignhcm-ai-marketing-skills` is named as though it contains Align work but its
tree holds Momentum 360 transfer material and no Align or SmartCare path. The
other 23 repositories contain no Align material.

### Sources consolidated

| Source | Repository or origin | Contribution |
|---|---|---|
| `master-template-reference/SOURCE-NOTES.md` | `align-hcm-august-2026-content` | Source verification and typography boundaries |
| `master-template-reference/brand-guidelines.md` | `align-hcm-august-2026-content` | Historical palette, voice, writing rules |
| `master-template-reference/gfx3.html` | `align-hcm-august-2026-content` | Motion master |
| `assets/source/website-brand-tokens.md` | `align-hcm-lead-intelligence` | Observed live web tokens |
| `presentation/DESIGN_SYSTEM.md` | `align-hcm-lead-intelligence` | Logo, photography, chart, layout, accessibility rules |
| `references/align-brand-system-reference.jpg` | `align-hcm-maher-brent-chatcut` | Earlier visual screenshot of the deck style |
| `_engine/deck8.html` | `align-hcm-public-content` | Motion-derived reusable engine |
| `vendor-intent-blog-batch/**/*.html` | `align-hcm-august-2026-content` | Shipped editorial system |
| `02_FullTimeJob/AlignHCM/*` | `dillon-os` | Brand, SmartCare, audience, deliverable context |
| `AlignHCM Monthly LinkedIn Calendar.md` | `mohr-vault` | Cross-agent brand workflow references |
| Primary deck attachment, 2026-08-13 | Supplied by the brand owner | Exact deck reference and embedded Align lockup |

The supplied attachment contained prior-client branding, contact data, pricing,
and engagement facts, so the original binary is not published. A privacy-scrubbed
visual clone is bundled instead; geometry, styles, colors, type, icons, Align
artwork, and the client-logo zone are preserved.

### Deck authority correction

An earlier draft assumed PowerPoint theme slots would become the deck authority
after extraction. The supplied file disproved it:

- color scheme: stock `Office`
- font scheme: stock `Office`
- actual design: explicit painted slide colors and direct font overrides
- measured primary navy `#232E3E`, primary orange `#E97722`, light-field orange
  `#B05512`
- measured type overrides: Calibri 131, Arial 9, Cambria 8

The correct runtime model is to clone and edit the designed slides. Office
`accent1` through `accent6` are not Align tokens.

## Earlier: consolidation of three legacy skills

`alignhcm-brand`, `alignhcm-smartcare`, and `alignhcm-carousel-video` were
pointer-only and all three were broken. Each loaded a machine-local file that
existed in no repository; `SOURCE-NOTES.md` independently recorded the same
paths as missing on 2026-07-16. Their inline tokens were salvaged, reconciled
against production files, and split by surface. Redirect stubs remain so old
prompts route here.

## Known limitations

1. The bundled deck is a painted reference on the stock Office theme, not a
   normalized `.potx`. Clone-based production is exact. A future approved custom
   theme would improve maintainability but must be compared visually before it
   replaces this authority.
2. The historical SmartCare GTM document and the original carousel source HTML
   remain unavailable. Copy produced for those two surfaces is net-new and needs
   review. Do not present reconstructed wording as approved.
3. A client logo is resolved per deck from current official evidence. Never
   bundle or reuse one client's logo for another client.
