# Course Agent System

Autonomous pipeline that turns a topic into a sellable digital course. 12 specialized agents, 4 human checkpoints, Markdown out for the MVP, platform packaging in the advanced version.

## Status

**MVP shipped.** 5 working agents, end-to-end CLI, Markdown export, schema-validated artifacts. Drop in an `ANTHROPIC_API_KEY` and run a course.

## Quickstart

```bash
# 1. Install (using uv — pip works too)
uv sync

# 2. Configure
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=...

# 3. Scaffold a course
uv run python cli.py new \
  --slug ai-productivity-os \
  --title "AI Productivity OS: Build Your Personal Automation Stack in 14 Days" \
  --audience "Knowledge workers and solopreneurs comfortable with ChatGPT but stuck below their potential" \
  --modules 5 --lessons-per-module 4 --target-hours 4 --price 197

# 4. Run the pipeline
uv run python cli.py run --slug ai-productivity-os

# 5. Read the export
open outputs/ai-productivity-os.md
```

## What gets produced

For each course, in `courses/<slug>/`:

- `outline.json` — modules → lessons → objectives (Bloom verbs)
- `lessons/<module>/<lesson>.md` — full teaching scripts (~1000 words each)
- `lessons/<module>/<lesson>.meta.json` — beat detection + word count + verify markers
- `slides/<lesson>.md` — slide-by-slide copy with speaker notes
- `assessments/<lesson>.json` — 3 MCQs + short-answer; worksheets on capstones
- `state.json` — pipeline state machine + checkpoint approvals
- `topic.json` — seed topic for re-runs

In `outputs/<slug>.md`: a single concatenated Markdown file ready to paste into Google Docs.

## Architecture

```
topic → curriculum → lessons → slides → quizzes → markdown export
              ↑                    ↑
        QA gates here     QA gates here
```

12 agents total, mapped in `prompts/` (one Markdown file each) and `agents/` (one Python class each). MVP implements 5; the rest are spec-ready for next phase.

| Agent | Status | Tier | Purpose |
|---|---|---|---|
| Curriculum Architect | live | deep (Opus 4.7) | Build the outline |
| Lesson Script | live | balanced (Sonnet 4.6) | Write teaching scripts |
| Slide Content | live | fast (Haiku 4.5) | Convert script → slides |
| Quiz & Worksheet | live | fast | Assessments per lesson |
| QA | live | balanced | Schema + content review |
| Opportunity Research | spec only | balanced | Find profitable topics |
| Topic Scoring | spec only | balanced | Rank topics |
| Landing Page | spec only | deep | Sales copy |
| Publishing Prep | spec only | balanced | Launch assets |
| Course Packaging | spec only | fast | Platform manifests |
| Optimization | spec only | deep | Performance recos |
| Project Manager | spec only | fast | Orchestrator |

## Tests

```bash
uv run pytest                 # all tests, no API key needed
uv run pytest tests/test_schemas.py     # JSON Schema validation
uv run pytest tests/test_prompts.py     # template rendering
uv run pytest tests/test_exporter.py    # markdown export
```

## Project layout

```
course-agent-system/
├── agents/         # Python agent classes (one per prompt)
├── prompts/        # 12 Jinja2 prompt templates
├── schemas/        # JSON Schema for every artifact
├── workflows/      # Pipelines: mvp_pipeline, re_render, state machine
├── exporters/      # Markdown (live) + Google Docs / Notion / Gumroad (next)
├── integrations/   # llm.py (Anthropic wrapper); search/reddit/youtube next
├── config/         # agents.yaml, qa.yaml — model + strictness knobs
├── courses/        # one folder per course (outline, lessons, slides, etc.)
├── outputs/        # Markdown exports
├── tests/          # pytest suite
└── docs/           # architecture, ADRs, contributor guide
```

## Roadmap

- [x] MVP: outline → lessons → slides → quizzes → markdown
- [ ] Opportunity Research + Topic Scoring (Serper + Reddit + YouTube)
- [ ] Landing Page + Publishing Prep
- [ ] Course Packaging (Gumroad → Teachable → Udemy)
- [ ] Optimization Agent (analytics → ranked recos)
- [ ] Next.js dashboard (read-only viewer + checkpoint approvals)
- [ ] Google Drive + Notion exporters
- [ ] Image gen for slides + thumbnails

See `docs/architecture.md` for design rationale.
