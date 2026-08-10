---
name: "hubspot-lead-scoring-builder"
description: "Designs and implements a lead-scoring model in HubSpot — fit + behavior weighting, score decay, threshold triggers for sales handoff. Outputs a scoring spec mapped to HubSpot's HubSpot Score property + supporting custom properties + workflows that act on score changes. Use when 'set up lead scoring', 'sales is getting bad leads', 'qualify leads automatically', or 'we need an MQL definition'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/automation
  domain: hubspot
  updated: 2026-04-26
  mcp_servers: ["hubspot"]
---

# HubSpot Lead Scoring Builder

You build lead-scoring models that sales actually trusts. Most lead scoring fails because the model is theoretical — built off "we think these things matter" — and never validated against closed-won data. Yours is data-grounded.

## When to use

- Sales complains about lead quality
- MQL/SQL definitions are vague or non-existent
- High lead volume + no automated qualification
- Onboarding new HubSpot account that needs foundational scoring

## Inputs you need

- **Closed-won deals from last 12 months** (HubSpot MCP can pull)
- **Closed-lost deals** for negative-signal calibration
- **Current MQL definition** (if any)
- **Sales handoff process:** what should trigger the alert?
- **Industry context:** B2B/B2C, ACV range, sales cycle length

## The two-axis scoring model

HubSpot supports a single `HubSpot Score` property out of the box. You'll likely need custom properties to track separately:

| Score type | Tracks | Custom property name |
|---|---|---|
| **Fit score** | Demographic + firmographic match (right ICP) | `Fit Score` |
| **Behavior score** | Engagement signals (interest level) | `Behavior Score` |
| **Composite** | Combined gate for sales handoff | `HubSpot Score` (default) |

A contact who's a perfect fit but hasn't engaged is not the same as a poor fit who keeps engaging. Single-axis scoring can't tell them apart.

## Process

### 1. Audit closed-won contacts

Pull last 12 months of closed-won deals' associated contacts. Identify common patterns:

- Industry / company size (B2B)
- Title / seniority (B2B)
- Geo
- Source channel
- Time from first touch to close
- Behaviors before close: # email opens, # site visits, content downloads

Build the **fit profile** from this. Anything > 60% of your closers shared = positive fit signal.

### 2. Audit closed-lost / disqualified contacts

Same pull, opposite end. Common patterns among bad-fit:

- Wrong industry (e.g. you sell B2B SaaS, lots of leads are students)
- Wrong title (lots of intern submissions)
- Wrong geo (you don't service that state)
- Wrong source (LinkedIn organic delivers tire-kickers vs. paid search)

Build the **disqualifier list** from this. Anything > 70% of your bad-leads shared = negative fit signal.

### 3. Design the fit-score model

Total range: -50 to +100. Examples:

| Property | Score | Reasoning |
|---|---|---|
| Industry = "Real Estate" or "Financial Services" | +30 | ICP match |
| Industry = "Other" | 0 | Neutral |
| Industry = "Education" or "Government" | -20 | Disqualifier |
| Title contains "Director", "VP", "CMO", "Head of" | +20 | Decision-maker |
| Title contains "Student", "Intern", "Looking for work" | -50 | Hard disqualifier |
| Country in ["US", "CA", "UK", "AU"] | +10 | Service area |
| Country not in service area | -30 | Disqualifier |
| Company size 50-500 | +15 | Sweet spot |
| Company size 1-10 | -10 | Too small for our ACV |
| Email domain is generic (gmail, yahoo) AND title contains "CEO" | -15 | Role-mismatch flag |

### 4. Design the behavior-score model

Total range: 0 to +100. Examples:

| Behavior | Score | Cap |
|---|---|---|
| Submitted high-intent form (demo, application) | +30 | once per form |
| Submitted low-intent form (newsletter, gated content) | +10 | once per form |
| Visited pricing page | +15 | once per 30 days |
| Visited 3+ pages in single session | +10 | once per session |
| Email opened | +2 | max +20 (cap repeat opens) |
| Email link clicked | +5 | max +30 |
| Replied to sales email | +25 | once |
| Booked a meeting | +50 | once |
| Engaged with chatbot | +5 | once per session |
| Downloaded mid-funnel asset (case study, comparison) | +15 | once per asset |

### 5. Score decay

Behavior scores decay if contact goes silent. Default: -10 every 14 days of no engagement, floor at 0.

This prevents stale scores from triggering sales actions. A contact who scored 80 a year ago and hasn't done anything since is not a hot lead.

Implement decay via a **scheduled workflow** that runs nightly:
- Trigger: contact-based, runs daily
- Filter: last engagement > 14 days ago
- Action: subtract 10 from Behavior Score (don't go below 0)

### 6. Composite + thresholds

`HubSpot Score = Fit Score + Behavior Score`

| Threshold | Lifecycle stage | Action |
|---|---|---|
| < 25 | Subscriber | Marketing nurture only |
| 25-49 | Lead | Marketing nurture + retargeting |
| 50-79 | MQL | Send to sales queue (long-tail) |
| 80-99 | SQL | Assign to AE; 24-hr SLA |
| 100+ | Hot | Assign to AE; 1-hr SLA + Slack alert |

### 7. Workflows that act on score

Build these alongside the scoring:

- **Score crosses 50:** lifecycle = MQL, assign owner via round-robin, send internal Slack notification, add to MQL list
- **Score crosses 80:** lifecycle = SQL, escalate to AE, send "hot lead" Slack
- **Score crosses 100:** hot-lead alert email to manager + AE, auto-create deal in pipeline
- **Score decays below 50:** lifecycle steps back to Lead, remove from MQL list (don't accidentally pass stale leads)

## Output format

```
# HubSpot Lead Scoring Model: <client>

## ICP profile (validated against closed-won)
[Industry, title, geo, size]

## Disqualifier profile
[List]

## Fit score property: 'Fit Score' (-50 to +100)
[Full criteria list with weights]

## Behavior score property: 'Behavior Score' (0 to +100)
[Full criteria list with weights + caps]

## Composite + thresholds
[Tier table]

## Workflows to build
1. Score crosses 50 (MQL)
2. Score crosses 80 (SQL)
3. Score crosses 100 (Hot)
4. Score decay (daily)
5. Score < 50 (lifecycle step-back)

## Implementation order
1. Create custom properties: Fit Score, Behavior Score
2. Set HubSpot Score property formula: Fit + Behavior
3. Build scoring rules in HubSpot Score settings
4. Build 5 workflows above
5. Test with 5 contacts across spectrum
6. Activate

## Validation plan
- Track: closed-won rate at each tier (validates the thresholds)
- Track: time from MQL → SQL → close (validates the cadence)
- Re-tune quarterly: add/remove criteria based on what predicts close
```

## Common mistakes

1. **Building lead scoring without closed-won data.** It's theoretical and sales won't trust it. Validate against actual deals.
2. **No score decay.** Old "hot" leads never cool down; sales gets handoff for stale leads.
3. **Single threshold (everyone above X is MQL).** Tiered handoff (MQL/SQL/Hot) reflects reality better.
4. **Scoring email opens too high.** Email opens are noisy (Apple Mail Privacy Protection inflates them). Cap at +20 total.
5. **No internal notification at top tier.** If a hot lead crosses 100 at 8pm and the sales team finds out at 9am, you've lost the lead.

## Leverage with other skills

- Pair with `hubspot-workflow-designer` for the workflows that act on score
- Use `hubspot-pipeline-architect` to define the deal-pipeline stages that score thresholds map to
- Run with `hubspot-blog-optimizer` so behavior scores from blog reads feed into the model

## MCP integration

With `hubspot` MCP: `Build the lead-scoring model exactly as specified above, including custom properties, scoring rules, and the 5 supporting workflows. Save all workflows as DRAFT. Generate a test plan with 5 contacts spanning the score tiers.`
