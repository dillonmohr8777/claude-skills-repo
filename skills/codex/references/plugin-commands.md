# codex-plugin-cc Command Reference

Detailed semantics for each `/codex:*` slash command exposed by the `codex-plugin-cc` plugin. This is a companion to `SKILL.md` — read that first for the *when*; this doc covers the *exactly how*.

All commands shell out to your local `codex` binary using auth from `~/.codex/config.toml` (or `.codex/config.toml` if present in the repo).

---

## `/codex:setup`

Verifies that:

1. The `codex` binary is on PATH.
2. You're authenticated (ChatGPT or API key).
3. The plugin can talk to the local Codex app server.

### Flags

- `--enable-review-gate` — installs a pre-commit gate that runs `/codex:review` automatically before allowing a commit. Off by default. Skip on hot codebases where review latency would be painful.

### When to run

- After installing the plugin.
- After upgrading `codex` (`npm update -g @openai/codex` or `brew upgrade --cask codex`).
- If any `/codex:*` command starts failing with auth or transport errors.

---

## `/codex:review`

Standard code review. Codex reads the diff and reports findings.

### Default behavior

- Reviews **uncommitted changes** (`git diff` + `git diff --cached`).
- Returns synchronously by default for small diffs.

### Flags

- `--base <ref>` — review the diff between `<ref>` and `HEAD` instead of working tree changes. Common: `--base main`, `--base origin/main`, `--base HEAD~5`.
- `--background` — run async; returns a job ID immediately. Use for diffs >500 lines.
- `--wait` — explicitly stream output until done. Useful in scripts.

### What you get

A structured review with severity-tagged findings (typically BLOCK / CONCERN / NIT or similar). Treat MEDIUM-and-above findings as merge blockers unless you have a specific reason to override.

### Decision rule

If `/codex:review` and your own (or `adversarial-reviewer`'s) review **disagree on severity**, that's the most valuable output of this command. Resolve the disagreement before merging — don't average it.

---

## `/codex:adversarial-review`

A read-only steerable critique of *design*, not just code. Codex is prompted to challenge tradeoffs, propose alternatives, and surface assumptions the author treated as obvious.

### Default behavior

- Read-only: never modifies files, never stages, never commits.
- Reviews uncommitted changes by default.

### Flags

- `--base <ref>` — same semantics as `/codex:review`.
- *(free text after the flags)* — focus areas. Forwarded to Codex as steering. Examples:
  - `/codex:adversarial-review focus on whether the new caching layer is racy`
  - `/codex:adversarial-review challenge the choice of REST over gRPC`

### When to use

- Before merging an architectural change (data model, auth, API surface).
- When a design has been discussed only with Claude and you want a non-author perspective.
- When the change touches a "load-bearing" boundary (anything where the cost of getting it wrong is much greater than getting it right).

### When NOT to use

- Implementation-level changes inside an already-decided design — that's a `/codex:review` job, not an adversarial review.

---

## `/codex:rescue`

Delegate an *active task* (investigate, fix, refactor) to Codex. Unlike `/codex:review`, this can modify files.

### Flags

- `--background` — run async. Returns a job ID. **Default for long tasks.**
- `--wait` — stream output until done. Good for short rescues you want to watch.
- `--resume` — continue the most recent Codex session (preserves context).
- `--fresh` — start a brand-new session, discarding prior context. Default.
- `--model <name>` — pin a specific Codex model. Defaults to whatever's in `config.toml`.
- `--effort <low|medium|high>` — reasoning budget. Higher = slower but more thorough.

### Prompt pattern

The text after the flags is the task description. Be specific. Codex doesn't have your conversation context with Claude.

Good:
```
/codex:rescue --background --fresh investigate why tests/billing/test_invoice.py::test_proration fails on CI but passes locally; the diff is in the last 3 commits on this branch; check timezone handling first
```

Bad:
```
/codex:rescue fix the bug
```

### Resuming

When `/codex:result <job-id>` shows a Codex session ID, you can resume that session directly inside the `codex` CLI (outside Claude Code) for interactive follow-up — useful when Codex is close but not done.

---

## `/codex:status`

Lists Codex jobs scoped to the current repo. Shows:

- Job ID
- Command (`review` / `adversarial-review` / `rescue`)
- State (running / done / failed / cancelled)
- Started-at, duration

No flags. Run anytime — it's free and read-only.

---

## `/codex:result`

Prints the final stored output of a finished job.

### Usage

```
/codex:result <job-id>
```

Get the job ID from `/codex:status`.

### Output

The complete review or rescue transcript, including the Codex session ID (use it in the `codex` CLI to resume).

---

## `/codex:cancel`

Stops an active background job.

### Usage

```
/codex:cancel <job-id>
```

Cancellation is graceful — Codex finishes the current tool call before exiting. Don't expect instantaneous termination.

### When to cancel

- The job is going down a wrong path obvious from `/codex:status` or partial output.
- You realize the prompt was wrong and want to redo with `--fresh`.
- Cost control: long-running rescues consume your ChatGPT quota.

---

## Common Patterns

### Pre-commit gate

Enable once:
```
/codex:setup --enable-review-gate
```

Now every commit triggers a `/codex:review`. Disable by re-running `/codex:setup` without the flag.

### Long diff, can't wait

```
/codex:review --base main --background
# ... keep coding ...
/codex:status
/codex:result <id>
```

### Continuing a Codex investigation

```
/codex:rescue --resume continue from where you left off; focus on the suspicion about lock ordering
```

### Cancel and redo

```
/codex:cancel <id>
/codex:rescue --background --fresh <better prompt>
```
