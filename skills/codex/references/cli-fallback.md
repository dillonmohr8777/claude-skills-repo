# Codex CLI Fallback (no plugin)

When the `codex-plugin-cc` plugin can't be installed (locked-down Claude Code, corporate policy, air-gapped environment with a self-hosted relay), invoke `codex` directly via Bash. You lose the slash-command UX and background job tracking, but the underlying agent is the same.

## Prerequisites

```bash
# Install
npm install -g @openai/codex
# or
brew install --cask codex

# Authenticate once interactively — pick "Sign in with ChatGPT"
codex
```

After the first interactive run, credentials live in `~/.codex/` and subsequent `codex exec` calls run non-interactively.

## Non-interactive invocation

`codex exec` runs Codex headlessly with a single prompt. Output goes to stdout.

```bash
codex exec "review the staged diff for correctness, security, and edge cases. respond with severity-tagged findings (BLOCK/CONCERN/NIT)."
```

Codex inherits the current working directory, so it can read files, run tools, and (if approval policy allows) modify code in the repo where you launch it.

### Useful flags

Exact flag names can shift between Codex releases — run `codex exec --help` to confirm. Commonly available:

- `--model <name>` — pin a specific model (otherwise uses `config.toml`'s default).
- `--cd <path>` — run Codex in a different directory than the current shell.
- Approval / sandbox controls — Codex defaults to asking before destructive actions. For one-shot review prompts that only read, you can confirm safety up-front in the prompt itself ("read-only; do not modify any files").

When in doubt about flags, check `~/.codex/config.toml` and set defaults there rather than passing flags every call:

```toml
# ~/.codex/config.toml
model = "gpt-5-codex"          # example — use whatever your plan supports
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

## Patterns That Replace Plugin Commands

### Replace `/codex:review`

```bash
# uncommitted changes
git diff HEAD | codex exec "review this diff. flag bugs, security issues, and obvious quality problems. severity-tag every finding."

# vs main
git diff main...HEAD | codex exec "review this diff for merge into main. severity-tag every finding."
```

Or let Codex read the working tree itself:

```bash
codex exec "review uncommitted changes in this repo (git diff + git diff --cached). severity-tag every finding."
```

### Replace `/codex:adversarial-review`

```bash
codex exec "adversarial design review of the changes on this branch vs main. read-only — do not modify files. challenge tradeoffs, surface assumptions the author treated as obvious, and propose at least two alternatives. focus areas: <your focus here>."
```

### Replace `/codex:rescue` (foreground)

```bash
codex exec "investigate why tests/billing/test_invoice.py::test_proration fails on CI but passes locally. the relevant diff is the last 3 commits. check timezone handling first. fix it if you find the cause."
```

### Replace `/codex:rescue --background`

There's no built-in job manager outside the plugin. Use a normal background shell:

```bash
nohup codex exec "investigate the flaky billing tests; fix if you find the cause" \
  > .codex-rescue.log 2>&1 &

echo $! > .codex-rescue.pid
```

Check progress:
```bash
tail -f .codex-rescue.log
```

Stop:
```bash
kill "$(cat .codex-rescue.pid)"
```

This is strictly worse than `/codex:status` / `/codex:result` / `/codex:cancel` — there's no per-repo job index, no session ID surfacing, no graceful cancel. Use the plugin if you can.

## When Claude Should Invoke This Itself

Claude can run `codex exec` via the Bash tool when the user has authorized Bash and the task fits the "delegate to Codex" pattern from `SKILL.md`. Default to:

1. **Asking first** if the user hasn't already said "use codex" — Codex calls cost money on the user's ChatGPT plan.
2. **Foreground for short prompts**, never background from inside Claude Code unless the user asked for it (background processes that outlive the Claude session are surprising).
3. **Quoting the prompt carefully** — `codex exec "<prompt>"` is shell-evaluated. Use single quotes or a heredoc when the prompt itself contains double quotes or backticks.

```bash
codex exec "$(cat <<'EOF'
Review the diff between origin/main and HEAD for security issues only.
Read-only — do not modify any files.
Severity-tag every finding.
EOF
)"
```

## Limits

Without the plugin you don't get:

- A repo-scoped job index (`/codex:status`).
- Pre-commit review gates (`--enable-review-gate`).
- Resumable session IDs surfaced in a structured way (you can still resume in the `codex` interactive UI).
- Codex's adversarial-review system prompt — you have to write that prompt yourself, as in the example above.

If you need any of these, install the plugin.
