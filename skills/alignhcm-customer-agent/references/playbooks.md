# Playbooks — how the Customer Agent does each job

Four pillars, each a repeatable recipe built on the real MCP tools. In **BUILD mode** every step that changes data stops at a **Proposed Write** (see `tools-and-permissions.md`) — you still *do* all the reading and *draft* the action, you just don't execute it.

Tool shorthand used below (all `mcp__HubSpot__*`): `search` = `search_crm_objects`, `get` = `get_crm_objects`, `sql` = `query_crm_data`, `props` = `get_properties` / `search_properties`, `owners` = `search_owners`, `manage` = `manage_crm_objects` (write — held).

---

## Pillar 1 — Support ticket agent

**Goal:** every ticket is correctly categorized, prioritized, routed, and answered with full customer context.

### 1a. Triage a new ticket
1. **Find the untriaged queue:** `search TICKET` where `hs_pipeline_stage = 1` (New), sort by `createdate` ASC. Check `total`.
2. **Read the ticket:** `get TICKET` for `subject`, `content`, `source_type`, `hs_ticket_category`, `hs_ticket_priority`, `hubspot_owner_id`.
3. **Pull customer context:** from the ticket's associated company/contact, run the **Customer-360** recipe (Pillar 4, lightweight version) so the reply is informed.
4. **Classify:**
   - **Category** → map the ask to `PRODUCT_ISSUE` / `BILLING_ISSUE` / `FEATURE_REQUEST` / `GENERAL_INQUIRY`.
   - **Priority** → use the matrix below.
   - **Route** → owner/queue per the routing rules below.
5. **Propose** the stage move (`New → In Progress`), the category/priority set, the owner assignment, and a first reply or internal note — as one Proposed Write block.

### Priority matrix (default heuristic — tune with Dillon)
| Signal | Priority |
|--------|----------|
| Payroll/production down, compliance deadline, or exec/large-account escalation | `URGENT` |
| Blocking a workflow, billing dispute, missed SLA | `HIGH` |
| Standard question/issue with a workaround | `MEDIUM` |
| Cosmetic, informational, or feature request | `LOW` |

### Routing rules
- **Billing** (`BILLING_ISSUE`) → finance/account owner of the associated company.
- **Technical / product** (`PRODUCT_ISSUE`) → **IT Support** (`160877160`) or the platform consultant for that customer's stack (UKG/Dayforce/Paylocity).
- **Post-go-live / managed-services** questions → **SmartCare Advisor** (`162168981`).
- **Feature request** → log, tag, and route to the product/consulting lead; set expectations, don't promise.
- If the associated company already has an active `hubspot_owner_id`, prefer keeping continuity with that owner.

### 1b. Stage hygiene / follow-ups
- Tickets in **Waiting on Customer** (`3`) with no activity in N days → propose a follow-up TASK or nudge.
- Tickets in **Waiting on Internal Team** (`3355665129`) → propose a TASK for the internal owner.
- **Escalated** (`3355665130`) → summarize for leadership; never let it sit silently.
- **Resolved** (`3355665131`) → propose a confirmation message before moving to **Closed** (`4`).

### 1c. Draft a reply
- Use the reply template in `assets/templates.md`.
- Tone: professional, warm, concise — Align HCM voice (see `alignhcm-brand` for voice tokens if writing customer-facing copy).
- Ground every claim in the record. Never invent a resolution, timeline, or credit.
- Output as a **Proposed Write** (email/note) — do not send.

---

## Pillar 2 — Customer success / churn & renewal

**Goal:** know which of the ~312 customers are healthy, which are at risk, and where expansion is real — from live HubSpot signals.

### 2a. Signals available in HubSpot
| Dimension | HubSpot signal |
|-----------|----------------|
| Engagement | Recent activity: notes, calls, emails, meetings on the account; last-modified dates |
| Support health | Open ticket count, escalations, `Waiting on Customer` age, category mix |
| Commercial | `Renewal` / `Change Order` deals, their stage & `closedate`, deal `amount` |
| Relationship | Active `hubspot_owner_id`, multi-threading (`num_associated_contacts`) |
| Lifecycle | `lifecyclestage = customer`, tenure via `createdate` |

### 2b. Health read (lightweight, deterministic)
1. `search CONTACT`/`COMPANY` where `lifecyclestage = customer` (association-walk to the account).
2. For each account, gather: open tickets (`search TICKET` associatedWith company, stage not in Resolved/Closed), last engagement date, open renewal/change-order deals.
3. Classify **Green / Yellow / Red** using the heuristic:
   - **Red:** open `URGENT`/`Escalated` ticket, OR renewal deal slipping/past `closedate`, OR no engagement in 90+ days.
   - **Yellow:** aging `Waiting on Customer` ticket, OR renewal within 90 days not yet in `Contracting`, OR thin multi-threading (1 contact).
   - **Green:** none of the above; recent positive engagement.
4. For portfolio-scale scoring, hand the assembled per-account JSON to the **`customer-success-manager`** skill's Python tools (health / churn / expansion) — that's the deeper, weighted model. This agent's job is to *feed it live data* instead of manual exports.

### 2c. Renewal watch
- `sql`: `SELECT dealstage, COUNT(*) FROM DEAL WHERE dealtype = 'Renewal' GROUP BY dealstage` for the pipeline view.
- Flag renewals with `closedate` inside 90 days not yet at `Contracting`/`Closed Won`.
- Propose: a TASK for the account owner, a check-in NOTE, or a heads-up summary — never auto-touch the deal.

### 2d. Expansion
- Look for customers with a single product/stack, growing headcount, or `Change Order` history → candidate for cross-sell (e.g., additional modules or a SmartCare tier upgrade).
- Output as ranked opportunities with the *why*, not a hard promise.

---

## Pillar 3 — SmartCare onboarding (post-go-live)

**Goal:** every customer that moves into SmartCare / post-implementation is tracked, and nothing stalls.

1. **Load context:** invoke `alignhcm-smartcare` for tiers (Essentials / Accelerate / Transform), Managed Services (Payroll / HRIS / WFM), and Strategic Advisory positioning.
2. **Identify the cohort:** customers recently `Closed Won` on an implementation deal, or explicitly flagged for SmartCare. Association-walk deal → company → contacts.
3. **Track status** per account: onboarding stage, assigned **SmartCare Advisor** (`162168981`), open tasks, next milestone, and any open tickets.
4. **Watch for stalls:** no activity, missed milestone, or an open issue with no owner → propose the next action (TASK / NOTE / check-in).
5. **Report** with the onboarding-status template in `assets/templates.md`.

> SmartCare is the retention engine — a healthy post-go-live experience is what turns a `Closed Won` into a `Renewal`. Treat Pillar 3 and Pillar 2 as two halves of the same loop.

---

## Pillar 4 — Customer-360

**Goal:** "tell me everything about this customer" → one clean, accurate brief.

### Assembly recipe
1. **Resolve the entity.** `search CONTACT`/`COMPANY` by name/email/domain. If multiple match, list them and ask which.
2. **Company core:** `get COMPANY` → name, domain, industry, type, lifecycle, owner, `num_associated_contacts`, `num_associated_deals`.
3. **People:** `search CONTACT` associatedWith the company → names, titles, emails, owners. Note the primary contact and multi-threading depth.
4. **Commercial:** `search DEAL` associatedWith the company → open deals (stage, amount+currency, closedate), plus renewal/change-order history.
5. **Support:** `search TICKET` associatedWith the company → open vs. closed, priorities, categories.
6. **Activity:** most recent notes/calls/emails/meetings for recency and sentiment.
7. **Assemble** with the customer-360 brief template. Include a one-line **health read** (Pillar 2) and any **next best action**.

### Quality bar
- Every fact traces to a record; link with the NA2 URL pattern.
- If a section is empty (no deals, no tickets), say "none found," don't omit silently.
- Lead with the answer to what was actually asked; the full brief supports it.

---

## Cross-pillar principles

- **Find → fetch → assemble → propose.** Never skip to a write.
- **Check `total`.** Don't reason from a truncated page.
- **Confirm owners live.** Rosters drift; `search_owners` before proposing assignment.
- **One account at a time for actions.** Portfolio *reads* can be bulk; *writes* are per-record and proposed.
