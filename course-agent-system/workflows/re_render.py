"""Re-render a single lesson without re-running the whole pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from agents.lesson_script import LessonScript
from agents.quiz_worksheet import QuizWorksheet
from agents.slide_content import SlideContent
from integrations.llm import LLM


REPO_ROOT = Path(__file__).resolve().parent.parent
COURSES_DIR = REPO_ROOT / "courses"


def re_render_lesson(course_id: str, lesson_id: str) -> None:
    course_dir = COURSES_DIR / course_id
    outline = json.loads((course_dir / "outline.json").read_text())
    state = json.loads((course_dir / "state.json").read_text())
    cfg = state["config"]
    llm = LLM()

    target_module = None
    target_lesson = None
    target_index = -1
    global_idx = 0
    for module in outline["modules"]:
        for lesson in module["lessons"]:
            if lesson["id"] == lesson_id:
                target_module, target_lesson, target_index = module, lesson, global_idx
                break
            global_idx += 1
        if target_lesson:
            break
    if not target_lesson:
        raise ValueError(f"Lesson {lesson_id} not found in outline")

    hook_style = LessonScript.hook_style_for_index(target_index)
    position_label = (
        f"{'first' if target_lesson is target_module['lessons'][0] else 'later'} lesson of module {target_module['index']}"
    )

    ls = LessonScript(course_dir, llm)
    result = ls.run(
        {
            "voice_reference": cfg["voice_reference"],
            "course": {"title": outline["title"], "outcome_statement": outline["outcome_statement"]},
            "module": target_module,
            "prev_lesson_summary": "(re-render: previous-lesson context omitted)",
            "lesson": {**target_lesson, "position_label": position_label},
            "hook_style": hook_style,
        }
    )
    meta = LessonScript.extract_metadata(
        script=result.output,
        lesson_id=target_lesson["id"],
        module_id=target_module["id"],
        title=target_lesson["title"],
        objective=target_lesson["objective"],
        hook_style=hook_style,
    )
    ls.write_outputs(course_dir, target_module["id"], target_lesson["id"], result.output, meta)

    sc = SlideContent(course_dir, llm)
    target_slides = max(4, round(target_lesson["runtime_minutes"] * 60 / 90))
    s_result = sc.run({"lesson": target_lesson, "lesson_script": result.output, "target_slides": target_slides})
    sc.write_output(course_dir, target_lesson["id"], s_result.output)

    qw = QuizWorksheet(course_dir, llm)
    is_capstone = target_lesson is target_module["lessons"][-1]
    q_result = qw.run(
        {
            "lesson": target_lesson,
            "lesson_script": result.output,
            "misconceptions": "common beginner mistakes in this domain",
            "is_module_capstone": is_capstone,
            "module": target_module,
        }
    )
    qw.write_output(course_dir, target_lesson["id"], q_result.output)
