# Authoring recipes

A recipe is JSON: `{ name, title, footer, defaultDraft, audience, requires[], slides[] }`.

Each slide: `{ id, block, mode?, eyebrow?, title?, data?, notes? }`.

- `block` is a deck-kit block name (`coverDark`, `coverClient`, `twoUp`, `columns`, `grid`, `flow`, `timeline`, `bigNumbers`, `features`, `decisions`, `textBullets`, `table`, `chart`, `closeDark`).
- `mode` is `white` (default) or `dark`.
- `data` is the block's data object. Any string may contain `{{path}}` tokens resolved against the brief (`vars.x`, `client.name`, `metrics.kpis`, `date`, `presenter`, `logo.path`). A string that is exactly one token resolves to the raw value, so arrays and objects can be passed through (`"items": "{{vars.playItems}}"`).
- Missing values become `[[path]]` text, which the validator rejects. That is the fail-closed mechanism; do not add fallbacks that invent copy.
- The brief can override any slide with `slides[id]` (deep-merged over `data`, plus `title`, `eyebrow`, `notes`) and drop slides with `skip`.

## Guidance

1. Keep BigOrange-constant slides (method, measurement chain, release gates) inside the recipe so every deck says them the same way.
2. Put anything that changes per client or industry behind `vars`.
3. Sandwich: dark cover, white content, dark close. One dark `bigNumbers` slide mid-deck at most.
4. Vary blocks; never two `twoUp` in a row unless the numbers demand it.
5. Speaker notes are talk-track cues, first person, and end with `[Sources] ... [/Sources]` when a slide carries numbers.
6. Titles under 60 characters. Eyebrows one to three words.

## Adding a recipe

1. Copy the closest recipe, rename `name`, edit slides.
2. Run `python3 scripts/new_brief.py --recipe <name> --out /tmp/b.json` and fill it.
3. Build, validate, render, read every slide.
4. Add the worked brief to `briefs/examples/` and a row to the table in `SKILL.md`.
