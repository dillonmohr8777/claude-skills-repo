---
name: "ab-test-designer"
description: "Designs statistically-sound A/B tests — hypothesis statement, variant spec, sample size calculation, win criterion, stop-loss rules, and analysis plan. Avoids the common pitfalls (too small a sample, peeking, multiple-test-correction misses). Use when 'design an A/B test', 'how do I test this change', 'how big a sample do I need', or 'is this test result valid'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/cro
  domain: experimentation
  updated: 2026-04-26
---

# A/B Test Designer

You design A/B tests that produce statistically valid answers, not anecdotal "felt like it worked" stories. Most "A/B tests" run in marketing teams are underpowered, peeked-at-too-early, and called wins on noise.

## When to use

- Need to validate a landing page / email / ad change
- Conflicting team opinions on which variant to ship
- Setting up an ongoing experimentation program
- Auditing a past test that produced a surprising result

## Inputs you need

- **Test target:** what's being tested (page, email, ad, etc.)
- **Current performance** (baseline conversion rate or relevant metric)
- **Traffic volume** to the test (per day or per week)
- **Acceptable detectable lift** (smaller lift = bigger sample needed)
- **Win criterion** (statistical significance threshold + business significance threshold)

## The 7-step test design

### Step 1: Write the hypothesis

Bad: "Let's test a new hero."
Good: "If we replace the feature-led hero ('AI-powered analytics') with an outcome-led hero ('See your traffic patterns in 30 seconds'), then conversion will increase by ≥ 15%, because the audience cares about outcomes more than features (per audit data)."

Hypothesis = If [change], Then [predicted outcome], Because [reasoning].

If you can't write a hypothesis, you don't have a test — you have a hunch.

### Step 2: Define the primary metric

ONE primary metric per test. Not "conversion rate AND time on page AND bounce rate". Pick one.

The primary metric should be:
- Closest to revenue (purchase > add-to-cart > page view)
- Reliably tracked (no missing data, no attribution noise)
- Sensitive enough to move within the test duration

Secondary metrics: track them, but don't make decisions on them.

### Step 3: Calculate sample size

Use this rule of thumb (or a proper calculator like Evan Miller's):

| Baseline conversion rate | Min lift to detect | Sample needed per variant |
|---|---|---|
| 1% | +20% (1% → 1.2%) | 25,000 |
| 2% | +20% | 12,500 |
| 5% | +20% | 5,000 |
| 10% | +20% | 2,500 |
| 20% | +20% | 1,250 |

**Power = 80%, alpha = 0.05.** If you want 95% power or stricter alpha, multiply by 1.5x.

If your traffic doesn't support the sample size in 2-4 weeks, the test isn't viable. Either:
- Test something with a bigger expected effect (hero rewrite, not button-color tweak)
- Combine with similar tests (e.g. test the whole landing page redesign as one variant)
- Reduce confidence threshold to 90% (with explicit acceptance of more false positives)

### Step 4: Define win criteria

Both must be met:

- **Statistical significance:** p < 0.05 (or alpha set higher with documented reasoning)
- **Business significance:** lift ≥ minimum interesting lift (typically 5-10%)

A test that hits stat-sig but only at +1% lift may not be worth the implementation cost.

### Step 5: Stop-loss rules

When to kill the test before reaching sample size:

- **Variant performs ≥ 50% worse with > 20% sample reached** → kill (clear loser)
- **Implementation bug detected** → invalidate, restart
- **External factor changes** (algorithm change, viral mention, news event) → pause until normal

NEVER stop a test early because the variant is "winning" before reaching sample size. That's peeking — false positives are very high.

### Step 6: Analysis plan

Pre-register the analysis plan BEFORE running the test:

- Which metric to evaluate
- Sample size to reach before evaluation
- Statistical method (t-test for continuous, z-test for proportions, sequential testing if you have a tool)
- How to handle anomalies / outliers
- Decision rule (A wins / B wins / inconclusive)

This prevents the post-hoc "let me slice by user segment until I find a positive result" trap.

### Step 7: Document the test

Every test gets logged with:
- Hypothesis
- Test dates
- Variants screenshots / details
- Results table (with confidence intervals)
- Decision made
- Implementation status

Builds organizational learning. Don't run the same test twice.

## Output format

```
# A/B Test Plan: <test name>

## Hypothesis
If [change], Then [outcome], Because [reasoning].

## Variants

### Variant A (Control)
[Description / screenshot]

### Variant B (Test)
[Description / screenshot]

## Primary metric
- Metric: <conversion rate / purchase rate / etc.>
- Current baseline: X% over last 30 days
- Tracking: [GA4 event / pixel / platform]

## Secondary metrics (track but don't decide on)
- Bounce rate
- Time on page
- Scroll depth

## Sample size calculation
- Baseline: X%
- Minimum detectable lift: +Y%
- Power: 80%
- Alpha: 0.05
- **Required sample per variant: N**
- Daily traffic to test: M
- **Estimated test duration: N/M days**

## Win criteria
- Statistical significance: p < 0.05
- Business significance: lift ≥ +Y%
- BOTH required to declare winner

## Stop-loss rules
- Variant B performs ≥ 50% worse than A at any point with > 20% of sample reached → kill
- Bug detected → invalidate test, restart
- External anomaly (algorithm change, news event) → pause

## Analysis plan
- Tool: [Optimizely / VWO / Google Optimize alternative / custom]
- Method: z-test for proportions (or sequential test if tool supports)
- Anomaly handling: exclude visits during [defined anomaly windows]
- Segment analysis: NONE pre-registered (don't slice post-hoc to find positives)

## Decision rule
- B wins (ship B): primary metric +Y% AND p < 0.05
- A wins (kill B): primary metric -Y% AND p < 0.05
- Inconclusive: anything else; default to keeping current

## Documentation
- Pre-register: [link to test doc]
- Post-test: update doc with results, decision, learnings

## Estimated calendar
- Test start: [date]
- Sample reached (estimate): [date + N days]
- Analysis: [date + N+1 days]
- Decision: [date + N+2 days]
```

## Common mistakes

1. **Underpowered tests.** Running a test with 100 conversions per variant and calling it. False positive rate >25%.
2. **Peeking.** Checking results daily and calling winners early. Multiplies false positive rate.
3. **No pre-registered plan.** Post-hoc slicing finds "winning segments" that are just noise.
4. **Multiple metrics.** Testing 5 metrics at p < 0.05 → 23% chance of false positive on at least one.
5. **No business-significance threshold.** Stat-sig +1.2% lift on a small change isn't worth implementing.
6. **Running tests during anomalies.** Black Friday traffic, algorithm shifts, news events distort results.

## Leverage with other skills

- Pair with `landing-page-auditor` to source the test backlog
- Pair with `funnel-leakage-mapper` to identify highest-impact test areas
- Pair with `ga4-setup-architect` to ensure tracking is reliable before running tests

## MCP integration

This skill is methodology + planning. No MCP required. Outputs feed into testing tools (VWO, Convert, custom) which usually have their own integrations.
