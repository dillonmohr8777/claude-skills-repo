# Eval & Cost Checklist — keep routing honest

Run this against every morning run (and any big ad-hoc workflow). It's the thing that stops a run from
being confidently wrong *or* quietly expensive — the two ways the Nerd Snipe crew's six figures got
spent. Two passes: **quality** (did the swarm check itself?) and **cost** (did routing hold?).

## Quality gate (per run — a fail blocks the push)

- [ ] **Verify-before-surface held.** Every board item + every report metric passed a *separate* verifier.
      No item reached the board on one agent's say-so.
- [ ] **Reject-if-uncertain enforced.** Ambiguous items were rejected or escalated to gated, not shipped.
- [ ] **Tier classification independently confirmed.** Verifier agreed on each Tier-1 item; any
      disagreement escalated to Tier 2 (safe direction won).
- [ ] **Reversibility proven.** Every Tier-1 item carries a stated undo path. No undo → it's Tier 2.
- [ ] **Metrics re-derived from source.** Report numbers reconcile to source; every link checked live.
      Any mismatch → pulled + flagged, not delivered.
- [ ] **Rejection rate under threshold.** Verifier rejection rate < `verification.run_flag_reject_rate`.
      Over it → the whole run flagged for human review instead of pushing a board.
- [ ] **Failures surfaced, not hidden.** Every `blocked` / `needs-reauth` / dropped node is on the board.
      Nothing silently missing.
- [ ] **No silent truncation.** Any coverage cut for budget (fewer clients, skipped research, top-N) is
      logged with what was dropped.

## Cost gate (per run — a fail tunes the next run)

- [ ] **Commander was Heavy + single-threaded.** No accidental parallel L0.
- [ ] **Scouts ran Fast.** No read-only gather node ran on a Heavy model.
- [ ] **Verifiers matched claim stakes.** High-stakes items verified Heavy; cheap claims verified Fast.
      (The one place under-spending is a bug.)
- [ ] **Caching hit.** Stable prefixes (contracts, brand tokens, client history) front-loaded; cache-hit
      rate logged. Low hit rate → reorder prompts.
- [ ] **No raw re-reads.** Parents consumed structured returns only; no parent re-read a child's raw work.
- [ ] **Budgets respected.** No node blew its token/minute ceiling without logging a forced synthesis.
- [ ] **Resume was cheap.** A re-run returned cached results for completed `node_id`s; only new/failed
      nodes re-ran.

## Per-run cost log (append to the run's evidence-log)

```
run: morning-YYYY-MM-DD
clients: N        agents spawned: N / cap
tokens: in ___ / out ___ / total ___ (ceiling ___)
cache hit rate: ___%
tier mix: heavy ___% · balanced ___% · fast ___%
verifier reject rate: ___%   (threshold ___%)
$ estimate: ___   (from routing-matrix worksheet prices)
promotions this run: <node type → tier, reason>
cuts this run: <what coverage was dropped for budget, if any>
```

## Weekly review (spot the drift)

- Which node types keep getting promoted to Heavy? → either the cheaper tier genuinely can't do it (bake
  the promotion into the matrix) or the prompt is weak (fix the prompt, not the model).
- Where did tokens actually go? Rank nodes by spend; the top 3 are your optimization targets.
- Did cost track value? A lane that spent the most but produced the fewest approved changes is mis-routed.
- Recurring unmapped directive? → hand to `self-improving-agent` / `agent-designer` to make it a pinned
  skill, so next time it's cheap and routed.

## The one-line rule

**Gather cheap, decide dear, verify to the stakes, cache the invariant, and never let a run narrow its
coverage without saying so.**
