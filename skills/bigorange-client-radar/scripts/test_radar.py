#!/usr/bin/env python3
"""
test_radar.py -- offline test for the BigOrange client radar.

1. Runs discover_clients.py against fixtures/ and asserts the expected two
   clients (Acme Roofing, Bright Path Dental) come back with the right
   evidence kinds.
2. Copies the fixture set, injects a third client's testimonial into the
   copied home page, re-runs discovery, and asserts diff_roster emits
   exactly one new_client event.

No network access. Exits 0 on pass, 1 on failure, and prints a plain-text
summary either way.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
FIXTURES_DIR = SKILL_DIR / "fixtures"
PYTHON = sys.executable

EXPECTED_CLIENTS = {
    "Acme Roofing": {"logo-alt", "testimonial"},
    "Bright Path Dental": {"case-study-title", "rest-post", "testimonial"},
}

THIRD_CLIENT_NAME = "Copper Kettle Landscaping"
THIRD_CLIENT_HTML_SNIPPET = """
    <h2>Case Study: Copper Kettle Landscaping</h2>
    <p>How Copper Kettle Landscaping doubled spring bookings with BigOrange.</p>
    <blockquote>
      The new campaigns from BigOrange booked out our spring calendar in
      three weeks.
    </blockquote>
    <p><strong>Dana Kim, Owner, Copper Kettle Landscaping</strong></p>
"""

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)
        print(f"FAIL: {message}")
    else:
        print(f"OK: {message}")


def run(args, cwd=None):
    result = subprocess.run(
        [PYTHON, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


def main():
    # -----------------------------------------------------------------
    # Part 1: base fixture set -> exactly two clients, correct kinds
    # -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        roster_a = tmp_path / "roster_a.json"

        result = run([
            str(SCRIPTS_DIR / "discover_clients.py"),
            "--fixture", str(FIXTURES_DIR),
            "--out", str(roster_a),
            "--quiet",
        ])
        check(result.returncode == 0, f"discover_clients.py exits 0 on base fixtures (stderr: {result.stderr[:500]})")
        check(roster_a.exists(), "base roster.json was written")

        if roster_a.exists():
            data = json.loads(roster_a.read_text(encoding="utf-8"))
            names_found = {c["name"]: {e["kind"] for e in c["evidence"]} for c in data["clients"]}

            check(set(names_found.keys()) == set(EXPECTED_CLIENTS.keys()),
                  f"exactly the expected two clients found (got: {sorted(names_found.keys())})")

            for name, expected_kinds in EXPECTED_CLIENTS.items():
                got_kinds = names_found.get(name, set())
                check(expected_kinds.issubset(got_kinds),
                      f"{name} has expected evidence kinds {sorted(expected_kinds)} (got {sorted(got_kinds)})")

        # -----------------------------------------------------------------
        # Part 2: inject a third client, re-run, diff -> exactly one
        # new_client event
        # -----------------------------------------------------------------
        fixture_b_dir = tmp_path / "fixtures_b"
        shutil.copytree(FIXTURES_DIR, fixture_b_dir)

        home_html = fixture_b_dir / "home.html"
        text = home_html.read_text(encoding="utf-8")
        injected = text.replace("</section>\n</body>", THIRD_CLIENT_HTML_SNIPPET + "  </section>\n</body>")
        check(injected != text, "third-client snippet was injected into the fixture copy")
        home_html.write_text(injected, encoding="utf-8")

        roster_b = tmp_path / "roster_b.json"
        result_b = run([
            str(SCRIPTS_DIR / "discover_clients.py"),
            "--fixture", str(fixture_b_dir),
            "--out", str(roster_b),
            "--quiet",
        ])
        check(result_b.returncode == 0, f"discover_clients.py exits 0 on injected fixtures (stderr: {result_b.stderr[:500]})")

        if roster_b.exists():
            data_b = json.loads(roster_b.read_text(encoding="utf-8"))
            names_b = {c["name"] for c in data_b["clients"]}
            check(THIRD_CLIENT_NAME in names_b,
                  f"third client '{THIRD_CLIENT_NAME}' appears in roster_b (got: {sorted(names_b)})")

        events_path = tmp_path / "events.json"
        result_diff = run([
            str(SCRIPTS_DIR / "diff_roster.py"),
            str(roster_a),
            str(roster_b),
            "--events-out", str(events_path),
        ])
        check(result_diff.returncode == 0, f"diff_roster.py exits 0 (stderr: {result_diff.stderr[:500]})")
        check(events_path.exists(), "events.json was written")

        if events_path.exists():
            events_data = json.loads(events_path.read_text(encoding="utf-8"))
            new_client_events = [e for e in events_data["events"] if e["type"] == "new_client"]
            check(len(new_client_events) == 1,
                  f"exactly one new_client event emitted (got {len(new_client_events)}: "
                  f"{[e['name'] for e in new_client_events]})")
            if new_client_events:
                check(new_client_events[0]["name"] == THIRD_CLIENT_NAME,
                      f"the new_client event names {THIRD_CLIENT_NAME} (got: {new_client_events[0]['name']})")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
