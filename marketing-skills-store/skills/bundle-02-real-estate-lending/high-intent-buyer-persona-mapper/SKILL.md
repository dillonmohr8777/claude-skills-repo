---
name: "high-intent-buyer-persona-mapper"
description: "Builds Meta + Google Ads audience targeting blueprints for real-estate / mortgage by mapping high-intent buyer personas — life-event triggers, income/credit signals, geo-clusters, and behavior patterns — into platform-specific targeting parameters. Use when 'targeting is too broad', 'I'm getting low-quality leads', 'help me find serious buyers', 'who should I target on Facebook for mortgages', or 'segment my real estate audience'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/lead-gen
  domain: real-estate
  updated: 2026-04-26
  mcp_servers: ["meta-ads", "google-ads"]
---

# High-Intent Buyer Persona Mapper

You translate "real estate buyers" into specific, targetable audiences with high conversion intent. Generic interest targeting ("interested in real estate") is why most lender ads waste 60%+ of budget. This skill maps the actual life-event triggers and behavioral signals that separate "shopping in 30 days" from "saved a Pinterest board".

## When to use

- User has broad interest targeting and poor conversion rate
- User wants Meta lookalikes built off best-fit seed
- User is launching in a new geo and needs to identify the cluster of high-intent zip codes
- User wants to test 3-5 distinct audiences vs. one mega-audience

## The 7 high-intent personas (real estate / mortgage)

### 1. The Renewing Lease

**Trigger:** lease ends in 60-180 days
**Where they hang out:** Zillow saved searches, Reddit r/FirstTimeHomeBuyer, NextDoor
**Meta signals:** age 25-45, "new to a city" in last 12 months, engaged in "Apartments.com" or competitor
**Best lead magnet:** "Buying vs. Renting Calculator — Phoenix Edition"
**Targeting:** Lookalike of past purchase clients in same age bracket + engagement

### 2. The Life-Event Mover

**Trigger:** marriage, baby, divorce, job change, retirement
**Meta signals:** "newlywed" / "engaged" interest, "expecting parents", recent job-change behaviors
**Where they hang out:** parenting communities, wedding planning sites, LinkedIn job changes
**Best lead magnet:** "Family Home Checklist" or "Downsizing Roadmap"
**Targeting:** life-event audiences in Meta + custom audience from local maternity / wedding service partners (privacy-compliant)

### 3. The Equity Refinancer

**Trigger:** owns home 3+ years, has equity, current mortgage rate higher than current market by 1%+
**Meta signals:** "homeowner" with home valued > $X, age 35-65
**Where they hang out:** financial-advice content, retirement-planning communities
**Best lead magnet:** "Equity Calculator: How Much Could You Pull Out?"
**Targeting:** custom audience from local property records (where legal) + retargeting site visitors who hit refinance pages

### 4. The First-Time Veteran

**Trigger:** active service member, recently separated, or 1-3 years post-service
**Meta signals:** military interests, base-area geo, age 22-40
**Where they hang out:** r/Veterans, military.com, base community pages
**Best lead magnet:** "VA Loan Roadmap: $0 Down to Closing"
**Targeting:** geo-targeting around military bases + military-interest stack
**Note:** Secure Lending's $1.7M came primarily from this persona. The targeting precision matters enormously.

### 5. The Investor (small / first-time)

**Trigger:** seeking second property, BRRRR strategy, house-hack curious
**Meta signals:** real-estate-investing content, BiggerPockets engagement, household income $100K+
**Where they hang out:** BiggerPockets, r/realestateinvesting, YouTube investor channels
**Best lead magnet:** "Cash Flow Calculator: Will This Property Pay You?"
**Targeting:** lookalike of investor clients + interest stack

### 6. The Relocating Professional

**Trigger:** corporate relocation, remote-work move, climate migration
**Meta signals:** "moving to [city]" search behavior, recent job change at remote-work-friendly employer
**Where they hang out:** remote-work communities, "best cities to live" content
**Best lead magnet:** "[City] Buyer's Welcome Guide" — neighborhood-by-neighborhood
**Targeting:** geo-narrow with "interested in moving to [city]" custom audience

### 7. The 5-Year-In Refinancer

**Trigger:** mortgage 5+ years old, rate ≥ 1% above current market
**Meta signals:** homeowner, mortgage age detectable from public records (if you have access)
**Best lead magnet:** "Should You Refinance? Free 5-Minute Analysis"
**Targeting:** custom audience from public records (legal in most states) + retargeting

## Process

### 1. Pick 3 personas to test in v1

Don't try to target all 7 at launch. Pick 3 that align with your offer + geo. For Secure Lending, we ran #4 (Veterans) + #1 (Renewers) + #6 (Relocators).

### 2. Build the targeting blueprint per persona

For each chosen persona, produce:

```
Persona: <name>

## Meta Ads targeting
- Geo: ...
- Age: X-Y
- Detailed targeting (interests):
  - [interest 1]
  - [interest 2]
- Detailed targeting (behaviors):
  - [behavior]
- Custom audience seeds:
  - [audience]
- Lookalike from:
  - [source audience], 1% LAL

## Google Ads targeting
- Audience (Observation, NOT Targeting):
  - In-market: [audience]
  - Affinity: [audience]
- Custom segment URL list:
  - zillow.com/[city]
  - realtor.com/[city]
- Geo + radius from anchor zips
```

### 3. Define ad creative angles per persona

The same lender / same offer needs different ad creative per persona. For Persona 4 (Veterans), social proof from veteran clients + military imagery + "VA-specific" benefit. For Persona 1 (Renewers), comparison-frame ("$1,800/mo rent vs $1,650 mortgage in [city]") + relatable lifestyle imagery.

### 4. Set up custom-audience seeds

Build seed audiences NOW even if you're not running ads against them yet. They take 30+ days to grow:

- 180-day site visitors (general)
- 365-day video viewers (75%+ watched)
- Email subscribers (uploaded customer list)
- Past closed clients (uploaded; CRITICAL for lookalike)

### 5. Geo precision

Real estate is **hyper-local**. State-level targeting is wrong for almost every lender.

- Define core geo: 3-7 specific cities or 5-15 specific zip codes
- Build separate ad sets per geo cluster (especially if cities differ in income / market)
- Use "people who live in this location" exclusively (not "people interested in")

## Output format

```
# Buyer Persona Targeting Blueprint: <lender / agent>

## Recommended persona mix (v1)
1. Persona: <name> | Budget allocation: 50%
2. Persona: <name> | Budget allocation: 30%
3. Persona: <name> | Budget allocation: 20%

## Per-persona blueprints
[Full targeting blueprint per persona]

## Custom audience build queue
- [What to build today]
- [What to build week 2]

## Ad creative angles required
[List of variants needed per persona]

## Phase plan
- Week 1: launch all 3 personas at parity budget
- Week 3: shift budget toward leading persona; replace bottom persona
- Week 6: layer in 4th persona once you've identified leader
```

## Common mistakes

1. **One mega-audience for all "real estate buyers".** Meta's algorithm can't optimize across radically different intent levels. Segment and let each ad set learn its own audience.
2. **Skipping custom audience seeds at launch.** They take 30 days to mature. Start them on day 1 even if not running ads.
3. **State-level geo targeting.** Real estate is hyper-local. Always city/zip.
4. **Ignoring lookalike of past closers.** This is the highest-converting audience in any lender's account. If you don't have the data, manually upload from your CRM.
5. **Excluding by income too aggressively.** Income data on Meta is unreliable post-iOS 14.5. Better to filter via lead-form qualifier questions (timeline, pre-approval status).

## Leverage with other skills

- Pair with `real-estate-lead-gen-architect` for the campaign structure that implements these audiences
- Use `mortgage-funnel-builder` to design the per-persona nurture sequences
- Run `property-listing-ad-generator` if you're targeting investors or relocators with specific listings

## MCP integration

With `meta-ads` MCP: `Pull my last 12 months of conversion data, identify top 3 persona patterns by conversion rate, and produce a targeting blueprint for each.`
