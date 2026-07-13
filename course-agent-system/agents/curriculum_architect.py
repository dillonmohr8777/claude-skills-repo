"""Curriculum Architect Agent.

Takes a topic + audience + length and produces a full course outline:
  modules → lessons → learning objectives + Bloom verbs.
"""

from __future__ import annotations

from agents.base import Agent


class CurriculumArchitect(Agent):
    agent_id = "curriculum_architect"
    prompt_file = "curriculum_architect.md"
    output_schema = "outline.schema.json"
    response_format = "json"
    tier = "deep"
    temperature = 0.5

    def system(self) -> str:
        return (
            "You are a master instructional designer with 15 years of experience producing "
            "high-completion-rate online courses. You apply Bloom's taxonomy rigorously and "
            "design every lesson around one measurable objective."
        )
