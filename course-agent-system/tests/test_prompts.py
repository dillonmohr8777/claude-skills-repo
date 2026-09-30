"""Smoke tests that every prompt template renders without StrictUndefined errors.

Doesn't call the LLM. Just ensures each prompt accepts the expected variables.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.base import _jinja


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


PROMPT_INPUTS = {
    "opportunity_research.md": {"domain": "AI productivity", "audience": "knowledge workers", "price_band": "$97-197", "research_data": "..."},
    "topic_scoring.md": {"topics": "[]"},
    "curriculum_architect.md": {
        "topic": {"title": "X", "audience": "Y"},
        "outcome": "outcome",
        "hours": 4,
        "modules": 5,
        "lessons_per_module": 4,
        "price": 97,
        "voice_reference": "voice",
    },
    "lesson_script.md": {
        "voice_reference": "voice",
        "course": {"title": "T", "outcome_statement": "O"},
        "module": {"index": 1, "title": "M", "stage_purpose": "S"},
        "prev_lesson_summary": "none",
        "lesson": {"title": "L", "objective": "Obj", "key_concepts": ["a"], "runtime_minutes": 8, "position_label": "first lesson of module 1"},
        "hook_style": "story",
    },
    "slide_content.md": {"lesson": {"title": "L", "runtime_minutes": 8}, "target_slides": 6, "lesson_script": "..."},
    "quiz_worksheet.md": {
        "lesson": {"title": "L", "objective": "Obj", "key_concepts": ["a"]},
        "lesson_script": "...",
        "misconceptions": "...",
        "is_module_capstone": False,
        "module": {"title": "M"},
    },
    "landing_page.md": {
        "outline": {"title": "T", "outcome_statement": "O"},
        "audience": "A",
        "price": 197,
        "module_outcomes": [],
        "objections": "...",
        "voice_reference": "voice",
    },
    "publishing_prep.md": {
        "outline": {"title": "T", "outcome_statement": "O"},
        "price": 197,
        "pain_quotes": "...",
        "module_outcomes": [],
        "launch_date": "2026-05-15",
        "voice_reference": "voice",
    },
    "course_packaging.md": {"manifest": "{}", "platform": "gumroad", "platform_schema": "{}"},
    "optimization.md": {
        "outline": {"title": "T"},
        "window_days": 30,
        "analytics_data": "{}",
        "student_reviews": "[]",
        "refund_reasons": "[]",
        "landing_analytics": "{}",
    },
    "qa_content.md": {"stage": "outline", "voice_reference": "voice", "strictness": "normal", "artifact": "{}", "stage_context": "{}"},
    "project_manager.md": {"state": "{}", "logs": "[]", "agents": "{}", "checkpoints": "{}"},
}


@pytest.mark.parametrize("prompt_filename,inputs", list(PROMPT_INPUTS.items()))
def test_prompt_renders(prompt_filename, inputs):
    tmpl = _jinja.get_template(prompt_filename)
    rendered = tmpl.render(**inputs)
    assert rendered.strip(), f"{prompt_filename} rendered empty"
    # Must contain at least one of the input keys to confirm interpolation happened.
    # (Some keys are deeply nested; we check that the file isn't suspiciously small.)
    assert len(rendered) > 200


def test_all_12_prompts_present():
    expected = set(PROMPT_INPUTS.keys()) | {"qa_schema.md"}
    actual = {p.name for p in PROMPTS_DIR.glob("*.md")}
    assert expected.issubset(actual), f"missing prompts: {expected - actual}"
