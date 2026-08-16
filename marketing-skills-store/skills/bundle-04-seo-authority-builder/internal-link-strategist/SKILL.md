---
name: "internal-link-strategist"
description: "Audits a site's internal-link graph and produces a prioritized fix list — orphan pages, link-deficient pages, anchor-text optimization, and pillar-cluster link relationships. Outputs a row-by-row 'add link from X to Y with anchor Z' action sheet. Use when 'fix my internal linking', 'audit site architecture', 'orphan pages', 'pages aren't ranking despite good content', or 'connect my blog posts'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/seo
  domain: site-architecture
  updated: 2026-04-26
  mcp_servers: ["semrush", "hubspot"]
---

# Internal Link Strategist

You audit and fix internal-link graphs. This is the single most under-leveraged ranking factor on most sites. Pages that should rank don't, because they're "orphaned" (no incoming internal links) or "isolated" (no outgoing internal links). Fix the graph, the rankings move.

## When to use

- Site has 50+ pages but rankings are flat
- New pages aren't getting indexed quickly
- Pillar-cluster strategy was planned but never linked properly
- Recent migration / replatform broke internal links

## Inputs you need

- **Site sitemap** (XML or crawl)
- **Current ranking data** per page (SEMrush MCP can pull)
- **Pillar/cluster structure** (if defined; otherwise this skill will identify candidates)
- **Domain authority context** for prioritization

## The 5-layer audit

### Layer 1: Orphan detection

A page is orphaned if it has zero incoming internal links from other pages on the same domain. Google sees these as low-priority and crawls them rarely.

**Audit:** crawl the site, list pages with 0 incoming links.

**Fix:** add 2-3 incoming links to each orphan from contextually-relevant pages.

### Layer 2: Link-deficiency

A page is link-deficient if it has < 3 incoming internal links. Threshold may be higher for important commercial pages (target 5-10 incoming).

**Audit:** rank pages by # of incoming links ascending, flag those below threshold.

**Fix:** prioritize commercial pages first; add links from related blog posts.

### Layer 3: Anchor-text optimization

Internal-link anchor text is a strong ranking signal. Use exact-match keywords (within reason — don't over-optimize for the same anchor everywhere).

**Audit:** for each page, list all incoming-link anchors. Flag:
- Pages where anchor is "click here", "read more", "this article" (waste)
- Pages where ALL anchors are identical exact-match (over-optimized)
- Pages where anchors don't include any keyword variant

**Fix:** rewrite anchors to use keyword variants. Diversity is good — primary keyword 40%, partial keyword 40%, branded/generic 20%.

### Layer 4: Pillar-cluster link relationships

If the site has pillar-cluster structure (or could):

**Audit:**
- Every cluster post links UP to its pillar — Y/N
- Every cluster post links sideways to ≥ 2 sibling clusters — Y/N
- Pillar links DOWN to ≥ 5 cluster posts — Y/N

**Fix:** add the missing links. Pillar pages especially need the down-links to act as a "hub" Google recognizes.

### Layer 5: Commercial-page authority flow

Commercial pages (services, pricing, application) are usually link-starved because they're not in the blog cluster. They miss the topical-authority flow.

**Audit:** for each commercial page, count incoming links from related blog content.

**Fix:** for every blog post on related topics, add 1-2 contextual links to the relevant commercial page. NOT a navigation link — a contextual in-body link.

This is how blog content actually drives revenue: by passing authority + traffic to commercial pages.

## Process

```
1. Pull full sitemap + crawl data (or via SEMrush Site Audit MCP)
2. Run all 5 layers; flag issues
3. Prioritize fixes:
   - Highest-traffic-potential commercial page first (Layer 5)
   - Then pillar-cluster relationships (Layer 4)
   - Then orphans (Layer 1)
   - Then link-deficient high-value pages (Layer 2)
   - Then anchor-text optimization (Layer 3) — usually a 6-month project
4. Output as row-by-row action list
5. Implement in HubSpot (or other CMS) via batch edit
```

## Output format

```
# Internal Link Audit: <site>

## Audit summary
- Pages crawled: X
- Orphan pages: Y (Z% of total)
- Link-deficient pages (< 3 incoming): A
- Pillar pages without cluster down-links: B
- Commercial pages with < 5 incoming blog links: C
- Anchor text issues: D total instances

## Layer 1: Orphan pages

| URL | Page topic | Recommended source pages | Recommended anchor text |
|---|---|---|---|
| /blog/post-x | Topic | /blog/post-y, /blog/post-z | "topic-keyword" |
| ... |

## Layer 2: Link-deficient pages

| URL | Current incoming | Target incoming | Source candidates | Anchor recommendations |
|---|---|---|---|---|
| ... |

## Layer 3: Anchor-text fixes

| Source page | Destination | Current anchor | Recommended anchor |
|---|---|---|---|
| /blog/x | /service/y | "click here" | "professional Y service" |
| ... |

## Layer 4: Pillar-cluster gaps

### Cluster: <pillar topic>
- Pillar URL: ...
- Cluster posts:
  - [URL]: missing UP-link to pillar
  - [URL]: missing side-link to [URL]
  - ...

## Layer 5: Commercial page authority flow

| Commercial page | Current incoming links | Recommended additions (post → page) |
|---|---|---|
| /services/va-loans | 2 | /blog/what-is-va-loan, /blog/va-eligibility, /blog/apply-va-loan |
| /apply | 1 | /blog/first-time-buyer-guide, /blog/calculator-explained, ... |

## Implementation order

### Week 1 (highest impact)
- Add 5 internal links to /apply commercial page from existing blog
- Resolve 3 highest-traffic orphans
- Build pillar-down-links on top 2 pillar pages

### Week 2-4
- Pillar-cluster connections for clusters 1-3
- Anchor-text fixes on top 20 high-traffic pages

### Month 2-3
- Orphan resolution
- Long-tail anchor optimization

## Estimated outcome
- New page time-to-index: 7 days → 2 days
- Orphan-page rankings: from "not in top 100" → page 2-3 within 30 days
- Commercial-page rankings: 1-3 position lift on average
```

## Common mistakes

1. **Treating navigation links as "internal links."** Footer nav and header nav don't pass meaningful authority. Contextual in-body links do.
2. **Same anchor text everywhere.** Over-optimization signal. Diversify.
3. **No links to commercial pages from blog.** Blog drives traffic; commercial pages convert. Connect them.
4. **Ignoring orphans.** Google crawls them rarely; they don't rank.
5. **Building pillar pages with no down-links.** Pillar without cluster-links is just a long article.
6. **Spam-anchoring with exact-match repeatedly.** Vary by 20-40% partial-match.

## Leverage with other skills

- Pair with `keyword-cluster-architect` to first define the pillar-cluster structure
- Pair with `hubspot-blog-optimizer` (Bundle 3) to retrofit existing posts with links
- Pair with `content-brief-builder` so new posts ship with their internal-link plan baked in

## MCP integration

With `semrush` MCP: `Pull site audit for domain X. Identify all orphan pages, link-deficient pages, and pillar-cluster gaps. Produce the row-by-row action list with source pages and recommended anchor text for each fix.`

With `hubspot` MCP: `For each fix in the action list, batch-update the source HubSpot blog posts to add the recommended internal links. Save as drafts for human review.`
