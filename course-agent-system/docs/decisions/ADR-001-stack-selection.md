# ADR-001: Stack selection

**Date:** 2026-04-26
**Status:** accepted

## Context

We need to ship an autonomous course-creation pipeline fast (MVP within days), with a path to a Next.js dashboard and platform integrations later. Two main forks: backend language (Python vs Node) and storage (filesystem vs DB).

## Decision

- **Python 3.12** as the backend language for all agent + workflow code.
- **Anthropic Claude** as the sole LLM provider for v0; tier across Opus 4.7 / Sonnet 4.6 / Haiku 4.5.
- **Filesystem JSON + Markdown** as the storage layer for MVP. Move to SQLite when course count exceeds ~30.
- **Click** for the CLI; **Jinja2 with StrictUndefined** for prompt templating.
- **Next.js 15 + Tailwind + shadcn** for the eventual dashboard, talking to a FastAPI sidecar.

## Consequences

- Python's LLM/scraping/PDF ecosystem is broader. Codex (or any other tool) can extend with minimal friction.
- Filesystem storage means every artifact is git-diffable. Diffs become the audit log.
- Single-provider lock-in is a risk; mitigated by routing all calls through `integrations/llm.py` so swapping providers means changing one file.

## Alternatives considered

- **Node + Next.js everywhere** — rejected; LLM tooling weaker, scraping libs weaker, no significant benefit.
- **Multi-provider from day 1** — rejected; abstraction tax not worth paying until we have a reason to switch.
- **SQLite from day 1** — rejected; filesystem JSON is faster to debug for MVP. Migration is straightforward.
