---
name: bigorange-client-decks
description: Deck engine for BigOrange.Marketing. Turns a JSON brief plus a recipe into a finished, validated BigOrange PowerPoint using the bigorange-brand-system kit. Four recipes: industry-pitch (MSP, manufacturing, landscaping, home builders), client-kickoff (auto-drafted when the client radar finds a new client), monthly-performance (client-report data contract, native charts), and leadership-review (audits, growth plans, decisions). Use when asked for a BigOrange pitch deck, kickoff deck, monthly review deck, leadership review deck, industry deck, or to turn a proposal or audit into slides.
---

# BigOrange client decks

## How it works

1. Pick a recipe in `recipes/`. A recipe is an ordered list of slides, each naming a deck-kit block and the `{{vars.*}}` slots it needs. Recipes carry BigOrange-constant slides (method, measurement chain, release gates) so a brief only supplies what changes.
2. Write a brief (`briefs/examples/` show every shape). Fill every slot the recipe references. Arrays must match the block's data shape (see `bigorange-brand-system/references/deck-system.md`).
3. Build: `cd ../bigorange-brand-system && node scripts/build_deck.js <brief.json> <out.pptx>`. The validator runs automatically; `[[slot]]` leftovers, a missing logo, or a missing draft banner fail the build.
4. Render and look: LibreOffice to PDF, `pdftoppm` to JPEG, read every slide. Fix overflow by shortening copy, not by shrinking type below the kit sizes.

## Recipes

| Recipe | Audience | Fill from | Slides |
|---|---|---|---|
| `industry-pitch` | A prospect in one of the four industries | `bigorange-vertical-<industry>/references/deck-narrative.md` and `industry-brief.md`; proof only from `bigorange-brand-system/references/brand-research-2026-09.md` or the hub page | 12 |
| `client-kickoff` | A new client at the first working session | proposal, intake call, `bigorange-client-radar` roster entry, verified logo | 10 |
| `monthly-performance` | An existing client, monthly | the `client-report` data contract (`metrics.kpis`, `charts`, `campaigns`, `wins`, `actions`, `summary`) from granted GA4, Search Console, HubSpot or ad platforms | 8 |
| `leadership-review` | BigOrange or client leadership deciding on an audit or plan | audit findings, evidence stats, rollout, decisions | 11 |

## Brief schema

```json
{
  "recipe": "industry-pitch | client-kickoff | monthly-performance | leadership-review",
  "date": "September 2026", "presenter": "Margee Moore",
  "sampleData": true,
  "client": { "name": "Acme", "line": "one line about them" },
  "logo": { "path": "acme.png", "source": "https://acme.com/press", "verified": true },
  "industry": "home-builders | msp | manufacturing | landscaping",
  "periodLabel": "August 2026",
  "metrics": { "kpis": [], "charts": [], "campaigns": [], "wins": [], "actions": [], "summary": "" },
  "vars": { "...every slot the recipe references..." },
  "slides": { "<slide id>": { "title": "override", "notes": "override", "...block data override..." } },
  "skip": ["<slide id>"]
}
```

`scripts/new_brief.py --recipe industry-pitch --industry msp --out brief.json`
scaffolds a brief with every slot listed and `[[TODO]]` values so nothing is
forgotten; the build fails until each is filled.

## Rules

- `sampleData` stays `true` until every number has a granted, dated source. The banner is the honesty signal; do not remove it to make a deck look finished.
- Proof slides use only verified BigOrange proof: the awards and review count on the site, case studies BigOrange publishes on its own hub pages, and figures from granted data. Never borrow a number from another client or from Dillon's other portfolios.
- Client identity comes from the `bigorange-client-radar` roster or the brief author's explicit source. Logos must be verified.
- Pricing: no public pricing page exists (checked 2026-09-02). Quote hub page tier language with attribution or use the proposal figure.
- Voice: `bigorange-brand-system/references/voice-and-copy.md`. Titles under 60 characters. No em dashes.
- Output goes to `client-operations-canonical/clients/bigorange-marketing/deliverables/<date>-<deck>/` with the brief beside it. Sending is approval-gated; append to `System/approval-queue.md`.

## Files

| Path | Purpose |
|---|---|
| `recipes/*.json` | the four recipes |
| `briefs/examples/*.json` | one worked brief per recipe plus the four industry pitches |
| `scripts/new_brief.py` | scaffold a brief with every slot |
| `references/recipe-authoring.md` | how to add or change a recipe |
| `references/data-contracts.md` | brief, metrics and roster shapes |
