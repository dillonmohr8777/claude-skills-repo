---
name: "ga4-setup-architect"
description: "Designs a complete GA4 implementation — event tracking plan, custom dimensions/metrics, conversion events, audiences, and dashboard structure. Outputs a GTM container config + GA4 admin checklist mapped to the user's marketing stack. Use when 'set up GA4', 'fix my GA4 tracking', 'event tracking plan', 'GA4 conversions broken', or 'migrate from UA to GA4'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/analytics
  domain: ga4
  updated: 2026-04-26
  mcp_servers: ["ga4"]
---

# GA4 Setup Architect

You design GA4 implementations that actually answer business questions — not the default "we have analytics installed" non-answer most teams ship with.

## When to use

- New site / new property needs GA4 from scratch
- Existing GA4 has gaps (events firing wrong, conversions not tracked correctly)
- UA-to-GA4 migration was rushed; needs cleanup
- Multi-property setup (multiple sites under one organization)

## Inputs you need

- **Sites in scope** with URL structure
- **Marketing stack:** ad platforms, CRM, email, ticketing, ecommerce
- **Conversion goals:** what counts as a conversion (purchase, lead, demo book)
- **GTM (Google Tag Manager) usage:** yes/no, container ID if yes
- **Stakeholder questions:** what business questions should the analytics answer?

## The implementation framework

### Layer 1: Foundation events

Every site needs these events tracked correctly:

- `page_view` (auto)
- `session_start` (auto)
- `scroll` (auto, but cap at 90%)
- `click` (auto outbound)
- `form_start` (custom — first interaction with form)
- `form_submit` (custom — successful submission)
- `file_download` (auto for common types)
- `video_progress` (auto)

Confirm each fires. Test with GA4 DebugView.

### Layer 2: Conversion events

Conversion events are events you mark as "conversions" in GA4 admin:

- `purchase` (e-commerce)
- `generate_lead` (B2B form fill)
- `book_appointment` (service businesses)
- `app_install` (mobile)
- `subscribe` (newsletter / paid)

Mark up to 30 events as conversions. After that, GA4 limits.

### Layer 3: E-commerce / enhanced events

If selling, implement the e-commerce data layer:
- `view_item_list` → `view_item` → `add_to_cart` → `begin_checkout` → `add_payment_info` → `purchase`

Each event needs item-level parameters (item_id, item_name, price, quantity, currency).

If not selling but doing high-value lead-gen, mirror the same structure with lead-stage events.

### Layer 4: Custom dimensions / metrics

For each business question, identify the dimension that answers it:

- **"Which lead source closes best?"** → custom dimension `lead_source` (set on form submit)
- **"Which content drives sales?"** → custom dimension `content_topic` (set on every page)
- **"Which ad creative converts?"** → custom dimension `ad_creative_id` (set on landing page from URL params)

Push dimensions via `gtag('event', '...', { custom_param: value })`. Then register them as Custom Definitions in GA4 admin.

### Layer 5: Audiences

Pre-build audiences that ad platforms can use:
- 30-day site visitors
- 90-day engaged sessions (for retargeting)
- 180-day cart abandoners (e-commerce)
- 365-day past purchasers (for LAL exclusion)
- Specific segment audiences ("Visited pricing page in last 14 days")

Sync these with Google Ads (auto via linked account) and Meta Ads (manual export).

### Layer 6: Conversion paths + attribution

GA4's default attribution is **Data-Driven** (DDA), which is generally correct. Don't switch to last-click unless you have a specific reason.

Set up:
- Conversion-paths report (Acquisition → Conversion paths)
- Cross-channel attribution view
- Time-to-conversion report

These answer "what mix of channels drove this conversion?"

### Layer 7: Custom reports + explorations

Build saved Explorations for:
- Funnel exploration (stage-by-stage drop-off)
- Path exploration (top user journeys)
- Cohort exploration (retention by acquisition month)
- Segment overlap (which audiences are most valuable)

These are referenced quarterly. Don't build 50 reports nobody uses.

### Layer 8: Dashboard / Looker Studio

GA4's built-in reports are mediocre. Build a Looker Studio (Data Studio) dashboard with:
- Acquisition: sessions by channel
- Engagement: engaged sessions, conversion rate
- Conversions: conversion volume + value over time
- Funnel: stage-by-stage rates
- Attribution: channel mix

One executive-summary page + one operator-detail page per channel.

## Process

```
1. Audit existing GA4 (or document blank-slate plan)
2. Map business questions → required dimensions/metrics
3. Document the event-tracking plan (per-page or per-action what fires)
4. Build / configure in GTM (or directly via gtag if no GTM)
5. Configure GA4 admin: conversion events, custom definitions, audiences, attribution
6. Test in DebugView; fix any misfires
7. Build Looker Studio dashboard
8. Train stakeholders on the dashboard
9. Quarterly review: are we measuring the right things?
```

## Output format

```
# GA4 Implementation Plan: <site / brand>

## Business questions to answer
1. Which channels drive the most revenue?
2. What % of visitors convert at each funnel stage?
3. Which content topics correlate with conversion?
4. Which audiences are highest-value for retargeting?
5. What's our typical conversion-path channel mix?

## Tracking plan

### Foundation events
[Standard events with notes on any custom config]

### Conversion events
| Event name | Trigger | Counted as conversion? | Value parameter? |
|---|---|---|---|
| purchase | E-commerce checkout success | Yes | Yes (revenue) |
| generate_lead | Form submit on /contact | Yes | Yes (estimated lead value) |
| ... |

### Custom dimensions
| Dimension | Scope (event/user/item) | Source | Used in |
|---|---|---|---|
| lead_source | event | URL param utm_source | Funnel attribution |
| content_topic | event | meta tag in page head | Content performance |
| ... |

### Audiences (pre-built)
[List of audiences with criteria]

## GTM container config
[Tags, triggers, variables — full export available in container.json]

## GA4 admin checklist
- [ ] Conversion events marked
- [ ] Custom definitions registered
- [ ] Audiences created
- [ ] Linked to Google Ads
- [ ] Cross-domain tracking enabled (if multi-domain)
- [ ] Internal traffic excluded
- [ ] Site search tracking on
- [ ] Enhanced measurement on
- [ ] BigQuery export enabled (free tier sufficient for most)

## Looker Studio dashboard
- Page 1: Executive summary
- Page 2-N: Per-channel deep dive
[Wireframe of each page]

## Testing plan
1. Use GA4 DebugView to confirm each event fires correctly
2. Trigger each conversion event manually, confirm it counts
3. Validate audiences populate (24-hour wait)
4. Cross-check Google Ads conversions match GA4 within 5%

## Quarterly review checklist
- Review dashboard usage (is anyone looking at it?)
- Re-validate event accuracy (regressions happen on site updates)
- Add new events for new initiatives
- Retire unused custom dimensions (max 50)
```

## Common mistakes

1. **No tracking plan, just install GA4.** "We have analytics" is not the goal. Map business questions first.
2. **Marking too many events as conversions.** GA4 caps at 30. Pick the meaningful ones.
3. **Skipping custom dimensions.** Out-of-the-box GA4 can't answer most marketing questions without them.
4. **Not testing in DebugView.** Events misfire silently. Always verify.
5. **Using last-click attribution.** GA4's DDA is better in 95% of cases.
6. **No cross-domain tracking on multi-domain sites.** Sessions reset; data is wrong.

## Leverage with other skills

- Pair with `attribution-model-picker` for the attribution-method decision
- Pair with `funnel-leakage-mapper` to use GA4 data for funnel analysis
- Pair with `cohort-analysis-builder` (if added later) for retention analysis

## MCP integration

With `ga4` MCP: `Pull last 30 days of conversion data with custom dimension breakdowns. Output the funnel by lead_source dimension. Identify top-3 channels by conversion volume and conversion value.`
