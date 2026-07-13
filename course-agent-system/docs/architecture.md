# Architecture

## Mental model

Every agent is a pure function:

```
input.json + prompt.md → output.json
```

That makes the system debuggable, resumable, and cheap to re-run a single stage. The Project Manager Agent is the only stateful component; it reads `state.json` and dispatches the next stage.

## Pipeline

```
topic.json
   ↓ (Curriculum Architect, deep)
outline.json
   ↓ (Lesson Script, balanced × N lessons)
lessons/<m>/<l>.md  +  lessons/<m>/<l>.meta.json
   ↓ (Slide Content, fast × N lessons)
slides/<l>.md
   ↓ (Quiz & Worksheet, fast × N lessons)
assessments/<l>.json
   ↓ (Markdown Exporter)
outputs/<course_id>.md
```

QA runs as a gate after every stage. Schema validation is deterministic (jsonschema); content validation is an LLM call against `prompts/qa_content.md`.

## State machine

Stored in `courses/<id>/state.json`. Stages:

```
research → scored → topic_chosen → outlined → outline_approved
  → lessons_drafting → lessons_qa → lessons_approved
  → assets_drafting → marketing_drafting
  → packaging → launch_ready → live → optimizing
```

Resume = `cli.py run --slug X` reads stage and runs forward.

## Agent contract

Every agent inherits `agents.base.Agent` and sets:

- `agent_id`: stable identifier; used as log key
- `prompt_file`: filename in `prompts/`
- `output_schema`: filename in `schemas/` (or `None` for free-form Markdown)
- `response_format`: `"text"` or `"json"`
- `tier`: `"deep" | "balanced" | "fast"` — overrideable in `config/agents.yaml`
- `temperature`: float
- `system()`: returns the system prompt string

`run(inputs: dict)` does:
1. Render the Jinja template with `inputs`
2. Call the LLM (caching system prompt by default)
3. If JSON, validate against schema; auto-retry once with errors appended to the prompt
4. Log to `logs/<course_id>/<agent_id>-<timestamp>.json`

## Cost model

Lesson generation is the dominant cost. With 5 modules × 4 lessons = 20 lessons:
- 20 lesson scripts × ~3500 tokens out (Sonnet) ≈ ~$1.05
- 20 slide decks × ~1500 tokens out (Haiku) ≈ ~$0.15
- 20 quizzes × ~600 tokens out (Haiku) ≈ ~$0.06
- 1 outline + cache reads ≈ ~$0.20
- **Total per course ≈ $1.50** (rough; varies with input size)

Prompt caching kicks in across the lesson fanout because the system prompt and course context are identical. Hit rate should be 80%+ after the first few lessons.

## Why this stack

- **Python over Next.js for backend:** LLM ecosystem, scraping libs, PDF/PPTX support. Next.js stays for the future dashboard only.
- **Filesystem JSON over SQLite for MVP:** every artifact is git-diffable and pasteable. Move to SQLite when courses > 30.
- **Jinja2 over f-strings:** prompts are the product; templates need StrictUndefined to catch missing variables at render time.
- **Click over Typer:** simpler, more battle-tested, good Rich integration.
- **Anthropic over multi-provider:** the agents themselves call Claude; first-party SDK gets caching and tool use first.

## Open architectural questions

- **Orchestration: agenthub or custom?** Currently custom (mvp_pipeline.py). agenthub gives parallel-agent + judge pattern for free but couples us to its session model. Decide before fanout becomes a bottleneck.
- **Optimization Agent: rebuild or wrap autoresearch-agent?** That skill's "edit → metric → keep-or-revert" loop fits exactly. Try wrapping first.
- **Dashboard: Next.js or Streamlit?** Streamlit ships in a day; Next.js is the production answer. If we never need multi-tenant, Streamlit may be enough.
