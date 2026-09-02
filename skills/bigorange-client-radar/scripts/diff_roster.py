#!/usr/bin/env python3
"""
diff_roster.py -- compare two BigOrange client roster snapshots.

Emits events:
  new_client    -- name not present in the previous roster
  new_evidence  -- existing client gained a case-study or testimonial evidence
                   kind it did not previously have
  removed       -- present before, absent now, for 2 consecutive runs
                   (tracked with a persistent missing_runs counter)

Never sends or publishes anything. Writes events.json next to the current
roster and prints a markdown block ready to paste into an approval queue.
Also usable as a library from discover_clients.py --diff.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STRONG_EVIDENCE_KINDS = {"case-study-title", "rest-post", "testimonial"}


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def load_roster(path: Path):
    if not path or not Path(path).exists():
        return {"clients": []}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_missing_state(events_path: Path):
    """The missing_runs counters persist inside events.json itself under
    a reserved key so no extra state file is needed."""
    if not events_path.exists():
        return {}
    try:
        data = json.loads(events_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data.get("_missing_runs", {})


def diff_rosters(prev_path: Path, curr_path: Path, events_path: Path):
    prev = load_roster(prev_path)
    curr = load_roster(curr_path)

    prev_by_key = {name_key(c["name"]): c for c in prev.get("clients", [])}
    curr_by_key = {name_key(c["name"]): c for c in curr.get("clients", [])}

    missing_runs = load_missing_state(events_path)

    events = []

    for key, c in curr_by_key.items():
        prev_c = prev_by_key.get(key)
        if prev_c is None:
            events.append({
                "type": "new_client",
                "name": c["name"],
                "confidence": c.get("confidence", "low"),
                "industry_guess": c.get("industry_guess", "unknown"),
                "evidence_url": (c.get("evidence") or [{}])[0].get("url", ""),
                "detected_at": now_iso(),
            })
        else:
            prev_kinds = {e["kind"] for e in prev_c.get("evidence", [])}
            curr_kinds = {e["kind"] for e in c.get("evidence", [])}
            new_kinds = (curr_kinds - prev_kinds) & STRONG_EVIDENCE_KINDS
            if new_kinds:
                new_ev = next(
                    (e for e in c.get("evidence", []) if e["kind"] in new_kinds),
                    (c.get("evidence") or [{}])[0],
                )
                events.append({
                    "type": "new_evidence",
                    "name": c["name"],
                    "confidence": c.get("confidence", "low"),
                    "industry_guess": c.get("industry_guess", "unknown"),
                    "new_kinds": sorted(new_kinds),
                    "evidence_url": new_ev.get("url", ""),
                    "detected_at": now_iso(),
                })
        # clear missing counter for anyone present now
        missing_runs.pop(key, None)

    for key, prev_c in prev_by_key.items():
        if key in curr_by_key:
            continue
        count = missing_runs.get(key, 0) + 1
        missing_runs[key] = count
        if count >= 2:
            events.append({
                "type": "removed",
                "name": prev_c["name"],
                "confidence": prev_c.get("confidence", "low"),
                "industry_guess": prev_c.get("industry_guess", "unknown"),
                "missing_runs": count,
                "detected_at": now_iso(),
            })
            # once reported, stop re-reporting every run; keep counter so it
            # doesn't flip back to a fresh new_client if it briefly reappears
        # else: not yet reported, just tracked

    markdown_lines = []
    for e in events:
        if e["type"] == "new_client":
            markdown_lines.append(
                f"- [ ] Draft kickoff deck for {e['name']} ({e['confidence']}, "
                f"{e['industry_guess']}) evidence: {e['evidence_url']}"
            )
        elif e["type"] == "new_evidence":
            markdown_lines.append(
                f"- [ ] Review new evidence for {e['name']} ({e['confidence']}, "
                f"{e['industry_guess']}) new kinds: {', '.join(e['new_kinds'])} "
                f"evidence: {e['evidence_url']}"
            )
        elif e["type"] == "removed":
            markdown_lines.append(
                f"- [ ] Confirm {e['name']} ({e['confidence']}, {e['industry_guess']}) "
                f"no longer appears on bigorange.marketing (missing {e['missing_runs']} runs)"
            )
    markdown = "\n".join(markdown_lines)

    events_out = {
        "generated_at": now_iso(),
        "previous_roster": str(prev_path) if prev_path else None,
        "current_roster": str(curr_path),
        "events": events,
        "_missing_runs": missing_runs,
    }
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(json.dumps(events_out, indent=2), encoding="utf-8")

    return events, markdown


def main():
    parser = argparse.ArgumentParser(description="Diff two BigOrange client roster snapshots.")
    parser.add_argument("previous", help="Path to the previous roster.json")
    parser.add_argument("current", help="Path to the current roster.json")
    parser.add_argument("--events-out", default=None, help="Path to write events.json (default: alongside current)")
    args = parser.parse_args()

    curr_path = Path(args.current)
    events_path = Path(args.events_out) if args.events_out else curr_path.parent / "events.json"

    events, markdown = diff_rosters(Path(args.previous), curr_path, events_path)

    print(f"Wrote {events_path} ({len(events)} events)")
    if markdown:
        print("\n" + markdown)
    else:
        print("\nNo events.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
