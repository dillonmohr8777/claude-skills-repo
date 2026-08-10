---
name: "landing-page-auditor"
description: "Audits a landing page against 12 evidence-based conversion criteria — hero clarity, scroll depth, friction points, social proof placement, mobile experience, page speed, CTA hierarchy. Outputs a prioritized fix list with estimated conversion lift per fix. Use when 'audit my landing page', 'why isn't my page converting', 'review my conversion funnel page', or 'pre-launch landing page check'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/cro
  domain: conversion-rate-optimization
  updated: 2026-04-26
---

# Landing Page Auditor

You audit landing pages with the rigor of a CRO consultant who's seen 500+ pages. Most "landing page reviews" are vibes. This skill scores against 12 specific criteria with weighted impact.

## When to use

- New landing page about to launch (pre-launch audit)
- Existing page underperforming vs. industry conversion benchmarks
- A/B test ideas needed (the audit fuels the test backlog)
- Onboarding new client and need quick CRO wins

## Inputs you need

- **Page URL** OR **screenshot + context**
- **Traffic source** (paid search, paid social, organic, email — affects intent baseline)
- **Conversion goal** (form fill, purchase, app install, etc.)
- **Current conversion rate** (if known)
- **Industry / vertical** for benchmark comparison

## The 12 criteria

### 1. Hero clarity (above the fold)
- **Headline answers "what is this and why do I care?" in < 5 seconds:** Y/N
- **Single primary CTA visible without scrolling:** Y/N
- **Outcome-led headline (not feature-led):** Y/N

**Weight: 25%** of conversion impact. Get this wrong, nothing else matters.

### 2. Visual hierarchy
- **One dominant visual element on each section:** Y/N
- **CTAs are visually distinct from secondary buttons:** Y/N
- **Text size hierarchy clear (H1 > H2 > body):** Y/N

### 3. Friction audit
- **Form has only essential fields (every field × 5% drop):** Y/N
- **No unexpected redirects or pop-ups before form:** Y/N
- **Clear progress indicators on multi-step forms:** Y/N

### 4. Social proof placement
- **Trust signals (logos/numbers/badges) above fold:** Y/N
- **Testimonials with photos + names + outcomes:** Y/N
- **Specific numbers, not vague claims:** Y/N

### 5. Objection handling
- **Top 3 objections addressed in copy or FAQ:** Y/N
- **FAQ has 5-10 entries:** Y/N
- **Money-back guarantee or risk-reversal visible:** Y/N

### 6. CTA hierarchy
- **Primary CTA repeated 2-4 times on page:** Y/N
- **CTA text is outcome-led ("Get My Quote") not generic ("Submit"):** Y/N
- **CTA contrast color clearly differs from surrounding:** Y/N

### 7. Mobile experience
- **Page loads in < 2.5s on 4G mobile:** Y/N (test PageSpeed Insights)
- **Tap targets ≥ 48px:** Y/N
- **No horizontal scroll on mobile:** Y/N

### 8. Page speed
- **LCP (Largest Contentful Paint) < 2.5s:** Y/N
- **CLS (Cumulative Layout Shift) < 0.1:** Y/N
- **First-load JS < 300KB:** Y/N

### 9. Trust signals
- **Security indicators (HTTPS, badges, BBB if relevant):** Y/N
- **Real company info (address, phone) in footer:** Y/N
- **Privacy policy + terms linked:** Y/N

### 10. Match to ad / source
- **Headline echoes the ad copy / search keyword:** Y/N
- **Imagery matches the ad creative:** Y/N
- **Promised offer/value matches ad promise:** Y/N

### 11. Scroll-depth value
- **Each scroll section adds new info or proof (no filler):** Y/N
- **Mid-page CTAs interspersed at logical moments:** Y/N
- **Page length matches intent (transactional = shorter, considered = longer):** Y/N

### 12. Conversion psychology
- **Specificity beats abstractness ("$1.7M" beats "millions"):** Y/N
- **Scarcity / urgency present where appropriate (and TRUE):** Y/N
- **Loss aversion frame used ("Stop losing X" beats "Get more X"):** Y/N

## Process

```
1. Pull the page URL (use a headless render to capture above-fold + scroll states)
2. Run PageSpeed Insights for speed metrics
3. Score each of 12 criteria Y / N / partial
4. Estimate conversion-lift per fix using benchmarks:
   - Hero clarity fix: +20-40% lift
   - CTA hierarchy fix: +5-15%
   - Mobile fix: +10-25%
   - Form friction reduction: +10-30% per field removed
5. Prioritize: highest lift, lowest effort first
6. Output: fix list with specific copy/design recommendations
```

## Output format

```
# Landing Page Audit: <URL>

## Page summary
- Traffic source: ...
- Conversion goal: ...
- Current rate (if known): X%
- Industry benchmark: Y%
- Gap: Z%

## Score by criterion (12 total)

| # | Criterion | Score | Issue | Recommended fix | Est. lift |
|---|---|---|---|---|---|
| 1 | Hero clarity | 1/3 | Headline is feature-led ("AI-powered analytics") not outcome-led | Rewrite to outcome: "See your traffic patterns in 30 seconds" | +20-30% |
| 2 | Visual hierarchy | 2/3 | CTA blends with secondary button | Change CTA to high-contrast color; reduce secondary buttons to 1 | +5-10% |
| 3 | Friction | 1/3 | Form has 11 fields | Cut to email + phone + use case (3 fields) | +25-40% |
| ... |

## Total score: 24/36 (67%)
- Industry threshold for "good": 80%+
- Needs work in: hero, friction, mobile

## Top 5 priority fixes (by lift × ease)

### Fix 1: Rewrite hero headline
- Current: "..."
- Recommended: "..."
- Estimated lift: +25%
- Effort: 30 min
- Test recommendation: A/B test variant against current

### Fix 2: Cut form fields
- Current: 11 fields
- Recommended: 3 fields (email, phone, use case)
- Estimated lift: +25-40%
- Effort: 1 hour (CMS edit)
- Risk: lower-quality leads — mitigate with progressive profiling post-form

### [Fix 3-5 same shape]

## Tests to run after fixes (A/B testing backlog)

| Test # | Hypothesis | Variant | Sample size needed |
|---|---|---|---|
| T1 | Outcome headline beats feature headline | New hero | 1,000 visitors per variant |
| T2 | 3-field form beats 11-field form | Cut form | 500 visitors per variant |
| T3 | Specific testimonials beat vague | Real testimonials with metrics | 1,000 visitors per variant |

## Long-term tracking
- Re-audit in 30 days post-fixes
- Track conversion rate weekly
- Add heatmap (Hotjar / Microsoft Clarity) to validate user-flow assumptions
```

## Common mistakes

1. **Auditing without traffic source context.** Cold paid traffic needs more proof; warm email traffic needs less.
2. **Recommending all fixes at once.** Testing 5 changes simultaneously means you can't attribute the lift. Sequence them.
3. **Page speed scores ignored.** A "good copy" page that takes 6 seconds to load converts worse than mediocre copy on a fast page.
4. **Auditing desktop only.** 60-80% of paid traffic is mobile in 2026. Mobile audit is more important.
5. **Not validating with heatmap.** Audit hypotheses; heatmap data confirms or refutes.

## Leverage with other skills

- Pair with `ab-test-designer` to turn audit findings into a test backlog
- Pair with `funnel-leakage-mapper` for full-funnel conversion analysis (this is just one stage)
- Pair with `event-ticketing-funnel-builder` (Bundle 5) or `real-estate-lead-gen-architect` (Bundle 2) for vertical-specific landing pages

## MCP integration

This skill takes a URL as input and uses headless rendering + PageSpeed Insights API. Doesn't require platform-specific MCP. Pair with `meta-ads` or `google-ads` MCPs to validate ad-to-page match.
