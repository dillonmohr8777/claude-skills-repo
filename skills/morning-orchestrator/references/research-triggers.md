# Research Triggers — knowing when to spawn research agents

The platforms change constantly. The orchestrator must not run 2026 campaigns on 2024 tactics. This
defines **when** the swarm spawns research agents, **what** they research, and **how** findings flow back
into the work. Research runs via the `research` lane skills (`deep-research`, `autoresearch-agent`,
`competitive-intel`) and is always Tier 0 (read-only) — findings never auto-apply, they inform.

## When to spawn research (the triggers)

**Scheduled (predictable):**
- **Weekly best-practices refresh** — one pass on current Google Ads + Meta Ads best practices, feature/policy changes, and algorithm shifts. Keeps the playbook current.
- **Monthly deep sweep** — bigger scan: new ad formats, bidding strategies, measurement/tracking changes (e.g. consent mode, CAPI updates), industry benchmarks.

**Event-driven (reactive — spawn on the signal):**
- A worker hits **uncertainty** — "is this still best practice?" confidence below threshold → spawn a scoped research agent before recommending.
- **Platform surprise** — a new UI element, a disapproval reason, a metric that moved for no local reason, a deprecated setting → research what changed.
- **Repeated loss in a ledger** — the same tactic underperforms across clients → research alternatives.
- **New client or new vertical** → research that industry's ad benchmarks and angles.
- **Dillon drops a directive** mentioning a tactic/tool/format the swarm doesn't have a skill for → research it.

## What they research (scope, not open-ended)
Each research agent gets a bounded question, not "learn everything." Examples:
- "Current Google Ads Performance Max best practices for local service businesses, 2026 — what changed in the last 90 days?"
- "Meta Advantage+ creative best practices 2026; signs of creative fatigue and refresh cadence."
- "Conversion tracking / measurement changes affecting [client vertical] in 2026."

## How findings flow back (the point)
Research that isn't wired into action is wasted. Every finding must land somewhere it changes behavior:
1. **Verified** like any other output (separate agent checks the source is real, current, and credible — 2026-dated, not recycled old advice).
2. Written to a durable, dated **best-practices note** in the vault (`04_SOPs/` or `11_Agents/Research/`), so it compounds instead of being re-researched.
3. Relevant findings **injected into the affected clients' campaign-intel briefs** as "current best practice says X — we're doing Y — recommend Z."
4. If a finding contradicts a pinned tactic, it's flagged in the cross-client pattern library for review.

## Guardrails
- Research is read-only and never triggers a Tier-1/2 action on its own — it produces recommendations that go through the normal board + approval.
- **Recency + credibility gate:** discard undated or pre-2026 "best practices" presented as current; prefer official platform docs and reputable recent sources. Verifier rejects stale or unsourced claims.
- Bounded budget per research agent (see `orchestrator.config.json` scout budget); a sweep is several bounded agents in parallel, not one unbounded crawl.
