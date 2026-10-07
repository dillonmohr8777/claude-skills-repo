#!/usr/bin/env python3
"""Today's OpenRouter spend, cached. Read-only GET /api/v1/key via the existing
with-openrouter launcher (the key stays in that process's env; never printed).
Usage: spend.py            -> prints cached JSON {daily, cap, remaining, ts}, refreshes in background
       spend.py --refresh  -> fetch now and write cache (used by the background job)"""
import json, os, subprocess, sys, time
CACHE = os.path.expanduser("~/.claude/cache/openrouter-spend.json")
CAP = float(os.environ.get("OR_DAILY_CAP", "10"))  # soft daily cap; key limit has no daily reset
TTL = 300

def refresh():
    try:
        out = subprocess.run([os.path.expanduser("~/.local/bin/with-openrouter"), "sh", "-c",
            'curl -s -m 4 -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/key'],
            capture_output=True, text=True, timeout=6).stdout
        d = json.loads(out)["data"]
        res = {"daily": d.get("usage_daily") or 0, "cap": CAP, "remaining": d.get("limit_remaining"),
               "limit": d.get("limit"), "ts": time.time()}
    except Exception:
        return
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE + ".t", "w").write(json.dumps(res)); os.replace(CACHE + ".t", CACHE)

if "--refresh" in sys.argv:
    refresh(); sys.exit(0)
try:
    cur = json.load(open(CACHE))
except Exception:
    cur = None
if not cur or time.time() - cur["ts"] > TTL:
    subprocess.Popen([sys.executable, __file__, "--refresh"], stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)
print(json.dumps(cur or {}))
