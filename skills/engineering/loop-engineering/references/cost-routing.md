# Cost routing: adopted policy and evidence boundary

Dillon adopted this policy on October 8, 2026. Its source is the user-supplied public research prompt "Agent cost prompt, Opus 5.5 vs Sonnet 5.5", summarized in the local source commit `68a7527e66228205bf6486345cc33a59903ef874`. That prompt attributes caching principles to Thariq Shihipar. Its wording, numerical examples and turn-six/escalation rules are third-party research and operator choices, not official Anthropic guidance. The prompt's quoted post attribution was not independently authenticated in this doc sync. No private transcript or local account path is included here.

## Session and handoff contract

- Start ordinary implementation Sonnet-first under the current host policy, with one effort level per session. Source-fed Haiku assists and public/synthetic Spark assists retain their separate contracts.
- At turn 6, inspect compilation, the first relevant test and changed files. Record the actual failed check rather than escalating from a model's confidence.
- If that check fails, create a fresh approved stronger session from `handoff.md`, bounded to 20K tokens. Include the task in one sentence, failing check and output, the three relevant files with line ranges, what was tried in at most five lines, and the hard budget. Exclude the transcript, secrets and unrelated client context.
- The handoff inherits the job's current policy, privacy classification, owner, acceptance check and remaining authorization ceiling. The 20K-token bound does not grant 20K tokens of spending or imply that a provider budget is enforced.
- Preserve a separately scoped impartial peer review for hard architecture/gap analysis. This policy does not require a reviewer to fail ordinary implementation first or declare one model universally superior.

## Cache and economics checks

Put stable content before changing context. Track observed cache reads/writes when the provider exposes them. Investigate an unexpected zero cache read on a repeated eligible prefix, including prefix drift, expiry, eligibility and telemetry limitations. An initial cold request or absent counter does not establish an incident by itself.

Compare cost per accepted result on matched jobs. Keep observed charges, estimates and missing evidence distinct. Report the biggest observed dollar leak first, with at most two numbers per line and a source log. Refresh prices when analysis needs them; do not copy the source prompt's dated prices or savings as current facts. Choosing a longer cache lifetime needs actual pause/usage evidence and current costs, not a universal turn-count rule.

[Anthropic's official prompt-caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), checked October 8, supports reuse of matching prefixes, cache usage inspection and lifetime selection. It does not establish the adopted turn-six threshold, a universal cheaper-model result, the source prompt's numerical break-even examples, or the original post attribution. Check the actual host/provider behavior before applying the policy.

## Scope

This is guidance only. No router, `outcome.py` metric, cache setting, provider route, hook or scheduler is installed by this document. A host that records accepted/edited/rejected outcomes can compute accepted-result cost from those receipts; this repository does not claim that metric already runs. Current task budgets and action-specific approvals remain authoritative even where a helper cap has been disabled.
