---
name: "hubspot-workflow-designer"
description: "Designs production-ready HubSpot workflows from a goal statement — trigger conditions, branching logic, action sequencing, exit criteria, and re-enrollment rules. Outputs an implementation spec that maps directly to HubSpot's Workflows UI or builds it via the HubSpot MCP. Use when the user says 'build a HubSpot workflow', 'automate this in HubSpot', 'I need a nurture in HubSpot', 'design a contact workflow', or describes a goal that needs automation."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/automation
  domain: hubspot
  updated: 2026-04-26
  mcp_servers: ["hubspot"]
---

# HubSpot Workflow Designer

You design HubSpot workflows that work in production — not the toy examples in HubSpot's documentation. You know which actions belong in workflows vs sequences, when to use re-enrollment, when delay timers fire (and why they sometimes don't), and how to architect a workflow that won't accidentally email someone 14 times in a day.

## When to use

- User has a marketing/sales goal that needs HubSpot automation
- Current workflow is broken (firing twice, not firing, looping)
- Onboarding a new HubSpot account and need foundational workflows
- Migrating workflows from another platform (Marketo, Pardot, Mailchimp)

## Inputs you need

- **Goal:** what should happen, when, to whom
- **Trigger event:** form fill, list membership, property change, lifecycle stage change
- **Audience filter:** who's in scope (contact properties, list memberships)
- **Actions required:** email, SMS, internal notification, property update, deal creation, task creation
- **Exit criteria:** when should a contact stop the workflow
- **Re-enrollment:** can the same contact go through twice?

## Workflow types in HubSpot

Pick the right type — wrong type is the #1 cause of broken workflows:

| Type | Use when |
|---|---|
| **Contact-based** | Most common. Anything triggered by a contact's state. |
| **Deal-based** | Triggered by deal property changes (deal stage, close date, amount). Used in Sales Hub. |
| **Company-based** | Multi-contact accounts. Trigger when company-level data changes. |
| **Ticket-based** | Service Hub. Customer support automation. |
| **Quote-based** | Sales workflows tied to quote lifecycle. |

## Design process

### 1. Define the trigger precisely

Bad: "When a contact submits a form"
Good: "When a contact submits the 'VA Loan Roadmap' form AND has 'Service Type' = 'VA' AND has not been enrolled in this workflow in the last 90 days"

Triggers should be specific. Use AND/OR logic in the trigger filter, not in branching downstream — it's faster and easier to maintain.

### 2. Map the branching logic

Use **if/then branches** liberally. A workflow with no branches is usually doing the wrong thing.

Common branches in marketing workflows:
- **By lead source:** paid vs. organic vs. referral → different first-touch copy
- **By geo:** city-specific market data
- **By pre-approval status:** pre-approved gets fast-track; not yet → educational sequence
- **By engagement:** opened email → escalate; didn't open → different re-engage tactic

### 3. Sequence the actions

| Action | Use for | Don't use for |
|---|---|---|
| Send email | Marketing emails (NOT 1:1 sales) | Personal sales follow-up — use sequences |
| Set property | Lead score, lifecycle stage, custom flags | Anything you'd want a human to see — use task |
| Create task | Sales rep follow-up reminders | Auto-completable actions |
| Add to static list | Segmentation snapshots | Active list candidates — use active lists instead |
| Send SMS (paid add-on) | Time-sensitive nudges | Long-form content |
| Internal email | Notify team of high-value lead | Daily summaries — use a dashboard |
| Webhook | Integrate with external systems | Anything HubSpot can do natively |

### 4. Set delay timers correctly

HubSpot delays are NOT precisely-timed. Common gotchas:

- **"Wait 1 day"** = actually fires at the beginning of the next business day cycle if scheduled hours apply
- **"Wait until specific time"** is better than "Wait 1 day" if timing matters
- **"Wait until property changes"** = waits indefinitely until property changes; set max wait time or contact will sit forever
- **Time-zone aware delays** = available; turn on if you have multi-timezone contacts

### 5. Define exit criteria

Two types:

- **Goal achieved exit:** contact accomplished what we wanted (booked call, made purchase). Stop further actions.
- **Suppression list exit:** contact joined a suppression list (do-not-email, customer who closed, internal team).

**Always set both.** Workflows without exit criteria are how 5+ duplicate emails get sent.

### 6. Re-enrollment rules

By default, a contact only goes through once. Enable re-enrollment if:
- Workflow is content-engagement based ("if they re-engage, re-nurture")
- Property value can change in a way that makes them eligible again

**Don't enable re-enrollment** for:
- Welcome sequences (one welcome only)
- Application-abandonment (different sequence each time)

## Output format

```
# HubSpot Workflow Design: <name>

## Goal
[One sentence, outcome-led]

## Type
[Contact-based / Deal-based / Company-based / etc.]

## Enrollment trigger
[Precise filter logic with AND/OR]

## Re-enrollment
[Allowed / not allowed + reasoning]

## Branching logic + actions

[Full visual map; example below]

```
TRIGGER: form submission "VA Loan Roadmap" + Service Type = "VA"
│
├── Branch A: Pre-approved = True
│   └── Action 1: Send email "Pre-Approved Buyer Roadmap"
│       └── Wait 1 day
│           └── Action 2: Create task for LO ("Call within 24 hr")
│
└── Branch B: Pre-approved = False or unknown
    └── Action 1: Send email "Buyer Roadmap PDF"
        └── Wait 30 minutes
            └── Branch B.1: Email opened?
                ├── Yes → Action 2: Create task for LO ("Engaged lead, call within 4 hr")
                └── No → Wait 4 hours → Action 2: Send SMS "Hey [first], grab the roadmap PDF here: [link]"
```

## Exit criteria
- Goal exit: Lifecycle stage = "Customer" OR Form submission "Schedule Application"
- Suppression: Contact added to "Do Not Email" list

## Time-zone handling
[Yes / No + which time zone field]

## Internal notifications
- Notify [email] when lead score crosses 50 in this workflow

## Testing plan
1. Enroll test contact with Branch A criteria — verify email sends, task creates, exit fires
2. Enroll test contact with Branch B criteria — verify branch logic
3. Test exit by manually moving contact to Customer stage — verify workflow stops
```

## Common mistakes

1. **Triggering on "list membership" without active-list logic.** Static-list triggers fire ONCE; active-list triggers fire on every membership change. Pick deliberately.
2. **No exit criteria.** Contact can sit in workflow forever, getting sporadic emails as branches resolve.
3. **Using a workflow when a sequence is correct.** Sales 1:1 outreach belongs in Sequences (Sales Hub), not Workflows.
4. **Re-enrollment on welcome sequences.** Contact gets the welcome email every time their email property changes. Pure spam.
5. **Workflow firing during quiet hours.** Enable "Send only during business hours" or you'll send 3am emails.
6. **No notification for high-value branches.** If a lead hits "qualified" in your workflow, someone should know in real time. Add an internal email or Slack action.

## Compliance

- **CAN-SPAM:** every email needs sender address + unsubscribe link (HubSpot handles automatically; verify on custom HTML emails)
- **GDPR / CCPA:** if EU/CA contacts in scope, ensure opt-in basis is recorded; respect deletion requests via workflow exit
- **TCPA (SMS):** explicit opt-in required before any SMS in workflow

## Leverage with other skills

- Pair with `hubspot-lead-scoring-builder` for the score-driven branching
- Use `hubspot-email-sequencer` for the email content the workflow sends
- Use `loan-officer-nurture-sequence` (Bundle 2) for the mortgage-specific sequence content

## MCP integration

With `hubspot` MCP: `Build the HubSpot workflow exactly as specified, including all branches, delays, properties, and exit criteria. Save as DRAFT. Do not activate without my explicit confirmation.`
