---
name: "hubspot-email-sequencer"
description: "Authors full email-sequence content for HubSpot Sequences (sales 1:1) and HubSpot Marketing Workflows (marketing 1:many) — subject lines, preview text, body copy, merge tags, branching by engagement, and A/B variants. Use when 'write me a HubSpot sequence', 'I need 5 cold emails', 'design a nurture in HubSpot', 'rewrite my email sequence', or 'sales sequences aren't working'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/email
  domain: hubspot
  updated: 2026-04-26
  mcp_servers: ["hubspot"]
---

# HubSpot Email Sequencer

You write email sequences that get replied to — not sequences that just send. The difference is subject lines, opening lines, and the brutal cut of anything that doesn't earn its place.

## When to use

- Sales team has Sequences that don't get replies
- Marketing nurture has low click-through rates
- New lead-gen campaign needs a 5–7 email follow-up
- Cold outreach sequence needs rewriting

## Inputs you need

- **Use case:** sales (1:1 from rep) vs marketing (1:many from list)
- **Audience:** specific persona, pain, role
- **Goal:** book a meeting, drive a download, re-engage cold leads
- **Sender voice:** rep's actual voice (paste sample emails) or brand voice
- **Subject-line constraint:** must include / must exclude (compliance, spam triggers)
- **Length:** how many emails in the sequence

## Sales sequences vs Marketing emails

| Dimension | Sales Sequence | Marketing Workflow Email |
|---|---|---|
| From | Individual rep | Brand or named persona |
| Tone | Conversational, 1:1 | Branded, scalable |
| Length | Short (50-150 words) | Medium (150-400 words) |
| Subject | Plain, conversational | Optimized for open rate |
| CTA | Specific ask (book / reply / call) | Click to content / page |
| Personalization | Manual + merge tags | Merge tags + segmentation |
| Reply expectation | High | Low |

Don't mix them up. A "marketing-style" sales sequence kills reply rates by 60%.

## Subject-line patterns that work

For **sales** (focus: open + reply):

- **Question:** "Worth 5 minutes on [their initiative]?"
- **Curiosity:** "Quick thought on [their company's recent move]"
- **Internal-style:** "re: [topic from prior email]" (only if there was a prior email — never fake this)
- **Specific:** "[Their company] + 3.2x conversion lift?"
- **Plain:** "Hey [first]" (counterintuitively high open + reply)

For **marketing** (focus: open + click):

- **Outcome-led:** "How [persona] save 8 hours/week with [tool]"
- **Number-led:** "5 mistakes killing your [metric]"
- **Question + curiosity:** "Are you making this $X mistake?"
- **News:** "Just released: [thing]"
- **Brevity:** "↓" or "thoughts?" (when appropriate to brand voice)

**Avoid:** ALL CAPS, urgency theater ("Last chance!!!"), spam-trigger words ("free", "guaranteed", "% off"), emoji unless brand-appropriate.

## Opening line patterns

The opening line is what decides if email gets read past the preview. Spam openers ("Hope this finds you well") fail.

For sales:
- **Specific observation:** "Saw your team hired 3 BDRs last month — congrats. That's why I'm reaching out."
- **Direct ask:** "I'll be brief: would 15 minutes next week be valuable?"
- **Permission:** "Quick question, then I'll get out of your way."

For marketing:
- **Outcome statement:** "Most [persona] lose [X hours] / week to [pain]. Here's how 3 of our customers fixed it."
- **Story setup:** "Last month, a customer named Jane closed $480K from a single sequence."

## Body copy rules

- One idea per email. If you have two, send two emails.
- Cut everything that doesn't move the reader toward the goal.
- White space matters. Short paragraphs.
- ONE call to action per email. Two CTAs = zero CTAs.

## Branching by engagement (HubSpot specific)

In sales Sequences, you can't branch (sequences are linear). You manually exit on reply.

In marketing Workflows, branch:

- Email opened → continue sequence on schedule
- Email NOT opened → resend with different subject 24-48 hours later
- Email clicked → escalate priority (lead score increase, internal alert)
- Email replied → exit sequence (handoff to sales)
- Email bounced (hard) → suppress + alert team

## Output format

```
# Email Sequence: <name>

## Use case
[Sales 1:1 / Marketing 1:many]

## Audience
[Persona, pain, goal]

## Sequence overview
- # of emails: N
- Cadence: [Day 0, +2, +5, +9, +14]
- Goal: [book meeting / download / etc.]
- Exit triggers: [reply / click target page / time-out]

## Email 1 — Day 0
**Subject A:** [...]
**Subject B (variant):** [...]
**Preview text:** [...]

[Body — under 150 words for sales, 250-400 for marketing]

**CTA:** [single, specific]
**Merge tags used:** [{first_name}, {company}, {custom_property_X}]

## Email 2 — Day +2
[...same structure]

## Email 3-N
[...]

## A/B test plan
- A/B subject lines on emails 1 and 4 (highest open-rate impact)
- Sample size: 200 sends per variant
- Win criterion: +25% open rate AND +10% reply rate

## Compliance check
- [ ] Sender info populated
- [ ] Unsubscribe link in marketing emails
- [ ] No spam-trigger words in subjects
- [ ] Quiet hours enabled (if SMS-adjacent)
```

## Common mistakes

1. **Sales sequences that read as marketing.** Branded, polished, generic = no reply.
2. **Marketing emails that read as 1:1.** "Hey Sarah" from "the team" feels fake.
3. **Multiple CTAs per email.** Pick one.
4. **Subject lines that promise too much.** "Open this for $1M secret" = unsubscribe spike.
5. **No merge-tag fallbacks.** When `{first_name}` is empty, email opens "Hey ,". Always set fallback ("Hey there").
6. **Sending on Friday afternoon or Sunday.** Open rates drop 30%. Schedule Tue-Thu morning.
7. **No exit on reply.** Rep gets a "yes" and the sequence keeps emailing them. Reputation damage.

## Compliance

- **CAN-SPAM:** unsubscribe + sender address required on marketing emails (HubSpot handles automatically)
- **GDPR / CCPA:** opt-in basis recorded; respect right to be forgotten
- **Industry-specific:** mortgage rate quotes need APR disclosures; financial advisory needs FINRA-compliant language

## Leverage with other skills

- Pair with `hubspot-workflow-designer` for the full automation that wraps the sequence
- Use `loan-officer-nurture-sequence` (Bundle 2) for mortgage-specific sequence content
- Run with `cold-email-sequence-builder` if equivalent — wait, that's not in this catalog yet; this skill covers cold-outbound use cases too

## MCP integration

With `hubspot` MCP: `Build the email sequence as specified above, save all emails as drafts, set up A/B variant testing on emails 1 and 4, and configure exit triggers. Do not activate without my confirmation.`

For sales sequences, also configure:
- Step types: email + LinkedIn touch + call task as appropriate
- Auto-pause on out-of-office reply
- Stop-sequence-on-meeting-booked
