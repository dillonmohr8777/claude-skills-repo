---
name: "google-ads-keyword-strategist"
description: "Builds a strategic keyword set for a Google Ads campaign — pulls seed terms, expands by intent, segments by buyer-funnel stage, and assigns match types and ad groups. Outputs a structured keyword plan ready to drop into Google Ads Editor or import via API. Use when the user says 'I need keywords for my Google Ads', 'expand my keyword list', 'find keywords for X service', 'I have a seed list and need to grow it', or 'group my keywords into ad groups'. Optimized for paid-search operators who care about intent and ad-group hygiene, not bulk keyword dumps."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-search
  domain: google-ads
  updated: 2026-04-26
  mcp_servers: ["google-ads", "semrush"]
---

# Google Ads Keyword Strategist

You build keyword strategies that match how people actually search — not bulk lists from a tool. Your job is to produce a keyword plan that an experienced paid-search operator would build manually after 4 hours of research, in 4 minutes.

## When to use

- User has a product/service and needs an initial keyword set
- User has a thin keyword list and wants intentional expansion
- User wants to restructure existing keywords into proper themed ad groups
- User is launching in a new vertical and needs the keyword landscape mapped

## Inputs you need (ask if missing)

- **Offer:** what's being sold, the customer's job-to-be-done
- **Geo:** city/state/country (affects modifier strategy and search volume)
- **Buyer stage focus:** are we buying high-intent only ("near me", "buy", "for sale") or full-funnel?
- **Existing seed keywords:** if any
- **Forbidden terms:** brand names you can't bid on, regulatory restrictions
- **Match-type budget:** how much you want in Phrase/Exact (precision) vs Broad (volume)

## Process

### 1. Build the intent ladder

Every offer has 4 intent tiers. Map each one explicitly:

| Tier | Intent | Example (real estate) | Match strategy |
|---|---|---|---|
| **Top of funnel** | Information | "is now a good time to buy a house" | Skip on a paid budget < $10K/mo |
| **Mid-funnel** | Comparison | "best mortgage lender in [city]" | Phrase + Exact, separate ad group |
| **Bottom-funnel** | Transactional | "apply for VA loan [city]" | Phrase + Exact, primary budget |
| **Brand/competitor** | Direct | "[brand] mortgage rates" / "[competitor] reviews" | Exact only, separate ad group |

For Secure Lending Inc. (314x ROAS), bottom-funnel + competitor was 80% of budget. We avoided top-of-funnel entirely.

### 2. Generate seed expansions

For each tier, produce keywords on these axes:

- **Service variants:** what people call the service ("VA loan", "VA mortgage", "veteran home loan")
- **Modifiers — buying intent:** "near me", "today", "fast", "best", "apply", "rates", "calculator"
- **Modifiers — qualifier:** "for first-time buyer", "with bad credit", "no down payment", "2026"
- **Geo modifiers:** city, county, region, state — at multiple granularities

Cross-product the axes. For a 3-city VA-loan campaign, you'll generate ~80–120 keywords from a single service.

### 3. Group into themed ad groups

The rule: **two keywords belong in the same ad group if and only if a single ad copy could win the auction for both.**

Examples of correct grouping:
- ✅ "va loan calculator" + "veteran mortgage calculator" — same intent, calculator-themed ad
- ❌ "va loan rates" + "best va lender" — different intents (rate-shopping vs lender-shopping); separate ad groups

### 4. Assign match types

In 2026:
- **Phrase + Exact** for tier 2 + 3 keywords with established CPCs you understand
- **Broad** ONLY when paired with Smart Bidding (tCPA or Maximize Conversions) AND with the negative-keyword list set up
- **Exact** for brand and competitor terms

Default split: 60% Phrase/Exact, 30% Broad-with-Smart-Bidding, 10% Brand-Exact.

### 5. Pre-build the negative list

For every ad group, generate the obvious negatives BEFORE launch:
- Free / DIY ("free", "diy", "how to", "tutorial")
- Career ("jobs", "salary", "career", "hiring")
- Wrong product ("software", "free download" — depending on offer)
- Wrong audience (brand competitors NOT being bid on)
- Geo exclusions (cities you don't service)

This prevents the first week's budget from being burned on garbage queries. See the `negative-keyword-mining` skill for ongoing discovery.

### 6. Estimate volume + CPC

If `google-ads` or `semrush` MCP is connected, pull live volume + CPC estimates per keyword. Otherwise, request the user share Keyword Planner forecast or SEMrush PPC keyword data.

Flag keywords that are:
- High CPC (>$15) without proven conversion economics
- Zero or low search volume (skip; not worth the ad-group bloat)
- Highly seasonal (note for budget pacing)

## Output format

```
# Keyword Strategy: <offer>

## Strategic summary
- Total keywords: X across Y ad groups
- Match-type split: P / Q / R (Phrase / Exact / Broad)
- Top 5 highest-intent keywords (recommended for initial budget skew):
  1. ...
  2. ...

## Ad group plans

### AG1: <theme name>  | Match types: Phrase + Exact
**Landing page:** <URL>
**Ad copy theme:** <hook>
**Keywords:**
| Keyword | Match | Est. monthly volume | Est. CPC | Intent tier | Notes |
|---|---|---|---|---|---|
| "..." | Phrase | 1,200 | $4.20 | Bottom | Primary money keyword |
| [...] | Exact | 800 | $3.80 | Bottom | |
| "..." | Phrase | 500 | $5.10 | Mid | |
**Initial negatives for this ad group:** [...]

### AG2: <theme name>
...

## Account-level negative-keyword list (apply to all ad groups)
- "free"
- "jobs"
- "diy"
- ...

## Watchouts + budget guidance
- Keyword X has CPC $18 and minimum monthly volume; only bid if conversion economics support
- Brand-bidding is included separately — confirm policy with client
- 30-day learning phase: expect $X-Y burn before tCPA is reliable

## Next skills to run
- `google-ads-ad-copy-tester` to write 10 ad variants per ad group
- `negative-keyword-mining` after week 1 search-term data
```

## Common mistakes to avoid

1. **Bulk-importing thousands of keywords from a tool.** It looks productive but Smart Bidding can't optimize across that much variance. Pick the 50–200 you actually believe in.
2. **One mega ad group with all keywords.** This is the #1 reason for bad Quality Scores.
3. **Skipping negatives at launch.** You'll waste 30-60% of week-1 budget on garbage queries.
4. **Bidding on top-of-funnel keywords on a small budget.** They burn cash and convert at 1/10th the rate of bottom-funnel.
5. **Using Broad without Smart Bidding.** It will match to anything tangentially related.

## Leverage with other skills

- Pair with `google-ads-campaign-architect` to design the campaign structure first, then this skill fills the keywords
- Run `google-ads-ad-copy-tester` per ad group after this skill produces the groupings
- Run `negative-keyword-mining` weekly starting week 2 to cull search-term garbage

## MCP integration

With `google-ads` MCP: pull existing account keywords and conversion data to inform the new plan.
With `semrush` MCP: pull volume, KD, and CPC estimates per keyword automatically — same agent that drove Datastrike's Authority Score from 2 → 24 (12x lift) by feeding clean keyword data into the SEO + paid-search stack.

Example invocation:
```
Run google-ads-keyword-strategist for "va home loans in Phoenix, Tucson, and Mesa". Pull volume from SEMrush MCP, CPC estimates from Google Ads MCP, and produce a 60-keyword plan across 4 themed ad groups with phrase + exact match types. Pre-build the negative list.
```
