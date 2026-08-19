---
name: alignhcm-proposal
description: Generate an Align HCM phased services proposal as a branded PowerPoint. Use whenever a priced proposal, phased approach, engagement roadmap, optimization proposal, advisory proposal, or services pitch is needed for an Align HCM client or prospect on any platform (UKG Pro, UKG WFM, Dayforce, HiBob, Paylocity). Builds current state, phased roadmap, deliverables, outcomes, timeline, and an investment table computed from phase hours so the arithmetic cannot drift. Do not use for a first-meeting company introduction (use alignhcm-intro-deck), a contract (use alignhcm-sow), or an RFP response (use rfp-responder).
---

# Align HCM phased proposal

A proposal argues a sequence: here is your current state, here is a phased path
through it, here is what you get at each phase, here is what it costs. That
order is fixed. The phases, the pain points, and the numbers change per deal.

## Build one

```bash
python3 scripts/build_proposal.py --spec <deal>.json --out-dir <folder>
```

### Minimum spec

```json
{
  "client_name": "Northwind Traders",
  "platform": "UKG Pro",
  "engagement_title": "Optimization Program",
  "rate": 200,
  "current_state": [
    {"category": "Core HR and Payroll",
     "items": ["Hire date changes take 30+ minutes", "Job history tables desync"]}
  ],
  "phases": [
    {"name": "Phase 1: Stabilization", "window": "Mar - Jul 2026", "hours": 1560,
     "summary": "Configure new terms for the July effective date.",
     "workstreams": [{"name": "CBA", "detail": "Job codes, pay rules, accruals."}],
     "deliverables": ["Configured terms", "Integration testing"]}
  ],
  "contact": {"name": "Rich Hennessey", "title": "Director of Services",
              "email": "rich.hennessey@alignhcm.com"}
}
```

Optional: `drivers`, `risks`, `outcomes`, `next_steps`, `why_us`,
`investment_notes`, `approach_framing`, `current_state_framing`, `date`,
`expected_total`, `forbid_terms`.

`current_state` needs at least two categories. That section is what proves you
listened rather than pitched; one bullet of it is not a discovery.

## The investment table is computed, not typed

Hours times rate, per phase, totalled. You cannot produce a proposal whose
phase numbers disagree with its total, because the total is derived from the
phases.

Set `expected_total` to what the deal team agreed and the build fails if the
phases do not reach it. That catches the error a prospect always finds: a
roadmap that says one number and a summary slide that says another.

## Slide order

Cover · agenda · **section 1** current state · pain points · drivers and risks ·
**section 2** phased approach · roadmap band · one slide per phase ·
**section 3** deliverables · outcomes · **section 4** timeline and investment ·
investment table · assumptions · why Align · next steps · close

Section dividers are numbered automatically. Phase slides render as a card grid
when the phase has workstreams, and as a single statement slide when it does
not, so a light phase does not produce an empty grid.

## What it refuses to ship

Another client's name, unresolved placeholders, a proposal that never names the
prospect, an off-brand colour, or an investment total that contradicts the spec.
Exits 2 with the reason; `--allow-invalid` overrides.

Naming and superseding work exactly as in `alignhcm-sow`.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_proposal.py` | The generator |
| `scripts/_core/` | Shared Align document engine, vendored |
| `references/spec-reference.md` | Every spec field, with examples |
| `scripts/selftest.py` | Proves the documented workflow runs |

## Composition

- **`alignhcm-intro-deck`** comes first. The proposal assumes they already know
  who Align is, which is why it opens on their problem rather than on us.
- **`alignhcm-sow`** comes next. Its workstreams and investment should match the
  accepted proposal; if they do not, one of the two is wrong.
- **`alignhcm-brand-system`** owns the visual system this renders in.
