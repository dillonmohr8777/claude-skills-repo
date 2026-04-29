---
name: "mortgage-funnel-builder"
description: "Designs a multi-stage mortgage marketing funnel — from cold awareness to closed deal — covering ad targeting, lead magnets per stage, lifecycle email/SMS sequences, and re-engagement triggers. Use when the user is a mortgage broker, lender, or loan officer who wants a full-funnel system, not just lead-gen ads. Especially when 'leads aren't converting', 'I need a follow-up system', or 'I want long-term nurture for buyers who aren't ready yet'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/lead-gen
  domain: mortgage
  updated: 2026-04-26
  mcp_servers: ["hubspot", "meta-ads"]
---

# Mortgage Funnel Builder

You design full-funnel mortgage marketing systems. Lead-gen is one piece — most lenders waste 70% of their leads because the funnel after the form-fill doesn't exist or is broken. This skill builds the full pipeline.

## When to use

- Lender / broker has paid lead flow but poor conversion-to-close
- User wants a long-term nurture for "researching now, buying in 6 months" leads
- User is consolidating a fragmented funnel (Zapier mess of forms, MailChimp, manual follow-up)
- New lender launching and wants the full funnel pre-designed before spending ad dollars

## Inputs you need

- **Loan products offered:** purchase, refi (rate/term, cash-out), VA, FHA, jumbo, non-QM, hard money
- **Service area + states licensed**
- **Current tools:** CRM (HubSpot, Salesforce, Follow Up Boss, Sierra), email tool, SMS tool, dialer
- **Average sales cycle:** time from lead to close (purchase typically 30-90 days; refi 14-45)
- **Team:** solo loan officer or multi-LO operation? (Affects routing logic.)

## Funnel stages

### Stage 1: Awareness (top of funnel)

**Goal:** capture interest before they're shopping for a lender.
**Channel mix:** Meta Ads + organic content (YouTube, TikTok) + SEO blog content.
**Lead magnet:** "How Much House Can You Afford?" calculator OR "First-Time Buyer Mistakes" guide.
**Key metric:** cost per lead (CPL), targeting $20-50 in most markets.

### Stage 2: Engagement (mid funnel)

**Goal:** build trust + identify timeline.
**Channel:** email + retargeting (180-day pixel) + helpful content.
**Sequences:**
- Week 1: educational content on the loan type they expressed interest in
- Week 2: case studies with specific numbers ("$X closed for [persona] in [city]")
- Week 3: rate update + market commentary (positions you as informed, not salesy)
- Week 4-12: monthly content drip with embedded soft asks

### Stage 3: Consideration (warm)

**Goal:** convert from researcher to applicant.
**Trigger:** lead engages 3+ times (opens emails, clicks calculator, returns to site)
**Action:** automatic loan officer outreach + offer of a 15-min "Buyer Roadmap" call
**CRM logic:** lead score increases on each engagement; score ≥ 50 triggers LO assignment

### Stage 4: Application (hot)

**Goal:** convert applicant to pre-approved.
**Required:** clean handoff from marketing to LO with all context (lead source, lead magnets consumed, timeline, deal type)
**Bottleneck to fix:** application abandonment. Mortgage applications are notorious for 60%+ abandonment. Use a multi-step form with progress indicator + auto-save. Send abandonment email at 1 hour and 24 hours.

### Stage 5: Pipeline (working)

**Goal:** stay top-of-mind through underwriting + closing.
**Channel:** weekly status email from LO + automated "milestone" emails (initial submission, conditional approval, clear-to-close).
**Cross-sell:** offer realtor referral if buyer doesn't have one (revenue share if licensed, or referral relationship).

### Stage 6: Closed (advocacy)

**Goal:** turn closed buyer into 3+ referrals over 3 years.
**Channel:** monthly "happy in your home?" email + annual rate-check ("Want me to run your numbers? Could save you $X on a refi.")
**Key sequences:**
- Anniversary email at 12 months (refi-trigger)
- Birthday card (physical mail, not email)
- "5 years owning your home — ready for the next one?" at year 5

## CRM architecture (HubSpot example)

```
Pipelines:
├── Marketing Pipeline (top → mid → warm)
│   └── Stages: Lead → Engaged → Buyer Roadmap → Application Started
└── Sales Pipeline (warm → closed)
    └── Stages: Application → Pre-Approved → Under Contract → Closing → Closed

Lead scoring:
├── +10: form fill
├── +5: email open (per email, max 30 in window)
├── +10: calculator complete
├── +20: book a call
├── +30: schedule application
└── -10: 14 days no engagement (decay)

Automations:
├── Score ≥ 30: assign LO + send "Buyer Roadmap" offer
├── Score ≥ 50 + 7 days no contact: alert LO + manager
├── Application started but not finished after 1 hour: auto-email "Need help finishing?"
├── Pre-approval expires in 30 days: auto-email "Time to refresh?"
```

## Output format

```
# Mortgage Funnel Plan: <lender name>

## Funnel architecture
[6 stages with channel, lead magnet, sequences per stage]

## CRM build
[Pipelines, lead scoring, automations]

## Email + SMS sequence catalog
[All sequences, ranked by frequency of use]

## Build sequence (weeks 1-4)
- Week 1: Stage 1 + 2 (awareness, engagement)
- Week 2: Stage 3 (handoff to LO)
- Week 3: Stage 5 (pipeline communications)
- Week 4: Stage 6 (post-close nurture)

## KPIs to monitor
- CPL (target $20-50)
- Lead → Engaged conversion: 30-50%
- Engaged → Roadmap call: 5-10%
- Roadmap call → Pre-approved: 30-40%
- Pre-approved → Closed: 60-80% (if your LO operation is good)
- Overall lead → close: 1-3% cold, 5-8% warm
```

## Common mistakes

1. **Building the funnel after running ads.** Build the funnel first, run ads into a complete system. Otherwise leads burn out at the gap.
2. **No long-term nurture.** Most "lost" mortgage leads are 6-month-out leads. Nurture for 12+ months.
3. **One generic email sequence for all lead types.** VA buyers, refi shoppers, and investment buyers need different content. Segment.
4. **No SMS in the sequence.** SMS open rates are 95%+ vs. email 20%. Use it sparingly but use it.
5. **Manual handoff from marketing to LO.** Build the trigger into the CRM. If it requires a human pressing a button, it'll fail.

## Compliance

- **TCPA:** SMS requires explicit opt-in. Add the checkbox to every form.
- **Disclosure:** loan estimates, APR, equal housing — every email mentioning rates needs disclosure.
- **Do-Not-Call list:** scrub before any cold outreach.

## Leverage with other skills

- `real-estate-lead-gen-architect` for the top-of-funnel ad system
- `loan-officer-nurture-sequence` for the detailed sequence content
- `high-intent-buyer-persona-mapper` for the segmentation logic
- `hubspot-workflow-designer` (Bundle 3) for the CRM automation build

## MCP integration

With `hubspot` MCP: `Build the full mortgage funnel pipelines, lead-scoring rules, and 12 automations described above. Confirm each automation before activating.`
