---
name: "model-routing"
description: "Cost + model routing for Dillon's marketing swarm. Decides which model tier runs each node of the morning-orchestrator (heavy reasoning/synthesis/final-QA on the top tier; high-volume research/drafting/formatting/data-pulls on cheaper tiers or Claude workers), enforces caching discipline, sets per-workflow token budgets, and ships an eval/QA checklist so a run can't get confidently wrong or quietly expensive. Use when assigning models to agents, tuning orchestrator.config.json budgets, or reviewing why a run cost what it did. NOT for reducing spend in a client's own product AI features — that's llm-cost-optimizer."
---

# Model Routing — spend where it moves the needle, nowhere else

> The Nerd Snipe crew burned six figures in tokens finding the edges of GPT-5.6 Sol. The lesson isn't
> "Sol is expensive" — it's that **the taxes (time, tokens, fixes) show up in long agent workflows**, and
> routing is how you don't pay them. Top tier for the last mile of judgment; cheap tiers for the 70–80%
> that's volume.

This skill is the routing policy for the [[Master Agent]] / `morning-orchestrator` swarm. It answers one
question per node: **which model runs this, and under what budget?** It does not replace
`orchestrator.config.json` — it's the reasoning behind the numbers in it, plus the eval that keeps them
honest.

Related: `llm-cost-optimizer` (reduce spend inside a *client's product*), `agent-protocol.md` (the worker
contract these budgets attach to).

## The tiers (capability, not brand loyalty)

Route by job, not by favorite model. Names/prices below are **placeholders you confirm against live
pricing** — the routing *logic* is what's stable. Update `references/routing-matrix.md` when the lineup or
prices change; never hardcode a price into an agent.

| Tier | Use for | Examples (confirm) |
|------|---------|--------------------|
| **Heavy** | orchestration, long-horizon reasoning, final synthesis, high-stakes creative, the verifier's hardest calls | GPT-5.6 **Sol**, Claude **Fable/Opus** |
| **Balanced** | per-client analysis, drafting that needs judgment, most builders | GPT-5.6 **Terra**, Claude **Sonnet** |
| **Fast/cheap** | research fan-out, data pulls, formatting, dedup, simple QA, high-volume scouts | GPT-5.6 **Luna**, Claude **Haiku** |

**Default:** the commander (L0) runs Heavy. Everything below it starts at Fast/cheap and is *promoted*
only when a node's output is provably degraded — not the other way around.

## Routing rules (in priority order)

1. **Commander stays Heavy, single-threaded.** One brain in charge (the video's whole point about subagent
   UX: coordination friction is the cost, not raw model quality). Never parallelize L0.
2. **Scouts are cheap.** L2/L3 read-only scouts (history, opportunity, inbox triage, ranking pulls) run
   Fast/cheap. They gather; they don't decide.
3. **Builders are Balanced.** Anything that drafts with judgment — a rec, a page, ad copy, a report
   section — runs Balanced. Promote to Heavy only for high-stakes creative or when Balanced fails QA twice.
4. **Verifiers match or exceed the thing they check.** A verifier refuting a Heavy-tier recommendation
   runs Heavy (a cheap model can't reliably refute a strong one). Cheap verifiers are fine for cheap
   claims. This is the one place you *don't* cut cost — verification is what makes autonomy safe.
5. **Final synthesis + client-facing QA run Heavy.** The last mile (board synthesis, report number
   re-derivation) is where a mistake reaches Dillon or a client. Pay there.
6. **Promote on evidence, not vibes.** A node moves up a tier only when logged output quality (QA fails,
   verifier rejects, ledger losses) justifies it. Log the promotion.

## Caching discipline (the cheapest token is the one you don't resend)

- **Stable prefix first.** Put the invariant context — brand tokens, agent contract, client history — at
  the *front* of every prompt so provider prompt-caching hits. Vary only the tail (the task).
- **Cache the roster + contracts.** The worker contract, autonomy policy, and brand skills are identical
  across every client's worker in a run — cache them once, reuse across the fan-out.
- **Don't re-read raw work.** Parents consume children's structured returns (`agent-protocol.md`), never
  the raw output — that alone kills the biggest hidden token sink in long runs.
- **Idempotent by `node_id`.** A resumed morning returns cached results for completed nodes; only failed/
  new nodes re-run. Re-running is nearly free.

## Budgets (per node role — mirror `orchestrator.config.json`)

Budgets are ceilings, not targets. Hitting one forces synthesis with what's in hand (logged, never
silent). Current config baseline:

| Role | Minutes | Tokens | Writes |
|------|---------|--------|--------|
| scout | 15 | 40k | none |
| builder | 40 | 80k | append-only |
| verifier | 10 | 25k | none |
| commander | 20 | 60k | run-artifacts |

Run-level ceilings: `max_agents_total`, `max_concurrent_agents`, `total_token_ceiling`. Raise limits only
after observing clean runs — never preemptively.

## Scaling to budget

When Dillon sets a token target for a run, scale *depth*, not the commander:

- **More budget →** more finder rounds (loop-until-dry), a bigger verifier panel (3–5 refuters on
  high-stakes items), deeper research. Not a fancier commander.
- **Less budget →** fewer clients per run, single-vote verify, Fast/cheap builders, skip non-essential
  research triggers. Log what got cut — never silently narrow coverage.

## What to read next

- `references/routing-matrix.md` — the node-by-node routing table + the tier/price worksheet to confirm.
- `references/eval-checklist.md` — the per-run QA + cost review that keeps routing honest and stops a
  six-figure surprise.
