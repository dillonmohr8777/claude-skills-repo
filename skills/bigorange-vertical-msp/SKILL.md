---
name: bigorange-vertical-msp
description: Vertical playbook for BigOrange Marketing's IT/MSP clients, buyer research, objections, proof patterns, keyword seeds, and a pitch deck narrative for managed service providers and IT companies. Use for an MSP pitch deck, IT services marketing audit, MSP marketing plan, IT company content plan, MSP keyword research, or any BigOrange client/prospect that is an MSP, IT services provider, or IT company.
---

# BigOrange vertical: MSP / IT services

## What this is

A packaged research base for pitching, planning, and writing for BigOrange's MSP and IT services clients and prospects. It is not a generic MSP-marketing guide, every claim in it is either sourced to a fetched, dated URL or explicitly labeled `unverified`, and the copy guidance is written in BigOrange's own brand voice, not a generic agency voice.

## When to use this

Reach for this skill whenever the client or prospect is a managed service provider, IT support company, or IT services firm, and the task is one of:

- Building an MSP pitch deck or IT services marketing audit
- Writing an MSP marketing plan, proposal, or one-pager
- Planning MSP/IT services content (blog angles, landing pages, social)
- Doing keyword research or SEO planning for an MSP or IT company
- Prepping talking points or objection handling for an MSP sales call
- Any task where the trigger phrase is "MSP pitch deck," "IT services marketing audit," "managed IT marketing plan," "IT company content plan," or similar

## Files inside

- `references/industry-brief.md`, who the MSP buyer is, how their own customers research, what's usually broken on MSP sites, objections and answers, proof patterns, a KPI ladder, market context with dated stats, and compliance cautions. Frontmatter carries `researched`, `expires`, and `sources`. Re-verify against fresh sources after the `expires` date.
- `references/deck-narrative.md`, a 14-slide MSP pitch arc: slot names, which `industry-brief.md` field fills each slot, BigOrange-voice guidance per slide, and which slides require a verified proof point before they can ship.
- `references/keyword-seed.json`, commercial, local, planning-question, comparison, and emerging (AI search) keyword clusters for the MSP vertical, each tagged by intent and suggested owner page type. All volumes are marked `unverified_volume`, no volume was invented.
- `references/content-angles.md`, 15 content angles grouped by buyer job, each with a one-line BigOrange-voice hook and the proof it needs before publishing.

## How this feeds bigorange-client-decks

`bigorange-client-decks/recipes/industry-pitch.json` builds an MSP pitch deck by reading `references/deck-narrative.md` for the slide arc and slot structure, and `references/industry-brief.md` for the actual content that fills each slot (buyer worries, market stats, objections, proof, KPIs). Do not duplicate brief content into the deck recipe, the recipe should read these files live so a brief update propagates to every deck built from it.

## Voice

Every piece of copy drafted from this skill follows BigOrange's brand voice contract (see `bigorange-brand-system` and the vault source at `client-operations-canonical/clients/bigorange-marketing/context/brand-voice.md`): warm, plain, one playful line per section max, no em dashes, lead with the reader's problem, pair every technical capability with a human consequence, state the source and date behind any proof, and never promise magic.

Avoid: unlock, elevate, empower, ecosystem, synergy, transformative, future-ready, robust.

## Fail-closed rule

Never cite a statistic, award, client result, or case study that is not already sourced in `references/industry-brief.md` (with a URL and a fetched/published date) or explicitly supplied and cleared by the person requesting the work. Never invent a case study, round a number up, or borrow a stat from a different vertical or a different year without re-verifying it. If no verified proof exists for a specific claim a deck or piece of content wants to make, say so plainly and either use BigOrange's own general MSP proof (properly cited) or leave the claim out, do not fabricate a substitute. When `references/industry-brief.md` is past its `expires` date, treat its stats as stale and re-run research before using them in client-facing work.
