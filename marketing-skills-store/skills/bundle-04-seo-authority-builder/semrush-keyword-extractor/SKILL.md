---
name: "semrush-keyword-extractor"
description: "Pulls 50+ keyword opportunities from SEMrush in a single MCP call — including current rankings, search volume, KD, intent classification, and SERP feature presence — and ranks them by 'highest-impact, easiest-to-win' score. Also generates 1,000 long-tail keyword ideas from a seed term. Built from the live agent that helped scale Datastrike's SEMrush Authority Score from 2 to 24 in under a year. Use when 'find keywords for my site', 'pull SEMrush data', 'identify SEO opportunities', 'expand my keyword list', or 'rank my keyword opportunities'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/seo
  domain: semrush
  updated: 2026-04-26
  mcp_servers: ["semrush"]
  receipts: "Datastrike: Authority Score 2→24 in under a year (12x lift)"
---

# SEMrush Keyword Extractor

You pull strategic SEO data from SEMrush via the MCP and turn it into a ranked action list — not a 5,000-row CSV no one will look at. **50 keywords in a 2-minute API call.** **1,000 long-tail ideas from a single seed.**

This is the live agent that helped scale Datastrike's SEMrush Authority Score from **2 → 24 in under a year** (12x lift) by feeding clean, ranked keyword data into the content + paid-search stack.

## When to use

- New site needing baseline keyword strategy
- Existing site needing to find low-hanging-fruit keywords (rank 4-15 → boost to 1-3)
- Generating long-tail ideas to fill a 6-month editorial calendar
- Competitor gap analysis (what they rank for, you don't)

## Inputs you need

- **Domain or seed keyword(s)** — the starting point
- **Target country / language** for SEMrush database
- **Use case:** "find quick wins" / "expand topical depth" / "competitor gap" / "long-tail brainstorm"
- **Forbidden topics** (e.g. brand-name terms, regulated content)

## The 4 modes

### Mode 1: Quick Wins (highest leverage on existing site)

Pulls keywords where the site currently ranks **positions 4-15** with monthly search volume ≥ 100.

These are the cheapest possible ranking gains — the page already exists, it's just not optimized enough to crack top 3.

For each, output:
- Keyword
- Current position
- Monthly search volume
- Estimated traffic at #1 (volume × CTR_at_1)
- Traffic gap (current_traffic - estimated_at_1)
- KD (keyword difficulty)
- Recommended action (on-page optimization / new page / link build / all)

**Sort by: traffic gap descending.** That's the priority order.

### Mode 2: Topical Depth Expansion

For a target keyword, pull all **related keywords** (semantically clustered) and identify which ones the site does NOT currently rank for.

These become the H2 sections you need to add to existing posts (or new posts) to win the topical-depth ranking signal that drove the Align HCM +17.2% organic lift.

### Mode 3: Competitor Gap

For up to 5 named competitors, pull keywords they rank top 10 for that the user's domain doesn't rank for at all.

Filter to:
- Search volume ≥ 100
- KD ≤ user's site's KD ceiling (calibrate from current rankings)
- Intent matches user's offer

Sort by competitor traffic value (estimated $ value of the traffic to that competitor for that keyword).

### Mode 4: Long-Tail Brainstorm (1,000+ ideas)

From a seed keyword, generate 1,000+ long-tail variations:

- Question-based ("how to [seed]", "what is [seed]", "why does [seed]", "when should [seed]")
- Modifier-based ("best [seed]", "cheap [seed]", "[seed] for [persona]", "[seed] vs [alternative]")
- Geo-based (per major city in service area)
- Year-based ("[seed] 2026", "[seed] in [year]")
- Comparison-based ("[seed] vs X", "[seed] alternative")
- Specific-use ("[seed] for [vertical]")

Validate which exist in SEMrush database with non-zero volume. Filter the 1,000 down to 100-200 that have actual search demand.

## Output format

```
# SEMrush Keyword Extraction: <site / seed>

## Mode: [Quick Wins | Topical Expansion | Competitor Gap | Long-Tail Brainstorm]
## Database: [country / language]
## Run date: ...

## Top 50 by impact

| # | Keyword | Current Pos | Volume | KD | Intent | Action | Est. traffic gain |
|---|---|---|---|---|---|---|---|
| 1 | "..." | 7 | 2,400 | 32 | Commercial | Optimize on-page H1 + add 400-word section on [LSI]; add 3 internal links | +850/mo |
| 2 | "..." | 11 | 1,200 | 28 | Informational | Add FAQ schema; add 200-word "common mistakes" section | +320/mo |
| ... |

## Long-tail ideas (Mode 4 only — 1,000 brainstormed, top 200 validated)

| Cluster theme | Ideas (sample) | Est. monthly volume |
|---|---|---|
| Question-based | "how to apply for VA loan", "what is a funding fee", ... | 8,400 combined |
| Modifier-based | "best VA lender Phoenix", "cheap VA loan refinance", ... | 5,100 combined |
| ... |

## Recommended next actions
1. Start with rows 1-10 of Quick Wins (highest traffic gain per hour of work)
2. Build editorial calendar from Long-Tail Mode 4 cluster themes
3. Run `keyword-cluster-architect` on the long-tail set to plan pillar/cluster structure
4. Run `content-brief-builder` for top 5 priority keywords

## Tracking
- Log keywords into a tracking doc with current position
- Re-run this skill in 30 days; compare position deltas
- Use deltas to refine the prioritization model
```

## Common mistakes

1. **Pulling all 5,000 keywords and trying to act on them.** No one will. Pull 50 prioritized.
2. **Ignoring intent classification.** Ranking #1 for an informational keyword on a commercial page = no conversion.
3. **Targeting keywords with KD > site's average ranking position.** You'll spend months and not crack page 2.
4. **Skipping Mode 2 (topical expansion).** Most sites have content that ranks #11-20 because it's missing 2-3 H2s of topical depth, not because of links.
5. **Brand keywords in long-tail brainstorm.** Filter them out — you already rank.

## Leverage with other skills

- Pair with `keyword-cluster-architect` for the editorial-plan structure on the long-tail set
- Pair with `content-brief-builder` for execution on top 5 priorities
- Pair with `hubspot-blog-optimizer` (Bundle 3) to act on the Quick Wins via existing-content edits
- Pair with `internal-link-strategist` for the link-graph plan to support new content

## MCP integration

The full live invocation:

```
Run semrush-keyword-extractor in Mode 1 (Quick Wins) for domain alignhcm.com, US database, English. Then run Mode 4 (Long-Tail Brainstorm) for the seed "PEO services". Cross-check: which of the long-tails are also Quick Wins? Output the merged top-50.
```

This pattern fed Datastrike's content engine for 12 straight months. Authority Score 2 → 24 was the result.
