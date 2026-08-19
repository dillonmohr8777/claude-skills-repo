---
name: alignhcm-pm-runbook
description: Align HCM project delivery methodology and the project status report generator. Use for any Align HCM implementation project management task - weekly status reports, status calls, RAID logs, risk registers, go/no-go readiness, client sign-offs, escalation, phase gates, project kickoff, sales-to-service transition, or onboarding a new project manager. Covers the five-phase Align methodology, what each phase requires, client level of effort, the difference between running on UKG paper and Align paper, and the weekly PM cadence. Generates a branded Word status report that refuses to report green while a high risk is open.
---

# Align HCM PM runbook

Align's project methodology, and the status report the methodology asks for but
did not have.

The PM onboarding deck says it plainly:

> Current state: PMs are sending an email summary of their project status call
> from OneNote.
> Future state: PMs will be sending a Project Status Report (pdf) for a
> consistent method of reporting out. This is currently being piloted.

This is that report, built to the nine-point structure the same deck defines, so
it matches the call it summarises section for section.

## Weekly status report

```bash
python3 scripts/build_status_report.py --spec week12.json --out-dir ./status
```

### Minimum spec

```json
{
  "client": "Northwind Traders",
  "project": "Dayforce Full Suite Launch",
  "pm": "Joann Scolaro, CPP",
  "reporting_period": "Week 12",
  "overall_status": "yellow",
  "go_live": "January 2027"
}
```

Optional and worth filling: `status_narrative`, `workstreams`,
`accomplishments`, `upcoming`, `risks`, `decisions_needed`, `action_items`,
`links`, `other`.

### It will not let you report a dishonest green

| Condition | Result |
|---|---|
| Status green while a high or critical risk is open | **Error.** Either the status is yellow, or the risk is not high |
| Status green while a decision is already past its needed-by date | **Error** |
| A workstream is red while the overall status is not | Warning, confirm it is deliberate |

This is the whole point. A status report that hides a red is worse than no
status report, because it converts a known problem into a surprise. The check
is cheap and the conversation it forces is the value.

## The methodology

Five phases, run the same way on every engagement:

1. **Project Readiness**: sales transition, welcome call, readiness workshops,
   system access, kickoff. Before the project clock starts.
2. **Analysis and Design**: requirements, business processes and rules, written
   design the client signs before anything is configured.
3. **Configuration and Build**: configuration with the client in the room, QA,
   integration build, knowledge transfer.
4. **Acceptance and Parallel Testing**: Align leads unit testing before UAT;
   parallel payroll runs twice.
5. **Go-Live and Transition**: production support, stabilization, documented
   wrap-up, deliberate handoff to ongoing support.

Full detail, including what each phase requires per workstream, the client's
level of effort per phase, and the sign-off gates:
`references/methodology.md`.

## UKG paper and Align paper are different

Access provisioning, sign-offs, escalation, and governance all differ depending
on whose paper the project runs on. Getting this wrong wastes the first two
weeks of a project. `references/paper-differences.md` has the comparison.

## Weekly cadence

| When | What |
|---|---|
| Monday | PM and PL check-in on at-risk projects; approve team timesheets |
| Before Friday | Update the project status Smartsheet and health report |
| Weekly | Client status call, internal team call the day before, PM to client-lead one-to-one |
| Within 24 hours of the call | Issue the status report |
| Monthly | Executive check-in with the client sponsor |

## Files

| Path | Purpose |
|---|---|
| `scripts/build_status_report.py` | The status report generator |
| `scripts/_core/` | Shared Align document engine, vendored |
| `references/methodology.md` | Five phases, gates, client level of effort |
| `references/paper-differences.md` | UKG paper vs Align paper |
| `references/raid-and-escalation.md` | RAID log discipline, escalation paths, go/no-go |
| `scripts/selftest.py` | Proves the documented workflow runs |

## Composition

- **`alignhcm-sow`** defines the scope this project delivers. The SOW's
  workstreams should be the status report's workstreams.
- **`alignhcm-brand-system`** owns the visual system the report renders in.
- Smartsheet remains the system of record for the project plan and RAID log.
  This report links to them rather than duplicating them.
