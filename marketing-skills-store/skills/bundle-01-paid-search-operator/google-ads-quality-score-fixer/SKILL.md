---
name: "google-ads-quality-score-fixer"
description: "Diagnoses and fixes low Quality Score in Google Ads systematically. Pulls keyword-level QS components (Expected CTR, Ad Relevance, Landing Page Experience), groups failures by root cause, and outputs a prioritized fix list with specific ad-copy/keyword/landing-page changes. Use when the user says 'my Quality Score is low', 'CPCs are climbing', 'I have keywords with QS 3 or below', 'fix my Quality Score', or 'why are my Google Ads so expensive'. Outputs a fix sequence ranked by impact."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-search
  domain: google-ads
  updated: 2026-04-26
  mcp_servers: ["google-ads"]
---

# Google Ads Quality Score Fixer

You diagnose Quality Score problems systematically. QS is the single biggest lever on CPC — moving from QS 4 to QS 8 cuts CPC by ~50% on the same keyword. Most marketers treat QS as a black box; you treat it as a three-component diagnostic.

## When to use

- User reports rising CPCs without traffic increase
- User has visible "Below average" or "Average" flags on QS components
- User wants to lower CPC across the account systematically
- User is preparing for a Q4 push and wants the account in fighting shape

## Inputs you need (ask if missing)

- **Account access:** via `google-ads` MCP server, or paste of the Keyword Performance Report with QS columns (Expected CTR, Ad Relevance, Landing Page Experience)
- **Account size:** number of campaigns, ad groups, keywords (impacts prioritization)
- **Time window:** last 30 / 60 / 90 days
- **Recent changes:** any account changes in the last 90 days that might have caused QS drop?

## Diagnostic process

QS is determined by three components. Diagnose each independently.

### Component 1: Expected CTR

**What it measures:** Google's prediction of how often your ad will be clicked when shown for this keyword, controlling for position.

**"Below average" diagnosis:**
- Keyword is too broad and matches search terms with low intent
- Ad headlines don't include the keyword (or a close variant) prominently
- Ad-group structure mixes too many themes (the ad doesn't match every keyword in the group well)
- Account has a history of low CTR (this is sticky for ~30 days even after fixes)

**Fix sequence:**
1. Run a **search-term audit** on the offending ad group — what queries are actually triggering this keyword? If 60%+ are off-theme, restructure the ad group.
2. Rewrite ad headlines to include the keyword in **Headline 1 or 2**. Use Dynamic Keyword Insertion (`{KeyWord:Default}`) only as a last resort — it's clunky.
3. If keyword is broad match without Smart Bidding, switch to Phrase or add Smart Bidding.
4. Pause keywords with QS ≤ 3 that you can't fix in 14 days. They're dragging down account-level QS.

### Component 2: Ad Relevance

**What it measures:** how closely your ad matches the meaning of the keyword.

**"Below average" diagnosis:**
- Ad copy uses synonyms but not the actual keyword
- Ad group has 30+ keywords on different themes (keyword-ad mismatch is statistical)
- No Responsive Search Ad with all 15 headlines + 4 descriptions filled

**Fix sequence:**
1. **Tighten the ad group.** If it has more than 15 keywords, split it. Single Theme Ad Groups only.
2. Ensure each ad group has at least one RSA with all 15 headline slots filled. Pin 1–2 critical headlines (the keyword variant and the offer).
3. Ad headlines must reference the keyword theme in at least 3 of 15 slots.
4. Descriptions must reference the offer + the audience.

### Component 3: Landing Page Experience

**What it measures:** does the page load fast, work on mobile, and match the ad's promise?

**"Below average" diagnosis:**
- Landing page is the homepage (always wrong unless brand keyword)
- Page has Core Web Vitals failures (LCP > 2.5s, CLS > 0.1)
- Page content doesn't reference the keyword theme in H1, H2, or first paragraph
- Page has interstitials, popups, or autoplaying video
- Mobile experience is broken (test on actual phone, not Chrome DevTools)

**Fix sequence:**
1. **One landing page per ad group theme** — never share the homepage across themes.
2. Run PageSpeed Insights. LCP must be < 2.5s on 4G mobile. If not, defer non-critical JS, optimize images, switch to a faster hosting tier.
3. Ensure the keyword (or a close variant) appears in: page title, H1, first paragraph, and at least one CTA button.
4. Remove interstitials. If you must have a popup, delay it 30+ seconds.
5. Add trust signals above the fold (testimonials, certifications, real customer logos).

## Output format

```
# Quality Score Diagnostic Report

## Account-level summary
- Total keywords: X
- Avg QS (weighted by impressions): Y/10
- Keywords at QS ≤ 4: Z (P% of impressions)
- Estimated CPC reduction if all fixed: $X / month

## Findings by component

### Expected CTR — N keywords flagged
[ranked list with specific keyword + ad group + recommended fix]

### Ad Relevance — N keywords flagged
[same shape]

### Landing Page Experience — N landing pages flagged
[per-page issue list with specific URL fix]

## Prioritized fix sequence

### Week 1 (highest impact, lowest effort)
1. ...
2. ...
3. ...

### Week 2 (structural changes)
- Restructure ad group: <name> → split into <new groups>
- ...

### Week 3 (landing page fixes — coordinate with web team)
- ...

## Expected outcome
- Account avg QS: Y/10 → Y'/10 within 30 days
- Avg CPC: $X → $X'
- Same conversion volume on $Z less spend (or +N% volume on flat spend)

## Watchouts
- QS updates lag 7-14 days after fixes. Don't panic if you don't see movement in week 1.
- Pausing low-QS keywords gives an immediate account-level lift but loses some traffic. Decide based on the keywords' conversion data.
```

## What NOT to do

- **Don't bid up on low-QS keywords to "force" them onto page 1.** You'll pay 2-3x normal CPC for traffic that won't convert.
- **Don't add tons of keywords to "give Google more data."** Account-level QS is dragged down by every low-QS keyword. Quality > volume.
- **Don't trust QS scores for keywords with < 100 impressions.** They're statistically noisy. Wait for more data or pause.
- **Don't ignore "Average" QS components.** "Average" means you're not winning the auction; "Below average" means you're losing it. Both deserve attention.

## Leverage with other skills

- `google-ads-campaign-architect` — restructure if your ad group sprawl is the root cause
- `google-ads-ad-copy-tester` — generate the new headline/description variants needed for Ad Relevance fixes
- `landing-page-auditor` (in the Conversion + Analytics bundle) — if Landing Page Experience is the dominant problem

## MCP integration

With the `google-ads` MCP connected, this skill can pull QS data directly: `Pull keyword-level QS for customer 123-456-7890 last 30 days, flag any keyword below QS 5 with > 100 impressions, and rank fixes by estimated CPC savings.`
