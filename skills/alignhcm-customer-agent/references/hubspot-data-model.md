# HubSpot Data Model — Align HCM (grounded in the live portal)

Everything here is captured from the real Align HCM portal so the agent doesn't have to rediscover it. Verify against live data before any write; treat the *volumes* below as a point-in-time snapshot and the *structure* (pipelines, stage IDs, property names) as stable.

- **Account:** Align HCM — `accountId 242825734`
- **UI domain:** `app-na2.hubspot.com` (record URLs: `https://app-na2.hubspot.com/contacts/242825734/record/<objectTypeId>/<recordId>`)
- **Timezone:** US/Eastern · **Currency:** USD (secondary CAD) · **Type:** STANDARD

---

## 1. Object availability & permissions

Read/write access for the current user (Dillon Mohr). "Write" capability is present but **held in BUILD mode**.

| Object | Read | Write | Notes |
|--------|:----:|:-----:|-------|
| CONTACT | ✅ | ✅ | Core customer person record |
| COMPANY | ✅ | ✅ | Core customer account record |
| DEAL | ✅ | ✅ | Sales + renewal/change-order motion |
| TICKET | ✅ | ✅ | Support Pipeline |
| NOTE | ✅ | ✅ | Log context on any record |
| TASK | ✅ | ✅ | Follow-ups / to-dos |
| CALL | ✅ | ✅ | Logged calls |
| EMAIL | ✅ | ✅ | 1:1 email engagement |
| MEETING_EVENT | ✅ | ✅ | Meetings |
| LINE_ITEM | ✅ | ✅ | Deal/quote line items |
| PRODUCT | ✅ | ✅ | Catalog |
| LANDING_PAGE | ✅ | ✅ | (Marketing — usually out of customer-agent scope) |
| INVOICE / QUOTE / SUBSCRIPTION / QUOTE_TEMPLATE | ✅ | ❌ | Read-only |
| USER / CAMPAIGN / FORM / OBJECT_LIST | ✅ | ❌ | Read-only |
| MARKETING_EVENT / BLOG_POST / SITE_PAGE | ✅ | ❌ | Read-only |

---

## 2. Tickets — the Support Pipeline

There is a single ticket pipeline: **Support Pipeline** (`hs_pipeline = 0`). The practice is new (only a few live tickets), so the agent should treat consistent triage as part of the value it adds.

**Stages (`hs_pipeline_stage`), in order:**

| Stage | ID | Meaning |
|-------|----|---------|
| New | `1` | Just arrived, untriaged |
| In Progress | `2` | Actively being worked |
| Waiting on Customer | `3` | Blocked pending customer reply |
| Waiting on Internal Team | `3355665129` | Blocked pending internal action |
| Escalated | `3355665130` | Raised beyond first-line |
| Resolved | `3355665131` | Fixed, pending confirmation/close |
| Closed | `4` | Done |

**Category (`hs_ticket_category`):** `PRODUCT_ISSUE` (Product issue) · `BILLING_ISSUE` (Billing issue) · `FEATURE_REQUEST` (Feature request) · `GENERAL_INQUIRY` (General inquiry)

**Priority (`hs_ticket_priority`):** `LOW` · `MEDIUM` · `HIGH` · `URGENT`

**Source (`source_type`):** `CHAT` · `EMAIL` · `FORM` · `PHONE`

**Key ticket properties:** `subject`, `content`, `hs_pipeline`, `hs_pipeline_stage`, `hs_ticket_priority`, `hs_ticket_category`, `source_type`, `hubspot_owner_id`, `createdate`, `hs_lastmodifieddate`, `hs_num_associated_companies`.

---

## 3. Deals — pipelines & stages

Deals are the biggest dataset and are **UKG-dominant**.

| Pipeline | ID | Deals (snapshot) |
|----------|----|------|
| **UKG Sales Pipeline** | `default` | ~1,437 |
| Dayforce Sales Pipeline | `1497621179` | ~34 |
| Paylocity Sales Pipeline | `1534968521` | ~3 |
| Channel Pipeline | `2314068682` | — |
| Test Pipeline | `1254922983` | (ignore — test data) |

**Standard sales stages** (labels shared across the platform pipelines; IDs differ per pipeline — resolve with `get_properties` on `dealstage` when a specific ID is needed):

`Expressing Interest` → `Qualification` → `Proposal/Quote` → `Partner of Choice` → `Contracting` → `Closed Won` / `Closed Lost`

The **Channel Pipeline** opens with `Referral Received` instead of `Expressing Interest`, then follows the same path.

**Deal type (`dealtype`):** `newbusiness` (New Business) · `existingbusiness` (Existing Business) · `Renewal` · `Change Order` · `Subcontract`

> For the customer agent, **`Renewal` and `Change Order` deals on existing customers are the most important signal** — they are the retention/expansion surface. Always include a currency code (`deal_currency_code`) when reading `amount`.

---

## 4. Contacts — lifecycle

| Lifecycle stage | Value | Count (snapshot) |
|-----------------|-------|------|
| Lead | `lead` | ~3,191 |
| Opportunity | `opportunity` | ~494 |
| **Customer** | `customer` | **~312** |
| (Unassigned) | — | ~811 |

Full enum also includes `subscriber`, `marketingqualifiedlead`, `salesqualifiedlead`, `evangelist`, `other`.

**Lead status (`hs_lead_status`):** `NEW`, `OPEN`, `IN_PROGRESS`, `OPEN_DEAL`, `UNQUALIFIED`, `ATTEMPTED_TO_CONTACT`, `CONNECTED`, `BAD_TIMING`.

**Key contact properties:** `firstname`, `lastname`, `email`, `phone`, `jobtitle`, `lifecyclestage`, `hs_lead_status`, `hubspot_owner_id`, `num_associated_deals`, `createdate`, `lastmodifieddate`.

---

## 5. Companies — accounts

| Type | Value | Count (snapshot) |
|------|-------|------|
| (Unassigned) | — | ~2,377 |
| Prospect | `PROSPECT` | ~23 |
| Partner | `PARTNER` | ~1 |

> **Data-hygiene note:** the vast majority of companies have no `type` set. Populating `type` and `lifecyclestage` on customer accounts is a legitimate agent task — but as a **proposed** batch, never an autonomous sweep.

Lifecycle enum matches contacts (`lead` … `customer` … `evangelist`). Industry uses HubSpot's ~150-value standard list (`get_properties companies industry` for the full enum).

**Key company properties:** `name`, `domain`, `website`, `industry`, `type`, `lifecyclestage`, `hubspot_owner_id`, `num_associated_contacts`, `num_associated_deals`.

---

## 6. Associations (how records connect)

- **Contact ↔ Company** — a customer person belongs to a customer account
- **Deal ↔ Company / Contact** — the commercial record; renewals/change-orders hang here
- **Ticket ↔ Company / Contact / Deal** — a support issue in the context of an account
- **Engagements (Note / Task / Call / Email / Meeting) ↔ any record** — the activity timeline

Use `search_crm_objects` with `associatedWith` filters to walk these (e.g., all tickets for company X, all deals for contact Y). See `playbooks.md` for the exact recipes.

---

## 7. Team roster (owners)

Route/attribute only to **active** owners. Confirm live status with `search_owners` before proposing a reassignment.

**Special / functional queues:**
- **SmartCare Advisor** — `162168981` (post-go-live customer work)
- **IT Support** — `160877160` (technical escalations)

**Active people (partial, by ownerId):** Maher El-Abdallah `159562438` · Moe El-Abdallah `159586136` · Menatalla Maher `164938100` · Mike Emsley `80231058` · Allison Cox `159586041` · Dianna Hammond `159586043` · Miranda Sarwan `159586060` · Sarah Poehland `159586133` · Snehal Patel `159586134` · Tammi Hardin `159586135` · Ben Harrison `159865635` · Neno Canji `159952996` · Rich Hennessey `160161008` · Michael Lederman `161751410` · Tosin Adeiga `163930574` · Daniel Sears `165445415` · Kirsten Bieranowski `165445416` · **Dillon Mohr `161749170`** (current user).

Numerous inactive owners exist (historical). Do not assign to them.

---

## 8. Reading data — practical notes

- `query_crm_data` (SQL) is best for **aggregates/counts/trends** — always call `tool_guidance` for `query_crm_data` first in a session, and `search_properties` to confirm internal names before querying.
- `search_crm_objects` is best for **finding records + association walks**; it returns a `total` — always check it so you don't miss data behind pagination.
- `get_crm_objects` (no `properties`) is the fastest way to inspect an unfamiliar record's shape.
- Record identifier is `hs_object_id`. For money, prefer `*_in_home_currency` and include the currency-code property.
