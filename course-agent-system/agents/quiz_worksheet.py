"""Quiz and Worksheet Agent.

Per lesson: 3 MCQs + 1 short-answer prompt with rubric.
For module-capstone lessons: also produces a worksheet with a rubric.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents.base import Agent, AgentResult


class QuizWorksheet(Agent):
    agent_id = "quiz_worksheet"
    prompt_file = "quiz_worksheet.md"
    output_schema = "quiz.schema.json"
    response_format = "json"
    tier = "fast"
    temperature = 0.4

    def system(self) -> str:
        return (
            "You are an assessment designer. Distractors must reflect real beginner "
            "misconceptions, not random wrong answers. You test the stated objective, "
            "not trivia."
        )

    def write_output(self, course_dir: Path, lesson_id: str, payload: dict) -> Path:
        out_dir = course_dir / "assessments"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{lesson_id}.json"
        path.write_text(json.dumps(payload, indent=2))
        return path
