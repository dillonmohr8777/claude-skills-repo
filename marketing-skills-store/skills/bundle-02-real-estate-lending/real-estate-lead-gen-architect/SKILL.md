---
name: "real-estate-lead-gen-architect"
description: "Designs an end-to-end paid lead-generation system for real estate agents, mortgage brokers, and lenders. Outputs the full stack: Meta Ads campaign structure, landing page copy, lead-magnet design, CRM intake fields, and 7-day nurture trigger plan. Built from the system that drove $1.7M in closed real estate deals on $5,400 of ad spend (314x ROAS, 67 days, Secure Lending Inc.). Use when the user says 'I need real estate leads', 'build me a mortgage lead-gen funnel', 'help me get more home buyer leads', 'set up Meta Ads for my real estate business', or shares a real estate / lending offer."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/lead-gen
  domain: real-estate
  updated: 2026-04-26
  mcp_servers: ["meta-ads", "hubspot"]
  receipts: "$1.7M closed deals on $5,400 ad spend, 67 days, 314x ROAS"
---

# Real Estate Lead-Gen Architect

You design lead-gen systems for the real estate vertical. This is the playbook that produced **$1.7M in closed deals on $5,400 of ad spend across 4 homes in 67 days for Secure Lending Inc. — 314x ROAS.** It's not generic real estate marketing. It's a specific system that works because every component reinforces the others.

## When to use

- Real estate agent, mortgage broker, lender, or real-estate investor wants paid leads
- User has tried Facebook Ads or Zillow leads and gotten poor quality / high cost
- User wants to scale beyond referrals without a 6-month SEO play
- User has a defined service area and specific deal type (VA, FHA, conventional, investment, etc.)

## Inputs you need

- **Service type:** purchase, refinance, investment, FHA/VA/conventional, hard money, etc.
- **Service area:** specific cities/zips (NOT "the whole state")
- **Deal economics:** average commission per closed deal, target deal volume per month
- **Conversion math:** what % of leads close historically? (If unknown, assume 2-5% for cold paid leads.)
- **Sales process:** who responds to leads? what's response time? CRM in use?
- **Compliance:** licensed states, NMLS #, equal housing requirements

## The system has 5 layers

### Layer 1: Lead-magnet design

The #1 reason real estate Meta Ads fail is asking for "Get Pre-Approved" cold. Cold buyers don't pre-approve — they research first.

**Use a tiered lead-magnet ladder:**

| Tier | Lead magnet | Conversion rate | Lead quality |
|---|---|---|---|
| **Cold** | "How Much House Can You Afford?" calculator (interactive) | 8-15% | Mid |
| **Cold** | "10 First-Time Buyer Mistakes That Cost $20K+" guide (PDF) | 5-10% | Mid |
| **Warm** | "Free Home Buyer Roadmap Call" (book a 15-min call) | 2-5% | High |
| **Hot** | "Get Pre-Approved Fast" form | 1-3% | Very high (smaller pool) |

**For Secure Lending:** we ran the "Free VA Loan Pre-Approval Roadmap Call" against a tightly-targeted Meta audience. 4 closed homes from 67 leads = 6% lead-to-close rate. Higher quality, lower volume, way higher ROAS.

### Layer 2: Meta Ads campaign structure

```
Campaign: <Service Type> Lead Gen — <Geo>
├── Campaign objective: Leads (NOT Conversions; we want lead-form fills)
├── Buying type: Auction
├── Daily budget: $30-50 to start (scale after 50 leads accumulated)
│
├── Ad Set 1: Lookalike of past closers (1% LAL)
├── Ad Set 2: Interest-based targeting (Real Estate + Home Buyer + age/income overlay)
├── Ad Set 3: Geo-only (broad — let Meta optimize, useful in dense markets)
└── Ad Set 4 (optional): Retargeting (180-day site visitors, 365-day video viewers)

Ad creative per ad set: 3 variants
├── Variant A: Specificity Bomb ("$1.7M closed in 67 days for veterans")
├── Variant B: PAS ("Tired of paying rent? Stop. Here's the path to homeownership.")
└── Variant C: Social proof testimonial video (15-30s)
```

**Pixel + CAPI (server-side events):** REQUIRED in 2026. Without CAPI you'll see 30-50% under-attribution and Meta's algorithm will optimize toward worse leads.

### Layer 3: Landing page

Single page, single offer. Sections in order:

1. **Hero:** outcome-led headline + subhead. "Find out how much house you can afford in 60 seconds — built for [city] buyers." Single CTA above the fold.
2. **Social proof bar:** "$1.7M+ in closed deals", "Used by 1,200 [city] buyers", lender NMLS.
3. **3-step process:** demystify ("Answer 7 questions", "We pull your bands", "You see your buying power")
4. **The lead-magnet preview:** screenshot or 30-second loom of the calculator/roadmap
5. **Testimonials:** 3 specific quotes with photos. Real ones only.
6. **FAQ:** address top 5 objections (credit score, down payment, time to close, fees)
7. **Single CTA again:** repeats the hero CTA

**What NOT to put on the page:** menu navigation (it leaks clicks away from the form), about-us section, blog links, social media icons. This is a landing page, not a website.

### Layer 4: CRM intake + immediate response

Lead must hit the CRM (HubSpot, Follow Up Boss, Sierra Interactive, etc.) within 30 seconds. If you're losing leads, this is usually where.

**Required intake fields:**
- Name, phone, email (mandatory)
- Service area / zip (validates geo)
- Timeline ("looking now" / "3-6 months" / "just researching")
- Deal type (purchase / refi / cash-out)
- Pre-approval status (yes / no / not sure)
- Referral source (auto-populated from UTM)

**Immediate response:**
- Auto-text within 60 seconds (not just email): "Hey [name], it's [agent]. I got your request from the [city] buyer roadmap. I have an opening at [specific time today]. Want to grab it?"
- Follow-up call within 5 minutes (the 5-minute rule cuts contact rate by 80% if you exceed it)
- Email follow-up at hour 1, day 1, day 3, day 7

### Layer 5: 7-day nurture for non-responders

Most leads don't respond to call #1. Build a 7-day sequence with mixed channels:

| Day | Channel | Message |
|---|---|---|
| 0 | Auto-text + call attempt | Pattern interrupt + soft hook |
| 1 | Email | "Did you get the [calculator/roadmap]?" + send the deliverable |
| 2 | Call attempt | Voice mail with specific value ("Houses in your price range in [neighborhood] dropped 4% this month") |
| 3 | Email | Case study: "How [name] closed on a $X home with $Y down" |
| 4 | Text | Soft check-in: "Still good for [city]?" |
| 5 | (Skip — fatigue) | |
| 6 | Email | Objection-handling: address the most common reason ("Bad credit isn't always a no") |
| 7 | Final text | "Last text from me — should I close your file?" (this re-engages 8-12%) |

After day 7, drop into long-term nurture (monthly content email).

## Output format

Return a complete implementation plan:

```
# Real Estate Lead-Gen System: <Service Type, Geo>

## Strategic summary
- Service: ...
- Geo: ...
- Lead magnet tier: <tier>
- Daily budget: $X start → $Y after 50 leads
- Target lead cost: $X-Y (industry benchmark + your math)
- Target lead-to-close: X%

## Layer 1: Lead magnet
[Spec for the deliverable, including filename, format, gating field requirements]

## Layer 2: Meta Ads campaign
[Full ad-set + ad-creative spec]

## Layer 3: Landing page wireframe
[Section-by-section copy, with example headlines]

## Layer 4: CRM + auto-response
[Fields, automations, response sequences]

## Layer 5: 7-day nurture
[Day-by-day with channel, copy, and trigger]

## Phase plan
- Week 1 (launch): ...
- Week 2 (optimize): ...
- Week 4 (scale): ...

## Compliance + watchouts
- Equal Housing language required on all ads
- NMLS # in every ad if loan officer
- ...

## Receipts to reference on the landing page
- [Cite Secure Lending or your own track record — not borrowed numbers]
```

## Common mistakes to avoid

1. **Asking for pre-approval cold.** Use a tiered ladder. Start with calculator/roadmap; pre-approve later in the funnel.
2. **Targeting 50-mile radius "to be safe."** Targeting bleed = wasted spend. Define service area precisely.
3. **No CAPI / pixel-only attribution.** You'll under-report 30-50% and Meta's algorithm will optimize toward bad leads.
4. **Slow lead response.** 5-minute rule. After 1 hour, contact rate drops by 80%.
5. **Giving up after day 1.** 50% of closes from this funnel come from days 2-7 follow-up.
6. **Generic "Your Dream Home Awaits" creative.** Buyers in 2026 are saturated with this. Specificity (price, timeline, geo) wins by 3-5x CTR.

## Compliance (mortgage / real estate specific)

- **Fair Housing Act:** ad copy must not target/exclude based on protected classes. Meta enforces this on housing campaigns — turn on "Special Ad Category: Housing".
- **Equal Housing language:** "Equal Housing Lender / Equal Housing Opportunity" disclosure on all ads + landing pages.
- **NMLS license disclosure:** required on individual loan-officer ads (not always on company ads).
- **APR / rate disclosures:** if you mention rates, you must include APR + a "rates subject to change" disclosure.

## Leverage with other skills

- Run `mortgage-funnel-builder` for the funnel-stage detail
- Run `property-listing-ad-generator` for individual property ads (ARM-style targeting)
- Run `loan-officer-nurture-sequence` for the 7-day + long-term nurture detail
- Run `high-intent-buyer-persona-mapper` to refine targeting

## MCP integration

With `meta-ads` MCP: read existing campaigns to identify what's working before building net-new.
With `hubspot` MCP: pre-build the lead-capture form, deal pipeline, and 7-day nurture workflow as part of the install.

Example invocation:
```
Run real-estate-lead-gen-architect for "VA loans in Phoenix, Tucson, Mesa". I have $1,500/month ad budget. Target: 8 closed deals/year. Build the Meta campaign, the landing page wireframe, and the HubSpot intake automation.
```
