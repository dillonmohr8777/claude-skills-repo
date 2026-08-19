#!/usr/bin/env python3
"""
Build an Align HCM Statement of Work.

    python3 build_sow.py --spec acme.json --out-dir ./sow

The SOW skeleton is fixed. What changes per deal is the client, the platform,
the workstreams, the hours, the rate, and the assumptions. This takes those as
a JSON spec, renders the standard document, checks that nothing from a previous
engagement survived, and writes it under a deterministic name.

Why a spec file rather than twenty flags: a SOW is negotiated. The spec is the
artifact that gets edited between rounds, and it diffs cleanly, which the .docx
does not.

Exit codes:
    0  written and clean
    2  written but failed validation
    3  the spec is incomplete or contradictory
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import alignhcm_core as core          # noqa: E402
import alignhcm_docx as D             # noqa: E402

REQUIRED = ["client_legal_name", "platform", "engagement_title",
            "align_entity", "workstreams", "rate"]

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def money(n):
    return "${:,.0f}".format(n)


def load_spec(path):
    with open(path, encoding="utf8") as fh:
        spec = json.load(fh)
    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        raise ValueError("spec is missing required field(s): " + ", ".join(missing))
    if not isinstance(spec["workstreams"], list) or not spec["workstreams"]:
        raise ValueError("spec needs at least one workstream")
    for i, ws in enumerate(spec["workstreams"], 1):
        for key in ("name", "hours", "description"):
            if key not in ws:
                raise ValueError(f"workstream {i} is missing '{key}'")
    return spec


def totals(spec):
    rate = float(spec["rate"])
    rows, hours_total, money_total = [], 0, 0.0
    for ws in spec["workstreams"]:
        hours = float(ws["hours"])
        amount = hours * rate
        hours_total += hours
        money_total += amount
        rows.append([ws["name"], f"{hours:,.0f}", f"${rate:,.0f}/hr", money(amount)])
    rows.append(["Total", f"{hours_total:,.0f}", "", money(money_total)])
    return rows, hours_total, money_total


def build_blocks(spec, facts):
    client = spec["client_legal_name"]
    rows, hours_total, money_total = totals(spec)
    today = spec.get("date") or datetime.date.today().strftime("%B %Y")

    blocks = [
        D.title("Statement of Work",
                f"{spec['platform']} {spec['engagement_title']}",
                meta=[("Prepared for", client),
                      ("Prepared by", spec["align_entity"]),
                      ("Date", today),
                      ("Status", spec.get("status", "Draft for review"))]),

        D.heading("1. Introduction"),
        D.para(f"This Statement of Work (\"SOW\") is a proposal for "
               f"{spec['align_entity']} (\"Align\") to provide {spec['platform']} "
               f"services to {client} (\"Client\"), and is subject to the terms of "
               f"the governing agreement between the parties. Work not included in "
               f"the deliverables listed below, but requested by Client, is "
               f"additional work and is handled under Section 6."),

        D.heading("2. Scope of Services"),
        D.para(spec.get("scope_summary",
                        f"Align will deliver the workstreams below for {client} "
                        f"on {spec['platform']}.")),
    ]

    for ws in spec["workstreams"]:
        blocks.append(D.heading(ws["name"], 2))
        blocks.append(D.para(ws["description"]))
        if ws.get("deliverables"):
            blocks.append(D.bullets(ws["deliverables"]))

    blocks += [
        D.heading("3. Align Responsibilities"),
        D.bullets(spec.get("align_responsibilities", [
            "Assign a named project manager and consultant team at signature, "
            "unchanged through go-live.",
            "Facilitate a weekly project status call and maintain the project "
            "plan and RAID log.",
            "Lead unit testing before user acceptance testing begins.",
            "Provide production support through the agreed stabilization period.",
        ])),

        D.heading("4. Client Responsibilities"),
        D.para("The engagement assumes Client participation at the levels below. "
               "Schedule risk follows directly from availability, so these are "
               "commitments rather than estimates."),
        D.bullets(spec.get("client_responsibilities", [
            "Name an executive sponsor and a project lead empowered to decide.",
            "Make subject matter experts available for analysis, validation, and "
            "testing at the hours per week stated in the project plan.",
            "Provide source data extracts and complete the data collection "
            "templates by the dates in the project plan.",
            "Review and sign off on requirements, configuration, data conversion, "
            "and testing at each gate.",
        ])),

        D.heading("5. Assumptions"),
        D.bullets(spec.get("assumptions", [
            "Pricing assumes the scope described above and the participation "
            "levels in Section 4.",
            "Services are delivered remotely unless onsite days are itemized.",
            "One production environment and one non-production environment.",
        ])),

        D.heading("6. Change Control"),
        D.para("Any change to scope, timeline, or investment is documented in a "
               "written change order, reviewed by Align's executive sponsor, and "
               "signed by both parties before the work begins. Work performed "
               "without a signed change order is not billable and not scheduled."),

        D.heading("7. Investment"),
        D.para(f"Services are delivered on a time and materials basis at a blended "
               f"rate of ${float(spec['rate']):,.0f} per hour."),
        D.table(["Workstream", "Hours", "Rate", "Investment"], rows,
                widths=[4000, 1500, 1600, 2100]),
    ]

    if spec.get("investment_notes"):
        blocks.append(D.para(spec["investment_notes"], size=19,
                             color=D.MUTED))

    blocks += [
        D.heading("8. Term"),
        D.para(spec.get("term",
                        "This SOW begins on the date of last signature and "
                        "continues until the deliverables in Section 2 are "
                        "accepted, or until terminated under the governing "
                        "agreement.")),
        D.page_break(),
        D.heading("9. Acceptance"),
        D.para("Signature below indicates agreement to the scope, assumptions, "
               "responsibilities, and investment described in this Statement of "
               "Work."),
        D.signature_block([
            f"{client}\nName, title, and date",
            f"{spec['align_entity']}\nName, title, and date"]),
    ]
    return blocks, hours_total, money_total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="path to the deal spec JSON")
    ap.add_argument("--out-dir", default=".", help="directory to write into")
    ap.add_argument("--allow-invalid", action="store_true",
                    help="write the file even if validation fails")
    ap.add_argument("--no-supersede", action="store_true",
                    help="leave older versions in place instead of archiving them")
    ap.add_argument("--json", action="store_true", help="machine-readable summary")
    args = ap.parse_args()

    try:
        spec = load_spec(args.spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    facts = core.Facts(os.path.join(SKILL_ROOT, "scripts", "_core",
                                    "company-facts.md"))
    if facts.stale():
        print(f"note: company facts were due for review on {facts.review_by}",
              file=sys.stderr)

    client = spec["client_legal_name"]
    blocks, hours, amount = build_blocks(spec, facts)

    os.makedirs(args.out_dir, exist_ok=True)
    version = core.next_version(args.out_dir, client, "SOW", ".docx")
    name = core.build_name(client, "SOW", ".docx", version)
    path = os.path.join(args.out_dir, name)
    D.build(blocks, path, doc_title=f"{client} Statement of Work",
            footer_text="alignhcm.com  ·  Confidential")

    report = core.Report(name)
    parts = core.read_parts(path)
    core.scan_residue(parts, client, report,
                      extra_terms=spec.get("forbid_terms", ()))
    core.scan_banned_colours(parts, report)
    core.check_filename(name, report)

    # A SOW whose numbers do not add up is worse than one that is late.
    stated = spec.get("expected_total")
    if stated is not None and abs(float(stated) - amount) > 0.5:
        report.error("investment",
                     f"the workstream table totals {money(amount)} but the spec "
                     f"states an expected total of {money(float(stated))}")

    moved = []
    if not args.no_supersede and report.passed:
        moved = core.supersede_previous(args.out_dir, client, "SOW", ".docx", name)

    print(f"wrote {path}")
    print(f"  {len(spec['workstreams'])} workstream(s), {hours:,.0f} hours, "
          f"{money(amount)}")
    if moved:
        print(f"  moved {len(moved)} earlier version(s) to _superseded/")
    print()
    print(report.render())

    if args.json:
        print(json.dumps({"path": path, "version": version,
                          "hours": hours, "investment": amount,
                          "superseded": moved,
                          **report.as_dict()}, indent=2))

    if not report.passed and not args.allow_invalid:
        print("\nValidation failed. Fix the spec and rebuild, or pass "
              "--allow-invalid to keep the file anyway.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
