# Plan-From-Angles Workflow

A trigger-prompt template for Claude Code's built-in Dynamic Workflows (research preview; requires v2.1.154+ on a paid plan). You paste a prompt that contains the word "workflow"; Claude writes a background script that drafts a hard plan from several independent angles and converges on the best one. Use this **before** committing to an approach.

## When to use

- You face a hard architecture, design, or approach decision where the cost of picking wrong is high.
- The problem has several plausible solutions and you want them drafted in parallel and weighed against each other, not just the first idea that sounds good.
- You want an adversarial pass that actively tries to break each candidate before you trust any of them.
- You need a defensible recommendation with a documented runner-up, not a single unexamined opinion.

## Trigger prompt

Copy, paste, and replace the placeholder. The word "workflow" is what spawns it.

```text
Run a planning workflow for <the decision/problem>.

Draft 4 independent candidate approaches in parallel. For each candidate,
spell out the design, its key tradeoffs, and its main risks.

Then run an adversarial critique pass: have separate agents try hard to
break each plan — find the failure modes, hidden costs, and assumptions
that don't hold — and refute the other candidates' claims.

Score the surviving candidates against my criteria below and converge on a
single recommendation. Give me the rationale, the explicit runner-up, and
why the runner-up lost.

Criteria / constraints: <list your evaluation criteria and hard constraints>
```

## What it tends to run

Conceptually, Claude orchestrates background agents across phases like these (it writes the script; you don't):

1. **Draft in parallel** — N candidate plans are drafted concurrently, each by an independent agent, with tradeoffs and risks attached.
2. **Adversarial critique / refutation** — separate agents attack each plan, surface failure modes and bad assumptions, and try to refute the others' findings.
3. **Score against criteria** — surviving candidates are evaluated against the criteria and constraints you stated.
4. **Converge** — results are weighed into one recommendation, with the runner-up and the reason it lost called out.

A run can fan out across many agents (up to 16 concurrent, 1,000 total per run), which is why the parallel-then-adversarial structure produces a more trustworthy result than a single pass.

## Note on ultracode

With `/effort ultracode` on, Claude runs at xhigh reasoning effort with automatic workflow orchestration, so it may auto-spawn this kind of planning workflow for substantive tasks without you asking for one explicitly. It resets to the default next session; run `/effort high` to exit sooner.

```text
/effort ultracode
```

## Tips

- State your evaluation criteria and hard constraints up front so the candidates are directly comparable — vague criteria produce vague rankings.
- Always ask for the runner-up and why it lost; the second-best plan and its weak point are often the most useful part of the output.
- This produces a plan, not code. Review and implement separately. If the run is worth keeping, save it: `/workflows` -> select the run -> press `s`.
