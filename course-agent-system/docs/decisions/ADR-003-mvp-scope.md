# ADR-003: MVP scope and human checkpoints

**Date:** 2026-04-26
**Status:** accepted

## Context

The full system has 12 agents and 4 human checkpoints. Shipping all of that before we've validated the core loop is wasteful. We need a defensible MVP boundary.

## Decision

MVP includes 5 agents:
1. Curriculum Architect
2. Lesson Script
3. Slide Content
4. Quiz & Worksheet
5. QA (schema-only mode by default; content review opt-in)

Excluded from MVP (built next, post-validation):
- Opportunity Research, Topic Scoring (need search/Reddit/YouTube APIs)
- Landing Page, Publishing Prep
- Course Packaging (per-platform schemas)
- Optimization (needs live analytics)
- Project Manager (custom orchestration; running mvp_pipeline.py linearly is enough for now)

Human checkpoints in MVP are **auto-approved** (`approver = "auto-mvp"`). Real human gates wire in once a real course is being shipped.

## Consequences

- MVP runs end-to-end on a single ANTHROPIC_API_KEY with no other credentials.
- Output is Markdown ready to paste into Google Docs; production exporters (Notion, Drive, Gumroad) come later.
- We discover voice and prompt issues against real course output before adding complexity.

## Alternatives considered

- **Ship all 12 agents at once** — rejected; we'd be shipping research and optimization without the loop validating they're useful.
- **MVP = outline only** — rejected; we don't get to test lesson voice or QA gates without going further.
