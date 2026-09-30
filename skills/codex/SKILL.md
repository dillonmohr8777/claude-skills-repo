---
name: "codex"
description: "Delegate code reviews, adversarial architecture critiques, and long-running bug investigations to OpenAI Codex from inside Claude Code. Use when you want a genuinely independent second opinion (different model family, different training), when you need to push a multi-hour investigation into the background while you keep coding, or when Claude is the author and you want a non-author reviewer. Wraps the official codex-plugin-cc plugin and falls back to the codex CLI directly."
tier: "POWERFUL"
category: "Engineering / Multi-Agent Workflows"
dependencies: "OpenAI Codex CLI (`codex`), authenticated via ChatGPT subscription or API key. Optional: codex-plugin-cc Claude Code plugin for slash-command UX."
author: "claude-skills-repo"
version: "1.0.0"
license: "MIT"
---

# Codex Integration

## Description

Run OpenAI Codex as a subagent from inside Claude Code. Codex is a separate coding agent built on OpenAI's models — using it alongside Claude gives you two genuinely independent perspectives on the same codebase in one terminal, without tab switching or copy-pasting.

This skill teaches Claude **when** to hand work off to Codex and **how** to invoke it, both through the official `codex-plugin-cc` plugin (slash commands, background jobs, status tracking) and through the raw `codex exec` CLI as a fallback.

## Why Delegate to Codex

The point is **not** "two agents are better than one." The point is that Claude reviewing Claude's own work shares mental models, blind spots, and assumptions with itself. Hand-offs to Codex break the monoculture:

- **Independent review.** Codex hasn't read the same chain-of-thought that produced the change. It will flag things Claude internalized as "obviously correct."
- **Different model family.** GPT-class reasoning catches a different distribution of bugs than Claude does. Disagreements between the two are signal.
- **Background execution.** Codex jobs run async — kick off a multi-hour bug rescue and keep coding in Claude.
- **Cost separation.** Codex jobs run on your ChatGPT subscription, not your Anthropic spend.

## When to Use This Skill

Use Codex when:

- You're about to merge non-trivial code Claude wrote and want a non-author reviewer.
- You're making a load-bearing architectural decision and want it stress-tested.
- A bug is going to take more than ~15 min of investigation and you'd rather not block.
- Tests are failing in a way you can't reproduce locally — let Codex run them in a loop while you move on.
- Claude has been agreeing with itself for 3+ turns ("LGTM", "you're right", "good call") — get an outside vote.

Skip Codex when:

- The change is trivial (typo, rename, one-line fix).
- The task requires the conversation context Claude already has and Codex doesn't.
- You're iterating fast — round-tripping through a second agent adds latency.
- You're on a network-restricted machine where `codex` can't reach OpenAI.

## Installation

### Option 1: codex-plugin-cc (recommended)

The official OpenAI-maintained Claude Code plugin. Provides `/codex:*` slash commands and background job management.

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/codex:setup` verifies that the `codex` binary is installed and authenticated. If it isn't, install Codex first:

```bash
npm install -g @openai/codex
# or
brew install --cask codex
```

Then run `codex` once interactively and choose **Sign in with ChatGPT** to authenticate against your Plus/Pro/Business/Edu/Enterprise plan. No API key required.

### Option 2: CLI only (no plugin)

If you can't install the plugin (corporate Claude Code policy, locked-down environment, etc.), invoke Codex directly through Bash. See [references/cli-fallback.md](references/cli-fallback.md).

## Core Workflows

### Workflow 1: Pre-merge Code Review

Claude implemented the change. Before staging or pushing, ask Codex to review.

```
/codex:review
```

Reviews uncommitted changes by default. Compare against a different base with `--base main`. Run synchronously by default; pass `--background` for big diffs.

**Decision rule:** if Codex flags anything **MEDIUM or higher**, address it before committing. Don't dismiss with "Codex didn't have full context" — that's exactly the perspective shift you wanted.

### Workflow 2: Adversarial Architecture Review

Use when Claude is about to commit to a design choice that's expensive to reverse (data model, auth flow, public API shape, framework selection).

```
/codex:adversarial-review focus on the auth boundary and trust assumptions
```

`/codex:adversarial-review` is read-only and explicitly steerable — it will challenge tradeoffs, question assumptions, and propose alternatives. The free-text after the command is forwarded as focus areas.

Pair with the `adversarial-reviewer` skill in this repo for a layered critique: Claude runs adversarial personas locally, then Codex runs an adversarial review with a different model family.

### Workflow 3: Background Bug Rescue

Bug investigation is taking long. Hand it off and keep working in Claude.

```
/codex:rescue --background investigate why the integration tests in tests/billing/ are flaky on CI but pass locally
```

Then check progress without blocking:

```
/codex:status
```

When Codex is done:

```
/codex:result <job-id>
```

Useful flags on `/codex:rescue`:
- `--background` — run async, return immediately
- `--wait` — stream output until done (default for short tasks)
- `--resume` — continue an earlier Codex session
- `--fresh` — discard prior session context
- `--model <name>` — pin a specific Codex model
- `--effort <low|medium|high>` — reasoning budget

### Workflow 4: Plan in Claude, Execute in Codex

Use Claude for design conversations (where context and explanation matter), then ship the spec to Codex for mechanical execution.

```
/codex:rescue --background --fresh implement the design in PLAN.md exactly as written; do not deviate from the file/function names listed in section 3
```

Why: Codex executing from a written spec doesn't drift from Claude's plan the way a long Claude session can.

## Command Reference

| Command | Purpose | Common flags |
|---|---|---|
| `/codex:setup` | Verify install + auth; optionally enable a review gate. | `--enable-review-gate` |
| `/codex:review` | Standard code review of current changes. | `--base <ref>`, `--background`, `--wait` |
| `/codex:adversarial-review` | Steerable challenge review of design/architecture. Read-only. | free-text focus, `--base <ref>` |
| `/codex:rescue` | Delegate a task (bug, fix, investigation) to Codex. | `--background`, `--wait`, `--resume`, `--fresh`, `--model`, `--effort` |
| `/codex:status` | List running and recent Codex jobs for this repo. | — |
| `/codex:result` | Print final output of a finished job (includes Codex session ID for resuming). | `<job-id>` |
| `/codex:cancel` | Stop an active background job. | `<job-id>` |

Full flag reference: [references/plugin-commands.md](references/plugin-commands.md).

## Anti-Patterns

1. **Rubber-stamping Codex's review.** If Codex says LGTM, that's one data point — don't skip your own review just because two agents agreed. They can both be wrong in correlated ways.
2. **Over-delegating.** Don't send every diff to `/codex:review`. Reserve it for non-trivial or load-bearing changes; otherwise the latency cost outweighs the signal.
3. **Ignoring disagreements.** When Claude and Codex disagree, that's the highest-value signal this skill produces. Resolve it explicitly — don't pick whichever agrees with what you already wanted to do.
4. **Background-and-forget.** `/codex:rescue --background` jobs need to be reaped. Run `/codex:status` periodically and `/codex:result` when done; don't leave them orphaned.
5. **Sending secrets.** Codex runs on your machine but talks to OpenAI. Don't `/codex:rescue` a task whose context includes plaintext credentials, customer PII, or anything covered by a DPA that doesn't include OpenAI as a sub-processor.
6. **Using Codex for trivial work.** If the task is "rename this variable," do it in Claude. The plugin overhead is real.

## Configuration

Both user-level (`~/.codex/config.toml`) and project-level (`.codex/config.toml`) config files are respected. Per-project config lets you pin model, reasoning effort, and sandbox/approval policy for everyone using Codex on this repo. See the [Codex docs](https://github.com/openai/codex) for the full TOML schema.

## When the Plugin Isn't Available

If `/plugin marketplace add` is disabled, fall back to invoking `codex exec` directly through Bash. Prompt patterns and a one-shot review wrapper are in [references/cli-fallback.md](references/cli-fallback.md).

## References

- [references/plugin-commands.md](references/plugin-commands.md) — full slash-command reference with flag semantics
- [references/cli-fallback.md](references/cli-fallback.md) — using `codex exec` directly when the plugin isn't installed
- [references/workflow-patterns.md](references/workflow-patterns.md) — multi-agent patterns (plan/execute, implement/review, adversarial)
- [Codex CLI on GitHub](https://github.com/openai/codex)
- [codex-plugin-cc on GitHub](https://github.com/openai/codex-plugin-cc)

## Related Skills in This Repo

- `adversarial-reviewer` — local adversarial personas; pair with `/codex:adversarial-review` for layered critique
- `agent-workflow-designer` — design the broader multi-agent flow this delegation fits into
- `changelog-generator` — run `/codex:review` before tagging a release
