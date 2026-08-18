# Align HCM logos, imagery, data visualization, and accessibility

This reference consolidates rules that existed in
`align-hcm-lead-intelligence/presentation/DESIGN_SYSTEM.md` but were absent from
the earlier package draft.

## Logo system

- Use `assets/logos/align-hcm-deck-lockup.png` for the supplied PowerPoint
  system. Never reconstruct, trace, recolor, sharpen, or image-generate it.
- On other surfaces, use the official primary mark on white or paper and the
  official white/reverse mark on navy. Do not derive one from the other.
- Preserve aspect ratio and clear space. Normalize multiple marks by optical
  height, not equal width.
- Separate official implementation partners from merely supported platforms.
  The verified partner row is Dayforce, HiBob, Paylocity, and UKG. Workday and
  ADP belong in a separately labeled supported-platform row unless newer source
  evidence changes that status.
- A logo obtained from search results, a screenshot, a favicon, or AI
  generation is not an approved source asset.

## Client logo sourcing

1. Resolve the deck's client from the current brief and source files.
2. Search attached approved assets and the canonical client project first.
3. If absent, use the client's official brand kit or official website.
   `scripts/fetch_client_logo.py --domain <site> --out <file>.png` automates
   this: it ranks the candidates on the company's own site, prefers a reverse or
   already-transparent mark, and refuses anything that will not hold up.
4. Prefer source SVG or transparent high-resolution PNG. Convert without
   changing paths, proportions, colors, or clear space.
5. Record the asset source locator. The fetcher writes a `.source.json` beside
   the PNG for this. If identity or provenance is ambiguous, stop before placing
   the mark.
6. Use the PowerPoint cover zone defined in `powerpoint-deck-system.md` and run
   `validate_client_deck.py` against the exact selected logo.

### Legibility on the cover field

The cover panel is navy `#232E3E`. A mark that looks correct on a white website
can disappear there, and transparency alone does not fix it. Require at least
**3:1** contrast between the mark's ink and the navy, which is what
`fetch_client_logo.py` measures and enforces.

When the only available mark is dark:

1. Look for the client's reverse, white, or knockout variant. Most brand kits
   ship one, and the fetcher already scores those highest.
2. If none exists, place the primary mark on the approved light-background
   plate with restrained clear space, as described in
   `powerpoint-deck-system.md`.
3. Never recolor, invert, or trace the client's mark to make it fit.

### What automated cleanup may and may not do

Permitted, because they do not alter the artwork:

- Removing a flat background that the mark was flattened onto
- Removing the pale halo that flattening leaves behind
- Trimming transparent margins
- Rasterising an official SVG at a larger size

Not permitted:

- Recoloring, inverting, or restyling the mark
- Upscaling a small raster to fake resolution
- Keying out a photographic or gradient background
- Reconstructing or redrawing any part of the mark

Any logo whose background was keyed is flagged `needs_human_review` in its
provenance file. Look at it on the navy cover before the deck goes out.

## Photography and illustration

- Use verified Align team photography only for opening context, leadership,
  or closing culture pages.
- Use a named person's portrait only where the source and narrative require
  that person.
- Apply a restrained navy overlay or duotone when photography becomes a
  background. Keep faces recognizable.
- Do not use unrelated stock photography as proof and do not imply that a
  representative person is a client employee.
- Generated visuals require the verified Align logo and at least one approved
  client or campaign reference. Keep generated work in review status until
  approved.

## Data visualization

- Lead with the business meaning, then the chart mechanics.
- Use orange for the one primary result or action. Do not paint every series
  orange.
- Direct evidence: filled orange marker plus the word `DIRECT`.
- Assisted evidence: outlined blue marker plus the word `ASSISTED`.
- Unresolved evidence: open gray marker plus the word `UNRESOLVED`.
- Context: amber rule or dash plus the word `CONTEXT`.
- Optional chart assist blue is `#4C91D8`; always pair it with a label, shape,
  or pattern.
- Use tabular numerals. Align major numbers on shared baselines.
- Limit a primary presentation table to six rows. Move full detail to an
  appendix or companion document.
- Cite the precise source file, workbook, or system and reporting window.

## Accessibility and export

- Meet 4.5:1 contrast for body text and 3:1 for large text and meaningful
  graphical objects.
- Never use color as the only distinction.
- Do not place orange body text on white.
- Avoid tiny footnotes, hairline chart labels, and low-opacity evidence text.
- Preserve reading order, meaningful alt text, and descriptive link text in
  editable documents.
- Review the final rendered PDF or images, not only the editable source.
