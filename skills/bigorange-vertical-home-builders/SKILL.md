---
name: bigorange-vertical-home-builders
description: Deep vertical playbook for BigOrange Marketing's custom home builder practice - buyer psychology, objections, proof patterns, keyword/ranking status, content angles, and a 52-point audit checklist, all sourced to BigOrange's own research and evidence. Use when writing a home builder pitch, a custom home builder audit, a builder marketing deck, a builder content plan, or builder keyword research, or any time you are writing something for BigOrange about home builders.
---

# BigOrange vertical: custom home builders

One-line summary: this is the sourced knowledge base for everything BigOrange writes or pitches about custom home builders - read it before you draft, and never write past what it or a live source can verify.

## What this is

A deep-research reference pack for one BigOrange vertical: custom home builders (custom, semi-custom, and design-build). It compiles what's actually known about this buyer, this market, and BigOrange's own evidence base for the vertical - not generic home-builder-marketing advice pulled from nowhere. Every claim in `references/` carries a source; anything without one is labeled `unverified`.

## When to use this

Load this skill whenever the task is:

- A home builder pitch or pitch deck
- A custom home builder audit (site, marketing, or agency-fit)
- A builder marketing deck
- A builder content plan or content calendar
- Builder keyword research or SEO/ranking status for the builder vertical
- Any other writing task for BigOrange that touches home builders

## Files inside

- `references/industry-brief.md` - the core brief: who the buyer is, the homeowner's journey, what's usually broken, objections and answers, proof patterns that work, the KPI/measurement ladder, seasonality and market context (Census, NAHB), and compliance cautions. Dated, sourced, and expiring - check the `expires` field before relying on it.
- `references/deck-narrative.md` - a 14-slide pitch arc for a custom home builder deck, with slot names (title/kicker/body/stat/proof) and BigOrange-voice copy guidance per slide, each mapped to the brief section that fills it. Two slides are hard-gated `[VERIFIED PROOF REQUIRED]`.
- `references/keyword-seed.json` - the builder-lane keyword clusters: the commercial hub terms, the five blog primary queries with their proposed slugs, planning-question seeds, and the local-modifier market-page pattern. Ranking/status labels are limited to what the local growth-plan text and Moz snapshot actually say.
- `references/content-angles.md` - 20 content angles (blog, email, social, video) grouped by the five buyer jobs, each with a one-line BigOrange-voice hook and the specific proof it needs before it can ship.
- `references/custom-home-builder-audit-checklist.md` - 52 yes/no audit questions across website/conversion, proof/permissions, local presence/GBP, search foundation, follow-up/CRM, and measurement, each with a "why it matters" grounded in the sourced brief.

## How this feeds bigorange-client-decks

`bigorange-client-decks`'s `recipes/industry-pitch.json` reads this skill's `references/deck-narrative.md` for slide structure and copy guidance, and `references/industry-brief.md` for the facts that fill each slide's slots. When building a builder deck through that recipe, this skill is the data source - do not duplicate brief content directly into the recipe; point it here instead. If `bigorange-client-decks` needs client-specific proof (slides 5 and 12 of the deck narrative), that proof comes from a real, current run of `custom-home-builder-audit-checklist.md` against the actual client or prospect - never from this skill's generic references.

## Voice

Every deliverable built from this skill follows BigOrange's brand voice contract (`/home/user/client-operations-canonical/clients/bigorange-marketing/context/brand-voice.md`): warm, plain, customer-first, one playful line per section at most, no em dashes, and avoid unlock / elevate / empower / ecosystem / synergy / transformative / future-ready / robust. State the source, date, number, and gap behind every proof claim. Do not promise magic - say what will be built, checked, or measured.

## Fail-closed rule

Never cite a builder statistic, ranking claim, or market fact that isn't sourced in this skill's references or freshly verified against a live source. Never invent a case study, homeowner quote, project story, or audit finding to fill a deck slide or content angle - if the real evidence doesn't exist yet, say so and offer to go get it (run the audit checklist, request the permission, pull a fresh keyword snapshot) rather than fabricating a placeholder that could ship as fact. When a reference's `expires` date has passed, re-verify before reuse rather than treating it as still current.
