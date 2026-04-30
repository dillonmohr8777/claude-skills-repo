---
name: "keyword-cluster-architect"
description: "Maps keywords into pillar-cluster topic architecture — identifies pillar pages, supporting cluster posts, internal-link relationships, and the priority order to publish them. Outputs an editorial map that powers topical authority. Use when 'plan my content architecture', 'group my keywords into topics', 'build a pillar cluster strategy', or 'organize 200 keywords into a content plan'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/seo
  domain: content-strategy
  updated: 2026-04-26
  mcp_servers: ["semrush"]
---

# Keyword Cluster Architect

You take a flat keyword list and turn it into a topical architecture — pillar pages, cluster posts, internal-link relationships, and a publish order. This is the structure Google rewards in 2026 (topical authority + helpful content).

The receipt context: this is the structure that drove Datastrike's Authority Score from 2 → 24 in under a year. Random posts don't build authority; clustered posts that link into a pillar page do.

## When to use

- 50+ keywords need organization into a content plan
- Existing site has scattered posts that don't reinforce each other
- Launching a content strategy for a new domain or new vertical
- Re-architecting an existing site for better topical depth signals

## Inputs you need

- **Keyword list** with search volume + KD (can come from `semrush-keyword-extractor`)
- **Existing site map** if site has content already
- **Business focus areas** — which 3-5 topics are core revenue drivers
- **Target persona(s)** for intent matching

## The pillar-cluster model

**Pillar page:** broad, comprehensive content on a top-level topic. 2,500-4,000 words. Targets a high-volume, mid-difficulty keyword. Acts as the hub.

**Cluster posts:** 800-1,500 word posts on specific subtopics. Each cluster post:
- Links UP to the pillar (anchor: keyword variant of pillar)
- Links sideways to 2-3 other cluster posts in the same cluster
- Links DOWN to deeper sub-cluster posts when they exist

This creates a "topic" Google can recognize. Random posts on unrelated topics dilute authority.

## Process

### 1. Group keywords by topic

Use semantic + intent grouping, not exact-match grouping:

| Group rule | Example |
|---|---|
| Same topic, different angle | "VA loan rates" + "VA loan APR" + "VA loan interest" → all one cluster |
| Same intent, different keyword | "best HubSpot consultant" + "top HubSpot agency" → same cluster |
| Different intent on same topic | "what is a VA loan" (informational) + "apply VA loan" (commercial) → DIFFERENT clusters |

**Rule of thumb:** if two keywords would be answered by the same article, cluster them. If they'd be answered by different articles, separate them.

### 2. Identify pillar candidates

Within each cluster, the **pillar** is the keyword that:
- Highest combined search volume + commercial intent
- Broad enough to be a hub for 5-15 cluster posts
- KD that the site can realistically win in 6-12 months (not 90+)

Examples:
- ✅ "VA loans" (broad, high volume, strong intent) — good pillar
- ❌ "VA loan refinance interest rate today" (narrow long-tail) — cluster post, not pillar

### 3. Identify cluster posts per pillar

For each pillar, identify 5-15 supporting cluster posts. Each cluster post:
- Has its own target keyword
- Answers a specific sub-question of the pillar
- Has a clear "ladder rung" — top of funnel ("what is") / mid ("how to") / bottom ("apply")

### 4. Map internal links

For each post, define:

- **Up-link:** to the pillar (1)
- **Side-links:** to 2-3 other cluster posts in same cluster
- **Down-links:** to sub-cluster posts (if any)
- **Cross-cluster links:** to relevant clusters in other topics (use sparingly — 1-2 per post)

### 5. Define publish order

Don't publish randomly. The right order:

1. **Pillar first** — gives subsequent cluster posts something to link UP to
2. **Highest-impact cluster posts** — bottom-funnel commercial intent first (closest to revenue)
3. **Mid-funnel cluster posts** — comparison / how-to
4. **Top-of-funnel cluster posts** — "what is" / educational

Reasoning: bottom-funnel posts produce revenue while you publish the rest. Top-funnel posts compound but are slow.

### 6. Define refresh cadence

Pillars: refresh every 6 months (Google rewards freshness signals on hub pages).
Cluster posts: refresh annually OR when a position drops below #5 OR when SERP top-3 average word count moves significantly.

## Output format

```
# Topical Architecture: <site>

## Cluster summary
- Total clusters: N
- Total pages planned: M
- Estimated 12-month organic traffic: X visits/month at maturity
- Recommended pace: 4 cluster posts + 1 pillar refresh per month

## Cluster 1: <Pillar topic>

### Pillar page
- **Target keyword:** "..."
- **Volume:** ...
- **KD:** ...
- **Word count target:** 3,000
- **Status:** [planned / drafted / live]
- **Publish priority:** 1 (must publish before cluster posts)

### Cluster posts (linked to pillar)

| # | Cluster post | Target KW | Volume | KD | Intent tier | Word count | Pub priority |
|---|---|---|---|---|---|---|---|
| 1 | "Apply for a VA Loan in 30 Days" | apply va loan | 3,200 | 28 | Bottom | 1,200 | 2 |
| 2 | "VA Loan Rates Today" | va loan rates today | 5,400 | 35 | Mid | 1,500 | 3 |
| 3 | "VA Loan Eligibility Checklist" | va loan eligibility | 2,100 | 22 | Mid | 1,000 | 4 |
| 4 | "What is a VA Loan?" | what is a va loan | 8,800 | 18 | Top | 1,500 | 5 |
| ... |

### Internal-link map (for cluster 1)

```
[Pillar: VA Loans Guide]
   ↑↓ (every cluster post links up)
   
[Apply for a VA Loan in 30 Days] ←→ [VA Loan Eligibility Checklist]
                                ←→ [VA Loan Rates Today]
[What is a VA Loan?] → [VA Loan Eligibility Checklist]
                     → [VA Loan Rates Today]
                     ↓ links DOWN to deeper Q&A: "VA Funding Fee Explained"
```

## Cluster 2-N
[Same structure]

## Cross-cluster relationships
- Cluster "VA Loans" links to Cluster "FHA Loans" (alternative loan type)
- Cluster "First-Time Buyer" links to all loan-type clusters
- Use sparingly: max 2 cross-cluster links per page

## Editorial calendar (12 months)
- Month 1: Publish pillar 1; cluster posts 1.1, 1.2
- Month 2: Cluster posts 1.3, 1.4, 1.5; refresh pillar 1
- Month 3: Publish pillar 2; cluster posts 2.1, 2.2
- ...

## KPIs to track per cluster
- Pillar position over time
- Cluster posts in top 3 / top 10
- Cluster organic traffic
- Internal-link coverage (every post should have ≥3 internal links)
- Time to first ranking (target: pillar < 90 days, cluster posts < 60 days)
```

## Common mistakes

1. **Treating every keyword as a separate post.** You'll dilute authority + cannibalize rankings.
2. **No pillar page.** Cluster posts have nothing to link UP to. No topical authority signal.
3. **Pillar that's too narrow.** "VA Loan Rates Today" can't anchor 10 cluster posts; pick "VA Loans" as pillar instead.
4. **Random publish order.** Top-funnel first burns months before revenue. Bottom-funnel first compounds while educational publishes.
5. **No internal links between cluster posts.** "Cluster" implies they're networked. Networking is the cluster.
6. **Refresh-once-a-year on pillars.** Hub pages need 6-month refresh to maintain freshness signals.

## Leverage with other skills

- Pair with `semrush-keyword-extractor` to source the keyword list
- Pair with `content-brief-builder` to brief writers on each post
- Pair with `internal-link-strategist` for the site-wide link plan
- Pair with `hubspot-blog-optimizer` (Bundle 3) to retrofit existing blog posts into the cluster structure

## MCP integration

With `semrush` MCP: `Pull the top 200 keywords for domain X. Group into 5-7 clusters by topic + intent. Identify pillar candidates per cluster. Build the editorial calendar with a 4-posts-a-month pace.`
