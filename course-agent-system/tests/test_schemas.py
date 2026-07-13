"""Schema validation tests. No API key required.

Run with:  uv run pytest tests/test_schemas.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _validator(schema_filename: str) -> Draft202012Validator:
    schema = json.loads((SCHEMAS_DIR / schema_filename).read_text())
    return Draft202012Validator(schema)


def test_all_schemas_load():
    for path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)


def test_sample_outline_validates():
    outline = json.loads((FIXTURES_DIR / "sample_outline.json").read_text())
    v = _validator("outline.schema.json")
    errors = list(v.iter_errors(outline))
    assert not errors, f"sample_outline.json failed schema: {errors}"


def test_sample_topic_validates_minimally():
    topic = json.loads((FIXTURES_DIR / "sample_topic.json").read_text())
    # The fixture is a CLI seed (subset of the research-agent topic schema), so
    # we only validate the fields that overlap.
    v = _validator("topic.schema.json")
    # Add minimum required fields the schema demands but the seed lacks.
    enriched = {
        **topic,
        "demand_signal": {"level": "medium", "evidence": "fixture"},
        "production_difficulty": 3,
        "estimated_price_usd": topic.get("price_usd", 97),
    }
    enriched.pop("price_usd", None)
    enriched.pop("outcome", None)
    errors = list(v.iter_errors(enriched))
    assert not errors, f"enriched topic fixture failed schema: {errors}"


def test_state_schema_initial():
    from workflows.state import initial_state
    s = initial_state(
        "ai-productivity-os",
        modules=5,
        lessons_per_module=4,
        target_hours=4.0,
        voice_reference="test-voice",
        qa_strictness="normal",
    )
    v = _validator("state.schema.json")
    errors = list(v.iter_errors(s))
    assert not errors, f"initial_state failed schema: {errors}"


@pytest.mark.parametrize("filename", [
    "topic.schema.json",
    "scored_topic.schema.json",
    "outline.schema.json",
    "lesson.schema.json",
    "slide.schema.json",
    "quiz.schema.json",
    "state.schema.json",
    "qa_result.schema.json",
])
def test_each_schema_present(filename):
    assert (SCHEMAS_DIR / filename).exists(), f"missing schema: {filename}"
