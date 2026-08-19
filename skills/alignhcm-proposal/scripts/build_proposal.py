#!/usr/bin/env python3
"""
Build an Align HCM phased services proposal.

    python3 build_proposal.py --spec rei.json --out-dir ./proposals

A proposal argues a sequence: here is your current state, here is a phased path
through it, here is what you get, here is what it costs. That order is fixed.
The phases, the pain points, and the numbers change per deal.

The investment table is computed from the phases rather than typed, because a
proposal whose phase hours do not add up to its stated total is the one mistake
a prospect will always find.

Exit codes:
    0  written and clean
    2  written but failed validation
    3  the spec is incomplete or the arithmetic is inconsistent
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import alignhcm_core as core          # noqa: E402
import alignhcm_pptx as P             # noqa: E402

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["client_name", "platform", "engagement_title", "rate",
            "current_state", "phases", "contact"]


def money(n):
    return "${:,.0f}".format(n)


def compact_money(n):
    return f"${n / 1000:,.0f}K" if n < 1_000_000 else f"${n / 1_000_000:,.2f}M"


def load_spec(path):
    with open(path, encoding="utf8") as fh:
        spec = json.load(fh)
    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        raise ValueError("spec is missing required field(s): " + ", ".join(missing))
    if not spec["phases"]:
        raise ValueError("a phased proposal needs at least one phase")
    for i, ph in enumerate(spec["phases"], 1):
        for key in ("name", "window", "hours", "summary"):
            if key not in ph:
                raise ValueError(f"phase {i} is missing '{key}'")
    if len(spec["current_state"]) < 2:
        raise ValueError("current_state needs at least two categories; this is "
                         "the section that proves you listened")
    return spec


def investment_rows(spec):
    rate = float(spec["rate"])
    rows, hours_total, money_total = [], 0.0, 0.0
    for ph in spec["phases"]:
        hours = float(ph["hours"])
        amount = hours * rate
        hours_total += hours
        money_total += amount
        rows.append([ph["name"], f"{hours:,.0f}", f"${rate:,.0f}/hr", money(amount)])
    rows.append(["Total engagement", f"{hours_total:,.0f}", "", money(money_total)])
    return rows, hours_total, money_total


def build_slides(spec, facts):
    client = spec["client_name"]
    today = spec.get("date") or datetime.date.today().strftime("%B %Y")
    rows, hours_total, money_total = investment_rows(spec)
    slides, dark = [], []

    def add(shapes, is_dark=False):
        slides.append(shapes)
        dark.append(is_dark)

    add(P.cover(client, f"{spec['platform']} {spec['engagement_title']}",
                "Services Proposal", [f"Prepared for {client}", today]), True)

    agenda = [("1", "Current State and Challenges"),
              ("2", "Phased Approach"),
              ("3", "Deliverables and Outcomes"),
              ("4", "Timeline and Investment")]
    add(P.cards("Today's conversation", "What We'll Cover",
                [(f"{n}  {t}", "") for n, t in agenda], columns=2))

    add(P.section(1, "Current State and Challenges",
                  spec.get("current_state_framing",
                           f"Understanding {client}'s environment and the "
                           f"urgency driving this engagement.")))

    add(P.cards("Pain points", "What We Heard",
                [(c["category"], " · ".join(c["items"]))
                 for c in spec["current_state"]],
                columns=3 if len(spec["current_state"]) >= 3 else 2))

    if spec.get("drivers") or spec.get("risks"):
        items = []
        for d in spec.get("drivers", []):
            items.append((f"Driver: {d['title']}", d["detail"]))
        for r in spec.get("risks", []):
            items.append((f"Risk: {r['title']}", r["detail"]))
        add(P.cards("Strategic context", "Drivers and Risks", items, columns=2))

    add(P.section(2, "Phased Approach",
                  spec.get("approach_framing",
                           "A roadmap that balances immediate deadlines against "
                           "long-term optimization.")))

    add(P.phases("Roadmap", f"{len(spec['phases'])}-Phase Engagement",
                 [(ph["name"], ph["window"]) for ph in spec["phases"]]))

    for ph in spec["phases"]:
        detail = [(w["name"], w["detail"]) for w in ph.get("workstreams", [])]
        if detail:
            add(P.cards(ph["window"], ph["name"], detail,
                        columns=2 if len(detail) > 2 else 1))
        else:
            add(P.statement(ph["window"], ph["name"], ph["summary"]))

    add(P.section(3, "Deliverables and Outcomes",
                  "What you receive at each phase, and the measurable impact."))

    deliverable_rows = [[ph["name"], " · ".join(ph.get("deliverables", []))]
                        for ph in spec["phases"] if ph.get("deliverables")]
    if deliverable_rows:
        add(P.data_table("Deliverables", "What You Receive",
                         ["Phase", "Deliverables"], deliverable_rows,
                         widths=[0.24, 0.76]))

    if spec.get("outcomes"):
        add(P.cards("Expected outcomes", "The Measurable Impact",
                    [(o["value"], o["label"]) for o in spec["outcomes"]],
                    columns=min(4, len(spec["outcomes"]))))

    add(P.section(4, "Timeline and Investment",
                  "Schedule and financial summary for the full engagement."))

    add(P.data_table("Investment", "Engagement Summary",
                     ["Phase", "Hours", "Rate", "Investment"], rows,
                     widths=[0.46, 0.16, 0.16, 0.22]))

    if spec.get("investment_notes"):
        add(P.statement("Assumptions", "How to Read These Numbers",
                        spec["investment_notes"]))

    add(P.cards("Why Align HCM", f"Why {client} Should Choose Align",
                [(w["title"], w["detail"]) for w in spec.get("why_us", [
                    {"title": "Deep platform expertise",
                     "detail": "Our consultants are hands-on practitioners, not "
                               "advisors who hand configuration to someone else."},
                    {"title": "Parallel workstream capacity",
                     "detail": "Multiple senior consultants working "
                               "simultaneously across modules."},
                    {"title": "Proven assessment methodology",
                     "detail": "We build stakeholder consensus before major "
                               "investment, de-risking complex programs."},
                ])], columns=3))

    if spec.get("next_steps"):
        add(P.data_table("Next steps", "Proposed Next Steps",
                         ["Step", "What happens", "When"],
                         [[str(i), s["what"], s["when"]]
                          for i, s in enumerate(spec["next_steps"], 1)],
                         widths=[0.08, 0.62, 0.30]))

    contact = spec["contact"]
    add(P.closing(spec.get("closing_title", f"We look forward to partnering with {client}."),
                  spec.get("closing_body",
                           "We would welcome a working session to walk through "
                           "this proposal with your team."),
                  [contact["name"], contact.get("title", ""),
                   contact.get("email", "")]), True)

    return P.with_footers(slides, dark_flags=dark), len(slides), hours_total, money_total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--allow-invalid", action="store_true")
    ap.add_argument("--no-supersede", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-contested", action="store_true",
                    help="render facts that shipped Align documents disagree "
                         "about, instead of failing")
    args = ap.parse_args()

    try:
        spec = load_spec(args.spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    facts = core.Facts(os.path.join(SKILL_ROOT, "scripts", "_core",
                                    "company-facts.md"))
    client = spec["client_name"]
    slides, count, hours, amount = build_slides(spec, facts)

    os.makedirs(args.out_dir, exist_ok=True)
    version = core.next_version(args.out_dir, client, "Proposal", ".pptx")
    name = core.build_name(client, "Proposal", ".pptx", version)
    path = os.path.join(args.out_dir, name)
    P.build(slides, path, title=f"Align HCM Proposal for {client}")

    report = core.Report(name)
    parts = core.read_parts(path)
    core.scan_residue(parts, client, report, extra_terms=spec.get("forbid_terms", ()))
    core.scan_banned_colours(parts, report)
    core.check_filename(name, report)

    stated = spec.get("expected_total")
    if stated is not None and abs(float(stated) - amount) > 0.5:
        report.error("investment",
                     f"phase hours total {money(amount)} but the spec states "
                     f"{money(float(stated))}")
    facts.check(report, args.allow_contested)
    facts.scan_forbidden_claims(parts, report)

    moved = []
    if not args.no_supersede and report.passed:
        moved = core.supersede_previous(args.out_dir, client, "Proposal",
                                        ".pptx", name)

    print(f"wrote {path}")
    print(f"  {count} slides, {len(spec['phases'])} phase(s), "
          f"{hours:,.0f} hours, {money(amount)}")
    if moved:
        print(f"  moved {len(moved)} earlier version(s) to _superseded/")
    print()
    print(report.render())

    if args.json:
        print(json.dumps({"path": path, "slides": count, "hours": hours,
                          "investment": amount, "superseded": moved,
                          **report.as_dict()}, indent=2))

    if not report.passed and not args.allow_invalid:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
