#!/usr/bin/env python3
"""
Build an Align HCM project status report.

    python3 build_status_report.py --spec week32.json --out-dir ./status

Align's PM onboarding deck describes this exactly:

    Current state: PMs are sending an email summary of their project status
    call from OneNote.
    Future state: PMs will be sending a Project Status Report (pdf) for a
    consistent method of reporting out. This is currently being piloted.

This is that report. The nine-point structure comes from the same deck, so a
report produced here matches the call it summarises, section for section.

It also refuses to emit a green status while a high-severity risk is open,
because a status report that hides a red is worse than no status report.

Exit codes:
    0  written and clean
    2  written but failed validation
    3  the spec is incomplete or self-contradictory
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import alignhcm_core as core          # noqa: E402
import alignhcm_docx as D             # noqa: E402

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["client", "project", "pm", "reporting_period", "overall_status",
            "go_live"]

STATUS_COLOURS = {"green": "2E7D32", "yellow": "B05512", "red": "B3261E"}
STATUS_MEANING = {
    "green": "On track. No open item threatens scope, schedule, or budget.",
    "yellow": "At risk. A named item needs attention or a decision this week.",
    "red": "Off track. Schedule, scope, or budget will move without intervention.",
}

# The workstreams Align tracks by phase, from the PM methodology.
DEFAULT_WORKSTREAMS = ["HR/Payroll", "Workforce Management", "Benefits",
                       "Data Conversion", "Integration", "Payment Services"]


def load_spec(path):
    with open(path, encoding="utf8") as fh:
        spec = json.load(fh)
    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        raise ValueError("spec is missing required field(s): " + ", ".join(missing))
    status = str(spec["overall_status"]).lower()
    if status not in STATUS_COLOURS:
        raise ValueError(f"overall_status must be green, yellow, or red, "
                         f"not {spec['overall_status']!r}")
    spec["overall_status"] = status
    return spec


def build_blocks(spec):
    client = spec["client"]
    status = spec["overall_status"]
    period = spec["reporting_period"]

    blocks = [
        D.title(f"Project Status Report",
                f"{client} · {spec['project']}",
                meta=[("Reporting period", period),
                      ("Project manager", spec["pm"]),
                      ("Target go-live", spec["go_live"]),
                      ("Overall status", status.upper())]),

        D.heading("1. Overall status"),
        D.para(STATUS_MEANING[status], bold=True,
               color=STATUS_COLOURS[status]),
    ]
    if spec.get("status_narrative"):
        blocks.append(D.para(spec["status_narrative"]))

    if spec.get("workstreams"):
        blocks.append(D.heading("2. Status by workstream"))
        blocks.append(D.table(
            ["Workstream", "Phase", "Status", "Note"],
            [[w["name"], w.get("phase", ""), w.get("status", "").upper(),
              w.get("note", "")] for w in spec["workstreams"]],
            widths=[2400, 1900, 1200, 3700]))

    blocks.append(D.heading("3. Accomplishments this period"))
    blocks.append(D.bullets(spec.get("accomplishments",
                                     ["No items recorded for this period."])))

    if spec.get("upcoming"):
        blocks.append(D.heading("4. Upcoming deliverables"))
        blocks.append(D.table(
            ["Deliverable", "Owner", "Due"],
            [[u["item"], u.get("owner", ""), u.get("due", "")]
             for u in spec["upcoming"]],
            widths=[4800, 2200, 2200]))

    if spec.get("risks"):
        blocks.append(D.heading("5. Risks and issues"))
        blocks.append(D.para(
            "Open items from the RAID log. Severity drives the overall status "
            "above, so an item here that is not reflected there is a reporting "
            "error rather than a judgement call.", size=19, color=D.MUTED))
        blocks.append(D.table(
            ["Item", "Severity", "Owner", "Mitigation"],
            [[r["item"], r.get("severity", "").upper(), r.get("owner", ""),
              r.get("mitigation", "")] for r in spec["risks"]],
            widths=[2900, 1300, 1700, 3300]))

    if spec.get("decisions_needed"):
        blocks.append(D.heading("6. Decisions needed"))
        blocks.append(D.para("Each item below is blocking work. The date is when "
                             "the schedule starts to move without an answer."))
        blocks.append(D.table(
            ["Decision", "Owner", "Needed by"],
            [[d["decision"], d.get("owner", ""), d.get("needed_by", "")]
             for d in spec["decisions_needed"]],
            widths=[5000, 2100, 2100]))

    if spec.get("action_items"):
        blocks.append(D.heading("7. Action items"))
        blocks.append(D.table(
            ["Action", "Owner", "Due", "Status"],
            [[a["action"], a.get("owner", ""), a.get("due", ""),
              a.get("status", "Open")] for a in spec["action_items"]],
            widths=[4200, 1800, 1500, 1700]))

    blocks.append(D.heading("8. Links"))
    links = spec.get("links", {})
    blocks.append(D.bullets([
        f"Project plan: {links.get('project_plan', 'not recorded')}",
        f"RAID log: {links.get('raid_log', 'not recorded')}",
        f"Project documentation: {links.get('documentation', 'not recorded')}",
    ]))

    if spec.get("other"):
        blocks.append(D.heading("9. Other"))
        blocks.append(D.para(spec["other"]))

    blocks.append(D.rule())
    blocks.append(D.para(
        f"Issued by {spec['pm']} within 24 hours of the status call, per the "
        f"Align project methodology. Questions on any item above go to the "
        f"project manager first; the escalation path is project manager, "
        f"practice lead, then President and COO.", size=19, color=D.MUTED))
    return blocks


def validate_consistency(spec, report):
    """
    A status report has to be internally honest.

    Green while a high risk is open, or a decision is already overdue, is the
    failure mode that makes status reporting worthless. The check is cheap and
    the conversation it forces is the point.
    """
    status = spec["overall_status"]
    high = [r for r in spec.get("risks", [])
            if str(r.get("severity", "")).lower() in ("high", "critical")]
    if status == "green" and high:
        report.error(
            "status",
            f"overall status is GREEN while {len(high)} high-severity risk(s) "
            f"are open: {', '.join(r['item'][:40] for r in high[:3])}. Either "
            f"the status is yellow, or those risks are not actually high.")

    today = datetime.date.today()
    for d in spec.get("decisions_needed", []):
        raw = d.get("needed_by")
        if not raw:
            continue
        try:
            due = datetime.date.fromisoformat(raw)
        except ValueError:
            continue
        if due < today and status == "green":
            report.error(
                "status",
                f"overall status is GREEN but the decision '{d['decision'][:40]}' "
                f"was needed by {raw}, which has passed.")

    ws_red = [w for w in spec.get("workstreams", [])
              if str(w.get("status", "")).lower() == "red"]
    if ws_red and status != "red":
        report.warn(
            "status",
            f"{len(ws_red)} workstream(s) are red while the overall status is "
            f"{status.upper()}. Confirm that is deliberate.")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--allow-invalid", action="store_true")
    ap.add_argument("--no-supersede", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        spec = load_spec(args.spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    client = spec["client"]
    blocks = build_blocks(spec)

    os.makedirs(args.out_dir, exist_ok=True)
    artifact = "Status-" + core.slugify(spec["reporting_period"])
    version = core.next_version(args.out_dir, client, artifact, ".docx")
    name = core.build_name(client, artifact, ".docx", version)
    path = os.path.join(args.out_dir, name)
    D.build(blocks, path, doc_title=f"{client} project status",
            footer_text="alignhcm.com  ·  Confidential  ·  Project status report")

    report = core.Report(name)
    parts = core.read_parts(path)
    core.scan_residue(parts, client, report, extra_terms=spec.get("forbid_terms", ()))
    core.scan_banned_colours(parts, report)
    core.check_filename(name, report)
    validate_consistency(spec, report)

    moved = []
    if not args.no_supersede and report.passed:
        moved = core.supersede_previous(args.out_dir, client, artifact,
                                        ".docx", name)

    print(f"wrote {path}")
    print(f"  status {spec['overall_status'].upper()}, "
          f"{len(spec.get('risks', []))} risk(s), "
          f"{len(spec.get('action_items', []))} action(s)")
    if moved:
        print(f"  moved {len(moved)} earlier version(s) to _superseded/")
    print()
    print(report.render())

    if args.json:
        print(json.dumps({"path": path, "version": version,
                          "status": spec["overall_status"],
                          "superseded": moved, **report.as_dict()}, indent=2))

    if not report.passed and not args.allow_invalid:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
