"""Lesson Script Agent.

Takes a single lesson node from the outline (plus course context) and produces
a Markdown teaching script with all 9 required beats.
"""

from __future__ import annotations

import re
from pathlib import Path

from agents.base import Agent, AgentResult


HOOK_STYLE_ROTATION = [
    "story",
    "statistic",
    "contrarian-question",
    "before-after",
    "mistake-confession",
    "scenario",
    "demo-tease",
]


class LessonScript(Agent):
    agent_id = "lesson_script"
    prompt_file = "lesson_script.md"
    output_schema = None  # script is Markdown; sidecar metadata generated separately
    response_format = "text"
    tier = "balanced"
    temperature = 0.7

    def system(self) -> str:
        return (
            "You are an experienced course instructor writing engaging, concrete lesson "
            "scripts. Your voice is direct, specific, and example-rich. You never use filler."
        )

    @staticmethod
    def hook_style_for_index(index: int) -> str:
        return HOOK_STYLE_ROTATION[index % len(HOOK_STYLE_ROTATION)]

    @staticmethod
    def extract_metadata(script: str, lesson_id: str, module_id: str, title: str, objective: str, hook_style: str) -> dict:
        beat_pattern = re.compile(r"^## Beat: (.+)$", re.MULTILINE)
        beats_found = beat_pattern.findall(script)
        word_count = len(script.split())
        verify_markers = re.findall(r"\[VERIFY: ([^\]]+)\]", script)
        return {
            "lesson_id": lesson_id,
            "module_id": module_id,
            "title": title,
            "objective": objective,
            "hook_style": hook_style,
            "word_count": word_count,
            "estimated_runtime_minutes": max(3, round(word_count / 130)),
            "beats": [{"name": b, "present": True} for b in beats_found],
            "verify_markers": verify_markers,
        }

    def write_outputs(self, course_dir: Path, module_id: str, lesson_id: str, script: str, metadata: dict) -> tuple[Path, Path]:
        out_dir = course_dir / "lessons" / module_id
        out_dir.mkdir(parents=True, exist_ok=True)
        md_path = out_dir / f"{lesson_id}.md"
        meta_path = out_dir / f"{lesson_id}.meta.json"
        md_path.write_text(script)
        import json
        meta_path.write_text(json.dumps(metadata, indent=2))
        return md_path, meta_path
