# Align HCM document suite

Four skills that produce Align's most-repeated client-facing documents, plus the
engine they share.

| Skill | Produces | Format |
|---|---|---|
| `alignhcm-intro-deck` | Partner introduction, one per new deal | 15-slide `.pptx` |
| `alignhcm-proposal` | Phased services proposal with a computed investment table | `.pptx` |
| `alignhcm-sow` | Statement of Work | `.docx` |
| `alignhcm-pm-runbook` | Weekly project status report, plus the delivery methodology | `.docx` |

They follow the deal in that order, which is also the order in which their
content should agree: the proposal argues, the SOW records what was agreed, and
the status report tracks what was recorded.

## Why a shared engine

All four solve the same problem: take an approved structure, fill it with this
deal's facts, prove nothing from the last deal survived, and write it where a
colleague can find it. That is solved once in `alignhcm_core.py` and vendored,
because a Claude skill installs standalone and cannot import a sibling.

Vendoring rots without discipline, so `sync_core.py` writes a hash manifest into
each skill and every self-test checks its copies against it. Editing a vendored
file directly fails the suite.

```bash
python3 sync_core.py           # copy the canonical core into all four skills
python3 sync_core.py --check    # verify only, non-zero if drifted
```

Never edit `*/scripts/_core/*`. Edit here, then sync.

## What the engine provides

| Module | Provides |
|---|---|
| `alignhcm_core.py` | Placeholder discovery and fill across Word and PowerPoint, residue scanning, deterministic naming and superseding, company facts, brand colour gate |
| `alignhcm_docx.py` | A branded Word writer: headings, tables, bullets, title blocks, signature blocks |
| `alignhcm_pptx.py` | A branded 16:9 deck writer: covers, section dividers, card grids, phase bands, data tables |
| `selftest_common.py` | The checks every skill shares |
| `company-facts.md` | Align's own numbers, in one place |

No third-party dependencies. An Office file is a zip of XML, which is all any of
this needs.

## The two problems this suite exists to fix

**Version chaos.** SharePoint holds four SOWs for one client, including one
named `_revisedMoe15Aug2025` and an `/OLD/` folder with three more. Every skill
writes `Client_Artifact_YYYY-MM-DD_vN.ext` and moves the previous version to
`_superseded/`. Nothing is deleted; it just stops competing.

**Facts that disagree.** Two decks shipped in 2026 saying 60+ and 100+ team
members, 115+ and 111 reviews. Both went to prospects. `company-facts.md` is the
single source, and it carries a review date so it can go stale loudly.
