# Autonomy Policy

The rule that lets the swarm run "fully autonomous" without ever putting Dillon's money, clients, or
credentials at risk: **autonomy is total on everything reversible; the only gate is the irreversible
last inch — and that gate is made frictionless (one morning tap), not removed.**

Removing the Tier-2 gate is not "more autonomous," it's reckless — it's the one thing Dillon's own 64GB
handoff forbids. This policy maximizes autonomy up to that line.

## What runs fully autonomous — no human, ever

The swarm does all of this on its own, every morning, and self-verifies before anything is surfaced:
- Read all sources (vault, Drive, public pages; authenticated Chrome pulls on the local machine)
- Pre-flight checks (authorization, tracking tags/versions, conversion intent)
- Analyze history, find mistakes, spot opportunities
- Draft the exact changes; classify tier; estimate impact
- **Adversarially verify** every candidate (see agent-protocol)
- Build report artifacts and QA them
- Write vault updates: ledger hypotheses (`pending`), reporting-log appends, queue entries
- Assemble the ranked approval board and send the one push

## What runs autonomous after ONE morning approval

- The **Tier-1 batch**: reversible tweaks (negatives, pause a wasteful keyword, fix a broken CTA/link,
  tighten a schedule, swap a QA'd creative) — executed across parallel client tabs, with before/after
  screenshots and readback, then logged. One tap covers all clients.

## What is never autonomous (Tier 2 — always a live yes)

Budget/bid increases, new campaigns, changing conversion goals, Gmail send, Slack post,
publish/production deploy, billing, credentials/2FA, file moves. The swarm prepares these fully —
drafted, verified, one-click-ready — but does **not** execute them without Dillon live.

## Making the gate frictionless (the real unblock)

The complaint was "approval blocks a lot of shit." The fix isn't fewer safeguards — it's front-loading
so the human decision is trivial:
- The push carries the **whole Tier-1 batch as one approve-all**, already verified. Reject/edit individual items if you want; default is approve-all.
- Tier-2 items arrive **decision-ready**: exact change, evidence, expected impact, and the reason it's gated — so "yes" takes seconds when you're live.
- Everything the human doesn't need to see (analysis, QA, drafting) never surfaces. Only decisions do.

Net effect: the human touches the system roughly **once a morning**, and that touch is a rubber stamp
on work that already checked itself.

## Guardrails that keep autonomy safe

- **Verify-before-surface:** no unverified item reaches the board (agent-protocol self-verification).
- **Safe-direction-wins:** any tier ambiguity escalates to gated; verifier ties reject.
- **Blast-radius cap:** per-run limits on how many changes the Tier-1 batch may contain per client; excess spills to tomorrow with a note (never silently dropped).
- **Reversibility proof:** a change is only Tier 1 if the worker can state how to undo it. No undo path → Tier 2.
- **Run-level circuit breaker:** verifier rejection rate over threshold, or any global ceiling hit → the run flags for human instead of pushing.
- **No self-authorization:** the swarm never logs in, re-auths, or enters 2FA. Missing access → `needs-reauth`, keep going on the rest.
- **Full audit trail:** every autonomous action is logged with evidence; nothing is untraceable.
