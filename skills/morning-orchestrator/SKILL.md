---
name: "morning-orchestrator"
description: "Dillon's daily order-shooter. Every morning it wakes on its own, refreshes state, fans out read-only scouts across every client (ads, web, reporting, SEO, comms) in parallel, builds one ranked approval board, and sends a single push notification. On one approval it executes the Tier-1 batch across parallel remote Chrome tabs — all clients at once. Evidence beats memory; spend/sends/publishes stay gated. Use to run the morning pass, or to (re)design the daily orchestra."
---

# Morning Orchestrator — the Order-Shooter

> One push. One approval. Every client's campaigns optimized in parallel before Dillon sits down.

This is the commander that drives the agents already defined in `mohr-vault/vault/11_Agents/`
(`Master Agent`, `Google Ads Agent`, `Web Agent`, `Reporting Agent`, `SEO Agent`) plus the
`campaign-intel` skill. It does **not** replace them — it schedules, fans them out, and gates them.

It is designed for the 64GB machine: heavy read-only fan-out in parallel, then parallel
execution across multiple remote Chrome tabs (one client per tab) after a single approval.

## Autonomy Model (read this first)

These are **self-driving agents**, not scripts a human runs step by step. Left alone each morning, the
commander spawns a **bounded parallel swarm** — lane leads → per-client workers → analyst facets (depth
3, capped) — that reads, analyzes, drafts, and **verifies its own work**, then surfaces a single
decision. The human touches it roughly **once**, to approve.

Autonomy is *total on everything reversible* and gated only at the irreversible last inch — and that
gate is made frictionless, not removed. The full rules live in:
- `references/agent-protocol.md` — swarm topology, worker contract, self-verification, budgets, failure isolation, kill switch
- `references/autonomy-policy.md` — exactly what runs unattended vs. gated, and the guardrails
- `orchestrator.config.json` — the machine-readable topology/concurrency/budget the runtime reads

The one thing that makes "fully autonomous" safe: **nothing reaches the board or a report until a
separate verifier agent has tried to refute it and failed** (default: reject if uncertain; ties escalate
to gated). The swarm checks itself before it asks you for anything.

## The Core Loop

```
  overnight ──► 0. INTAKE  (read Morning Directives — Dillon's dropped tasks — and inject as lanes)
                1. WAKE (scheduled, no human)
                2. PRE-FLIGHT  (authorization + tag/version + conversion-intent checks)
                    └─ RESEARCH?  spawn scoped research agents if a trigger fires (see references/research-triggers.md)
                3. FAN-OUT SCOUTS  (parallel, read-only) ── route each job to a skill via skill-map.json
                4. SYNTHESIZE  (commander builds the ranked approval board)
                5. PUSH  ──────────────────────────────────► Dillon's phone: one notification
  Dillon taps "approve" ──►
                6. EXECUTE Tier-1 batch  (parallel remote Chrome tabs, one client per tab)
                7. READBACK + LEDGER  (log every change as a hypothesis to learn from)
                8. DELIVER  (draft recaps; sends stay gated)
```

Steps 0–5 need **no human** and run to completion on their own. The human touches it once, at step 6 —
plus the optional 30 seconds of dropping tasks into Morning Directives whenever the work evolves.

## Step 0 — Morning Task Intake (your evolving directives)

Your work changes, so the loop starts by reading **`mohr-vault/vault/11_Agents/Morning Directives.md`** —
a plain drop-box you (or a Slack/phone note) fill with freeform tasks. The commander parses each into a
bounded lane, classifies its tier, routes it to a skill via `skill-map.json`, and folds it into the same
board. Anything it can't map to a skill it flags back to you in the board rather than guessing. Directives
are one-shot (cleared after the run) unless you mark one `recurring`.

## Use Dillon's own toolkit (routing)

Before any worker builds from scratch, it checks **`skill-map.json`** (+ `references/skill-registry.md`)
for a matching skill — your design skills, `mirror`, `paid-ads`, `client-report`, `deep-research`, etc.
Pinned "most-used" skills win ties. Build-from-scratch is the fallback, not the default. This is how the
swarm runs *your* system instead of a generic one.

## Staying current (research)

The swarm spawns scoped, read-only research agents when a trigger fires — weekly best-practices refresh,
a worker's uncertainty, a platform surprise, or a repeated ledger loss — to pull **current 2026 Google/
Meta best practices** and inject verified findings into the affected briefs. Full rules and the
recency/credibility gate: `references/research-triggers.md`.

## Tiered Approval — why this unblocks the day

The old handoff gated *every* write. That's why "approval blocks a lot of shit." Fix: tier by
reversibility, and batch the reversible tier into the single morning push.

| Tier | Examples | Gate |
|------|----------|------|
| **0 — Auto** | read history, analyze, find mistakes, draft changes, QA, build report artifacts, screenshot | none — runs in steps 2–4 |
| **1 — Morning batch** | add negative keywords, pause a keyword/ad wasting spend, fix a broken link/CTA, tighten a schedule, swap in a QA'd creative | **one** approval on the push notification, then executes for all clients |
| **2 — Live only** | budget/bid increases, new campaigns, changing conversion goals, Gmail send, Slack post, publish/deploy to production, billing, credentials/2FA | held for a live, explicit yes — never in the batch |

Rule of thumb: **if Dillon can undo it himself in 30 seconds, it's Tier 1.** Everything irreversible or
outbound is Tier 2. The push shows the Tier-1 batch as *approve all / edit / reject each*, and lists
Tier-2 items separately as "needs you live."

## Step 2 — Pre-Flight (run before any client work)

Per client, before scouting, verify the ground is real:

1. **Authorization check** — is the logged-in Chrome session valid for this client's Google Ads / Meta / GA4 / GBP / CMS? If a session is expired or access is missing, **do not fake it**: mark the client `blocked: needs-reauth` and carry on with the others. Never attempt a login or 2FA autonomously.
2. **Tag / version check** — confirm tracking is present and current: GTM container published version, GA4 tag firing, Google Ads conversion tag, Meta pixel + CAPI. Flag any tag that is missing, unpublished, or on a stale version. A recommendation built on broken tracking is worthless, so this gates the client's ads lane.
3. **Conversion-intent check** — confirm each active campaign is actually pointed at conversions, not vanity traffic: a real conversion goal/action is set, bidding aligns with it, and the keywords/audiences carry buying intent (not broad junk siphoning spend). Where intent is weak, that becomes the top recommendation.

Pre-flight is Tier 0 (read-only) and its results head every client's card on the board.

## Step 3 — Fan-Out Scouts (parallel, read-only)

Activate the existing vault agents as bounded scouts, one lane per agent, **all clients in parallel**.
On 64GB this is cheap RAM-wise; the real cap is API rate limit, so keep scout budgets small
(10–15 min, no writes). Delegate one level only — scouts do not spawn scouts.

| Scout | Backed by | Produces (Tier 0, no approval) |
|-------|-----------|-------------------------------|
| Ads intel | `campaign-intel` + `Google Ads Agent` | per-client: mistakes-not-to-repeat, ranked changes, each tagged Tier + expected impact |
| Web | `Web Agent` | pages needing work today, tracking gaps, mobile issues, CRO drafts |
| Reporting | `Reporting Agent` | what's due, dashboard/Slack/Gmail reconciliation, metric QA flags |
| SEO / AEO-GEO | `SEO Agent` | content due, schema/extractability gaps, authority tasks |
| Comms | Gmail/Slack read | client asks, approvals, dates, access proof → drafts only |

Each scout is a **lane lead** that itself spawns per-client workers in parallel (and ads workers spawn
the four analyst facets) per `references/agent-protocol.md`. Every node returns the worker-handoff JSON;
the commander never re-derives, it consumes structured returns. Every candidate recommendation and every
report metric passes the verifier before it counts.

## Step 4 — Synthesize the Approval Board

Commander merges all scout output into one board, ranked by impact × confidence:

```
automation-runs/morning-orchestrator/YYYY-MM-DD/
  run-state.json         # per-client status: ok | blocked:needs-reauth | blocked:tags
  approval-board.md       # the thing the push links to
  tier1-batch.json        # exact reversible changes, per client, ready to execute
  tier2-queue.md          # needs-you-live items
  evidence-log.md         # screenshots/pointers backing every recommendation
  ledger-updates.jsonl    # hypotheses to write back after execution
```

Board layout — one card per client, most-impactful client first:

```
### <Client>            status: ok | needs-reauth | tags-broken
Learned: <1-line mistake-not-to-repeat from the ledger>
Tier 1 (batch): [ ] add 6 negatives  [ ] pause "cheap ___" (spent $X, 0 conv)  [ ] fix mobile CTA
Tier 2 (live):  raise Search budget $20→$35 (capped, CPA under target 14d)
Web:            hero + form QA on /scheduling
```

## Step 5 — The Push

Send **one** notification: "Morning board ready — N clients, M Tier-1 changes queued, K need you live."
Deep-link to `approval-board.md`. That's the only interrupt before Dillon chooses to engage.

## Step 6 — Parallel Execution (the 64GB payoff)

On approval, execute the Tier-1 batch **concurrently, one client per remote Chrome tab**. This is the
part Dillon specifically wants: 3+ clients optimized at the same time instead of one-by-one.

Concurrency contract (this is where RAM earns its keep — see `references/parallel-execution.md`):

- **One tab = one client = one CDP context.** Never let two tabs write to the same ads account.
- Realistic simultaneity on 64GB: **3–6 client tabs** executing at once (each authenticated Chrome ≈ 0.5–0.7 GB; the true ceiling is API rate limit, not memory).
- Each tab: screenshot → apply approved change → screenshot → read back the result → return outcome. Never close Dillon's live browser; disconnect from CDP instead.
- If a tab hits an expired session mid-run, it stops that client cleanly and reports `needs-reauth` — the other tabs keep going.
- Tier-2 items are **never** executed here. They wait for a live yes.

## Step 7 — Readback + Ledger (how it learns)

Every applied change is written to that client's optimization ledger as a **hypothesis**, not a
fact: what changed, why, and the expected effect. The `campaign-intel` skill reads these back after
~7 days, labels each win/loss, and feeds the verdict into the next morning's analysis. That loop is
what makes the orchestra get smarter about each specific client over time — see `campaign-intel`.

## Step 8 — Deliver

Build client-facing artifacts (reports as linkable URLs), draft the delivery message in Gmail/Slack —
but **sends stay Tier 2.** The morning run ends with drafts staged and a one-page status for Dillon.

## Running it

- **Scheduled (default):** a local scheduler on the 64GB machine fires the run each morning; steps 1–5 complete unattended and the push arrives. See `references/scheduling.md` for the local cron/Task Scheduler + wake pattern.
- **On demand:** invoke this skill to run the pass now.
- **Design mode:** invoke with a change request to evolve the orchestra (add a lane, retune tiers, adjust concurrency).

## Who runs this (model roles)

The default commander on the 64GB machine is **GPT-5.6 / Codex** — it's the persistent orchestrator that
owns the swarm, the board, and the push. **Claude Code (desktop, run occasionally) is a specialist
worker** Codex can delegate a bounded lane to via the worker contract. The contract is model-agnostic —
`orchestrator.config.json` + the `references/` files are plain JSON/markdown that either model reads.
This SKILL.md is the Claude-friendly wrapper around that same contract; see
`dillon-os/11_Agents/64gb Morning Orchestrator Spec 2026-07-08.md` for the Codex-facing entry point.

## Runtime boundary

Ads/Meta/CMS execution needs Dillon's logged-in Chrome, so **steps 2, 6, and 7's live readback run on
the 64GB machine** (Codex as commander, or local Claude Code as a worker, over CDP at
`127.0.0.1:9222`). Steps 3–5 and 8's artifact-building are cloud-safe and can run in a hosted session
against the vault, Drive, and public pages. Same contract, both places — only the authenticated Chrome
half is pinned local.

## Hard stops (unchanged from the 64GB handoff)

No Gmail send, Slack post, ad publish/budget/bid/billing change, production deploy, file move, or
credential/2FA action without an explicit live yes. The morning batch approval covers **Tier 1 only.**
