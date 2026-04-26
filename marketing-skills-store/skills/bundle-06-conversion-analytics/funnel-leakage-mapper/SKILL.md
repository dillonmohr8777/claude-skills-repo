---
name: "funnel-leakage-mapper"
description: "Maps end-to-end conversion funnels and identifies the highest-impact drop-off step — quantifies traffic loss at each stage, estimates revenue impact of fixing each leak, and prioritizes by impact-per-effort. Use when 'where am I losing customers', 'audit my funnel', 'why is my conversion rate so low', or 'what should I fix first'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/cro
  domain: funnel-analysis
  updated: 2026-04-26
  mcp_servers: ["ga4", "hubspot", "google-ads", "meta-ads"]
---

# Funnel Leakage Mapper

You map the actual conversion funnel — every step from ad impression to closed deal — and quantify the leakage at each stage. Most marketers optimize the step they can see ("CTR went up!") and ignore the step that matters ("...but lead-to-close dropped").

## When to use

- Conversion rate is below benchmark and you don't know where the leak is
- Multi-channel campaign with no integrated attribution
- New strategy launching — want baseline funnel mapped before iterating
- Ongoing performance reviews (monthly or quarterly)

## Inputs you need

- **Channels in scope:** paid search, paid social, organic, email, etc.
- **Goal definition:** what's the final conversion (purchase, closed deal, signup)
- **Data sources:** GA4, ad platforms (Meta/Google), CRM (HubSpot), email tool
- **Time window:** typically last 30/90 days

## The standard 7-stage funnel

Most B2C/B2B funnels collapse to this shape:

| Stage | Tracking source | Common conversion rate range |
|---|---|---|
| 1. Ad impression | Ad platform | (baseline) |
| 2. Click → page visit | Ad platform + GA4 | 0.5-5% (CTR) |
| 3. Page visit → form view / engaged session | GA4 | 30-60% |
| 4. Engaged session → form fill / lead | GA4 + CRM | 10-30% (form fill) |
| 5. Lead → MQL (qualified) | CRM | 30-60% |
| 6. MQL → SQL / Sales-engaged | CRM | 30-50% |
| 7. SQL → Closed deal | CRM | 20-50% |

End-to-end (impression → closed deal): typically 0.001-0.01% in B2B paid; 0.1-2% in B2C.

## Process

### Step 1: Pull data per stage

For the chosen window, get:
- Total impressions per channel (ad platform)
- Clicks → sessions (GA4 unique pageviews on landing pages)
- Engaged sessions (GA4 engagement_rate)
- Form fills (GA4 + CRM contact creation)
- MQL count (CRM lifecycle stage = MQL)
- SQL count (CRM lifecycle stage = SQL)
- Closed deals (CRM deal stage = Closed Won)

### Step 2: Calculate stage-to-stage conversion

For each adjacent pair of stages, compute the conversion rate.

### Step 3: Compare to benchmarks

Use industry benchmarks (or your own historical data, which is better):

- Stage 2 → 3 (page → engaged): if < 40%, page experience problem
- Stage 3 → 4 (engaged → form): if < 10%, form/page friction
- Stage 4 → 5 (lead → MQL): if < 30%, lead quality / scoring problem
- Stage 5 → 6 (MQL → SQL): if < 30%, sales handoff or sales process problem
- Stage 6 → 7 (SQL → close): if < 20%, sales close skill or product/market problem

The biggest negative deviation from benchmark is your highest-impact leak.

### Step 4: Quantify the dollar impact

For each leak:
- "If I move stage X→Y from current rate to benchmark, additional conversions = N"
- "N additional conversions × avg deal value = $X annual revenue impact"

This is the line that gets prioritization right. A 10% conversion-rate fix at stage 2 might be $20K/year. A 5% fix at stage 6 might be $200K/year.

### Step 5: Identify root causes

Each leak has 1-3 candidate root causes. Don't guess — investigate.

| Stage leak | Common root causes | Diagnostic |
|---|---|---|
| 2 → 3 (poor engagement) | Ad-page mismatch, slow page, wrong intent | Heatmap; ad creative review |
| 3 → 4 (low form fill) | Form length, friction, no trust | Form-field-level analytics |
| 4 → 5 (low MQL rate) | Wrong audience targeting, weak lead scoring | Lead-source analysis by stage |
| 5 → 6 (slow handoff) | No SLA, manual handoff, unclear MQL definition | Time-in-stage analysis |
| 6 → 7 (low close) | Sales skill, product fit, pricing | Win/loss analysis |

### Step 6: Prioritize fixes

Score each leak by:
- **Impact:** $ revenue lift if fixed to benchmark
- **Effort:** S/M/L (hours, days, or weeks of work)
- **Confidence:** how certain are you the proposed fix will work?

Impact ÷ Effort = priority score. Top 3 fixes get scheduled in the next 2 weeks.

## Output format

```
# Funnel Leakage Map: <channel / campaign / brand>

## Window: last X days

## Funnel summary

| Stage | Volume | Conversion to next | Benchmark | Variance |
|---|---|---|---|---|
| Impressions | 500,000 | — | — | — |
| Clicks | 5,000 (1.0% CTR) | 1.0% | 1.5% | -0.5% |
| Engaged sessions | 1,800 (36%) | 36% | 50% | -14% |
| Form fills | 90 (5%) | 5% | 15% | -10% |
| MQLs | 30 (33%) | 33% | 40% | -7% |
| SQLs | 12 (40%) | 40% | 40% | 0% |
| Closed deals | 4 (33%) | 33% | 30% | +3% |

End-to-end: 0.0008% (impression → close) — vs. benchmark 0.003%

## Top 3 leaks (by revenue impact)

### Leak 1: Engaged session → form fill (5% vs. 15% benchmark)
- Impact: if fixed to 15%, +180 form fills/window = +60 MQLs = +6 SQLs = +2 closed deals = $X revenue
- Likely root cause: form too long (currently 11 fields) or page-ad mismatch
- Recommended fixes:
  1. Cut form to 4 essential fields (est. lift 5% → 12%)
  2. A/B test new outcome-led headline (est. lift +10%)
  3. Add live testimonial above form
- Effort: S (form edit + headline test, 2 days)
- Priority: 1

### Leak 2: Click → engaged session (36% vs 50% benchmark)
- Impact: if fixed to 50%, +700 engaged sessions = ~+33 form fills = $Y additional revenue
- Likely root cause: page speed (LCP 4.2s) + above-fold copy mismatch with ad
- Recommended fixes:
  1. PageSpeed optimization (defer JS, optimize images)
  2. Rewrite hero to match ad copy verbatim
- Effort: M (page speed work, 1 week)
- Priority: 2

### Leak 3: Lead → MQL (33% vs 40%)
- Impact: marginal — $Z additional revenue
- Likely root cause: lead-source mix shifted toward broader audiences
- Recommended fixes:
  1. Tighten Meta Ads audience to 1% LAL only (kill the 5% LAL)
  2. Re-tune lead scoring weights
- Effort: M
- Priority: 3

## Tests to run after fixes
- Re-measure funnel in 30 days
- Check for downstream impact (did fixing form fills hurt MQL rate?)

## Quarterly review cadence
- Re-map funnel quarterly
- Track each leak's variance from benchmark over time
- Prioritize new fixes based on highest-variance leaks
```

## Common mistakes

1. **Optimizing the easy-to-measure stage.** CTR is easy; lead-to-close is hard. The hard one usually has bigger leverage.
2. **Single-channel funnel analysis.** Channels behave differently. Map per-channel separately.
3. **No revenue quantification.** "Improve CTR by 0.5%" doesn't tell anyone what it's worth.
4. **Looking at conversion rates without volume.** A 50% conversion rate at stage 7 with 4 SQLs/month means very different things at 4 SQLs/year vs 4 SQLs/day.
5. **Comparing to wrong benchmarks.** B2B SaaS benchmarks don't apply to local services. Find vertical-specific benchmarks or use your own historical data.

## Leverage with other skills

- Pair with `ab-test-designer` to test the proposed fixes
- Pair with `landing-page-auditor` for stage 2-3 specific audits
- Pair with `attribution-model-picker` to confirm channel-level data is reliable before mapping
- Pair with `ga4-setup-architect` if your tracking has gaps making the analysis unreliable

## MCP integration

With multiple MCPs together: `Pull stage-by-stage funnel data from GA4 (sessions, engaged sessions, conversions), HubSpot (leads, MQLs, SQLs, closed deals), Google Ads (impressions, clicks), and Meta Ads (impressions, clicks). Merge by date. Compute stage-to-stage conversion. Compare to provided benchmarks. Output prioritized leak list with revenue impact.`
