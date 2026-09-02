---
name: bigorange-vertical-manufacturing
description: Vertical playbook for BigOrange Marketing's manufacturing clients, buyer research, objections, proof patterns, keyword seeds, and a pitch deck narrative for manufacturers, machine shops, and industrial suppliers. Use for a manufacturer marketing deck, industrial content plan, manufacturing marketing audit, manufacturing keyword research, or any BigOrange client/prospect that is a manufacturer, contract manufacturer, machine shop, or industrial supplier.
---

# BigOrange vertical: manufacturing

## What this is

A packaged research base for pitching, planning, and writing for BigOrange's manufacturing and industrial clients and prospects. It is not a generic manufacturing-marketing guide, every claim in it is either sourced to a fetched, dated URL or explicitly labeled `unverified`, and the copy guidance is written in BigOrange's own brand voice, not a generic agency voice.

## When to use this

Reach for this skill whenever the client or prospect is a manufacturer, contract manufacturer, machine shop, fabricator, or industrial supplier, and the task is one of:

- Building a manufacturer marketing deck or industrial marketing audit
- Writing a manufacturing marketing plan, proposal, or one-pager
- Planning industrial content (blog angles, capability landing pages, social)
- Doing keyword research or SEO planning for a manufacturer or industrial supplier
- Prepping talking points or objection handling for a manufacturing sales call
- Any task where the trigger phrase is "manufacturer marketing deck," "industrial content plan," "manufacturing marketing audit," "industrial SEO plan," or similar

## Files inside

- `references/industry-brief.md`, who the manufacturer buyer is, how their own customers (engineers, procurement) research suppliers, what's usually broken on manufacturer sites, objections and answers, proof patterns, a KPI/RFQ ladder, market context with dated stats, and compliance cautions. Frontmatter carries `researched`, `expires`, and `sources`. Re-verify against fresh sources after the `expires` date.
- `references/deck-narrative.md`, a 14-slide manufacturing pitch arc: slot names, which `industry-brief.md` field fills each slot, BigOrange-voice guidance per slide, and which slides require a verified proof point before they can ship.
- `references/keyword-seed.json`, commercial, local, planning-question, comparison, spec/capability-specific, and emerging (AI search / directory) keyword clusters for the manufacturing vertical, each tagged by intent and suggested owner page type. All volumes are marked `unverified_volume`, no volume was invented.
- `references/content-angles.md`, 15 content angles grouped by buyer job, each with a one-line BigOrange-voice hook and the proof it needs before publishing.

## How this feeds bigorange-client-decks

`bigorange-client-decks/recipes/industry-pitch.json` builds a manufacturing pitch deck by reading `references/deck-narrative.md` for the slide arc and slot structure, and `references/industry-brief.md` for the actual content that fills each slot (buyer worries, market stats, objections, proof, KPIs). Do not duplicate brief content into the deck recipe, the recipe should read these files live so a brief update propagates to every deck built from it.

## Voice

Every piece of copy drafted from this skill follows BigOrange's brand voice contract (see `bigorange-brand-system` and the vault source at `client-operations-canonical/clients/bigorange-marketing/context/brand-voice.md`): warm, plain, one playful line per section max, no em dashes, lead with the reader's problem, pair every technical capability with a human consequence, state the source and date behind any proof, and never promise magic.

Avoid: unlock, elevate, empower, ecosystem, synergy, transformative, future-ready, robust.

## Fail-closed rule

Never cite a statistic, award, client result, or case study that is not already sourced in `references/industry-brief.md` (with a URL and a fetched/published date) or explicitly supplied and cleared by the person requesting the work. Never invent a case study, round a number up, or claim a certification (ISO, AS9100, ITAR, etc.) on a client's behalf without their own documentation. If no verified proof exists for a specific claim a deck or piece of content wants to make, say so plainly and either use BigOrange's own general manufacturing proof (properly cited) or leave the claim out, do not fabricate a substitute. When `references/industry-brief.md` is past its `expires` date, treat its stats as stale and re-run research before using them in client-facing work.
