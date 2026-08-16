"""Markdown exporter.

Concatenates outline + lessons + slides + quizzes into a single Google-Doc-ready
Markdown file at outputs/<course_id>.md, plus a per-lesson tree at outputs/<course_id>/.
"""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPO_ROOT / "outputs"


def export_course(course_dir: Path) -> Path:
    course_id = course_dir.name
    outline = json.loads((course_dir / "outline.json").read_text())
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = OUTPUTS_DIR / course_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-lesson tree (mirrors courses/<id>/lessons/...).
    for module in outline["modules"]:
        mod_dir = out_dir / module["id"]
        mod_dir.mkdir(exist_ok=True)
        for lesson in module["lessons"]:
            for kind, src_subpath in [
                ("lesson", f"lessons/{module['id']}/{lesson['id']}.md"),
                ("slides", f"slides/{lesson['id']}.md"),
                ("quiz",   f"assessments/{lesson['id']}.json"),
            ]:
                src = course_dir / src_subpath
                if src.exists():
                    dst = mod_dir / f"{lesson['id']}.{kind}{src.suffix}"
                    dst.write_text(src.read_text())

    # Single concatenated file.
    parts: list[str] = []
    parts.append(f"# {outline['title']}\n")
    parts.append(f"**Audience:** {outline['audience']}\n")
    parts.append(f"**Outcome:** {outline['outcome_statement']}\n")
    parts.append("\n## Learner Journey\n\n" + outline.get("learner_journey", ""))
    parts.append("\n\n---\n\n")

    for module in outline["modules"]:
        parts.append(f"# Module {module['index']}: {module['title']}\n")
        parts.append(f"**Stage purpose:** {module['stage_purpose']}\n")
        parts.append(f"\n**Capstone:** {module['capstone_exercise']}\n\n")
        for lesson in module["lessons"]:
            parts.append(f"## {lesson['title']}\n")
            parts.append(f"*Objective:* {lesson['objective']}  · *Runtime:* {lesson['runtime_minutes']}m\n\n")

            lesson_md = course_dir / "lessons" / module["id"] / f"{lesson['id']}.md"
            if lesson_md.exists():
                parts.append("### Script\n\n" + lesson_md.read_text() + "\n")

            slide_md = course_dir / "slides" / f"{lesson['id']}.md"
            if slide_md.exists():
                parts.append("\n### Slides\n\n" + slide_md.read_text() + "\n")

            quiz_path = course_dir / "assessments" / f"{lesson['id']}.json"
            if quiz_path.exists():
                quiz = json.loads(quiz_path.read_text())
                parts.append("\n### Quiz\n\n")
                for i, q in enumerate(quiz.get("quiz", {}).get("mcq", []), 1):
                    parts.append(f"**Q{i}.** {q['stem']}\n\n")
                    for j, opt in enumerate(q["options"]):
                        marker = "✓" if j == q["correct_index"] else " "
                        parts.append(f"- [{marker}] {opt}\n")
                    parts.append(f"\n*Why correct:* {q['explanations']['correct']}\n\n")
                sa = quiz.get("quiz", {}).get("short_answer")
                if sa:
                    parts.append(f"**Short answer:** {sa['prompt']}\n\n")
                    parts.append("*Rubric:*\n")
                    for c in sa["rubric"]:
                        parts.append(f"- {c}\n")
                ws = quiz.get("worksheet")
                if ws:
                    parts.append(f"\n### Worksheet — {ws['title']}\n\n{ws['instructions']}\n\n")
                    for t in ws.get("tasks", []):
                        parts.append(f"- ({t['time_estimate_min']}m) {t['task']}\n")
                    parts.append(f"\n**Deliverable:** {ws['deliverable']}\n")

            parts.append("\n---\n\n")

    final = OUTPUTS_DIR / f"{course_id}.md"
    final.write_text("".join(parts))

    # Manifest of every file produced.
    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(REPO_ROOT))
        except ValueError:
            return str(p)

    manifest = {
        "course_id": course_id,
        "single_file": _rel(final),
        "tree": _rel(out_dir),
        "module_count": len(outline["modules"]),
        "lesson_count": sum(len(m["lessons"]) for m in outline["modules"]),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return final
