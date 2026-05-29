# Codebase Audit Workflow

A trigger-prompt template for Claude Code's Dynamic Workflows (research preview, v2.1.154+, paid plans). Paste the prompt below; Claude Code writes and runs the workflow script for you. This is a prompt, not runnable code.

## When to use

- Repo-wide bug sweeps that are too large to hold in a single conversation.
- Security reviews across many files (injection, authz, secret handling, unsafe deserialization).
- Convention or style conformance checks against a documented standard.
- Dead-code / unused-export / orphaned-file detection across the tree.

## Trigger prompt

```text
Run a codebase audit as a workflow.

Scope: audit <path/glob> (e.g. src/**/*.ts), excluding <paths to skip>.
Goal: find every instance of <what to check for> (e.g. SQL built via string
concatenation, missing authorization checks, swallowed exceptions).

What counts as a finding: <precise definition of a true positive>. Do NOT
report stylistic nitpicks or anything outside the definition above.

For each finding report:
  - file:line
  - severity (critical / high / medium / low) with a one-line justification
  - a 1-2 line explanation of why it matches the definition
  - a suggested fix

Process:
  1. Enumerate the in-scope files first.
  2. Inspect them in parallel batches; each agent reports candidate findings.
  3. Have a separate set of independent agents adversarially review each
     candidate and try to REFUTE it (read surrounding context, callers,
     guards). Drop or downgrade anything that cannot be confirmed, to cut
     false positives.
  4. Synthesize the surviving findings into a single markdown report grouped
     by severity, with a short summary and counts at the top.

Do not modify any files. Output the report only.
```

## What it tends to run

Conceptually, Claude Code will write a script that runs phases like:

1. Enumerate — list and filter the in-scope files (often a cheap single agent).
2. Parallel inspect — fan out across file batches; each agent flags candidates against the definition.
3. Adversarial verify — independent agents re-examine each candidate with surrounding context and attempt to refute it.
4. Synthesize — merge confirmed findings into one severity-grouped report.

Exact phases and batching are decided by Claude at run time.

## Before you run

- Add the read-only commands agents will need to your tool allowlist BEFORE starting (e.g. your grep/ripgrep, `ls`, `find`, language-specific linters, any MCP read tools). Subagents run in acceptEdits mode and inherit your allowlist regardless of session permission mode, so unlisted commands cause mid-run prompts that stall a long audit.
- Keep the work inside the limits: up to 16 concurrent agents and 1,000 agents total per run. Large trees may need tighter scope or batching.
- Consider a smaller/faster model for the enumerate phase, since file listing needs little reasoning.

## Tips

- Narrow the path/glob and the finding definition to keep cost and false positives down; broad audits burn agents fast.
- Always ask for a markdown report grouped by severity with file:line — it makes triage and follow-up fixes much faster.
- If the audit is one you'll repeat, save the run: `/workflows` -> select the run -> press `s` -> `.claude/workflows/` (shared) or `~/.claude/workflows/` (personal).
