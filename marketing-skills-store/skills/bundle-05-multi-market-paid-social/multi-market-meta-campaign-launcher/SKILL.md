---
name: "multi-market-meta-campaign-launcher"
description: "Builds Meta Ads campaigns that scale across N cities/markets simultaneously — naming conventions, geo + audience structure, CBO logic, creative-rotation rules, and per-market KPI dashboards. Use when 'launch the same offer in 5 cities', 'multi-market Meta campaign', 'scale my paid social', or 'roll out a campaign nationally'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-social
  domain: meta-ads
  updated: 2026-04-26
  mcp_servers: ["meta-ads"]
---

# Multi-Market Meta Campaign Launcher

You launch and scale the same offer across multiple geographic markets without making the classic mistakes — wrong campaign hierarchy, no naming convention, no per-market reporting. The receipt: this is the structure that ran simultaneously across multiple Bar Crawl USA cities.

## When to use

- Same offer/event/product launching in 3-15 cities at once
- National brand running localized campaigns per DMA
- Franchise / multi-location business standardizing paid social
- Existing single-market campaign needs to scale geographically

## Inputs you need

- **Cities/markets list** with population, target attendee count per market, and venue address(es) if applicable
- **Total budget** + per-market budget (or CBO budget)
- **Offer/conversion event** (purchase, lead, install, registration)
- **Creative assets** — at minimum, video + 5 image variants
- **Time-zone considerations** — start/end dates relative to local time

## The naming convention

Without consistent naming, multi-market reporting becomes garbage. Use this:

```
Campaign: [Brand] | [Offer] | [Goal]
Example: BarCrawlUSA | Taco&Tequila | Tickets

Ad Set: [Market] | [Audience] | [Phase]
Example: Phoenix | LAL1pct | Phase2Conversion

Ad: [Variant] | [Format] | [Hook]
Example: VarA | Video15s | LifestyleFOMO
```

This makes filter views in Ads Manager trivial: "show me all Phoenix Phase2 ad sets across all campaigns" works.

## Campaign hierarchy

```
ONE campaign per offer (NOT per market)
├── ONE ad set per market × audience
│   ├── 3 creative variants
```

Multi-market in ONE campaign with CBO is correct. Separate campaigns per market = budget locked per market = can't shift to where it's working.

**Exception:** if markets have radically different audiences (e.g. luxury Manhattan vs. budget Atlanta), separate campaigns can be justified.

## CBO (Campaign Budget Optimization)

CBO is on by default in 2026. The question is: do you let it run free, or constrain it?

| Approach | When to use |
|---|---|
| **Free CBO** | All markets are roughly equivalent in size. Let Meta find the winners. |
| **Min/max constrained CBO** | Some markets are non-negotiable ("must spend $X in NYC"). Set ad-set min spend. |
| **CBO off (manual budgets)** | When you need per-market accountability for client reporting. |

For event ticketing, free CBO drove a 28% better cost-per-ticket than manual budgets — Bar Crawl USA learning.

## Geo + audience structure per market

Per market, build the ad set as:

- **Geo:** city center + 25-50mi radius (depends on event/offer)
- **Geo precision:** "Live in this location" (NOT "interested in")
- **Audience:** stack 3 layers
  - 1% lookalike of past converters (city-specific where data exists)
  - Interest-based (the proven interests from the offer's persona)
  - Broad + narrowed (let Meta find net-new in this market)

For markets with no historical conversion data:
- Use national lookalike (1% of all past converters) instead of city-specific
- Lean heavier on interest-based targeting
- Plan to have local LAL after 30-60 conversions accumulate

## Output format

```
# Multi-Market Meta Campaign: <offer>

## Markets in scope (N markets)

| Market | DMA size | Goal tickets/leads | Budget allocation (CBO baseline) |
|---|---|---|---|
| Phoenix | 1.5M | 600 | $X |
| Tucson | 0.4M | 200 | $X |
| ... |

## Campaign structure
- Campaign name: [Brand] | [Offer] | [Goal]
- Objective: [Sales / Leads]
- Bid strategy: [Lowest Cost / tCPA $X]
- Budget mode: CBO at $X/day
- Schedule: [start] to [end] in each market's local time

## Ad set table

| Market | Ad set name | Geo | Audience | Min budget | Notes |
|---|---|---|---|---|---|
| Phoenix | Phoenix \| LAL1pct \| Phase2 | Phoenix DMA + 25mi venue radius | 1% LAL past purchasers + interests + age 21-40 | $30/day | Primary market |
| Phoenix | Phoenix \| Retargeting \| Phase2 | Phoenix DMA | 180-day cart abandoners + 365-day video viewers | $15/day | Phase 2+ only |
| Tucson | ... | | | | |
| ... |

## Creative rotation rules
- Each ad set runs 3 variants (A=Lifestyle, B=Specificity, C=Personality)
- Cull rule: any variant < 50% of leader CTR after 1,000 impressions → pause
- Replace cycle: monthly creative refresh OR when campaign enters Phase 3

## Reporting dashboard
- Per-market: spend, CPC, CPM, CTR, CPP, ROAS
- Per-creative variant: same plus engagement rate
- Per-day: pacing vs. goal (running total tickets/leads)
- Anomaly flags: any market 50% above or below average CPP

## Daily monitoring (10-min check)
1. Spend pacing vs. goal
2. Top + bottom market by CPP — investigate bottom
3. Top + bottom creative variant — replace bottom if cycle complete
4. CAPI signal health — confirm events firing for each market
```

## Common mistakes

1. **Separate campaigns per market.** Locks budget. Can't shift dollars to winners.
2. **No naming convention.** Reporting is impossible at scale.
3. **Same creative for every market.** Local references and dialects matter; localize creative for top 2-3 markets.
4. **Ignoring time zones.** A 9pm ad in NYC is midnight in LA. Schedule per local time.
5. **Free CBO without min-spend constraints when client demands market-level guarantees.** You'll have to defend why Phoenix got 80% of budget.

## Leverage with other skills

- Pair with `local-event-paid-social-playbook` for event-specific structure
- Pair with `instagram-reels-promo-script-writer` for video creative
- Pair with `tiktok-ads-strategist` for parallel TikTok deployment

## MCP integration

With `meta-ads` MCP: `Build a multi-market campaign for [offer] across these N cities: [list]. Use the naming convention above. Enable CBO at $[X]/day. Set ad sets per the table. Pre-build all 3 creative variants per ad set. Save campaign as paused.`
