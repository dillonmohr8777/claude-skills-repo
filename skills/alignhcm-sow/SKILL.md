---
name: alignhcm-sow
description: Generate an Align HCM Statement of Work as a branded Word document from a deal spec, using Align's real thirteen-section SOW template. Use whenever a SOW, statement of work, scope document, or services agreement is needed for an Align HCM client or prospect, on any platform (UKG Pro, UKG WFM, Dayforce, HiBob, Paylocity), for implementation, migration, optimization, managed services, or SmartCare. Handles client details, applications in scope, per-application service assumptions, launch methodology and parameters, roles, out of scope, change requests, additional terms, fees on either a fixed fee or time and materials basis, and the acknowledgement and signature blocks. Checks that the MSA clauses survived, that no previous client's content did, that the signing entity is real, that the numbers add up, and writes under a deterministic filename so versions stop competing. Do not use for proposals (use alignhcm-proposal) or RFP responses (use rfp-responder).
---

# Align HCM Statement of Work

The most-produced document at Align, and the one with the worst version
problem. SharePoint currently holds four SOWs for one client, including
`Prime_Communications_SOW2.docx`,
`Prime_Communications_SOW_revisedMoe15Aug2025.docx`, and an `/OLD/` folder with
three more. Nobody can tell which is real.

This produces one file, named so the current version is obvious, and moves the
previous one aside.

## The structure is Align's, not invented

Thirteen sections, matching
`1 - All Things Sales/Templates/SOWs/Align HCM UKG Pro Launch SOW Template v1.docx`
and cross-checked against executed contracts for World Central Kitchen,
Interfor, CHFA, Ashley Furniture, and Redberry. Section list and rationale:
`references/sow-structure.md`.

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
  "align_entity": "Align HCM Services LLC",
  "platform": "UKG Pro",
  "engagement_title": "Full Suite Launch",
  "pricing_model": "fixed_fee",
  "pricing_valid_through": "31 December 2026",
  "scope_items": [
    {"application": "UKG Pro Pay and People Center - US",
     "assumptions": [
       "Implement HR, Payroll, Benefits, ESS/MSS, and standard interfaces.",
       "Support one launch of UKG Pro Pay and UKG Pro People Center."]}
  ],
  "milestones": [
    {"label": "Contract Execution", "amount": 1000},
    {"label": "Month 2 Fees", "amount": 89750}
  ]
}
```

Optional and worth filling: `client_details`, `launch_parameters`,
`phase_deliverables`, `out_of_scope`, `additional_terms`, `change_order_rate`,
`currency`, `expected_total`, `scope_summary`, `investment_notes`, `status`,
`date`, `forbid_terms`.

Full field reference: `references/spec-reference.md`.

## Two things it will not guess

**The signing entity.** Align signs as `Align HCM, Inc.` or
`Align HCM Services LLC`. Both appear in executed contracts, and which applies
is a legal decision. `align_entity` must be exactly one of those two strings.
A near-miss such as "Align HCM Services, LLC" is rejected before anything is
written, rather than printed onto a signature page.

**Scope without limits.** An application listed in scope with an empty
`assumptions` list is rejected. Every quantity in Service Assumptions is a
future change order avoided; the real template writes them explicitly, down to
"configure up to 5 attestation workflows each containing up to 4 questions".

## Pricing works two ways

`"pricing_model": "fixed_fee"` renders the payment milestone table Align's
template uses. `"time_and_materials"` renders hours times rate per workstream.
Either way the total is computed, never typed, so the table cannot disagree
with itself. Set `expected_total` to the number the deal team agreed and the
build fails if the rows do not reach it.

## What it refuses to ship

| Check | Why |
|---|---|
| A missing MSA clause | Five sentences do the legal work. The build asserts each survived into the rendered file |
| Another client's name anywhere | The worst failure in a reused template. Word-boundary matched |
| An invented signing entity | Puts the wrong company on a contract |
| An application in scope with no assumptions | Turns a fixed fee into an argument |
| Unresolved `{{TOKEN}}` | Reaches the client as a literal placeholder |
| Fee total disagrees with `expected_total` | Arithmetic errors survive review; they do not survive a client |
| Off-brand colour | Same never-use list as the rest of the Align system |
| No `pricing_valid_through` | Warns. A quote with no expiry can be executed months later at stale rates |

Failing exits 2 and the document is still written, so you can look at it.
`--allow-invalid` keeps it and exits 0. A spec that is incomplete or names a
fake entity exits 3 and writes nothing.

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
whichever prior SOW was copied. Shipped documents disagree on team size and
review count; that file is the fix. It carries a review date and the build
warns when it lapses.

## Marks

Every document carries the exact Align lockup, vendored and SHA-256 pinned, so
a re-exported or substituted logo fails the build rather than shipping. Full
rules, including where a client mark belongs and where it does not:
`scripts/_core/marks.md`.

**No client logo, ever.** A SOW is a contract. Putting the counterparty's logo
on a document you drafted is presumptuous, and in procurement it raises a
trademark-use question nobody wants to answer mid-deal. Their legal name goes
in the parties block. The self-test asserts the only image in a generated SOW
is Align's own mark, even when the spec supplies one.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_sow.py` | The generator |
| `scripts/_core/marks.md` | Which logo goes on what, and why |
| `scripts/_core/brand-voice.md` | Voice rules every Align document shares |
| `scripts/_core/` | Shared Align document engine, vendored. Do not edit here |
| `references/spec-reference.md` | Every spec field, with examples |
| `references/sow-structure.md` | The thirteen sections and why each exists |
| `scripts/selftest.py` | Proves the documented workflow runs |

## Composition

- **`alignhcm-brand-system`** owns colour, type, and logo rules. This skill
  applies them; that skill defines them.
- **`alignhcm-proposal`** comes first in the deal. A SOW turns an accepted
  proposal into a contract, so scope and fees should match it.
- **`alignhcm-pm-runbook`** picks up after signature. The SOW's scope becomes
  the status report's workstreams.
