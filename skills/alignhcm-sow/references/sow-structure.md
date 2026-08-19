# The nine sections, and why each exists

The SOW skeleton is fixed. Knowing what each section is for makes it obvious
which ones need real attention per deal and which can take the default.

| # | Section | Purpose | Per-deal attention |
|---|---|---|---|
| 1 | Introduction | Names the parties, the platform, and the governing agreement. Establishes that out-of-scope work is handled under section 6 | Low |
| 2 | Scope of Services | The workstreams. This is the document | **High** |
| 3 | Align Responsibilities | What Align commits to. Named PM, weekly cadence, unit testing before UAT, production support | Low, unless the deal differs |
| 4 | Client Responsibilities | The participation the schedule assumes. Understating this is the single most common cause of a slipped go-live | **High** |
| 5 | Assumptions | What the price depends on. Every assumption here is a future change order avoided | **High** |
| 6 | Change Control | Written change order, executive review, signature before work. The section that protects both sides | Low |
| 7 | Investment | The table, computed from workstream hours | **High**, and check `expected_total` |
| 8 | Term | Start, end, and termination | Low |
| 9 | Acceptance | Signature blocks | Low |

## Sections 4 and 5 deserve real thought

Client responsibilities and assumptions are where a SOW either protects the
project or does not. The methodology reference in `alignhcm-pm-runbook` carries
the client level of effort by phase, in hours per week per workstream. Put the
real numbers in section 4 rather than the defaults when the client's capacity is
already a known risk.

## What this document is not

It is not the proposal. The proposal argues; the SOW records what was agreed. If
the SOW's scope and investment do not match the accepted proposal, one of the
two is wrong, and it is worth finding out which before signature rather than
after.
