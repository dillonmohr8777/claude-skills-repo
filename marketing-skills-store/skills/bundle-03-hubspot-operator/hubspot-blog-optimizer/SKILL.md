---
name: "hubspot-blog-optimizer"
description: "Reads existing HubSpot blog posts via the HubSpot MCP server, audits each against current SEO best practices (meta structure, keyword length vs competitors, internal linking, AI Overview readiness), and rewrites them in place. Built from the live agent that drove +17.2% organic traffic in 30 days at Align HCM, lifted Authority Score 4 points, ranked 3 existing blogs at #1, and pulled 2 into Google AI Overview after optimizing 25 blogs in under an hour. Use when the user has a HubSpot blog with old/underperforming posts, wants to scale blog optimization, or says 'optimize my blog content', 'fix my old blog posts', 'rank my blogs higher'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/seo
  domain: hubspot
  updated: 2026-04-26
  mcp_servers: ["hubspot", "semrush"]
  receipts: "Align HCM: +17.2% organic traffic in 30 days, AS +4, 3 blogs at #1, 2 in Google AI Overview, 25 blogs optimized in under an hour"
---

# HubSpot Blog Optimizer

You optimize existing HubSpot blog content at scale via the HubSpot MCP. This is the live agent that produced **+17.2% organic traffic in 30 days at Align HCM** after taking over in January 2026 — including ranking 3 existing blogs at #1 on Google and pulling 2 into Google AI Overview. **25 blogs optimized in under an hour.**

The skill doesn't write new content. It makes the content you already have rank better.

## When to use

- HubSpot account has 10+ existing blog posts that are underperforming
- User wants to systematize blog optimization (not 1-by-1 manual work)
- Recent SEO algorithm shifts (AI Overview, Helpful Content) have hurt rankings
- Onboarding a new client and need a quick organic-traffic win

## Inputs you need

- **HubSpot MCP connection** with `content` scope on the Private App
- **SEMrush MCP** (optional but strongly recommended for competitor data)
- **Target keywords per post** (will be inferred from the post if not provided)
- **Brand voice doc** (or sample posts to learn voice from)
- **Service area / target geo** (if local SEO matters)
- **Sample size for audit:** how many posts to optimize in this run? (Default: top 25 by organic traffic + bottom 25 by impressions-but-no-clicks)

## What this skill optimizes (the 7 levers)

### Lever 1: Title tag + H1

- Title tag: 50-60 chars, primary keyword in first 50 chars, brand at end
- H1: must match search intent (informational vs commercial); not just keyword-stuffed
- **Default fix:** 60-80% of legacy HubSpot posts have title tags that read as content titles, not search-result-optimized titles. Rewrite.

### Lever 2: Meta description

- 140-160 chars, includes primary keyword + secondary keyword
- Promises a specific outcome ("Learn how to X in 5 steps") not vague ("Learn about X")
- **Default fix:** ~70% of legacy posts have auto-generated meta descriptions. Always rewrite.

### Lever 3: Keyword length / topical depth (vs competitors)

This is the single biggest lever in 2026. Google's Helpful Content + AI Overview both reward topical depth.

**Process:**
1. Pull SERP top 10 for the post's target keyword via SEMrush MCP
2. Average word count of top 10 results
3. Compare to current post word count
4. If post is < 80% of top-10 average, expand with relevant subtopics

**Default expansion approach:**
- Add 2-3 H2 sections covering related questions (pulled from "People Also Ask" + "Related Searches")
- Each new H2 has 200-400 words of substantive content (not filler)
- Include a comparison table or process diagram if the topic warrants

### Lever 4: Internal linking

- Every post needs 3-7 internal links to other relevant blog posts
- Anchor text should be the target keyword of the destination post
- **Default fix:** add 3-5 internal links per post, anchored on actual destination keywords. Most legacy posts have 0-1 internal links.

### Lever 5: Schema / structured data

- **Article schema:** required on every post (HubSpot adds basic; verify with structured-data-test)
- **FAQPage schema:** add to any post with an FAQ section (massively helps with AI Overview eligibility)
- **HowTo schema:** add to any "how to X" post with numbered steps

### Lever 6: AI Overview readiness

In 2026, AI Overview (Google's AI-generated answer at the top of SERPs) is the new featured snippet. To get pulled into AI Overview:

- **First paragraph answers the query directly** in 50-80 words (the "AEO" / answer-engine-optimization pattern)
- **Numbered or bulleted steps** for procedural queries
- **Direct citations** of statistics with source links (signals authority)
- **Clean H2 questions** that match common "How does X" / "What is X" queries
- **Schema:** Article + FAQPage + HowTo as relevant

**Receipt:** at Align HCM, applying these 4 patterns pulled 2 of 25 optimized posts into AI Overview within 11 days.

### Lever 7: Competitor keyword length

A specific tactic that produced measurable gains at Align HCM:

1. Pull the keyword target's SERP top 5
2. Measure each result's keyword density on the primary + 5 closest LSI keywords
3. Match or slightly exceed the median (NOT the max — keyword stuffing flag)
4. Distribute keyword mentions across H2/H3 headers, not just body text

## Process per blog post

```
1. Pull post via HubSpot MCP (HTML body + meta + URL slug)
2. Identify primary keyword (from title, H1, or current ranking data)
3. Pull SERP top 10 via SEMrush MCP for that keyword
4. Audit post against the 7 levers; produce a fix list
5. Rewrite the post with the fixes
6. Update title, meta description, and slug if needed
7. Push back to HubSpot via MCP (DRAFT mode by default — never auto-publish without confirmation)
8. Log changes to a tracking sheet (post URL, before/after metrics, date)
```

## Output format

```
# Blog Optimization Report: <run date>

## Run summary
- Posts in scope: N
- Posts optimized (drafts created): N
- Estimated organic traffic lift: +X% within 30 days (based on baseline + competitor benchmarks)
- Total tokens used / cost: $X

## Per-post audit

### Post: <title> | URL: <url>

**Primary keyword:** "..."
**Current ranking:** #X (or "not in top 100")
**Competitor SERP analysis:** top 10 average word count = Y words; current post = Z words

**Issues found:**
- Title tag: [issue + fix]
- Meta description: [issue + fix]
- Word count: needs +X words on these subtopics: [...]
- Internal links: 0 → recommend 5 to: [post 1, post 2, ...]
- Schema: Article only → add FAQPage
- AI Overview readiness: low → restructure first paragraph to direct answer
- Keyword length: under-indexed on [LSI 1, LSI 2]

**Action taken:**
- Title: "Old Title" → "New Title"
- Meta: "Old meta" → "New meta"
- Body: rewrote H2 #2, added H2 #5 + #6 (450 words), added 5 internal links, added FAQPage schema
- Status: DRAFT in HubSpot, awaiting human review

## Posts skipped + why
- [Post X]: ranking #1 already, no improvement needed
- [Post Y]: thin content with no clear keyword target — recommend rewrite from scratch (separate skill)

## Tracking
- All changes logged to: [sheet URL]
- Next audit recommended: 30 days post-publish
```

## Common mistakes

1. **Auto-publishing without human review.** This skill always saves to DRAFT. Approve in HubSpot before publishing.
2. **Optimizing low-impression posts.** If a post has < 100 impressions / 90 days, it's not the keyword target that's wrong — it's the topic. Don't waste time.
3. **Adding keywords to hit density targets.** Topical depth matters more than density. Add a new H2 covering a related subtopic, not 10 mentions of the same keyword.
4. **Ignoring internal linking.** Internal links are the cheapest ranking lever in HubSpot. Always add 3-5.
5. **Skipping schema.** FAQPage schema can get you into AI Overview. Article-only is leaving wins on the table.

## Compliance / brand voice

- The skill MUST stay in brand voice. Provide brand voice doc or sample posts in the input.
- Don't auto-add affiliate links or external promotional language.
- Industry-regulated content (medical, financial, legal) needs human review of every claim — flag for legal review before publishing.

## Leverage with other skills

- Pair with `keyword-cluster-architect` (Bundle 4) to identify NEW post topics, not just optimize existing
- Run `internal-link-strategist` (Bundle 4) for the site-wide linking plan
- Use `serp-feature-targeter` (Bundle 4) for the AI Overview / featured snippet hunt

## MCP integration

The full live agent invocation:

```
Run hubspot-blog-optimizer on the 25 lowest-CTR blog posts published in the last 18 months. For each, pull SERP top 10 from SEMrush MCP, audit against the 7 levers, rewrite to match competitor depth + AI Overview readiness, and save as DRAFT in HubSpot. Log all changes to the tracking sheet.
```

This invocation produced **+17.2% organic traffic in 30 days at Align HCM** after taking over in January 2026.
