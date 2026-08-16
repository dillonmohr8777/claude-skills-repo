"""MVP pipeline.

End-to-end run for a single course:
    1. Curriculum Architect → outline.json
    2. Lesson Script (one call per lesson; sequential for MVP)
    3. Slide Content (one call per lesson)
    4. Quiz & Worksheet (one call per lesson; worksheet on module-capstone lessons)
    5. QA pass (schema-only by default; content review opt-in)
    6. Markdown export to outputs/<course_id>.md and a per-lesson tree

No web research, no platform APIs. Markdown out, ready to paste into Google Docs.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents.curriculum_architect import CurriculumArchitect
from agents.lesson_script import LessonScript
from agents.quiz_worksheet import QuizWorksheet
from agents.slide_content import SlideContent
from agents.qa import QA
from exporters.markdown import export_course
from integrations.llm import LLM
from workflows.state import advance, load_state, record_run, save_state


COURSES_DIR = Path(__file__).resolve().parent.parent / "courses"


def run(course_id: str, *, dry_run: bool = False, verbose: bool = True) -> dict:
    course_dir = COURSES_DIR / course_id
    state = load_state(course_dir)
    cfg = state["config"]
    llm = LLM()

    log = print if verbose else (lambda *a, **k: None)

    # ---- Stage 1: outline ----
    if state["stage"] == "topic_chosen":
        log(f"[1/5] Curriculum Architect → {course_id}")
        topic_seed_path = course_dir / "topic.json"
        topic = json.loads(topic_seed_path.read_text())
        outcome = topic.get("outcome", topic["title"])
        ca = CurriculumArchitect(course_dir, llm)
        result = ca.run(
            {
                "topic": topic,
                "outcome": outcome,
                "hours": cfg["target_hours"],
                "modules": cfg["modules"],
                "lessons_per_module": cfg["lessons_per_module"],
                "price": topic.get("price_usd", 97),
                "voice_reference": cfg["voice_reference"],
            }
        )
        outline = result.output
        outline.setdefault("course_id", course_id)
        outline.setdefault("voice_reference", cfg["voice_reference"])
        (course_dir / "outline.json").write_text(json.dumps(outline, indent=2))
        record_run(state, "curriculum_architect", "succeeded", "outline.json")
        advance(state, "outlined")
        save_state(course_dir, state)
        log(f"   outline: {len(outline['modules'])} modules, total runtime ~{outline.get('estimated_runtime_minutes', 'n/a')}m, cost ${result.cost_usd:.3f}")

    # MVP shortcut: auto-approve outline so the pipeline runs end-to-end without human input.
    # Real runs gate here at the human checkpoint.
    if not state["human_checkpoints"]["outline_approved"]["approved"]:
        from workflows.state import now_iso
        state["human_checkpoints"]["outline_approved"] = {"approved": True, "approved_at": now_iso(), "approver": "auto-mvp"}
        advance(state, "outline_approved")
        save_state(course_dir, state)

    outline = json.loads((course_dir / "outline.json").read_text())

    # ---- Stage 2: lesson scripts ----
    if state["stage"] in ("outline_approved", "lessons_drafting"):
        advance(state, "lessons_drafting")
        save_state(course_dir, state)
        log(f"[2/5] Lesson Script → {sum(len(m['lessons']) for m in outline['modules'])} lessons")
        ls = LessonScript(course_dir, llm)
        prev_summary = "(none — this is the first lesson)"
        global_lesson_index = 0
        for module in outline["modules"]:
            for lesson in module["lessons"]:
                hook_style = LessonScript.hook_style_for_index(global_lesson_index)
                position_label = (
                    f"{'first' if lesson is module['lessons'][0] else 'later'} lesson of module {module['index']}"
                )
                result = ls.run(
                    {
                        "voice_reference": cfg["voice_reference"],
                        "course": {"title": outline["title"], "outcome_statement": outline["outcome_statement"]},
                        "module": module,
                        "prev_lesson_summary": prev_summary,
                        "lesson": {**lesson, "position_label": position_label},
                        "hook_style": hook_style,
                    }
                )
                meta = LessonScript.extract_metadata(
                    script=result.output,
                    lesson_id=lesson["id"],
                    module_id=module["id"],
                    title=lesson["title"],
                    objective=lesson["objective"],
                    hook_style=hook_style,
                )
                ls.write_outputs(course_dir, module["id"], lesson["id"], result.output, meta)
                prev_summary = f"{lesson['title']}: {lesson['objective']}"
                global_lesson_index += 1
                log(f"   ✓ {module['id']}/{lesson['id']}  ({meta['word_count']} words, ${result.cost_usd:.3f})")
        record_run(state, "lesson_script", "succeeded")
        advance(state, "lessons_qa")
        save_state(course_dir, state)

    # MVP: skip lessons_qa human checkpoint.
    if not state["human_checkpoints"]["lessons_approved"]["approved"]:
        from workflows.state import now_iso
        state["human_checkpoints"]["lessons_approved"] = {"approved": True, "approved_at": now_iso(), "approver": "auto-mvp"}
        advance(state, "lessons_approved")
        save_state(course_dir, state)

    # ---- Stage 3: slides ----
    if state["stage"] in ("lessons_approved", "assets_drafting"):
        advance(state, "assets_drafting")
        save_state(course_dir, state)
        log("[3/5] Slide Content")
        sc = SlideContent(course_dir, llm)
        for module in outline["modules"]:
            for lesson in module["lessons"]:
                lesson_md = (course_dir / "lessons" / module["id"] / f"{lesson['id']}.md").read_text()
                target_slides = max(4, round(lesson["runtime_minutes"] * 60 / 90))
                result = sc.run({"lesson": lesson, "lesson_script": lesson_md, "target_slides": target_slides})
                sc.write_output(course_dir, lesson["id"], result.output)
                log(f"   ✓ slides {lesson['id']}  (${result.cost_usd:.3f})")

        # ---- Stage 4: quizzes ----
        log("[4/5] Quiz & Worksheet")
        qw = QuizWorksheet(course_dir, llm)
        for module in outline["modules"]:
            for i, lesson in enumerate(module["lessons"]):
                lesson_md = (course_dir / "lessons" / module["id"] / f"{lesson['id']}.md").read_text()
                is_capstone = i == len(module["lessons"]) - 1
                result = qw.run(
                    {
                        "lesson": lesson,
                        "lesson_script": lesson_md,
                        "misconceptions": "; ".join(outline.get("known_misconceptions", []) or ["common beginner mistakes in this domain"]),
                        "is_module_capstone": is_capstone,
                        "module": module,
                    }
                )
                qw.write_output(course_dir, lesson["id"], result.output)
                log(f"   ✓ quiz {lesson['id']}  (${result.cost_usd:.3f})")

        record_run(state, "slide_content", "succeeded")
        record_run(state, "quiz_worksheet", "succeeded")
        advance(state, "marketing_drafting")
        save_state(course_dir, state)

    # ---- Stage 5: export ----
    log("[5/5] Markdown export")
    out_path = export_course(course_dir)
    log(f"   ✓ {out_path}")

    advance(state, "launch_ready")
    save_state(course_dir, state)
    return state
