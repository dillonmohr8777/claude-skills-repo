# Large Migration Workflow

A trigger-prompt template for Claude Code's Dynamic Workflows (research preview, requires v2.1.154+, paid plans). You paste the prompt below; Claude Code writes and runs the workflow script in the background, fanning the work out across parallel agents.

## When to use

- A repetitive, well-defined change that must be applied across dozens to hundreds of files.
- The transformation is mechanical and rule-based (API rename, framework/library upgrade, codemod-style edit).
- There are too many files to coordinate reliably in a single conversation.
- Each file can be changed and verified independently of the others.

## Trigger prompt

```text
Run a workflow to migrate <old pattern> to <new pattern> across <path/glob>.

Transformation (apply to every matching file):
- Replace every use of <old pattern> with <new pattern>, including imports, call
  sites, type references, and comments/docstrings that name it.
- Preserve surrounding formatting, ordering, and unrelated code exactly.

Do NOT touch:
- Files outside <path/glob>.
- <other pattern> or anything that merely looks similar but is unrelated.
- Generated files, vendored/third-party code, lockfiles, and test fixtures
  unless I list them explicitly.

After editing each file, verify it still builds and lints with <build/lint command>
(and <test command> where tests exist for that file). If a file fails verification,
revert that file's changes and add it to the skipped list instead of leaving it broken.

When done, give me a summary: total files scanned, files changed, files skipped for
manual review (with the reason for each), and any ambiguous cases you were unsure about.
```

Fill in the placeholders before pasting. The more precisely you define `<old pattern>`, `<new pattern>`, and what NOT to touch, the cleaner the run.

## What it tends to run

Claude Code typically structures the script into these phases:

1. **Enumerate** — resolve `<path/glob>` and find every file containing `<old pattern>` to build the work list.
2. **Migrate in parallel batches** — distribute files across agents, each applying the transformation to its assigned files.
3. **Per-file verify** — run the build/lint (and tests, where present) on each changed file; revert and flag any file that no longer passes.
4. **Collect edge cases** — gather files that were skipped, failed verification, or were ambiguous into a manual-review list.
5. **Report** — return the summary of files scanned, changed, and skipped with reasons.

(Conceptual phases only — Claude Code writes the actual script.)

## Before you run

- **Allowlist commands first.** Subagents run in acceptEdits mode (file edits auto-approved), but shell commands still hit the allowlist. Add your `<build/lint command>` and `<test command>` to the allowlist before starting so the run doesn't stall on a prompt — there is no mid-run input.
- **Know the limits.** A run uses up to 16 concurrent agents and 1,000 agents total. Very large migrations are batched within those limits.
- **Start from a clean tree.** Commit or stash existing changes first so the migration diff is reviewable on its own.
- **Run on a branch.** Create a dedicated branch for the migration so it's easy to review, revert, or open as a PR.

## Tips

- **Split into stages when you want sign-off.** There's no mid-run user input, so if you need to approve results between, say, the migration and a follow-up cleanup, run each stage as its own separate workflow.
- **Always review the final diff.** Mechanical changes at scale can match more than you intended; read the diff and the skipped list before merging.
- **Save migrations you'll repeat.** After a good run, `/workflows` -> select the run -> press `s` to save it to `.claude/workflows/` (shared) or `~/.claude/workflows/` (personal).
