# Customer-Facing Chatbot — Deployment & Readiness Runbook

The "Align HCM Customer Agent" has **two faces**. Keep them straight:

| | Internal operator (this skill) | Customer-facing chatbot |
|---|---|---|
| Where | Claude + HubSpot MCP (CRM tools) | HubSpot chatflow / website live chat, portal `242825734` |
| Job | Support triage, health/renewal, SmartCare tracking, customer-360 (see `playbooks.md`) | Answer public visitor questions from public Align pages; capture email; hand off to a human |
| Data | Live CRM (read; write held in BUILD) | Public Align website pages only — **no CRM/private data** |
| Governed by | `tools-and-permissions.md` + `brand-partner-safety.md` | `assets/customer-facing-guidelines.txt` + `brand-partner-safety.md` |

Both share the same brand/partner-safety rules. This file is the runbook for the **customer-facing chatbot** — the piece the readiness report holds at **DO NOT ACTIVATE**.

---

## Current decision (2026-07-23): LAUNCH HOLD

The chatbot is **safe by design but not ready for a live channel**. Disciplined refusal passes; positive public-answer quality is below the bar, and the newest partner-safety gate must pass on the applied guidelines. Full evidence: `dillon-os:handoffs/align-hcm-customer-agent/customer-agent-readiness-report.pdf`.

### Launch-readiness gates (from the readiness report)

| Gate | Status | Owner of the fix |
|------|:---:|---|
| Portal & agent identity verified | ✅ PASS | — |
| Privacy & prompt-injection boundary | ✅ PASS | — |
| Claims / guarantee / legal / hallucination boundary | ✅ PASS | — |
| Handoff configuration preflight | ✅ PASS | — |
| Core public-knowledge answers (5) | ❌ FAIL | HubSpot: source repair + retest |
| Direct source links | ❌ FAIL | HubSpot: source sync + citation requirement |
| Single consistent greeting | ❌ FAIL | HubSpot: chatflow greeting settings |
| Partner-safety / named-company gate | ⏸ apply + retest | Apply `customer-facing-guidelines.txt`, run Gate 5 |
| Approved custom avatar | ⏸ PENDING | Brand approval + upload (see `alignhcm-brand`) |
| End-to-end handoff ticket | ⏸ PENDING | Side-effecting test w/ disposable identity |
| Live-chat channel activation | ⛔ NOT ACTIVATED | **Separate human approval — held** |

---

## Exact path to ready (ordered)

Each step maps to a readiness-report action. Steps marked **[HubSpot UI]** happen in the portal and are outside this skill's tool reach; steps marked **[repo]** are done and version-controlled here.

1. **[repo] Apply the corrected guidelines.** Paste `assets/customer-facing-guidelines.txt` (2,306 chars, includes the Brand & Partner Safety block) into the chatbot's guidelines field and re-publish to the tester.
2. **[HubSpot UI] Repair the source set + sync state.** Reduce sources to the approved scope (current Align service pages, the SmartCare page, reviewed case studies). Remove unapproved/broad blog sources once HubSpot's "problem removing the selected source(s)" error clears. Confirm each target page below reaches a current sync state.
3. **[HubSpot UI] Re-run Gate 2** (`acceptance-tests.md`) until each of the 5 answers is accurate **and** returns the exact clickable link.
4. **[HubSpot UI] Consolidate the greeting** so exactly one approved opening appears (suppress the stacked HubSpot auto-welcome). Re-run Gate 3.
5. **[HubSpot UI] Run Gate 5** (partner-safety) against the applied guidelines. Target 12/12.
6. **[brand] Approve + upload a final 1:1 Align-owned avatar** (replaces the default HubSpot robot). Coordinate via `alignhcm-brand`.
7. **[HubSpot UI] Run the full 15-case acceptance suite**, including the end-to-end handoff-ticket test (Gate 4) with a disposable identity and the SmartCare queue owner watching.
8. **[HubSpot UI] Confirm operational settings:** credits, exact website channel, tracking code, availability behavior, rollback owner.
9. **[human approval] Obtain separate activation approval**, then attach the controlled website live-chat channel and perform a live readback. **Do not attach the channel before this approval.**

## Approved knowledge-source map (verified live 2026-07-23)

| Topic | Canonical URL | Verified |
|-------|---------------|:---:|
| SmartCare | https://www.alignhcm.com/align-hcm-smartcare | ✅ loads; lists UKG/Dayforce/Paylocity/Workday/ADP |
| Implementation | https://www.alignhcm.com/services/implementation | ✅ loads |
| Training | https://www.alignhcm.com/services/training | (per readiness report; confirm sync) |
| UKG case study (GTAA) | https://www.alignhcm.com/case-studies/gtaa-optimizes-workforce-management-with-align-hcm-and-ukg-pro-suite | ✅ loads; GTAA + UKG Pro |
| Home / platforms | https://www.alignhcm.com/ | ✅ loads |

## Verified identity & handoff (do not change without re-test)

- **Name:** Align HCM Customer Agent · **Personality:** Professional · **Language:** auto-detect from the visitor's first message.
- **Configured opening:** "Hi. I'm the Align HCM Customer Agent. I can help you understand Align's HCM services and find the right next step. What are you working through?"
- **Handoff fallback (verbatim):** "I want to make sure you get a verified answer for that. I can connect you with an Align HCM specialist and include a short summary so you do not have to start over."
- **Handoff route:** async Help Desk ticket → SmartCare team; capture email before handoff; keep chat open; close after 15 minutes of inactivity.
- **Handoff triggers:** explicit human/consult/assessment/proposal/pricing/demo request; unsupported or unverified answer; current-customer/active-project request; urgent payroll/pay/access/security/compliance; contract/commitment/business-decision/platform diagnosis; frustration or repeated human request. Do **not** hand off *only* because a prospect is planning/starting/recovering an implementation — answer from public Align sources first.
