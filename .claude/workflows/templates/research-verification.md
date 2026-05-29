# Research & Verification Workflow

A trigger-prompt template for Claude Code's built-in **Dynamic Workflows** (research
preview; requires v2.1.154+ on a paid plan). You paste a prompt; Claude Code writes
and runs a background workflow that fans out research, cross-checks sources against
each other, and returns a cited report. This file is guidance plus copy-paste prompts —
not runnable code.

## When to use

- You have a question that needs **multiple independent sources** cross-checked rather than a single web search.
- You want **low-confidence or unsupported claims filtered out**, not just summarized.
- You need a **cited report** you can trust, with contradictions surfaced instead of buried.
- The answer matters enough to justify adversarial verification (facts, comparisons, due diligence).

## Fastest path

Claude Code ships a bundled workflow built for exactly this. Just run:

```text
/deep-research <your question>
```

It fans out web searches across several angles, fetches and cross-checks the sources,
votes on each claim, and returns a cited report with claims that didn't survive
cross-checking filtered out. It requires the **WebSearch** tool to be available.

## Custom trigger prompt

When you want more control over angles, output format, or confidence handling, paste a
prompt that includes the word **workflow** so Claude Code runs it in the background:

```text
Run a research workflow on: <your question>

- Break the question into several independent search angles and search each one separately.
- Fetch the underlying sources, don't rely on snippets.
- Cross-check every source against the others; have independent agents try to refute each finding.
- Tag each claim with a confidence level and inline citations to the sources backing it.
- Drop or clearly flag any claim that is contradicted or unsupported after cross-checking.
- Return a synthesized report grouped by sub-question, with a list of open questions at the end.
```

## What it tends to run

Conceptual phases (Claude decides the exact shape per question):

1. **Fan out** — split the question into angles and dispatch parallel search agents (up to 16 at once).
2. **Fetch sources** — pull the actual pages/documents behind the top results for each angle.
3. **Adversarial cross-check** — independent agents compare sources, refute each other's findings, and vote on each claim.
4. **Synthesize** — assemble surviving, well-supported claims into a cited report; flag or drop the rest.

## Before you run

- Ensure the **WebSearch** tool is allowed for the session — without it the bundled and custom flows can't search.
- Allow any **fetch/MCP tools** you want sources pulled from (e.g. WebFetch, document or repo MCP servers).
- Limits: up to **16 concurrent agents** and **1,000 total** agents per run — broad questions consume the budget faster.

## Tips

- Give a **sharp, specific question** (scope, region, timeframe, criteria) — vague prompts spread the agent budget thin.
- Explicitly **ask for inline citations and per-claim confidence** so you can audit what survived cross-checking.
- Save a good run to reuse it: **`/workflows`** -> select the run -> press **`s`**.
