# Data contracts

## Brief (input to `build_deck.js`)

See `SKILL.md`. Required keys per recipe are listed in each recipe's `requires`.

## Metrics (monthly-performance)

Identical to the `client-report` skill in dillon-os so one JSON feeds the HTML
report, the review dashboard and the deck:

```json
{
  "kpis": [{ "label": "Qualified inquiries", "value": "14", "delta": "+3", "deltaGoodWhenDown": false }],
  "charts": [{ "title": "Organic clicks by week", "labels": ["W1", "W2"], "values": [120, 140], "prefix": "" }],
  "campaigns": [{ "name": "Builder hub", "status": "live", "statusLabel": "Live", "spend": "$0", "results": "13 terms in top 3", "note": "Moz 2026-08-14" }],
  "wins": ["..."], "actions": ["..."], "summary": "Two sentences in plain language.",
  "sources": [{ "name": "Search Console", "granted": true, "asOf": "2026-08-31" }]
}
```

`sampleData` must remain `true` until every source in `sources` is `granted`.
Status vocabulary: `live`, `watch`, `blocked`, `paused`.

## Roster entry (from `bigorange-client-radar`)

```json
{ "name": "Acme Custom Homes", "domain": "acmecustomhomes.com", "industry_guess": "home-builders",
  "confidence": "high",
  "evidence": [{ "url": "https://bigorange.marketing/...", "kind": "case-study-title", "text": "...", "seen_at": "2026-09-02T14:00:00Z" }] }
```

A kickoff brief copies `name` into `client.name`, `industry_guess` into
`industry`, and cites the first evidence URL in the cover notes. The logo is
never taken from the roster; it must be sourced and verified separately.

## Vertical references (industry-pitch)

`bigorange-vertical-<industry>/references/deck-narrative.md` maps its slides
to the recipe's `vars`: `whoBullets`, `brokenItems`, `journeySteps`,
`playItems`, `plan1..plan4`, `investment*`, `close*`. `industry-brief.md`
supplies the facts and their sources; `keyword-seed.json` supplies query
language for the "what usually breaks" and "first plays" slides.
