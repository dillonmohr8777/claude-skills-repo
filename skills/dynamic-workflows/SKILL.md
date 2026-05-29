---
name: "dynamic-workflows"
description: "Enable and drive Claude Code's built-in Dynamic Workflows — Claude writes a JavaScript orchestration script and fans a task across up to 1,000 subagents running in the background. Use when: (1) enabling /effort ultracode or the 'workflow' trigger, (2) running heavy tasks like repo-wide audits, large migrations, or cross-checked research, (3) saving a good run as a reusable /command. Requires Claude Code v2.1.154+ and a paid plan."
---

# Dynamic Workflows

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** Multi-Agent Systems / AI Orchestration

---

## Overview

Dynamic Workflows is a **native Claude Code feature** (research preview, v2.1.154+).
A workflow is a JavaScript script Claude writes for the task you describe; a
runtime executes it in the background while your session stays responsive,
spawning many subagents that attack the problem from independent angles and
adversarially check each other before reporting.

There is nothing to download — this skill teaches the workflow itself: when to
reach for one, how to trigger it, and how to capture good runs. Ready-to-paste
trigger prompts live in [`.claude/workflows/templates/`](../../.claude/workflows/templates).

## When to Use

- A task needs more agents than one conversation can coordinate (repo-wide
  sweeps, 100+ file migrations).
- You want orchestration codified as a script you can read and rerun.
- You want a result hardened by independent agents cross-checking each other,
  not a single pass.

Prefer plain **subagents/skills** when Claude can hold the plan turn-by-turn and
results should stay in context.

## Quick Start

```text
# Trigger one task as a workflow — just include the word "workflow"
Run a workflow to audit every endpoint under src/routes/ for missing auth checks

# Let Claude auto-orchestrate every substantive task this session (the tweet's "/ultracode")
/effort ultracode        # xhigh effort + automatic workflow orchestration

# Run the bundled research workflow
/deep-research What changed in the Node permission model between v20 and v22?

# Watch / manage runs
/workflows               # list runs; Enter to open progress; s to save a run
```

## Triggers

| Goal | Action |
| :-- | :-- |
| One task as a workflow | Put `workflow` anywhere in the prompt (`alt+w` to ignore a false trigger) |
| Auto-orchestrate all substantive tasks | `/effort ultracode` (resets next session; `/effort high` to exit) |
| Prebuilt research | `/deep-research <question>` |

## Limits & Behavior

- **16 concurrent** agents (fewer on low-core machines), **1,000 total** per run.
- Subagents run in `acceptEdits` and inherit your tool allowlist regardless of
  session permission mode — add needed shell/MCP commands to the allowlist
  before long runs to avoid mid-run prompts.
- No mid-run user input; the script coordinates, the agents do all file/shell IO.
- Resumable within the same session; starts fresh if you exit Claude Code.

## Save for Reuse

`/workflows` → select a good run → press **`s`** → save to `.claude/workflows/`
(shared) or `~/.claude/workflows/` (personal). It becomes a `/<name>` command.

## Turn Off

`/config` toggle, or `"disableWorkflows": true` in settings, or
`CLAUDE_CODE_DISABLE_WORKFLOWS=1`.

## References

- Official docs: https://code.claude.com/docs/en/workflows
- Setup guide & recipes: [`.claude/workflows/`](../../.claude/workflows)
