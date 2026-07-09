---
name: "campaign-intel"
description: "Per-client Google Ads / Meta campaign intelligence and learning engine. Fans out read-only analyst agents over a client's campaign + change history to find what hurt performance (mistakes not to repeat), where the headroom is, and the exact ranked changes to make — each tagged with risk tier and expected impact. Maintains a per-client optimization ledger that reads back past changes as win/loss so it gets smarter about each client every cycle. Use for a deep single-client audit, or as the ads scout inside morning-orchestrator."
---

# Campaign Intelligence — Analyze, Learn, Recommend

> Evidence beats memory. Every change is a logged hypothesis. The ledger is how the agents learn.

Produces, per client: a **campaign intelligence brief** (what we learned, mistakes not to repeat,
ranked recommendations) and updates the **optimization ledger** that makes the next run smarter.
Called by `morning-orchestrator` as the ads scout, or run standalone for a deep audit.

## The Agents (fan out in parallel, read-only, Tier 0)

One commander + four bounded analyst workers. All read-only — they never touch the account. On 64GB run
all four at once per client, and multiple clients in parallel. When run inside `morning-orchestrator`,
this is the L2→L3 layer of the swarm (`morning-orchestrator/references/agent-protocol.md`): the ads
lane lead spawns one campaign-intel worker per client, each spawning these four facets. Every output is
adversarially **verified before it enters a brief or the Tier-1 batch** — default reject if uncertain.

| Agent | Reads | Returns |
|-------|-------|---------|
| **History scout** | Google Ads/Meta **change history** + performance timeseries (needs logged-in Chrome) | timeline of changes correlated with metric moves |
| **Postmortem** | the timeline + ledger | changes that *hurt* — CPC spikes, CTR/conv drops right after an edit, wasted spend, over-broad match blowups |
| **Opportunity** | current account state | headroom: budget-capped keywords, low Quality Score, weak mobile, dayparting gaps, missing negatives, audience gaps |
| **Creative** | ads + creatives performance | which ads/creatives won and why; what to retire |

Commander synthesizes into the brief. It does **not** re-analyze raw data — it consumes the four
workers' structured returns.

## Pre-Flight Gates (inherited by the orchestrator)

Before trusting any recommendation, confirm:

1. **Authorization** — session valid for this account; else `blocked: needs-reauth`, no faking.
2. **Tags / versions** — GTM published version current, GA4 firing, Google Ads conversion tag live, Meta pixel + CAPI present. A stale/missing tag flags the account and de-rates any metric that depends on it.
3. **Conversion intent** — a real conversion action is set and bidding targets it; keywords/audiences carry buying intent, not vanity traffic. Weak intent becomes the #1 recommendation, because scaling junk just wastes budget faster.

## The Brief (output)

```markdown
# <Client> — Campaign Intelligence Brief — YYYY-MM-DD
Status: ok | needs-reauth | tags-broken
Accounts: Google Ads <id> · Meta <id>

## Learned (mistakes not to repeat)
- <from the ledger + postmortem: e.g. "broad-match 'affordable ___' burned $340 at 0 conv in May — keep it exact/phrase">

## Ranked recommendations
| # | Change | Tier | Expected impact | Evidence |
|---|--------|------|-----------------|----------|
| 1 | Add negatives: [...] | 1 | −$X/wk waste | search-terms report link |
| 2 | Pause keyword "___" | 1 | recover $Y | 0 conv / 60 days |
| 3 | Raise Search budget $20→$35 | 2 | +~N leads/wk | CPA under target 14d |

## Conversion-intent read
<is the account structured to convert, or to spend?>

## Tag / tracking status
<what's firing, what's broken, what's stale>
```

## The Optimization Ledger (how it learns)

One ledger per client at `01_Clients/<Client>/Optimization Ledger.md` (template in
`mohr-vault/vault/_templates/Optimization Ledger.md`). Every applied change is appended as a
**hypothesis with an expected outcome and a review date** — not a fact:

```jsonl
{"date":"2026-07-08","client":"Onsite","account":"gads","change":"added 6 negatives","hypothesis":"cut irrelevant clicks","expected":"CTR +, CPC -, spend recovered ~$40/wk","tier":1,"review_on":"2026-07-15","verdict":null}
```

**The learning loop:**
1. Orchestrator applies a Tier-1 change → writes the hypothesis row (`verdict: null`).
2. On/after `review_on`, the history scout pulls the actual result.
3. Postmortem labels it `win` / `loss` / `neutral` with the measured delta.
4. That verdict feeds the next brief's "Learned" section — so a change that backfired becomes a
   documented mistake-not-to-repeat, and a winner becomes a pattern to lean into.

Over weeks this compounds into a **client-specific playbook**: the agents stop repeating what failed
for *that* account and double down on what worked. That is the "learn from mistakes, do better" Dillon
asked for, made concrete and durable.

## Current paid-media map (verify before trusting)

From the 64GB handoff — confirm against live state each run, don't treat as gospel:

- **Meta Ads:** Shadow, Fagan, Kimberly James, NKCDC
- **Google Ads:** Replenish, Omega, Onsite, NKCDC
- Reconcile Fagan and Kimberly James Google Ads status before excluding them. Do not assume Shadow is on Google Ads without current evidence.

## Runtime boundary

The history scout and any readback need the logged-in Chrome → **local (64GB machine, CDP).** The
postmortem/opportunity/creative synthesis, the brief, and the ledger read/write are cloud-safe against
the vault. Run the analysis anywhere; pin the authenticated pulls local.

## Writes to (existing vault targets)

- `01_Clients/<Client>/Reporting Log.md` (append only)
- `01_Clients/<Client>/Optimization Ledger.md` (append only)
- `02_Campaigns/Google Ads Optimization Queue.md`
- `02_Campaigns/Search Terms Review Queue.md`

Never overwrite client source notes. Append to logs and ledger only. Flag unclear actions before execution.
