---
name: bigorange-vertical-landscaping
description: Vertical playbook for BigOrange Marketing's landscaping and hardscape clients. Use for a landscaping pitch deck, lawn care marketing audit, landscaper content plan, hardscape SEO plan, irrigation or lighting marketing angle, design-build lead generation review, or any request to brief BigOrange's landscaping vertical (design-build firms, maintenance and lawn care companies, hardscape and outdoor living contractors, commercial grounds crews). Supplies the industry brief, deck narrative, keyword seeds, and content angles the industry-pitch deck recipe reads.
---

# BigOrange vertical: landscaping

## What this is

A packaged brief on the landscaping and hardscape vertical for BigOrange
Marketing: what these business owners are actually dealing with, what is
usually broken in their marketing, what proof convinces them, and how to talk
about it in BigOrange's voice. It is reference material, not a template to
fill in blind: read the brief, then write like you actually know this owner.

## When to use this

Reach for this skill any time a task touches a landscaping, lawn care,
hardscape, or outdoor-living business (a prospect, not necessarily an
existing client). Trigger phrases: landscaping pitch deck, lawn care marketing
audit, landscaper content plan, hardscape SEO, irrigation marketing,
outdoor lighting marketing angle, design-build lead gen, commercial grounds
maintenance marketing, green industry marketing.

Do not use this for home builders, remodelers, or general contractors. See
`bigorange-vertical-home-builders` for that adjacent vertical.

## Files inside

- `references/industry-brief.md`: the core brief. Buyer types, customer
  journey, what's usually broken, objections and answers, proof patterns,
  KPIs, seasonality, compliance cautions, and every source used to write it.
  Carries `researched:` and `expires:` dates in its frontmatter; check the
  expiry before treating a stat as current, and re-run research past it.
- `references/deck-narrative.md`: a 12 to 14 slide industry-pitch arc with
  slot names (title, kicker, body, stat, proof), which `industry-brief.md`
  field fills each slot, and which slides are not allowed to run without a
  verified number or a named, sourced case study.
- `references/keyword-seed.json`: keyword clusters (commercial, hardscape,
  lighting, irrigation, maintenance, planning-stage questions, local
  modifiers) with intent and the page type that should own each cluster.
  Every volume figure is marked `unverified_volume`; pull real numbers from
  a keyword tool before a client sees them.
- `references/content-angles.md`: 15 content angles grouped by buyer job,
  each with a one-line hook in BigOrange voice and the proof it needs before
  it ships.

## How this feeds bigorange-client-decks

`bigorange-client-decks`'s `recipes/industry-pitch.json` recipe reads
`references/deck-narrative.md` for slide structure and slot definitions, and
`references/industry-brief.md` for the facts, quotes, and stats that fill
those slots. When building a landscaping pitch deck, load this skill first so
the brief and narrative are in context before the recipe runs.

## Voice

Everything written from this brief follows BigOrange's brand voice contract
at `/home/user/client-operations-canonical/clients/bigorange-marketing/context/brand-voice.md`.
Read it before drafting copy: talk to one busy owner as "you," lead with what
they're worried about, one playful line per section at most, no em dashes,
and never these words: unlock, elevate, empower, ecosystem, synergy,
transformative, future-ready, robust (as a capability claim).

## Fail-closed rule

Never cite a statistic, survey number, or industry claim that isn't sourced
with a URL and a date seen in `industry-brief.md`. Never invent a case study,
client name, or result. If a deck slide calls for proof and this vertical
has no verified example yet, say so and mark the slide as needing a real
client story; don't write a plausible-sounding one. An `unverified` label
beats a fabricated number every time.
