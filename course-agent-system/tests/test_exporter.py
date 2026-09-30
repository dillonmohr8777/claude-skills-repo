"""Exporter smoke test.

Sets up a minimal courses/<id>/ tree from the fixture and verifies the markdown
exporter assembles a non-empty file. No LLM calls.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from exporters.markdown import export_course


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def staged_course(tmp_path):
    """Build a courses/<id>/ tree under tmp_path with one fake lesson."""
    course_dir = tmp_path / "courses" / "ai-productivity-os"
    course_dir.mkdir(parents=True)
    outline = json.loads((FIXTURES_DIR / "sample_outline.json").read_text())
    (course_dir / "outline.json").write_text(json.dumps(outline))

    module = outline["modules"][0]
    lesson = module["lessons"][0]

    (course_dir / "lessons" / module["id"]).mkdir(parents=True)
    (course_dir / "lessons" / module["id"] / f"{lesson['id']}.md").write_text(
        "## Beat: Hook\nFake hook.\n## Beat: Promise\nFake promise.\n"
    )
    (course_dir / "slides").mkdir()
    (course_dir / "slides" / f"{lesson['id']}.md").write_text("### Slide 1: Title\n- bullet\n")
    (course_dir / "assessments").mkdir()
    (course_dir / "assessments" / f"{lesson['id']}.json").write_text(
        json.dumps(
            {
                "quiz": {
                    "lesson_id": lesson["id"],
                    "mcq": [
                        {
                            "stem": "Test?",
                            "options": ["a", "b", "c", "d"],
                            "correct_index": 0,
                            "explanations": {"correct": "because"},
                        }
                    ],
                    "short_answer": {"prompt": "Apply X to Y", "rubric": ["clarity", "accuracy"]},
                }
            }
        )
    )
    return course_dir


def test_exporter_produces_markdown(staged_course, monkeypatch):
    # Redirect outputs/ to a temp dir.
    monkeypatch.setattr("exporters.markdown.OUTPUTS_DIR", staged_course.parent.parent / "outputs")
    out_path = export_course(staged_course)
    assert out_path.exists()
    content = out_path.read_text()
    assert "AI Productivity OS" in content
    assert "Why Your ChatGPT Routine" in content
    assert "Q1." in content
