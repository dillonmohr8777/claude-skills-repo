# ADR-002: Agent contract and base class

**Date:** 2026-04-26
**Status:** accepted

## Context

12 agents need to share infrastructure (LLM calls, retries, logging, schema validation) without coupling. We want adding a new agent to be a 5-file change, not a refactor.

## Decision

Every agent inherits `agents.base.Agent` and declares:

- `agent_id`, `prompt_file`, `output_schema`, `response_format`, `tier`, `temperature`, `system()`.

The base class provides:
- Jinja2 prompt rendering (StrictUndefined; missing variables fail loudly)
- LLM dispatch via `integrations/llm.py` (caching, retry, cost tracking)
- JSON-Schema validation with **one auto-retry** on schema failure (the schema errors are appended to the user prompt)
- Per-call logging to `logs/<course_id>/<agent_id>-<timestamp>.json`

## Consequences

- Adding an agent is a 5-file change: prompt, schema (optional), Python class, config row, workflow integration.
- Auto-retry handles transient model misformatting without bloating prompt files with fallback instructions.
- All cost data lands in one log format, making cost dashboards trivial later.

## Alternatives considered

- **Decorator-based agents** — rejected; class-based is more discoverable for a pipeline with this many distinct agent types.
- **Pydantic models as the schema source of truth** — deferred; JSON Schema files are easier to share with non-Python tooling (Codex, dashboard, MCP server).
