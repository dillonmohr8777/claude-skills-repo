#!/usr/bin/env python3
"""Cache MomoBot gateway readiness; never infer it from Rockbot or login HTML."""
import json
import os
from pathlib import Path
import urllib.request

READY_URL = "http://127.0.0.1:2026/health/ready"
CACHE = Path.home() / ".claude/cache/momobot-readiness.status"


def readiness(opener=urllib.request.urlopen):
    try:
        with opener(READY_URL, timeout=4) as response:
            if response.status != 200:
                return "down"
            body = json.loads(response.read(16384))
            return "up" if body.get("status") == "ready" and body.get("service") == "deer-flow-gateway" else "down"
    except Exception:
        return "down"


def refresh():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    temporary = CACHE.with_name(f"{CACHE.name}.{os.getpid()}.tmp")
    temporary.write_text(readiness())
    temporary.replace(CACHE)


if __name__ == "__main__":
    refresh()
