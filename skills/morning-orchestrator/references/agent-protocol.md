# Autonomous Swarm Protocol

How the orchestrator spawns a bounded, parallel, multi-level sub-agent swarm — safely. This is what
makes the agents self-driving instead of scripts a human babysits. Dillon has explicitly authorized the
swarm (overriding the handoff's default one-level limit), so depth up to 3 is allowed — but bounded.

## Topology

```
L0  Commander (1, persistent, never parallel)
      owns: run-state, approval board, final readiness, kill switch
        │  spawns lane leads in parallel
        ▼
L1  Lane Leads (≤5: Ads · Web · Reporting · SEO · Comms)     ── parallel
        │  each spawns one worker per client in parallel
        ▼
L2  Client Workers (one per client per lane)                 ── parallel
        │  ads workers spawn the 4 analyst facets in parallel
        ▼
L3  Analyst Facets (history · postmortem · opportunity · creative)  ── parallel
        └──► every L2/L3 output passes a VERIFIER before it counts
```

Delegation depth is capped at **3** (L0→L1→L2→L3). No agent below L3 may spawn. This is a swarm, not
uncontrolled recursion.

## Worker Contract (every spawned agent gets this, no exceptions)

```json
{
  "run_id": "morning-YYYY-MM-DD",
  "node_id": "ads.onsite.postmortem",   // lane.client.facet — unique, idempotent
  "level": 3,
  "lane": "ads",
  "client": "Onsite",
  "objective": "one sentence",
  "sources": ["exact paths / accounts to read"],
  "expected_artifact": "what to return",
  "budget": {"minutes": 15, "tokens": 40000},
  "stop_condition": "when to quit even if incomplete",
  "may_spawn": false,               // true only for L1/L2 within depth cap
  "write_scope": ["append-only paths"] // empty for read-only scouts
}
```

Every agent returns **only** the structured handoff (from the 64GB handoff):

```json
{"lane":"","client":"","sources_checked":[],"verified_facts":[],"artifacts_created":[],
 "draft_or_publish_state":"","blockers":[],"approval_required":[],"qa_status":"",
 "recommended_next_action":"","tier":0,"confidence":0.0}
```

The parent consumes the structured return — it never re-reads the child's raw work.

## Self-Verification (why autonomy is trustworthy)

Nothing enters the Tier-1 batch or a report on a single agent's say-so. Each candidate is checked by a
**separate verifier agent** whose job is to *refute* it:

- **Recommendations:** verifier tries to break the case ("is this change actually reversible? does the evidence support the expected impact? would it hurt conversion intent?"). Default to **reject if uncertain.** Survives → eligible for the batch.
- **Report metrics:** a QA facet re-derives each number from source and checks every link. Any mismatch → the metric is pulled and flagged, not delivered.
- **Tier classification:** verifier independently confirms the tier. If it disagrees and rates it higher-risk, the item escalates to Tier 2 (gated). Ties escalate. The safe direction always wins.

A run where the verifier rejects more than the configured threshold of candidates flags the *whole run*
for human review instead of pushing a board — the system refuses to be confidently wrong at scale.

## Concurrency, Budgets, Failure Isolation

- Max concurrent agents and per-level breadth are set in `orchestrator.config.json`; excess queues.
- **Failure is local:** an agent that errors or times out drops its node to `null`; siblings continue; the parent notes the gap. One client never takes down the run.
- Bounded retries (default 1) with backoff; then mark `blocked` and move on.
- **Idempotent by `node_id`:** re-running a morning resumes — completed nodes return cached results, only failed/new nodes re-run.
- **Global ceilings:** total-agents cap and total-token cap per run. Hitting either stops new spawns and forces synthesis with what's in hand (logged, never silent).

## Kill Switch & Audit

- Commander checks a `STOP` flag at every phase boundary; if set, it finishes in-flight nodes and halts.
- Every spawn/return/verdict is appended to `evidence-log.md` and `run-state.json` — the full run is auditable after the fact.
- The commander is the only writer of the board and the only thing that sends the push. Workers never message Dillon directly.
