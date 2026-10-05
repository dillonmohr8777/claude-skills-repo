#!/usr/bin/env python3
"""Read-only fleet snapshot: launchd com.dillon.*, tmux, service health. 1s timeouts, parallel,
cached 10s. --json for the pane; default prints a colored table (NO_COLOR respected)."""
import json, os, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
CACHE = os.path.expanduser("~/.claude/cache/fleet.json")
PORTS = [(2026, "MomoBot prod"), (2030, "Momo private"), (3434, "rockbot"), (4310, "Jevbox")]

def sh(argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=2).stdout
    except Exception:
        return ""

def probe(p):
    try:
        class NoRedir(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        urllib.request.build_opener(NoRedir).open(f"http://127.0.0.1:{p[0]}/", timeout=1)
        return "up"
    except urllib.error.HTTPError as e:
        return "up" if e.code < 500 else "down"  # 3xx/4xx = something is answering
    except Exception:
        return "down"

def snapshot():
    jobs = []
    for line in sh(["launchctl", "list"]).splitlines():
        f = line.split("\t")
        if len(f) == 3 and f[2].startswith("com.dillon."):
            state = "running" if f[0] != "-" else ("failed" if f[1] not in ("0", "-") else "loaded")
            jobs.append({"name": f[2][11:], "state": state, "code": f[1]})
    jobs.sort(key=lambda j: ({"failed": 0, "running": 1, "loaded": 2}[j["state"]], j["name"]))
    tm = [l.split(":")[0] for l in sh(["tmux", "ls"]).splitlines() if ":" in l]
    with ThreadPoolExecutor(4) as ex:
        svc = [{"port": p[0], "name": p[1], "state": s} for p, s in zip(PORTS, ex.map(probe, PORTS))]
    return {"ts": time.time(), "jobs": jobs, "tmux": tm, "services": svc}

def get():
    try:
        d = json.load(open(CACHE))
        if time.time() - d["ts"] < 10:
            return d
    except Exception:
        pass
    d = snapshot()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE + ".t", "w").write(json.dumps(d)); os.replace(CACHE + ".t", CACHE)
    return d

if __name__ == "__main__":
    d = get()
    if "--json" in sys.argv:
        print(json.dumps(d)); sys.exit()
    P = os.environ.get("NO_COLOR") and not os.environ.get("CLAUDE_MODS_FORCE_COLOR")
    rb = [(235,95,87),(245,139,87),(250,195,95),(145,200,130),(130,170,220),(155,130,200),(200,130,180)]
    col = lambda c, t, b=False: t if P else f"\033[{'1;' if b else ''}38;2;{c[0]};{c[1]};{c[2]}m{t}\033[0m"
    dot = lambda s: col((145,200,130) if s in ("up","running") else (235,95,87) if s in ("down","failed") else (154,160,166), "●")
    print(col(rb[0], "SERVICES", True))
    for s in d["services"]: print(f" {dot(s['state'])} {col(rb[1], str(s['port']))} {s['name']}")
    print(col(rb[2], "LAUNCHD", True))
    for j in d["jobs"]: print(f" {dot(j['state'])} {col(rb[3], j['name'])} {j['state']}")
    print(col(rb[4], "TMUX", True))
    for t in d["tmux"]: print(f" {col(rb[5], '●')} {t}")
