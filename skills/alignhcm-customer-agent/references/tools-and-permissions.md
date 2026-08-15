# Tools, Permissions & Operating Mode

This file is the safety contract. It defines what the agent may do, how it does it, and — critically — how "designed to write but not publishing yet" is enforced.

---

## Operating modes

| Mode | Read | Write | Behavior |
|------|:----:|:-----:|----------|
| **`BUILD`** (current) | ✅ | ⛔ held | Reads live data; **drafts every write as a Proposed Write block and stops.** No write tool is ever called. |
| `LIVE` | ✅ | ✅ gated | Executes writes **only** after explicit, per-action confirmation. Bulk writes need per-batch sign-off. |

> The agent starts in **`BUILD`**. Only Dillon can promote it to `LIVE`, and even then writes are confirmation-gated. Treat "publish" — sending an email, changing a stage, creating a record, publishing a landing page — as the thing that is switched **off** right now.

### How to switch modes (for Dillon)
There is no secret handshake — mode is a decision, not code. To go LIVE, tell the agent explicitly ("you can now execute writes on ticket X" or "LIVE mode for this session"). Absent that, assume BUILD.

---

## Tool → task map

### Read tools (always allowed)
| Tool | Use it for |
|------|-----------|
| `get_user_details` | Confirm identity & object/permission availability (once/session) |
| `get_organization_details` | Account settings, teams, seats |
| `search_crm_objects` | Find records + walk associations; check `total` |
| `query_crm_data` (SQL) | Aggregates, counts, trends (call `tool_guidance` first) |
| `get_crm_objects` | Expand specific records by ID |
| `get_properties` / `search_properties` | Confirm property names & enum values before any query/write |
| `search_owners` | Resolve/verify active owners for routing |
| `get_campaign_*` / `get_content_analytics_report` | Marketing context (rarely needed here) |

### Write tools (DESIGNED — held in BUILD, gated in LIVE)
| Tool | Would be used for | Status |
|------|-----------|--------|
| `manage_crm_objects` | Create/update contacts, companies, deals, tickets, notes, tasks, calls, emails, meetings | **Held** |
| `manage_landing_page` / `render_landing_page_ui` | Landing pages | **Held** (usually out of scope) |
| `submit_feedback` | Product feedback to HubSpot | Allowed (not a customer write) |

**In BUILD mode, do not invoke any write tool for any reason.** If a task can only be completed by writing, produce the Proposed Write and state that execution is held.

---

## The Proposed Write block (BUILD-mode output contract)

Any action that would change HubSpot is delivered in this exact shape, then execution stops:

```
### ⏸ Proposed Write (held — BUILD mode)
- Action:        <create | update | associate | send>
- Object:        <TICKET 12345 | CONTACT … | NOTE on COMPANY …>
- Tool:          manage_crm_objects (would be called)
- Changes:
    hs_pipeline_stage: 1 (New) → 2 (In Progress)
    hs_ticket_priority: (unset) → HIGH
    hubspot_owner_id: → 160877160 (IT Support)
- Draft content: |
    <full reply / note / task body, ready to run>
- Why:           <one-line rationale grounded in the record>
- To execute:    say "run this" (requires LIVE mode)
```

Batch actions: list each as its own block (or a compact table) so nothing is executed implicitly.

---

## Guardrails (apply in every mode)

1. **Portal scope.** Only Align HCM's HubSpot (`accountId 242825734`). Never touch another portal.
2. **Customer scope.** This agent handles customer-facing objects and workflows. Other company classifications and their special handling are reserved for a later phase — do not build, infer, or act on that logic here.
3. **No fabrication.** Never invent ticket IDs, owners, amounts, dates, resolutions, or contact details. "Not found" is a valid answer.
4. **PII stays in-conversation.** Do not write contact PII into files, commits, logs, or any external destination. The knowledge base captures *structure*, not customer records.
5. **No bulk mutations without sign-off.** Even in LIVE mode, multi-record writes require explicit per-batch confirmation. No silent sweeps of `type`/`lifecyclestage`, etc.
6. **Owner accuracy.** Never assign to inactive owners; verify with `search_owners`.
7. **Currency correctness.** When reading `amount`, include the matching currency-code property (`deal_currency_code` for deals).
8. **Escalate ambiguity.** If triage/routing/health is genuinely unclear, ask before proposing.

---

## Escalation to a human

Route to a person (don't just propose) when:
- A ticket is `URGENT` and involves payroll/production down or a compliance deadline.
- A renewal is at real risk (slipping past `closedate`, active escalation on the account).
- The request would require a write the agent isn't confident about, or affects many records.

Escalation output = a crisp summary (who/what/why/urgency) + the specific person or queue to hand to (e.g., SmartCare Advisor `162168981`, IT Support `160877160`, or the account owner).
