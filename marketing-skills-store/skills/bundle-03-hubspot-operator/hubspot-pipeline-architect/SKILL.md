---
name: "hubspot-pipeline-architect"
description: "Designs HubSpot deal pipelines and ticket pipelines that match how sales/service teams actually work — stage definitions, required-field gates, automation hooks, and reporting alignment. Outputs a stage-by-stage spec ready to build via HubSpot MCP. Use when 'set up a HubSpot pipeline', 'pipeline stages don't match our process', 'reporting is broken', or 'multiple pipelines for different products'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/sales-ops
  domain: hubspot
  updated: 2026-04-26
  mcp_servers: ["hubspot"]
---

# HubSpot Pipeline Architect

You design deal pipelines that actually match the sales reality, not generic templates. Most HubSpot pipelines are wrong because they were copy-pasted from a template — stages don't match the team's process, reps fudge stages to hit metrics, and reporting becomes meaningless.

## When to use

- New HubSpot account / new sales process needs a foundational pipeline
- Reporting is unreliable (deals jump stages, stay in stages too long)
- Multiple products / motions need separate pipelines
- Sales team is misusing existing stages

## Inputs you need

- **Sales motion:** inbound, outbound, channel/partner, hybrid
- **Average sales cycle length**
- **Average deal value (ACV)**
- **Team size + structure** (BDR/SDR + AE? solo AE? hybrid?)
- **Reporting needs:** what metrics does leadership ask for?
- **Existing pipelines:** if any, audit before recommending

## Pipeline design principles

### 1. Stages should be exit-criteria-defined, not activity-defined

Bad: "Discovery Call Booked"
Good: "Champion Identified + Pain Confirmed"

Stages should describe a *state* the deal has reached, not an *activity* a rep performed. Activities can fail — a deal can have a discovery call and not have a confirmed pain. State-based stages prevent rep fudging.

### 2. Every stage has a deal-stage probability

HubSpot's default probabilities are nonsense (10/20/30/40/50/60/100). Replace with actual:

- Stage 1 (Open): 5%
- Stage 2 (Engaged): 15%
- Stage 3 (Qualified): 30%
- Stage 4 (Proposal): 50%
- Stage 5 (Negotiation): 70%
- Stage 6 (Closed Won): 100%
- Stage 7 (Closed Lost): 0%

Calibrate from your actual win rates per stage in HubSpot Reports. Update quarterly.

### 3. Required fields gate stage progression

Every stage transition should require certain fields to be populated. Examples:

| Move to stage | Required fields |
|---|---|
| Engaged | Decision Timeline, Budget, Use Case |
| Qualified | Champion Name, Pain Statement, Buying Process Confirmed |
| Proposal | Total Contract Value, Proposal Sent Date, Proposal Type |
| Negotiation | Counterparty Legal Review (Y/N), Pricing Approval (if discounted) |
| Closed Won | Contract Signed Date, Implementation Owner, Renewal Date |
| Closed Lost | Loss Reason (dropdown), Competitor (if applicable) |

If reps don't fill required fields, they can't move the deal. This forces data hygiene.

### 4. Stage age alerts

Stages have expected dwell times. If a deal sits too long, flag it:

| Stage | Expected dwell | Alert at |
|---|---|---|
| Open | < 7 days | 14 days |
| Engaged | < 14 days | 30 days |
| Qualified | < 21 days | 45 days |
| Proposal | < 30 days | 60 days |
| Negotiation | < 14 days | 30 days |

Build a workflow: deal in stage > X days → alert deal owner + manager.

### 5. Multiple pipelines for distinct motions

Don't shove different sales motions into one pipeline. Split when:

- Different products with different sales cycles (SaaS vs services)
- Different motions (inbound vs outbound)
- Different ACVs (small biz vs enterprise)
- Different teams (US vs EU)

Each pipeline gets its own stages and reporting. HubSpot supports up to 50 deal pipelines on most plans.

### 6. Closed-Lost stage is non-negotiable

Many teams skip Closed Lost or use one generic "Lost" stage. Build it properly:

- **Loss Reason** required dropdown: Budget, Competitor (which one), No Decision, Wrong Fit, Lost to Status Quo, Timeline, Other
- **Competitor** if applicable (free-text or controlled list)
- **Re-engage Date** if appropriate

This is the data that powers competitive analysis + win-back campaigns.

## Process

```
1. Audit existing process via interviews / current pipeline review
2. Map current stages → state-based names; eliminate activity-based stages
3. Define required fields per stage (gate progression)
4. Set realistic probabilities per stage (calibrate from actual data)
5. Define stage-age alert thresholds
6. Build supporting workflows (alerts, lifecycle changes, contact owner sync)
7. Build via HubSpot MCP; save as DRAFT
8. Run pilot with 5-10 active deals before account-wide cutover
```

## Output format

```
# HubSpot Pipeline Design: <client / motion>

## Pipeline overview
- Name: ...
- Currency: ...
- Used for: <product / motion>
- Expected sales cycle: X days
- Expected win rate: Y%

## Stages

### Stage 1: Open
- Probability: 5%
- Definition: New opportunity created. No qualification yet.
- Required fields to ENTER: Lead Source, Deal Owner
- Required fields to MOVE FORWARD: First Activity Logged
- Stage-age alert: 14 days
- Automation: notify deal owner of new deal

### Stage 2: Engaged
- Probability: 15%
- Definition: Two-way conversation established. Buyer expressed interest.
- Required fields to MOVE FORWARD: Decision Timeline, Budget Range, Use Case
- Stage-age alert: 30 days
- Automation: send 'meeting prep' template to rep at Day 7

### [Stage 3-6 same shape]

### Closed Won
- Probability: 100%
- Required fields: Contract Signed Date, Implementation Owner, Renewal Date, Total Contract Value
- Automation: trigger handoff workflow → notify CSM, create implementation tasks, update company ARR field, send customer welcome sequence

### Closed Lost
- Probability: 0%
- Required fields: Loss Reason (dropdown), Competitor (if any), Re-engage Date (optional)
- Automation: add to "lost deals" reporting; if Loss Reason = "Timeline" → auto-set re-engage task in 90 days

## Supporting workflows
1. Stage age alerts (per stage)
2. Closed Won handoff
3. Closed Lost re-engagement (timeline-based losses)
4. Owner change notifications

## Reporting alignment
- Pipeline coverage: 3x quota target
- Stage conversion rates: tracked per quarter
- Velocity report: avg dwell per stage; flag outliers
- Loss reason distribution: monthly review for product/marketing feedback

## Implementation plan
1. Build pipeline as DRAFT
2. Migrate existing 5 active deals manually with stage mapping
3. Train sales team (30-min walkthrough of stage definitions)
4. Activate; monitor first 2 weeks for stage-age alerts firing correctly
5. Quarterly review: re-tune probabilities + required fields
```

## Common mistakes

1. **Activity-based stages ("Demo Booked").** Use state-based ("Champion Identified + Pain Confirmed") so failed activities don't pollute the funnel.
2. **No required fields.** Reps move deals without data. Reporting becomes garbage.
3. **Default probabilities.** They don't match reality. Calibrate quarterly.
4. **One pipeline for everything.** Different motions need different pipelines.
5. **Skipping Closed Lost detail.** No competitive intel, no win-back triggers.
6. **No stage-age alerts.** Deals rot in stage; reps don't notice; quarter ends with nothing closed.

## Leverage with other skills

- Pair with `hubspot-workflow-designer` to build the supporting automations
- Use `hubspot-lead-scoring-builder` so MQL/SQL transitions map cleanly to pipeline stages
- Run with `mortgage-funnel-builder` (Bundle 2) for the marketing → sales handoff in mortgage operations

## MCP integration

With `hubspot` MCP: `Build the deal pipeline exactly as specified, including all stages, probabilities, required fields, and the 4 supporting workflows. Save as DRAFT in a separate test pipeline before migrating active deals.`
