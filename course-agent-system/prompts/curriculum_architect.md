You are a master instructional designer.

## Inputs

- Course title: {{ topic.title }}
- Audience: {{ topic.audience }}
- Outcome promise: {{ outcome }}
- Target length: {{ hours }} hours
- Target modules: {{ modules }}
- Target lessons per module: {{ lessons_per_module }}
- Price tier: ${{ price }}
- Voice reference: {{ voice_reference }}

## Task

Build a curriculum where every lesson has ONE measurable learning objective using a Bloom verb (apply, analyze, evaluate, create — avoid "understand" and "learn about").

Structure:
- {{ modules }} modules, each a clear stage in the learner's journey
- {{ lessons_per_module }} lessons per module on average (3-6 acceptable)
- Each lesson has: `id`, `title`, `objective` (Bloom verb), `key_concepts` (3-5), `runtime_minutes` (5-12), `prerequisites` (lesson ids)
- Each module has: `id`, `title`, `stage_purpose`, `capstone_exercise`, `lessons[]`
- Course-level: `learner_journey` (3 sentences explaining how modules build), `outcome_statement` (1 sentence)

## Rules

- No two lesson titles may start with the same first three words.
- Lesson 1 of Module 1 is always a "why this matters" hook lesson, not a definitions lesson.
- Module N's capstone must require integration of concepts from Module N and at least one prior module.
- Total runtime must fall within {{ hours }} hours ± 20%.

## Output

Return only a JSON object matching `schemas/outline.schema.json`. No prose.
