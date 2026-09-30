# Claude Code conventions for `course-agent-system/`

This file is read at the start of every session. Keep it short and action-oriented.

## What this project is

An autonomous pipeline that takes a topic and produces a sellable digital course. 12 specialized agents (5 live in MVP), 4 human checkpoints, Markdown out by default.

## Working rules

- **Edit prompts in `prompts/*.md`, not in Python.** Agent classes are thin wrappers; prompts are the product.
- **Every artifact has a JSON Schema in `schemas/`.** Touch the schema before changing artifact shape.
- **Add new agents by mirroring `agents/curriculum_architect.py`.** Set `agent_id`, `prompt_file`, `output_schema`, `tier`.
- **Tier choices live in `config/agents.yaml`** — don't hardcode model IDs in agent classes.
- **Cost matters.** Lessons fan out 20+ calls. Use `tier: fast` for fanout work; `tier: deep` only for whole-course reasoning.

## File ownership

- `integrations/llm.py` — single LLM entry point. Adds caching, retry, cost tracking. Don't bypass.
- `agents/base.py` — base class. JSON-Schema validation + auto-retry on failure happens here.
- `workflows/mvp_pipeline.py` — end-to-end run; gateway to all agents.
- `cli.py` — Click commands; thin shell over workflows.

## Commands

```bash
uv sync                                    # install deps
uv run pytest                              # tests (no API key required)
uv run python cli.py new --slug X ...      # scaffold a course
uv run python cli.py run --slug X          # execute pipeline
uv run python cli.py status --slug X       # state inspection
```

## Don't

- Don't add new top-level folders without updating README's "Project layout" table.
- Don't write fake testimonials, bios, or stats. Use `[BRACKETED_PLACEHOLDER]` so QA catches them.
- Don't skip schema validation by writing JSON files directly. Go through an Agent class.
- Don't add backwards-compat shims for prompt or schema changes. Bump versions, migrate forward.

## Model IDs (locked)

- `deep` → `claude-opus-4-7`
- `balanced` → `claude-sonnet-4-6`
- `fast` → `claude-haiku-4-5-20251001`

If newer models ship, update `integrations/llm.py:MODEL_TIERS` and bump `pyproject.toml` version.

## Decisions log

Architecture decisions go in `docs/decisions/ADR-NNN-*.md`. Never amend an existing ADR; supersede with a new one.
