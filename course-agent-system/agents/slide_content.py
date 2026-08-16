"""Slide Content Agent.

Converts a lesson script (Markdown) into slide-by-slide copy: title, bullets,
speaker notes, visual cue.
"""

from __future__ import annotations

from pathlib import Path

from agents.base import Agent


class SlideContent(Agent):
    agent_id = "slide_content"
    prompt_file = "slide_content.md"
    output_schema = None  # Markdown output; structured slide.schema.json sidecar can be derived later
    response_format = "text"
    tier = "fast"
    temperature = 0.5

    def system(self) -> str:
        return (
            "You are a slide designer who compresses lesson scripts into deck copy. "
            "One idea per slide. No wall-of-text. You write speaker notes the instructor "
            "actually says — not paraphrases of the bullets."
        )

    def write_output(self, course_dir: Path, lesson_id: str, slides_md: str) -> Path:
        out_dir = course_dir / "slides"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{lesson_id}.md"
        path.write_text(slides_md)
        return path
