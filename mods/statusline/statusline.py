#!/usr/bin/env python3
"""Claude Code status line: model, effort, fast | branch | ctx bar | cost | client | momo.
One line, ~100 cols. Never blocks: MomoBot health is read from a cache that a
detached background curl refreshes. Off: restore ~/.claude/statusline.sh in settings."""
import json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
REGISTRY = HOME + "/code/client-operations-canonical/registry/clients.json"
CACHE = HOME + "/.claude/cache/momobot.status"
# Claude Code's own ultracode/ultrathink rainbow (dark theme rgb values, from the CLI bundle)
RED, ORANGE, YELLOW, GREEN = (235, 95, 87), (245, 139, 87), (250, 195, 95), (145, 200, 130)
BLUE, INDIGO, VIOLET = (130, 170, 220), (155, 130, 200), (200, 130, 180)
GRAY = (154, 160, 166)
RAINBOW = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]
PLAIN = bool(os.environ.get("NO_COLOR"))
TRUE = os.environ.get("COLORTERM", "") in ("truecolor", "24bit")
RST = "" if PLAIN else "\033[0m"

def c(rgb, text, bold=False):
    if PLAIN:
        return text
    if TRUE:
        code = f"38;2;{rgb[0]};{rgb[1]};{rgb[2]}"
    else:
        q = lambda v: round(v / 255 * 5)
        code = f"38;5;{16 + 36 * q(rgb[0]) + 6 * q(rgb[1]) + q(rgb[2])}"
    return f"\033[{'1;' if bold else ''}{code}m{text}\033[0m"

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

def or_spend():
    try:
        out = subprocess.run([HOME + "/code/claude-skills-repo/mods/spend/spend.py"], capture_output=True, text=True, timeout=0.3).stdout
        d = json.loads(out)
        return d if "daily" in d else None
    except Exception:
        return None

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

    head = c(RED, model, True)
    if isinstance(effort, str) and effort:
        head += " " + c(ORANGE, {"medium": "med"}.get(effort, effort))
    if fast:
        head += " " + c(YELLOW, "fast", True)
    parts = [head]
    if branch:
        parts.append(c(GREEN, branch[:12]))
    if pct is not None:
        n = max(0, min(8, round(pct / 12.5)))
        bar = "".join(c(RAINBOW[i * 7 // 8], "▰") for i in range(n)) + c(GRAY, "▱" * (8 - n))
        parts.append(bar + " " + c(BLUE, f"{round(pct)}%"))
    spend = RED if cost >= 15 else ORANGE if cost >= 5 else YELLOW if cost >= 1 else GREEN
    parts.append(c(spend, f"${cost:.2f}"))
    sp = or_spend()
    if sp:
        r = max(0.0, min(1.0, sp["daily"] / sp["cap"]))
        stops = [GREEN, YELLOW, ORANGE, RED]
        k = min(2, int(r * 3)); f = r * 3 - k
        rgb = tuple(round(stops[k][i] + (stops[k + 1][i] - stops[k][i]) * f) for i in range(3))
        parts.append(c(rgb, f"OR ${sp['daily']:.2f}/{sp['cap']:.0f}", r > 0.8))
    cl = client_for(f"{cwd} {branch}")
    if cl:
        parts.append(c(INDIGO, "◆ " + cl[:12], True))
    m = momo()
    if m:
        parts.append(c(GREEN if m == "up" else RED, "momo" + ("✓" if m == "up" else "✗"), True))
    print(c(GRAY, " │ ").join(parts), end="")

main()
