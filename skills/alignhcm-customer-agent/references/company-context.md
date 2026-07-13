# Company Context — Align HCM

Business context the agent needs to interpret the CRM correctly. For SmartCare GTM/pricing/positioning, load `alignhcm-smartcare`. For brand voice/visuals, load `alignhcm-brand`.

---

## Who Align HCM is

Align HCM is an **HCM (Human Capital Management) implementation and managed-services partner**. It helps companies select, implement, and then operate major HCM/payroll platforms. The book of business is platform-centric:

- **UKG** — the primary platform (~1,437 deals, by far the largest pipeline).
- **Dayforce** — secondary (~34 deals).
- **Paylocity** — small (~3 deals).
- **Channel** — partner/referral-sourced deals (opens with `Referral Received`).

The commercial lifecycle: prospect → implementation deal (`Closed Won`) → **go-live** → **post-implementation** (SmartCare) → **renewal / change order**. The customer agent lives in the back half of that arc.

## SmartCare — the customer/retention engine

**SmartCare** is Align HCM's post-implementation managed-services line — the offering that keeps a customer healthy after go-live and drives renewals/expansion. Structure (see `alignhcm-smartcare` for the canonical detail):

- **Maintenance tiers:** Essentials, Accelerate, Transform
- **Managed Services:** Payroll, HRIS, WFM
- **Strategic Advisory**
- Entry motions: free assessment workshop, FTE ROI calculator, Post-Implementation Maturity Assessment
- Proof: Troon, Peco Foods, Burnco/Hammerstone, Humber Meadows, Cavvy Energy case studies

In HubSpot, SmartCare work shows up as: `customer` lifecycle contacts/companies, `Renewal`/`Change Order`/`Existing Business` deals, support tickets, and activity owned by the **SmartCare Advisor** queue (`162168981`).

## Customer base snapshot

- **~312** contacts at `customer` lifecycle stage — the active retention/expansion population.
- **~494** opportunities and **~3,191** leads in flight above them.
- Most **companies are untyped** (~2,377 with no `type`) — a hygiene opportunity, handled only as proposed updates.
- Support ticketing is **new** — a chance to establish clean triage/routing from the start.

## Key people (active owners)

- **Maher El-Abdallah** (`159562438`) — leadership / primary Align HCM contact.
- **Moe El-Abdallah** (`159586136`), **Menatalla Maher** (`164938100`) — leadership / key accounts.
- **SmartCare Advisor** (`162168981`) — functional queue for post-go-live customer work.
- **IT Support** (`160877160`) — technical/support escalations.
- **Dillon Mohr** (`161749170`) — current user; marketing / GTM (owner of this build).
- Plus an active implementation/consulting team (see full roster in `hubspot-data-model.md`).

## How to sound (voice)

Professional, warm, direct, competent. Align HCM is the experienced partner who makes complex HCM platforms manageable — reassuring, never salesy, never over-promising. For any customer-facing copy, pull exact voice/visual tokens from `alignhcm-brand`. (Branding/logo application on any deliverable is handled separately by Dillon.)

## Deliberately out of scope (this phase)

Non-customer company classifications and their special handling rules are **reserved for a later phase** and intentionally excluded from this agent's logic. Keep v1 focused on customers, support, success, and SmartCare onboarding.
