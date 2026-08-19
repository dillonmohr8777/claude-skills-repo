---
name: alignhcm-sow
description: Generate an Align HCM Statement of Work as a branded Word document from a deal spec. Use whenever a SOW, statement of work, scope document, or services agreement is needed for an Align HCM client or prospect, on any platform (UKG Pro, UKG WFM, Dayforce, HiBob, Paylocity), for implementation, migration, optimization, managed services, or SmartCare. Handles scope, workstreams, responsibilities, assumptions, change control, investment tables, and signature blocks. Checks that no previous client's content survived, that the numbers add up, and writes under a deterministic filename so versions stop competing. Do not use for proposals (use alignhcm-proposal) or RFP responses (use rfp-responder).
---

# Align HCM Statement of Work

The most-produced document at Align, and the one with the worst version
problem. SharePoint currently holds four SOWs for one client, including
`Prime_Communications_SOW2.docx`, `Prime_Communications_SOW_revisedMoe15Aug2025.docx`,
and an `/OLD/` folder with three more. Nobody can tell which is real.

This produces one file, named so the current version is obvious, and moves the
previous one aside.

## Build one

```bash
python3 scripts/build_sow.py --spec <deal>.json --out-dir <folder>
```

The spec is JSON because a SOW is negotiated. The spec is what gets edited
between rounds, it diffs cleanly, and the `.docx` is regenerated from it rather
than hand-patched.

### Minimum spec

```json
{
  "client_legal_name": "Northwind Traders, Inc.",
  "align_entity": "Align HCM Services, LLC",
  "platform": "Dayforce",
  "engagement_title": "Full Suite Launch",
  "rate": 200,
  "workstreams": [
    {"name": "Core HR and Payroll", "hours": 680,
     "description": "Company structure, pay and tax codes, payroll configuration.",
     "deliverables": ["Configured org levels", "Two parallel payroll cycles"]}
  ]
}
```

Every other section has a sensible Align default and can be overridden:
`scope_summary`, `align_responsibilities`, `client_responsibilities`,
`assumptions`, `investment_notes`, `term`, `status`, `date`.

Set `expected_total` to the number the deal team agreed. The build fails if the
workstream table does not reach it, which catches the single error a client
always finds.

Full field reference: `references/spec-reference.md`.

## What it refuses to ship

| Check | Why |
|---|---|
| Another client's name anywhere | The worst failure in a reused template. Word-boundary matched against known Align sample and prior-engagement names |
| Unresolved `{{TOKEN}}` | Reaches the client as a literal placeholder |
| Client name absent entirely | Means nothing was actually filled |
| Investment total disagrees with `expected_total` | Arithmetic errors survive review; they do not survive a client |
| Off-brand colour | Same never-use list as the rest of the Align system |

Failing exits 2 and the document is still written, so you can look at it.
`--allow-invalid` keeps it and exits 0.

## Naming

```
Northwind-Traders-Inc_SOW_2026-08-19_v2.docx
```

Client, artifact, ISO date, version. Sorts correctly, reads correctly, and the
version is derived from what is already in the folder rather than from whoever
remembers. On a clean build the previous version moves to `_superseded/`.
Nothing is deleted. Use `--no-supersede` to keep everything in place.

Never rename the output to add `final`, `latest`, `revised`, or an editor's
initials. The convention exists precisely to make those unnecessary, and the
build warns if it sees them.

## Company facts

Numbers about Align come from `scripts/_core/company-facts.md`, not from
whichever prior SOW was copied. Two shipped decks disagreed on team size and
review count; that file is the fix. It carries a review date and the build warns
when it lapses.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_sow.py` | The generator |
| `scripts/_core/` | Shared Align document engine, vendored. Do not edit here |
| `references/spec-reference.md` | Every spec field, with examples |
| `references/sow-structure.md` | The nine sections and why each exists |
| `scripts/selftest.py` | Proves the documented workflow runs |

## Composition

- **`alignhcm-brand-system`** owns colour, type, and logo rules. This skill
  applies them; that skill defines them.
- **`alignhcm-proposal`** comes first in the deal. A SOW turns an accepted
  proposal into a contract, so scope and investment should match it.
- **`alignhcm-pm-runbook`** picks up after signature. The SOW's workstreams
  become the status report's workstreams.
