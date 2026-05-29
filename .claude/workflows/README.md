# Dynamic Workflows

Reusable scaffolding for Claude Code's **Dynamic Workflows** — the built-in
feature (research preview) that lets Claude write a JavaScript orchestration
script and fan a task out across many subagents running in the background.

> **This is a native Claude Code feature, not a downloadable skill.** There is
> nothing to install to get the capability. This folder gives you (a) a setup
> guide and (b) ready-to-paste *trigger prompts* that reliably spawn good
> workflows for common heavy tasks.

## Requirements

- Claude Code **v2.1.154+**
- Any paid plan (Pro / Max / Team / Enterprise), Anthropic API, or Bedrock /
  Vertex AI / Microsoft Foundry
- A model that supports `xhigh` effort (e.g. **Opus 4.8**) if you want
  `ultracode`

## Enable it

On **Pro**, turn it on in `/config` → **Dynamic workflows**. On other plans it's
on by default. Then pick how Claude decides to use it:

| You want… | Do this |
| :-- | :-- |
| One task as a workflow | Put the word **`workflow`** anywhere in your prompt |
| Claude to auto-orchestrate every substantive task | `/effort ultracode` (this is the tweet's "/ultracode": `xhigh` effort **+** automatic workflow orchestration) |
| A prebuilt one | `/deep-research <question>` |

`/effort ultracode` lasts for the current session and resets on a new one. Drop
back to routine work with `/effort high`.

### Turn it off

- `/config` → toggle **Dynamic workflows** off, **or**
- `"disableWorkflows": true` in `~/.claude/settings.json`, **or**
- `CLAUDE_CODE_DISABLE_WORKFLOWS=1`

## How a run works

A workflow is a JS script the runtime executes in an isolated environment while
your session stays responsive. Intermediate results live in script variables,
not Claude's context — only the final answer lands back in your chat.

- Up to **16 concurrent** agents (fewer on low-core machines), **1,000 total**
  per run.
- Subagents always run in `acceptEdits` and inherit your tool allowlist,
  regardless of your session's permission mode. **Add the shell/MCP commands
  agents will need to your allowlist before a long run** to avoid mid-run
  prompts.
- No mid-run user input and no direct filesystem/shell access from the script
  itself — the agents do the reading, writing, and running; the script just
  coordinates them.

## Watch & manage

- `/workflows` — list running/completed runs; Enter to open the progress view.
- In the progress view: `↑/↓` select, `Enter/→` drill in, `p` pause/resume,
  `x` stop, `r` restart an agent, **`s` save the run's script as a command**.

## Save a good run for reuse

When a run does what you wanted, `/workflows` → select it → press **`s`** →
choose a location:

- `.claude/workflows/` (this folder) — shared with everyone who clones the repo
- `~/.claude/workflows/` — personal, available in every project

The saved script becomes a `/<name>` command in future sessions. If a project
and personal workflow share a name, the project one wins.

> Saved `.js` scripts will appear in this folder after you save them. The
> templates below are the *prompts you paste* to generate those runs in the
> first place — they don't require knowing the internal script API.

## Recipes (trigger-prompt templates)

Each file in [`templates/`](./templates) is a copy-paste prompt tuned to spawn a
high-quality workflow, plus notes on the phases it tends to run and tips.

| Recipe | Use it for |
| :-- | :-- |
| [`codebase-audit.md`](./templates/codebase-audit.md) | Repo-wide bug / security / convention sweep |
| [`large-migration.md`](./templates/large-migration.md) | Mechanical change across dozens–hundreds of files |
| [`research-verification.md`](./templates/research-verification.md) | Research a question with sources cross-checked against each other |
| [`plan-from-angles.md`](./templates/plan-from-angles.md) | Draft a hard plan from several independent angles, then converge |

## Cost note

A workflow spawns many agents, so one run can use meaningfully more tokens than
doing the task in conversation. Check `/model` before a large run, and ask
Claude to route lighter phases to a smaller model.
