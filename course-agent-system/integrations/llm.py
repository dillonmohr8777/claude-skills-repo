"""LLM wrapper.

Centralizes model routing, prompt caching, retry, and structured output handling
so every agent in the system uses the same code path.

Tier rules (locked in `config/agents.yaml`, not hard-coded):
  - "deep": Opus 4.7 for reasoning-heavy work (curriculum_architect, optimization, qa_content).
  - "balanced": Sonnet 4.6 default for most agents.
  - "fast": Haiku 4.5 for fanout (per-lesson slides, per-lesson quizzes).

Prompt caching is applied to the system prompt and any input block tagged with
`cache: true`, which keeps cost flat across the 20+ lesson fanout.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import anthropic
    from anthropic.types import MessageParam


MODEL_TIERS = {
    "deep": "claude-opus-4-7",
    "balanced": "claude-sonnet-4-6",
    "fast": "claude-haiku-4-5-20251001",
}

DEFAULT_MAX_TOKENS = {
    "deep": 8000,
    "balanced": 4000,
    "fast": 2000,
}


@dataclass
class LLMRequest:
    system: str
    user: str
    tier: str = "balanced"
    max_tokens: int | None = None
    temperature: float = 0.6
    cache_system: bool = True
    cache_user_blocks: list[str] = field(default_factory=list)
    response_format: str = "text"  # "text" | "json"


@dataclass
class LLMResponse:
    text: str
    parsed: Any | None
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    duration_ms: int

    def cost_usd(self) -> float:
        # Rough public pricing (per 1M tokens). Adjust as needed.
        prices = {
            "claude-opus-4-7":            {"in": 15.0, "out": 75.0, "cache_w": 18.75, "cache_r": 1.50},
            "claude-sonnet-4-6":          {"in": 3.0,  "out": 15.0, "cache_w": 3.75,  "cache_r": 0.30},
            "claude-haiku-4-5-20251001":  {"in": 1.0,  "out": 5.0,  "cache_w": 1.25,  "cache_r": 0.10},
        }
        p = prices.get(self.model)
        if not p:
            return 0.0
        return (
            (self.input_tokens / 1_000_000) * p["in"]
            + (self.output_tokens / 1_000_000) * p["out"]
            + (self.cache_write_tokens / 1_000_000) * p["cache_w"]
            + (self.cache_read_tokens / 1_000_000) * p["cache_r"]
        )


class LLM:
    def __init__(self, api_key: str | None = None):
        import anthropic
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def call(self, req: LLMRequest, *, max_retries: int = 3) -> LLMResponse:
        anthropic = self._anthropic
        model = MODEL_TIERS[req.tier]
        max_tokens = req.max_tokens or DEFAULT_MAX_TOKENS[req.tier]

        system_blocks = [
            {
                "type": "text",
                "text": req.system,
                **({"cache_control": {"type": "ephemeral"}} if req.cache_system else {}),
            }
        ]

        user_content: list[dict] = [{"type": "text", "text": req.user}]
        for block in req.cache_user_blocks:
            user_content.append(
                {"type": "text", "text": block, "cache_control": {"type": "ephemeral"}}
            )

        messages: list[dict] = [{"role": "user", "content": user_content}]

        attempt = 0
        last_err: Exception | None = None
        while attempt < max_retries:
            attempt += 1
            try:
                t0 = time.time()
                resp = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=req.temperature,
                    system=system_blocks,
                    messages=messages,
                )
                duration_ms = int((time.time() - t0) * 1000)
                text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
                parsed: Any | None = None
                if req.response_format == "json":
                    parsed = self._extract_json(text)
                usage = resp.usage
                return LLMResponse(
                    text=text,
                    parsed=parsed,
                    model=model,
                    input_tokens=getattr(usage, "input_tokens", 0),
                    output_tokens=getattr(usage, "output_tokens", 0),
                    cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
                    cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
                    duration_ms=duration_ms,
                )
            except (anthropic.RateLimitError, anthropic.APIStatusError) as e:
                last_err = e
                # Exponential backoff: 2s, 4s, 8s
                time.sleep(2**attempt)
        raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_err}")

    @staticmethod
    def _extract_json(text: str) -> Any:
        s = text.strip()
        # Strip markdown fences if model wrapped JSON.
        if s.startswith("```"):
            s = s.split("\n", 1)[1] if "\n" in s else s
            if s.endswith("```"):
                s = s.rsplit("```", 1)[0]
            s = s.strip()
            if s.startswith("json"):
                s = s[4:].lstrip()
        return json.loads(s)
