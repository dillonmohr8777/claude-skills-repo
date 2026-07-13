"""Base Agent class. All 12 agents inherit from this.

Contract:
    agent = SomeAgent(course_dir, llm)
    output = agent.run(inputs: dict) -> dict | str

Each agent owns:
    - A prompt file in `prompts/<agent_id>.md`
    - An optional output schema in `schemas/<artifact>.schema.json`
    - A tier ("deep" | "balanced" | "fast") and temperature, configured in `config/agents.yaml`

The base class handles:
    - Jinja2 prompt rendering
    - LLM call via integrations.llm
    - JSON-Schema validation for structured outputs
    - Logging to logs/<course_id>/<agent_id>-<timestamp>.json
    - Retry on schema-validation failure (one auto-retry with the failure message appended)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jinja2
import yaml
from jsonschema import Draft202012Validator

from integrations.llm import LLM, LLMRequest, LLMResponse


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
SCHEMAS_DIR = REPO_ROOT / "schemas"
CONFIG_DIR = REPO_ROOT / "config"


_jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(PROMPTS_DIR)),
    undefined=jinja2.StrictUndefined,
    keep_trailing_newline=True,
)


def _load_agent_config() -> dict[str, Any]:
    path = CONFIG_DIR / "agents.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


@dataclass
class AgentResult:
    output: Any
    raw_text: str
    response: LLMResponse
    cost_usd: float
    schema_valid: bool


class Agent:
    """Base class. Override `system_prompt`, `user_prompt_template`, and optionally `output_schema`."""

    agent_id: str = "base"
    prompt_file: str = ""  # filename in prompts/, e.g. "lesson_script.md"
    output_schema: str | None = None  # filename in schemas/, e.g. "outline.schema.json"
    response_format: str = "text"  # "text" or "json"
    tier: str = "balanced"
    temperature: float = 0.6
    cache_user_blocks: list[str] = []

    def __init__(self, course_dir: Path, llm: LLM | None = None):
        self.course_dir = course_dir
        self.llm = llm or LLM()
        self.config = _load_agent_config().get(self.agent_id, {})
        self.tier = self.config.get("tier", self.tier)
        self.temperature = self.config.get("temperature", self.temperature)

    # ------- subclass-overridable -------

    def system(self) -> str:
        return f"You are the {self.agent_id} agent in an autonomous course-creation pipeline."

    def render_prompt(self, inputs: dict) -> str:
        if not self.prompt_file:
            raise NotImplementedError(f"{self.agent_id} must set prompt_file")
        tmpl = _jinja.get_template(self.prompt_file)
        return tmpl.render(**inputs)

    # ------- main entry point -------

    def run(self, inputs: dict, *, allow_retry: bool = True) -> AgentResult:
        user = self.render_prompt(inputs)
        req = LLMRequest(
            system=self.system(),
            user=user,
            tier=self.tier,
            temperature=self.temperature,
            response_format=self.response_format,
            cache_user_blocks=self.cache_user_blocks,
        )
        resp = self.llm.call(req)

        output: Any = resp.parsed if self.response_format == "json" else resp.text
        valid = True
        if self.output_schema and self.response_format == "json":
            valid = self._validate(output)
            if not valid and allow_retry:
                # One auto-retry with validation feedback appended.
                errors = self._collect_errors(output)
                retry_user = (
                    user
                    + "\n\nYour previous output failed schema validation. Errors:\n"
                    + "\n".join(f"- {e}" for e in errors)
                    + "\n\nReturn corrected JSON only."
                )
                req2 = LLMRequest(
                    system=self.system(),
                    user=retry_user,
                    tier=self.tier,
                    temperature=self.temperature,
                    response_format="json",
                )
                resp = self.llm.call(req2)
                output = resp.parsed
                valid = self._validate(output)

        result = AgentResult(
            output=output,
            raw_text=resp.text,
            response=resp,
            cost_usd=resp.cost_usd(),
            schema_valid=valid,
        )
        self._log(inputs, result)
        return result

    # ------- helpers -------

    def _validate(self, output: Any) -> bool:
        schema_path = SCHEMAS_DIR / self.output_schema
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema)
        return validator.is_valid(output)

    def _collect_errors(self, output: Any) -> list[str]:
        schema_path = SCHEMAS_DIR / self.output_schema
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema)
        return [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in validator.iter_errors(output)][:10]

    def _log(self, inputs: dict, result: AgentResult) -> None:
        course_id = self.course_dir.name
        log_dir = REPO_ROOT / "logs" / course_id
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = log_dir / f"{self.agent_id}-{ts}.json"
        path.write_text(
            json.dumps(
                {
                    "agent_id": self.agent_id,
                    "timestamp": ts,
                    "tier": self.tier,
                    "model": result.response.model,
                    "duration_ms": result.response.duration_ms,
                    "input_tokens": result.response.input_tokens,
                    "output_tokens": result.response.output_tokens,
                    "cache_read_tokens": result.response.cache_read_tokens,
                    "cache_write_tokens": result.response.cache_write_tokens,
                    "cost_usd": round(result.cost_usd, 5),
                    "schema_valid": result.schema_valid,
                    "input_keys": list(inputs.keys()),
                },
                indent=2,
            )
        )
