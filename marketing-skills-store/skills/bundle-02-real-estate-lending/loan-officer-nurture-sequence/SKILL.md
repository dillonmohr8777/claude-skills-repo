---
name: "loan-officer-nurture-sequence"
description: "Builds full email + SMS nurture sequences for mortgage leads — pre-application, application-in-progress, post-close, and 12-month long-term — with copy, send-time logic, segmentation, and abandonment recovery. Use when the user is a loan officer, mortgage broker, or lender who is losing leads to slow follow-up, has no nurture system, or needs to systematize their existing one."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/lead-gen
  domain: mortgage
  updated: 2026-04-26
  mcp_servers: ["hubspot"]
---

# Loan Officer Nurture Sequence

You build the email + SMS sequences that keep mortgage leads warm — from form-fill to closed deal to 5-year refi-trigger. The single highest-leverage lever for any LO operation.

The receipt: Secure Lending's $1.7M / $5,400 ad spend depended as much on the post-form-fill nurture as the ads. 50%+ of closes came from leads on day 3-7, not day 1.

## When to use

- LO has paid leads but slow conversion
- New LO operation needs nurture sequences pre-built before launching ads
- Existing CRM has fragmented sequences; user wants to consolidate
- Long-term re-engagement for 6+ month-old leads

## Sequence catalog

### Sequence 1: 7-Day Speed-to-Lead

**Trigger:** form fill (any source)
**Goal:** book a 15-min Buyer Roadmap call
**Cadence:**

| When | Channel | Purpose | Sample copy |
|---|---|---|---|
| 0 min | Auto-text | Pattern interrupt | "Hey [first], it's [LO] — got your request. Free at [time today]?" |
| 5 min | Live call attempt #1 | Speed = trust | (LO calls personally) |
| 30 min | Email | Send promised deliverable | "Here's your [Buyer Roadmap]. PS — I have an opening at 2pm tomorrow if you want to talk through your numbers." |
| Day 1, 9am | Email | Story-led value | "Quick story: [client] thought they couldn't afford a home. Here's what changed." |
| Day 1, 4pm | Live call attempt #2 | Voicemail with specific value | "Saw two homes hit the market in [city] at your price range — wanted to flag." |
| Day 2 | Email | Objection handle (credit) | "If your credit isn't perfect, we still have options. Quick read." |
| Day 3 | Email | Case study with specific numbers | "[Name] closed on $X home, $Y down. Here's the timeline." |
| Day 4 | SMS | Soft check-in | "Hey [first] — still good for a 15-min call about your [city] options?" |
| Day 5 | Skip | Avoid fatigue | — |
| Day 6 | Email | Urgency (rates, market) | "Rates moved 0.25% this week. Here's what it means for [city]." |
| Day 7 | Final SMS | "Close the file" pattern | "Last text from me — should I close your file or keep an eye out?" |

**Re-engagement rate from "close the file" text: 8-12%.** Don't skip it.

### Sequence 2: Application Abandonment Recovery

**Trigger:** application started but not submitted in 1 hour
**Goal:** recover the application

| When | Channel | Sample copy |
|---|---|---|
| 1 hour | Auto-email | "Need help finishing your app? Most people get stuck on [common field]. Reply with the question and I'll walk you through it." |
| 4 hours | SMS | "Saw you started the app. What's holding you up? — [LO name]" |
| Day 1 | Live call | "Hey [first], saw you started the app yesterday. Want to finish it together over the phone? I can do it in 10 min." |
| Day 3 | Email | Different angle: "Some people change their mind after seeing the rate. Here's how rates work in plain English." |
| Day 7 | Email | Soft re-engage with content (e.g. "5 home types that move fastest in [city]") |

**Recovery rate when this sequence is active: 25-40% of abandoned apps complete.**

### Sequence 3: Active File (during underwriting)

**Trigger:** file moved to "Application Submitted" stage
**Goal:** keep buyer engaged + reduce stress

| When | Channel | Sample copy |
|---|---|---|
| Day 1 | Email from LO | "Here's what happens next: [3-step underwriting timeline]. I'll text you at every milestone." |
| Day 3 | SMS | "Update: docs received, in underwriting review." |
| Day 7 | Email | "What to NOT do during underwriting: don't open new credit, don't change jobs, don't move money." |
| Day 14 | SMS milestone | "Conditional approval — congrats! 2 small items needed: [item1, item2]." |
| Day 21 | SMS milestone | "Clear to close — congrats! Closing scheduled for [date]." |
| Day before closing | SMS | "Tomorrow's the day. Bring [docs]. Closing at [time, location]." |

### Sequence 4: Post-Close Advocacy (year 1)

**Trigger:** loan funded
**Goal:** referral capture + 12-month relationship

| When | Channel | Sample copy |
|---|---|---|
| Day 0 (closing day) | Physical card | Handwritten thank-you sent same day |
| Week 1 | Email | "Settling in? Here's a quick guide to your first 30 days as a homeowner." |
| Month 1 | SMS | "How's the new place treating you?" |
| Month 3 | Email | "Quarterly check-in — anything you wish you'd known about your loan?" |
| Month 6 | Email | "Refi market check: rates have moved [X]. Here's what it means for you." |
| Month 9 | Email | "If you know anyone shopping for a home, I'd love an intro. Here's how the referral process works." |
| Month 12 | Physical card | Anniversary card (drives review requests) |

### Sequence 5: Long-Term (year 2+)

**Trigger:** 12 months post-close
**Cadence:** monthly content email + annual rate-check + birthday card

**Monthly email content rotation:**
- Local market update (specific to their city)
- Refi-trigger ("if rates drop to X, here's your savings")
- Home-improvement / equity content
- Investment property "did you know" content
- Tax-time content (Q1)

**Annual rate-check at 12, 24, 36, 48, 60 months post-close:**
"Hey [first] — annual rate check. Current rates are [X] vs your [Y]. Save you ~$[Z]/month if we refi'd. Want me to run the numbers?"

This single email recovers more refi business than any other touch.

## Output format

```
# Nurture Sequence Build: <LO / brokerage name>

## Sequences to build (ranked by priority)
1. 7-Day Speed-to-Lead (HIGHEST priority — affects all paid leads)
2. Application Abandonment Recovery
3. Active File / Underwriting
4. Post-Close Year 1
5. Long-Term

## Per-sequence build spec
[Full cadence, channel, copy, send-time logic per sequence above]

## CRM automations required
[Triggers, conditions, exit criteria for each]

## Segmentation
- Loan type: VA / FHA / conventional / refi → different content per
- First-time buyer vs. repeat → different objections
- Geo: city-specific market data plug-ins

## Compliance
- TCPA: SMS opt-in checkbox required on every form
- Quiet hours: SMS only 9am-8pm in recipient's timezone
- Disclosure: rate-quote emails need APR + "subject to change"

## Build sequence (4-week implementation)
- Week 1: Sequences 1 + 2 (speed-to-lead + abandonment) — biggest revenue impact
- Week 2: Sequence 3 (active file) — reduces cancellation rate
- Week 3: Sequence 4 (post-close) — drives reviews + referrals
- Week 4: Sequence 5 (long-term) — refi engine

## KPIs to track
- Speed-to-lead: lead-to-roadmap-call conversion (target 5-10%)
- Abandonment recovery: app-completion lift (target +25%)
- Active file: cancellation rate (target < 5%)
- Post-close: referral rate (target 0.5+ per closed loan in year 1)
- Long-term: refi reactivation (target 5%+ annual)
```

## Common mistakes

1. **Email-only nurture.** Email opens are 20%; SMS opens are 95%. Use both.
2. **Same sequence for VA and conventional.** Veterans care about $0-down + funding fee; conventional buyers care about PMI + DTI. Segment.
3. **Stopping at day 7.** Most "lost" leads convert at day 30-90. Long-term content nurture is critical.
4. **No "close the file" message.** This single SMS at day 7 drives 8-12% re-engagement.
5. **Sending rate quotes in email without disclosure.** APR + "subject to change" is required by federal law on every rate mention.
6. **Forgetting the physical card.** A $2 card at closing day drives more reviews than a $200 ad spend.

## Compliance (mortgage / TCPA)

- **TCPA:** explicit SMS opt-in required. Use checkbox on every lead form.
- **Quiet hours:** SMS 9am-8pm recipient's local time. Most CRMs handle automatically; double-check.
- **DNC:** scrub against state + federal Do Not Call lists for any cold outreach.
- **Rate disclosures:** APR + "rates subject to change" on every email mentioning rates.
- **Equal Housing language:** include in every email footer.

## Leverage with other skills

- `mortgage-funnel-builder` for the funnel-stage architecture these sequences slot into
- `hubspot-workflow-designer` (Bundle 3) for the actual CRM build
- `hubspot-email-sequencer` (Bundle 3) for the email-template authoring

## MCP integration

With `hubspot` MCP: `Build all 5 nurture sequences as HubSpot workflows, with the email and SMS templates filled in, segmentation by loan type, and TCPA-compliant opt-in handling. Confirm each workflow before activating.`
