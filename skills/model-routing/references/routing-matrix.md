# Routing Matrix — which model runs each node

The node-by-node routing table for the morning-orchestrator swarm. Tiers are **Heavy / Balanced /
Fast** (see `SKILL.md`). Model names are placeholders — confirm against live pricing in the worksheet at
the bottom and keep the *logic*, not the prices, as the durable part.

## By swarm node

| Node (`lane.client.facet`) | Level | Job | Tier | Why |
|---|---|---|---|---|
| commander | L0 | route, synthesize board, gate, final readiness | **Heavy** | single brain; the coordination is the hard part |
| lane lead (ads/web/seo/reporting/comms) | L1 | plan the lane, fan out workers, roll up | **Balanced** | delegation + light judgment |
| client worker | L2 | own one client in one lane | **Balanced** | judgment, but bounded |
| history / opportunity / ranking / triage scout | L3 | read-only gather | **Fast** | gathers facts, decides nothing |
| postmortem / creative facet | L3 | correlate + judge what hurt/won | **Balanced** | needs judgment on causality |
| **verifier (cheap claim)** | any | refute a low-stakes item | **Fast** | matches the claim |
| **verifier (Tier-1/2 or Heavy claim)** | any | refute a high-stakes item | **Heavy** | can't refute strong work with a weak model |
| builder — draft copy/page/report section | L2/L3 | produce with judgment | **Balanced** | promote to Heavy only on 2× QA fail |
| builder — high-stakes creative (launch hero, brand piece) | L2 | flagship creative | **Heavy** | last-mile quality reaches a client |
| final board synthesis | L0 | rank + assemble | **Heavy** | one mistake reaches Dillon |
| report number re-derivation (QA) | L2 | reconcile metrics to source | **Heavy** | one wrong number reaches a client |

## Routing decision (per node, in order)

1. Read-only and decides nothing? → **Fast**.
2. Drafts or judges, bounded stakes? → **Balanced**.
3. Orchestrates, synthesizes for a human, or verifies high-stakes work? → **Heavy**.
4. A cheaper tier failed QA/verify **twice** on this node type? → promote one tier, log it.
5. Unsure? → the safe direction is **cheaper for gather, dearer for verify**. Never cheap-out the verifier
   on a high-stakes item.

## Provider notes (confirm each release; do not trust from memory)

- **GPT-5.6 family** (from the Nerd Snipe teardown, treat as unverified until confirmed): **Sol** =
  top-tier reasoning/coding/agentic + browser use; **Terra** = balanced daily driver; **Luna** = fast &
  cheap. A parallel multi-agent mode was discussed — validate it exists and measure it before relying on
  it; the episode's own takeaway was that subagent coordination is where real runs lose time.
- **Claude family** — Fable/Opus (heavy), Sonnet (balanced), Haiku (fast).
- The commander is **model-agnostic**: Sol/Codex holds L0 on the 64GB machine; Claude holds it in cloud/
  local sessions. Route the *role*, not the vendor.

## Price/tier worksheet (fill from live pricing, then wire into `orchestrator.config.json`)

| Tier | Model (confirm) | $/M in | $/M out | Cache discount | Assigned roles |
|------|-----------------|--------|---------|----------------|----------------|
| Heavy | _______ | _____ | _____ | _____ | commander, high-stakes verify/creative, final QA |
| Balanced | _______ | _____ | _____ | _____ | lane leads, client workers, builders |
| Fast | _______ | _____ | _____ | _____ | scouts, data pulls, formatting, cheap verify |

> Do **not** hardcode a price into an agent file. Prices live here; agents reference the tier. When a
> price or model changes, update this one table and the config — nothing else moves.
