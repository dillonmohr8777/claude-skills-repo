"""QA Agent.

Two-phase: schema validation (cheap, deterministic) → content review (LLM).
The schema phase short-circuits if the artifact violates its JSON Schema.
The content phase runs the qa_content.md prompt and returns structured findings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from agents.base import Agent, REPO_ROOT, SCHEMAS_DIR


class QA(Agent):
    agent_id = "qa"
    prompt_file = "qa_content.md"
    output_schema = "qa_result.schema.json"
    response_format = "json"
    tier = "balanced"
    temperature = 0.2

    def system(self) -> str:
        return (
            "You are a strict QA reviewer. Your job is to BLOCK low-quality artifacts before "
            "they ship. You err on the side of catching issues, not approving."
        )

    def schema_check(self, artifact: Any, schema_filename: str | None) -> list[dict]:
        if not schema_filename:
            return []
        schema = json.loads((SCHEMAS_DIR / schema_filename).read_text())
        validator = Draft202012Validator(schema)
        return [
            {
                "severity": "blocker",
                "location": "/" + "/".join(str(p) for p in e.absolute_path),
                "rule": "schema",
                "message": e.message,
            }
            for e in validator.iter_errors(artifact)
        ]

    def review(
        self,
        *,
        stage: str,
        artifact: Any,
        schema_filename: str | None,
        voice_reference: str,
        strictness: str = "normal",
        stage_context: dict | None = None,
    ) -> dict:
        # Phase 1: schema (deterministic).
        schema_issues = self.schema_check(artifact, schema_filename)
        if schema_issues:
            return {
                "passed": False,
                "stage": stage,
                "issues": schema_issues,
                "summary": f"Schema validation failed with {len(schema_issues)} issue(s); content review skipped.",
            }

        # Phase 2: content review (LLM).
        result = self.run(
            {
                "stage": stage,
                "artifact": artifact if isinstance(artifact, str) else json.dumps(artifact, indent=2),
                "voice_reference": voice_reference,
                "strictness": strictness,
                "stage_context": json.dumps(stage_context or {}, indent=2),
            }
        )
        return result.output
