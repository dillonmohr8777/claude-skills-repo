---
name: "google-ads-ad-copy-tester"
description: "Generates 10+ Responsive Search Ad copy variants per ad group following proven direct-response frameworks (PAS, AIDA, BAB, FAB), with strategic headline pinning, character-count compliance, and a structured A/B test plan. Use when the user says 'write Google Ads copy', 'I need ad variants', 'my ad relevance is low', 'rewrite my ads', 'help me test new headlines', or 'build out a Responsive Search Ad'. Optimized for ad-relevance lift + measurable variant testing."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-search
  domain: google-ads
  updated: 2026-04-26
  mcp_servers: ["google-ads"]
---

# Google Ads Ad Copy Tester

You write paid-search ad copy that survives Google's auction AND converts. Most ad copy is generic. Yours follows proven direct-response frameworks, fills all 15 RSA headline slots strategically, and structures a real A/B test plan — not "let's see what happens."

## When to use

- User has an ad group needing fresh ad copy
- Ad relevance is flagged "Below average" or "Average"
- User is launching a new campaign and needs the first set of ads
- User wants to A/B test a new angle (price, urgency, social proof, etc.)
- CTR has plateaued and user wants to try a structurally different ad

## Inputs you need

- **Ad group theme** — what is this ad group selling, and to whom?
- **Keywords in the ad group** — the ad must relate to all of them
- **Landing page URL** — and a one-line description of what the page says
- **Offer / hook** — what's the unique value? (price, speed, exclusive, social proof, etc.)
- **Compliance constraints** — regulated industry? (mortgage, health, financial — different rules)
- **Existing top performer** — if any, paste it. We'll keep what works.

## Process

### 1. Pick 3 ad-copy frameworks for this ad group

Don't write 10 variants of the same hook. Run 3 different frameworks against the same audience:

| Framework | Best for | Structure |
|---|---|---|
| **PAS** (Problem, Agitate, Solve) | Pain-driven offers (debt relief, fixing a broken thing) | "Tired of X? Stop wasting Y. Get Z today." |
| **AIDA** (Attention, Interest, Desire, Action) | Awareness-stage offers | "[Stat]. Here's why. Here's what it does. Apply." |
| **BAB** (Before, After, Bridge) | Transformation offers (services, transformation products) | "[State A]. [State B in 30 days]. [How: Z]." |
| **FAB** (Features, Advantages, Benefits) | Technical/B2B | "[Feature]. [What it means]. [Outcome]." |
| **Social Proof First** | Crowded markets where trust is the gate | "Used by 8,200 [audience]. [What]. [Apply]." |
| **Specificity Bomb** | Real-estate, B2B services with verifiable numbers | "$1.7M closed in 67 days. [How]. [CTA]." |

For Secure Lending, **Specificity Bomb + PAS** drove the 314x ROAS — specific dollar amounts and timelines outperformed generic mortgage ads by 4x.

### 2. Fill all 15 headline slots

Google requires 3+ headlines for an RSA. They allow up to 15. Always fill 15.

Strategic distribution:
- **3 keyword-led headlines** — must include the ad-group's primary keyword. Pin one to position 1.
- **3 offer/hook headlines** — the unique value (price, guarantee, speed)
- **2 social-proof headlines** — numbers, named clients, awards
- **2 urgency/scarcity headlines** — only if true. Never fake.
- **2 CTA headlines** — "Get a Free Quote", "Apply in 60 Seconds"
- **2 brand/qualifier headlines** — "Veteran-Owned", "BBB Accredited", "Since 2015"
- **1 question headline** — "Looking for a VA Loan in Phoenix?"

Character limits:
- Headlines: 30 chars each
- Descriptions: 90 chars each
- Path 1 + Path 2: 15 chars each

### 3. Pinning strategy

By default, don't pin (let Google's machine optimize). Pin only when you must:

- **Pin a keyword headline to position 1** if Ad Relevance is "Below average" — forces the keyword to show
- **Pin a compliance line to position 3** if your industry requires disclosure (mortgage, financial, health)
- **NEVER pin all positions** — that defeats RSA's whole point

### 4. Write descriptions

Fill 4 descriptions:
- **Description 1:** the offer + outcome ("Get pre-approved in 24 hours. No origination fees.")
- **Description 2:** social proof or specificity ("314x ROAS for our last 4 client homes.")
- **Description 3:** objection handling ("Bad credit? We work with scores from 580.")
- **Description 4:** CTA + urgency ("Apply now. Closing in 21 days or less.")

### 5. Path display

Use `path1` and `path2` to show implied URL structure. Always include:
- The keyword theme (e.g., `/va-loans` or `/phoenix-mortgage`)
- The offer (e.g., `/apply-today` or `/free-quote`)

### 6. Build the A/B test plan

For the variants you produce, define:
- **Hypothesis:** "Specificity Bomb beats Generic by 25%+ CTR"
- **Sample size:** how many impressions per variant before calling it (default: 1,000 per variant minimum)
- **Win criterion:** CTR delta with stat significance, OR conversion-rate delta if conversion sample is sufficient
- **Stop loss:** kill any ad that's < 50% of the leader's CTR after 2,000 impressions

## Output format

```
# Ad Copy Variants: <ad group name>

## Strategy
- Frameworks tested: PAS, Specificity Bomb, BAB
- Hypothesis: ...
- Sample size: 1,000 impressions per variant minimum

## Variant A: PAS framework

### Headlines (15)
1. "Stop Overpaying for VA Loans" [pin position 1]
2. "Phoenix VA Loans, Done Right"
3. "Veteran? Get Pre-Approved Fast"
4. "$0 Origination Fees Today"
5. "BBB Accredited, A+ Rated"
6. "VA Loan Calculator Inside"
7. "Apply in 60 Seconds"
8. "Closing in 21 Days or Less"
9. "Bad Credit? We Help"
10. "Get a Free VA Loan Quote"
11. "Used by 1,200 Veterans"
12. "Phoenix's #1 VA Lender"
13. "No Down Payment Required"
14. "Talk to a Loan Officer"
15. "Looking for a VA Loan?"

### Descriptions (4)
1. "Tired of high mortgage fees? Phoenix's VA loan specialists. Pre-approved in 24 hrs."
2. "$1.7M closed for veterans last quarter. Real numbers, real homes. See how."
3. "We work with scores from 580. No down payment required for qualified buyers."
4. "Apply today. Pre-approval in 24 hours. Close in 21 days or less. Get started."

### Paths
- Path 1: va-loans
- Path 2: apply-today

## Variant B: Specificity Bomb
[same shape]

## Variant C: BAB
[same shape]

## A/B test plan
- Run all 3 simultaneously in same ad group
- Optimize ad rotation: "Optimize" (default) NOT "Rotate evenly"
- Review at 1,000 impressions per variant
- Kill anything < 50% of leader CTR
- Promote winner to baseline; iterate next round of variants vs. winner
```

## Common mistakes

1. **Filling 3 headlines and calling it done.** Google has 15 slots — use them. Fewer headlines = fewer experiments running = slower learning.
2. **Pinning every headline.** Defeats RSA. Only pin when you have a structural reason.
3. **Generic headlines.** "Best mortgage rates" beats nothing. "$1.7M closed in 67 days for veterans" beats "best mortgage rates" by 3-5x CTR.
4. **No A/B structure.** Running 1 ad means you have no idea what's working. Always 2-3 variants minimum.
5. **Faking urgency.** "Limited time offer" with no actual end date hurts trust + Google quality. Be specific or skip.

## Compliance watchouts (industry-specific)

- **Mortgage / lending:** must include APR disclosure, equal housing language, loan officer NMLS if individual. Pin compliance to position 3.
- **Health / wellness:** no disease cure claims. Avoid "guaranteed".
- **Financial advisory:** SEC/FINRA disclosures required for ad copy mentioning returns.
- **Real estate:** Fair Housing Act compliance — no demographic targeting language.

## Leverage with other skills

- Run after `google-ads-keyword-strategist` produces the ad-group structure
- If Ad Relevance is "Below average" after testing, check `google-ads-quality-score-fixer`
- Pair with `landing-page-auditor` (Conversion + Analytics bundle) — ad copy without matching landing page wastes the click

## MCP integration

With `google-ads` MCP: `Read existing top-performing ads in customer 123-456-7890's account, identify the headline patterns that drive 1.5x+ avg CTR, and generate 3 new variants per top ad group following the same patterns plus 2 contrarian frameworks.`
