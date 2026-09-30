---
name: "attribution-model-picker"
description: "Picks the right attribution model for the user's business — last-click, first-click, linear, time-decay, position-based, or data-driven — with rationale, tradeoffs, and platform-specific implementation. Includes the iOS 14.5+ adjustments for mobile attribution. Use when 'which attribution model should I use', 'my channels are double-counting', 'attribution is broken', or 'compare attribution models'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/analytics
  domain: attribution
  updated: 2026-04-26
---

# Attribution Model Picker

You pick attribution models that match how the business actually makes decisions, not the default. Wrong attribution = wrong budget allocation = burned money.

## When to use

- Multi-channel marketing operation (paid + organic + email + referral)
- Channels are double-counting conversions
- Need to defend budget allocation to leadership
- Switching from one platform's attribution to a unified model
- Long sales cycles where last-click clearly under-credits early touches

## The 6 attribution models

### Model 1: Last-Click
- Credits 100% to the last channel before conversion
- **Use when:** simple, single-channel marketing OR very short sales cycles
- **Pros:** simple, deterministic, fast
- **Cons:** under-credits awareness channels (organic, top-funnel paid)

### Model 2: First-Click
- Credits 100% to the first channel
- **Use when:** brand-building focus; want to reward awareness channels
- **Pros:** rewards top-funnel investment
- **Cons:** ignores everything that happens after the first touch

### Model 3: Linear
- Splits credit equally across all touchpoints
- **Use when:** you genuinely have no opinion on which step matters most
- **Pros:** simple, fair-feeling
- **Cons:** doesn't reflect reality (not all touches are equal)

### Model 4: Time-Decay
- Credits more to touches closer to the conversion
- **Use when:** longer sales cycle (B2B 30+ day cycles); recent touches matter more
- **Pros:** acknowledges proximity matters
- **Cons:** still arbitrary weighting

### Model 5: Position-Based (40/20/40)
- 40% to first touch, 40% to last touch, 20% split among middle
- **Use when:** want to reward both awareness AND closing channels
- **Pros:** acknowledges both ends matter
- **Cons:** middle channels get short shrift

### Model 6: Data-Driven Attribution (DDA)
- Algorithm assigns credit based on actual conversion contribution
- Available in GA4, Google Ads, some other platforms
- **Use when:** you have enough data (GA4 needs ~3,000 conversions/30 days)
- **Pros:** reflects actual contribution; updates as patterns change
- **Cons:** black box; can't audit; needs volume

## Decision matrix

| Business situation | Recommended model |
|---|---|
| < $5K/mo total spend, single channel | Last-click (it's fine) |
| Multi-channel, B2C, ≤ 7-day cycle | Last-click OR DDA |
| Multi-channel, B2C, > 7-day cycle | DDA OR Time-Decay |
| Multi-channel, B2B, 30-90 day cycle | Position-Based OR DDA |
| Multi-channel, B2B, 90+ day cycle | Position-Based with multi-touch tracking |
| Awareness-heavy strategy | First-Click for budget defense; DDA for tactical |

## iOS 14.5+ mobile attribution

Apple's App Tracking Transparency (ATT) broke deterministic mobile attribution starting 2021. By 2026:

- **iOS web tracking:** ~50% of users opt-out of tracking; conversions under-report 20-50%
- **App-to-app:** SKAdNetwork is the protocol; aggregate, time-delayed
- **Workaround:** Conversion API (CAPI) for web — server-side events Apple can't block
- **Workaround:** modeled conversions in Google Ads + Meta — algorithms fill in the gaps

For Meta Ads, **CAPI is non-negotiable in 2026.** Without it, you'll under-report 30-50% and the algorithm optimizes toward the wrong audiences.

For Google Ads, enhanced conversions (server-side hash of customer email/phone) recover ~70% of iOS-lost data.

## Process

### Step 1: Audit current attribution

Each platform reports its own attribution. They overlap, double-count, and disagree:
- Google Ads: last-click within 30-day window by default
- Meta Ads: 7-day click + 1-day view by default
- GA4: data-driven by default
- Email tools: usually last-click

If your channels claim more conversions in total than you actually had, you're double-counting. This is the #1 sign you need a unified model.

### Step 2: Decide the unified source of truth

Pick ONE platform as the system of record. Usually:
- **GA4** for B2C / e-commerce
- **CRM (HubSpot/Salesforce)** for B2B / lead-gen
- **Custom dashboard (Looker Studio)** if you need cross-platform synthesis

Other platforms become subordinate — their numbers are inputs, not truth.

### Step 3: Pick the attribution model

Use the decision matrix above. Document the choice + rationale. Re-evaluate quarterly.

### Step 4: Implement the model

In GA4: Admin → Attribution Settings → Reporting Attribution Model
In Google Ads: Tools → Conversions → Attribution Model
In Meta: leave as default (7-click/1-view); use unified GA4 / CRM data for cross-platform

### Step 5: Set up CAPI / enhanced conversions

For web:
- Meta CAPI via Stape or platform-native integration
- Google Ads Enhanced Conversions via GTM

For mobile:
- SKAdNetwork on iOS
- Standard install events on Android

### Step 6: Build the attribution dashboard

In Looker Studio:
- Conversions by source (your unified model)
- Each platform's self-reported conversions (for diagnostic)
- Time-to-conversion distribution
- Conversion paths (top 10 channel sequences)

## Output format

```
# Attribution Model Decision: <brand>

## Business context
- Cycle length: X days average
- Channels: [list]
- Monthly spend: $X
- Conversion volume: Y / month
- Industry: ...

## Recommended model
**[Model name]**

### Rationale
[Why this model fits the business — referencing decision matrix factors]

### Implementation plan
1. Set GA4 attribution model to [X]
2. Set Google Ads attribution model to [X]
3. Implement Meta CAPI via [Stape / native / custom]
4. Implement Google Ads Enhanced Conversions via [GTM / Tag Assistant]
5. Build unified Looker Studio dashboard with [model] applied

## iOS 14.5+ adjustments
- CAPI required for Meta — set up via [path]
- Enhanced conversions for Google Ads — set up via [path]
- Expect 15-25% modeled-conversion rate from Meta/Google AI fill-in

## Source-of-truth platform
[GA4 / CRM / Looker Studio]

## Diagnostic dashboard sections
- Self-reported conversions per platform (for sanity checking)
- Cross-platform overlap (should reconcile to unified count)
- Channel mix in conversion paths
- Time-to-conversion histogram

## Quarterly review
- Has cycle length changed? (May warrant different model)
- Has channel mix changed? (DDA needs re-baselining)
- Are we ≥ 3,000 conversions / 30 days? (DDA viability check)
```

## Common mistakes

1. **Trusting platform-reported conversions in aggregate.** They double-count. Always reconcile through one system of record.
2. **Last-click on long sales cycles.** Severely under-credits awareness investment.
3. **No CAPI / enhanced conversions.** Losing 30-50% of data on iOS web traffic.
4. **Switching attribution models monthly.** Each model gives different numbers; switching tells you nothing.
5. **DDA without sufficient data.** GA4 falls back to last-click silently if you have < 3K conversions / 30 days.
6. **Ignoring view-through conversions on Meta.** They exist and matter for awareness ROI.

## Leverage with other skills

- Pair with `ga4-setup-architect` for the underlying tracking
- Pair with `funnel-leakage-mapper` once attribution is reliable
- Pair with `landing-page-auditor` if attribution shows specific channels under-converting

## MCP integration

This skill is decision-support. After picking the model, use platform MCPs to implement: `ga4`, `google-ads`, `meta-ads` MCPs each have attribution-config endpoints.
