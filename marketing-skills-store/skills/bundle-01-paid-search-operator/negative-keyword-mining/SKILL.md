---
name: "negative-keyword-mining"
description: "Mines wasted spend from your Google Ads search-term report and produces a ranked list of negative keywords to add. Identifies query patterns that match but never convert, recommends ad-group vs campaign vs account-level negatives, and projects budget recovery. Use when the user says 'audit my search terms', 'find wasted ad spend', 'build my negative keyword list', 'why is my CPC so high on broad match', or 'I think Google is showing me for the wrong queries'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-search
  domain: google-ads
  updated: 2026-04-26
  mcp_servers: ["google-ads"]
---

# Negative Keyword Mining

You find the budget leaks. The single biggest waste in Google Ads is paying for clicks on queries that have no chance of converting. You mine those queries from the search-term report and turn them into negatives — at the right level of the account hierarchy.

This skill is run weekly. It pays for itself the first time.

## When to use

- Account has been running ≥ 14 days and accumulated search-term data
- User reports rising CPC or falling conversion rate
- User has Broad match keywords and Smart Bidding (where mining is most critical)
- Onboarding a new account and need to clean up inherited mess

## Inputs you need

- **Search-term report** — last 30/60/90 days, exported from Google Ads or pulled via MCP
- **Conversion column** included (zero-conversion queries are the targets)
- **Spend threshold** — only mine queries that have spent enough to matter (default: $10+ in the window)
- **Existing negative list** so you don't duplicate

## Process

### 1. Filter the search-term report

Apply these filters in order:

1. **Spend ≥ threshold** (default $10 in window)
2. **Conversions = 0** (or conversion rate < 30% of ad-group average if there's been some)
3. **Sort by spend descending**

This produces the "bleed list" — every dollar above the line is a candidate negative.

### 2. Categorize each query

For each query, decide which bucket it falls into:

| Category | Example | Negative scope |
|---|---|---|
| **Job seekers** | "VA loan officer salary", "marketing manager career" | Account-level |
| **DIY / informational** | "how to refinance", "VA loan tutorial youtube" | Account-level |
| **Wrong product** | "VA loan calculator app", "free credit report" | Ad-group or campaign |
| **Wrong intent stage** | "is now a good time to buy", "what is a VA loan" | Campaign-level (in conversion-focused campaigns) |
| **Competitor brand (unintended)** | "[unrelated brand] VA loan" | Campaign-level |
| **Geo mismatch** | Queries from cities outside service area | Campaign-level (also fix Geo targeting) |
| **Misspellings of negatives** | "veteren home loan" | Skip (Google handles close variants) |
| **Real intent but wrong landing page** | "VA loan refi" matched a "VA loan purchase" ad | Don't add as negative — restructure ad groups |

### 3. Decide the right scope

**Account-level negative list** for queries that are NEVER valuable to any campaign:
- "free", "diy", "how to", "tutorial", "youtube"
- "jobs", "salary", "career", "hiring"
- "scam", "lawsuit", "complaint" (unless you're a defense lawyer)

**Campaign-level negatives** for queries irrelevant to a specific campaign but valuable to others:
- In a "VA Purchase" campaign, exclude "refinance" queries (they belong in a "VA Refi" campaign)
- In a "Phoenix" geo campaign, exclude queries from "Tucson", "Mesa" if those have their own campaigns

**Ad-group negatives** for queries that are valid for the campaign but should hit a different ad group:
- "VA loan calculator" should hit the "VA Loan Tools" ad group, not the "VA Loan Application" ad group
- Add to the "Application" ad group as negative; Google will route the query to the "Tools" group

### 4. Match-type your negatives

- **Negative phrase match** — most common, blocks queries containing the phrase in order
- **Negative exact match** — surgical; blocks only the exact query (use when "free" is fine but "free trial" isn't)
- **Negative broad match** — blocks queries containing all words in any order (use sparingly; can over-block)

For account-level lists like "jobs", use phrase match. For "free trial" specifically, use exact.

### 5. Project budget recovery

For each negative recommendation, estimate:
- Wasted spend in the window: $X
- Annualized waste if pattern continues: $12X
- Recovered budget that can be redirected to converting keywords

This is the line that gets your boss/client to approve cleanup time.

## Output format

```
# Negative Keyword Mining Report

## Bleed summary
- Window: last X days
- Total wasted spend (zero-conversion queries above $10): $X
- Annualized waste if unchecked: $Y
- Recommended negatives: N (broken down below)
- Estimated CPA improvement: $X → $X' after fixes

## Account-level negatives (apply globally)

| Negative term | Match type | Spend wasted | Conversions | Reason |
|---|---|---|---|---|
| jobs | Phrase | $342 | 0 | Career searches |
| salary | Phrase | $189 | 0 | Career searches |
| free | Phrase | $124 | 0 | DIY intent |
| ... | | | | |

## Campaign-level negatives

### Campaign: <name>
| Term | Match | Spend | Reason |
|---|---|---|---|
| ... | | | |

## Ad-group level negatives (route to right ad group)

### Ad group: <name>
| Term | Match | Spend | Route to ad group |
|---|---|---|---|
| ... | | | |

## Restructure recommendations (NOT negatives)

These queries are valid intent but matched the wrong ad group. Don't make them negative — fix the ad-group targeting:
- Query "X" matched ad group "A" but belongs in ad group "B" — restructure or add new ad group

## Apply order
1. Add account-level negatives first (immediate savings, low risk)
2. Add campaign-level next (after 24 hr, monitor impressions)
3. Add ad-group-level after restructure
4. Run again in 7 days to mine the next layer
```

## Common mistakes

1. **Adding negatives without checking match type.** Adding "free" as negative broad blocks "free trial" AND "freelance" — over-blocks.
2. **Adding everything as account-level.** "Refinance" should NOT be account-level if you have a refi campaign. Use campaign-level.
3. **Mining every week without restructuring.** If 30% of search terms hit the wrong ad group, the ad-group structure is wrong. Fix the structure.
4. **Mining on small samples.** Don't mine on < 100 queries — you'll false-positive your way to over-blocking.
5. **Negativing brand misspellings.** Google handles close variants. Don't add "veteren" if "veteran" is your keyword.

## Leverage with other skills

- Run weekly alongside `google-ads-quality-score-fixer` — query mining + QS diagnosis often reveal the same root cause
- Pair with `google-ads-campaign-architect` if mining reveals you need to restructure
- Use after `google-ads-keyword-strategist` to refine the initial pre-launch negative list

## MCP integration

With `google-ads` MCP: `Pull the search-term report for customer 123-456-7890 last 30 days, filter to spend > $10 with zero conversions, and produce a tiered negative-keyword recommendation with estimated budget recovery.`

This skill alone has saved one of my clients ~$2,800/month in misallocated spend. Run it weekly.
