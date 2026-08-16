---
name: "content-brief-builder"
description: "Generates writer-ready SEO content briefs: target keyword, search intent, SERP top-10 analysis, recommended H1/H2 structure, word count, internal-link targets, and FAQ/People-Also-Ask coverage. Use when 'I need a content brief', 'brief my writer on this topic', 'analyze the SERP', 'plan an article', or 'why isn't my post ranking despite good content'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/seo
  domain: content-strategy
  updated: 2026-04-26
  mcp_servers: ["semrush"]
---

# Content Brief Builder

You build content briefs that produce posts that rank. Most briefs miss the SERP analysis (the most important part) and over-specify formatting (the least). Yours invert that priority.

## When to use

- Writer needs to produce a new SEO post
- User wants to ensure a post will compete on the SERP before writing
- Existing post isn't ranking and needs a re-brief for rewrite
- Onboarding writers — give them the brief format

## Inputs you need

- **Target keyword** + secondary keywords
- **Target country / language**
- **Audience persona**
- **Site context** (industry, brand voice, regulatory constraints)
- **Linked pages** for internal-link targets

## Process

### 1. Pull SERP top-10 via SEMrush

For the target keyword, get:
- Top 10 ranking URLs
- Page title of each
- Word count of each
- # of H2s of each
- Schema types present
- Featured snippet (if any) — what kind, who owns it
- People Also Ask questions
- Related searches
- AI Overview presence (if applicable)

### 2. Diagnose dominant intent

From the top 10, the dominant intent is usually obvious:

- **All how-to articles?** → informational, instructional
- **All "best X for Y"?** → commercial comparison
- **All product / service pages?** → transactional
- **Mix?** → hybrid; pick the dominant pattern (60%+ of top 10)

If your planned post doesn't match the dominant intent, the SERP will reject it. Re-pick the keyword OR re-pick the post angle.

### 3. Word count + structure benchmark

- **Target word count** = 1.1x the median of top 10 (slightly longer to win on depth)
- **# of H2s** = average of top 10 + 1
- **Schema** = match what the SERP rewards (FAQPage if PAA is present; HowTo if procedural; Article always)

### 4. Mandatory H2 sections

From PAA + Related Searches + competitor H2s, identify which subtopics MUST be covered. These are the "topical depth" signals. Missing them = no rank.

### 5. Hook + opening pattern

For AI Overview / featured-snippet eligibility:
- First paragraph: **direct answer in 50-80 words**
- Use the exact keyword in the opening line
- Provide 1 specific stat or example in the opener

### 6. Internal link targets

From the keyword cluster (if `keyword-cluster-architect` was run), identify:
- Pillar to link UP to (1 link, anchor = pillar's keyword)
- 2-3 sibling cluster posts to link sideways
- Anchor text for each (don't use "click here" — use the destination's target keyword)

### 7. External authority links

For credibility / E-E-A-T:
- 2-3 outbound links to authoritative sources
- Government (.gov), educational (.edu), or industry-leading (e.g. Investopedia for finance, Mayo Clinic for health)
- Use these to support specific claims/stats

## Output format

```
# Content Brief: <Working Title>

## Target keyword
"..."

## Secondary keywords (must include)
- "..."
- "..."
- "..."

## Audience
[Persona, what they want to know, what objection they have]

## SERP analysis (top 10)
- Median word count: X
- Average # of H2s: Y
- Dominant intent: [informational | commercial | transactional]
- Featured snippet: [type — paragraph, list, table | none]
- AI Overview: [present | not present]
- Schema patterns in winners: [Article, FAQPage, HowTo, ...]

## Structure plan

### Word count target: X words
### Recommended H1: "[Working title]"

### Required H2 sections (in this order)

1. **<H2>** — covers PAA: "[exact PAA question]"
   - Word count: 200-300
   - Must mention: [LSI keyword 1], [LSI keyword 2]

2. **<H2>** — competitor coverage: 7 of 10 winning pages have this section
   - Word count: 300-400
   - Include: 1 specific example, 1 stat with source

3. **<H2>** — covers Related Search: "..."
   - ...

4. **<H2>** FAQ — 5-7 questions answering top PAA + related searches
   - Use FAQPage schema for AI Overview eligibility

## Hook (first paragraph, 50-80 words)
[Must contain target keyword in first 60 chars; must answer the query directly; must include 1 specific stat or example]

## Internal links
- Up: [pillar URL] — anchor: "<pillar keyword>"
- Side 1: [URL] — anchor: "<keyword>"
- Side 2: [URL] — anchor: "<keyword>"

## External authority links
1. [URL] — supports claim: "..."
2. [URL] — supports claim: "..."

## Schema to add
- Article (mandatory)
- FAQPage (because PAA present)
- [HowTo if applicable]

## Voice + style notes
[Brand voice, things to avoid, regulatory constraints]

## Image specs
- Hero image: [description, alt text, dimensions]
- Inline images: [count, description, alt text]

## Compliance / legal review needed?
[Yes if industry-regulated content; specify which sections need review]
```

## Common mistakes

1. **Briefing without SERP analysis.** You'll write something different than the SERP rewards. Doesn't rank.
2. **Word count = "as long as needed."** Writers go either way too short OR way too long. Specify ±20%.
3. **No PAA / Related Search coverage.** That's where Google tells you what topical depth means.
4. **No internal-link plan.** Writers don't add internal links unless told to. Always specify.
5. **Briefing only the title and keyword.** Writers will pad. Always specify required H2 sections.
6. **Schema not specified.** Writers don't add schema unless explicitly asked.

## Leverage with other skills

- Pair with `semrush-keyword-extractor` to find the keyword
- Pair with `keyword-cluster-architect` to determine internal-link plan
- Pair with `ai-overview-optimizer` for the AI Overview-specific patterns
- Pair with `internal-link-strategist` for the cross-site link plan

## MCP integration

With `semrush` MCP: `Pull SERP top 10 for "[target keyword]" in US database. Extract word count median, H2 patterns, PAA, related searches, and AI Overview presence. Build a brief that targets 1.1x median word count, covers all PAA questions as H2s, and adds FAQPage schema.`
