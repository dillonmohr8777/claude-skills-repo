"""Course state I/O. Reads/writes courses/<slug>/state.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path(course_dir: Path) -> Path:
    return course_dir / "state.json"


def load_state(course_dir: Path) -> dict:
    return json.loads(state_path(course_dir).read_text())


def save_state(course_dir: Path, state: dict) -> None:
    state["updated_at"] = now_iso()
    state_path(course_dir).write_text(json.dumps(state, indent=2))


def initial_state(course_id: str, *, modules: int, lessons_per_module: int, target_hours: float, voice_reference: str, qa_strictness: str) -> dict:
    ts = now_iso()
    return {
        "course_id": course_id,
        "stage": "topic_chosen",
        "created_at": ts,
        "updated_at": ts,
        "human_checkpoints": {
            "topic_chosen":     {"approved": True,  "approved_at": ts, "approver": "cli"},
            "outline_approved": {"approved": False, "approved_at": None, "approver": None},
            "lessons_approved": {"approved": False, "approved_at": None, "approver": None},
            "launch_ready":     {"approved": False, "approved_at": None, "approver": None},
        },
        "agent_runs": [],
        "config": {
            "modules": modules,
            "lessons_per_module": lessons_per_module,
            "target_hours": target_hours,
            "voice_reference": voice_reference,
            "qa_strictness": qa_strictness,
        },
    }


def record_run(state: dict, agent_id: str, status: str, output_path: str | None = None, error: str | None = None) -> None:
    state.setdefault("agent_runs", []).append(
        {
            "agent_id": agent_id,
            "started_at": now_iso(),
            "finished_at": now_iso(),
            "status": status,
            "attempt": 1,
            "output_path": output_path,
            "error": error,
        }
    )


def advance(state: dict, new_stage: str) -> None:
    state["stage"] = new_stage
