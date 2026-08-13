# Template drop point

Put the Align HCM master PowerPoint template here — `.potx` preferred, `.pptx`
or `.thmx` also work.

The known filename, from the screenshot in
`align-hcm-maher-brent-chatcut/references/align-brand-system-reference.jpg`,
begins `Align_HCM_Master_Template_9…`.

Then run, from the skill root:

```bash
python3 scripts/extract_pptx_theme.py assets/templates/<file>.potx \
  --md references/powerpoint-tokens.md \
  --json references/powerpoint-tokens.json
```

That generates the deck token reference from the file itself. Regenerate it
whenever the template changes — never hand-edit the output.

## A note on size

Templates with embedded imagery can be large. If the file is over ~50 MB,
consider committing a stripped copy (theme and layouts, no sample media) and
keeping the full version outside git — the extractor only needs the theme and
layout parts.
