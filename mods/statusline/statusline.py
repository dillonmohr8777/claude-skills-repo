#!/usr/bin/env python3
"""Claude Code status line: model, effort, fast | branch | ctx bar | cost | client | momo.
One line, ~100 cols. Never blocks: MomoBot health is read from a cache that a
detached background curl refreshes. Off: restore ~/.claude/statusline.sh in settings."""
import json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
REGISTRY = HOME + "/code/client-operations-canonical/registry/clients.json"
CACHE = HOME + "/.claude/cache/momobot.status"
OR, GR, DIM, RST = "\033[38;2;255;107;53m", "\033[38;2;154;160;166m", "\033[2m", "\033[0m"
GREEN, RED = "\033[38;2;61;220;132m", "\033[38;2;230;80;80m"

def g(d, *path):
    for p in path:
        d = d.get(p) if isinstance(d, dict) else None
    return d

def git_branch(cwd):
    try:
        return subprocess.run(["git", "-C", cwd, "symbolic-ref", "--short", "-q", "HEAD"],
                              capture_output=True, text=True, timeout=0.15).stdout.strip()
    except Exception:
        return ""

def client_for(text):
    """Map cwd + branch to an ACTIVE client in the registry; unknown -> None."""
    try:
        reg = json.load(open(REGISTRY))["clients"]
    except Exception:
        return None
    t = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()) + " "
    t = t.replace(" bridge of hope", " ")  # Bridge Software != Bridge of Hope OTC
    for c in reg:
        if c.get("status") != "active" or c["id"] == "momentum-360":
            continue
        names = [c["id"], c["displayName"]] + c.get("aliases", [])
        for n in names:
            n = re.sub(r"[^a-z0-9]+", " ", n.lower()).strip()
            if len(n) >= 4 and f" {n} " in t:
                return c["displayName"].split(" / ")[0]
    return None

def momo():
    try:
        age = time.time() - os.path.getmtime(CACHE)
        val = open(CACHE).read().strip()
    except Exception:
        age, val = 1e9, ""
    if age > 30:  # refresh detached; never wait on it
        try:
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            subprocess.Popen(["sh", "-c",
                f'curl -s -m 1 http://127.0.0.1:3434/api/health | grep -q ready && echo up > {CACHE}.t || echo down > {CACHE}.t; mv {CACHE}.t {CACHE}'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception:
            pass
    return val

def main():
    try:
        j = json.load(sys.stdin)
    except Exception:
        j = {}
    cwd = g(j, "workspace", "current_dir") or j.get("cwd") or os.getcwd()
    try:
        s = json.load(open(HOME + "/.claude/settings.json"))
    except Exception:
        s = {}
    model = g(j, "model", "display_name") or "?"
    effort = g(j, "effort", "level") or j.get("effort") or s.get("effortLevel")
    fast = g(j, "fast_mode") if "fast_mode" in j else s.get("fastMode")
    branch = git_branch(cwd)
    pct = g(j, "context_window", "used_percentage")
    cost = g(j, "cost", "total_cost_usd") or 0

    head = f"{OR}{model}{RST}"
    if isinstance(effort, str) and effort:
        head += f"{GR} {effort}{RST}"
    if fast:
        head += f"{OR} fast{RST}"
    parts = [head]
    if branch:
        parts.append(f"{GR}{branch[:20]}{RST}")
    if pct is not None:
        n = max(0, min(8, round(pct / 12.5)))
        parts.append(f"{OR}{'▰' * n}{DIM}{'▱' * (8 - n)}{RST}{GR} {round(pct)}%{RST}")
    parts.append(f"{GR}${cost:.2f}{RST}")
    cl = client_for(f"{cwd} {branch}")
    if cl:
        parts.append(f"{OR}◆ {cl[:16]}{RST}")
    m = momo()
    if m:
        parts.append(f"{GREEN if m == 'up' else RED}momo {m}{RST}")
    print(f"{GR} │ {RST}".join(parts), end="")

main()
