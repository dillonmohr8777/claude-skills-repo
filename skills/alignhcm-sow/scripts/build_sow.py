#!/usr/bin/env python3
"""
Build an Align HCM Statement of Work.

    python3 build_sow.py --spec acme.json --out-dir ./sow

The skeleton is Align's real SOW template, section for section: the one in
SharePoint under `1 - All Things Sales/Templates/SOWs/`. What changes per deal
is the client, the platform, the modules in scope, their assumptions, the
client parameters, and the money. This takes those as a JSON spec, renders the
document, checks that nothing from a previous engagement survived, and writes
it under a deterministic name.

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

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Align signs as one of exactly two legal entities. Which one is a real legal
# decision, not a formatting preference, so the spec has to say. Guessing it
# would put the wrong company on a contract.
ENTITIES = ("Align HCM, Inc.", "Align HCM Services LLC")

PRICING_MODELS = ("fixed_fee", "time_and_materials")

CURRENCIES = {"USD": "$", "CAD": "CA$"}

REQUIRED = ["client_legal_name", "platform", "engagement_title",
            "align_entity", "pricing_model", "scope_items"]

# Verbatim from the template. These are the same in every Align SOW, which is
# exactly why they belong in code rather than in each drafter's copy-paste.
PM_PROCESS = [
    ("Planning for Scope and Resources",
     "Reviewing all contract documents and confirming deliverables the project "
     "team will complete. The scope is defined during the analysis of your "
     "business requirements in the planning phase. Assembling the project team, "
     "so the proper resources with the right skills are available for specific "
     "tasks when needed."),
    ("Developing the Project Schedule",
     "Creating a list of tasks and placing them in sequence with due dates. The "
     "schedule identifies critical tasks and milestones so the project team "
     "knows where to focus. The project schedule is documented in Smartsheet."),
    ("Creating and Maintaining an Action Log",
     "Creating and maintaining a list of open Risks, Actions, Issues, Decisions, "
     "and change requests. A Project RAID Log is maintained during the project "
     "in Smartsheet."),
    ("Facilitating Status Meetings",
     "Scheduling and executing recurring team meetings to review the project "
     "dashboard, schedule, RAID Log, and project risks in Smartsheet. Working "
     "sessions to resolve items are scheduled outside of the status meetings."),
    ("Managing Risk",
     "Identifying, mitigating, and controlling scope creep, schedule impacts, "
     "and resource management."),
    ("Closing the Project",
     "Confirm all project deliverables have been delivered and accepted by an "
     "authorized team member."),
]

# UKG Launch phase names. Note these are the UKG labels, not the five Align
# phase names in alignhcm-pm-runbook; they map one to one but a SOW uses these.
LAUNCH_PHASES = [
    ("WELCOME",
     "Readiness and Planning activities, resource assignments, Client "
     "preparation and information gathering, and a kickoff meeting."),
    ("REQUIREMENTS",
     "Analysis and Design. Collaborative working sessions with Align and Client "
     "subject matter experts to understand current requirements, analyze and "
     "define future state requirements, and decide on future system design."),
    ("BUILD",
     "CONFIGURE: the applicable systems are configured and unit testing is "
     "performed. CONVERT: the Client's source data from their legacy system is "
     "converted into the platform. INTEGRATE: unification of applications and "
     "file integrations are built."),
    ("TEST",
     "Functional testing, user acceptance testing, pilot testing, and parallel "
     "testing as appropriate for the applicable modules."),
    ("GO-LIVE",
     "Align assists the Client with the first live processing, the Client "
     "rollout of the solution, and transition to ongoing support."),
]

ALIGN_ROLES = [
    ("Executive Sponsor",
     "Act as Align project sponsor responsible to gain commitment for all "
     "project resources. Provide executive-level support to the project team."),
    ("Project Manager",
     "Serve as primary point of contact responsible for achieving project "
     "objectives. Develop and manage the project schedule, communicate overall "
     "status, and serve as the initial point of escalation for all project "
     "related issues."),
    ("Lead Solution Consultant",
     "Provide oversight for the solution consultants, assist in resolving "
     "system configuration issues, and complete Quality Assessments during the "
     "implementation to ensure alignment with platform best practices."),
    ("Solution Consultant",
     "Serve as primary point of contact for implementation activities and lead "
     "specific workstreams based on expertise."),
    ("Integration Consultant",
     "Create and deliver all in-scope integrations. Work with Client and "
     "third-party vendors to determine requirements for file automation."),
]

CLIENT_ROLES = [
    ("Executive Sponsor",
     "Act as Client project sponsor responsible to gain commitment for all "
     "project resources and provide executive-level support to the project team."),
    ("Project Manager / Lead",
     "Serve as primary point of contact responsible for achieving project "
     "objectives. Identify and manage project risks and serve as the Client's "
     "initial point of escalation."),
    ("System Administrator",
     "Serve as the Client's primary resource for system configuration, testing, "
     "system knowledge, and application security. Responsible for ramping up on "
     "the modules in scope to assume ownership of the configured system during "
     "testing, go-live, and after."),
    ("Technical Resource",
     "Serve as the Client's primary resource for technical issues related to "
     "integrations, network, subscription service security, and data conversion."),
    ("Subject Matter Experts",
     "Serve as the Client's primary representative and designated decision maker "
     "in key areas such as Payroll, HR, Workforce Management, Scheduling, "
     "Benefits, Talent Acquisition, and Learning."),
    ("Education and Change Management Resource",
     "Act as the Client's primary resource and designated decision maker for end "
     "user training, user adoption, and change management."),
]

STANDARD_OUT_OF_SCOPE = [
    ("Application Customizations",
     "Customization is any system change that extends the applications beyond "
     "what the delivered application provides. Creating, delivering, and testing "
     "customizations are not included in the scope of this SOW."),
    ("Non-Platform Applications and Hardware",
     "Troubleshooting applications or hardware not provided by the platform "
     "vendor is the responsibility of the Client."),
    ("Training Materials and End User Training",
     "If additional change management, end-user training, or train-the-trainer "
     "services are needed from Align resources, the Client must define "
     "requirements and request additional services no fewer than four weeks in "
     "advance to allow lead time to resource the appropriate team member."),
    ("Vendor Service Requests",
     "For services that must be provided by the platform vendor, a separate "
     "service request is required and may result in additional costs to Client. "
     "Project timelines are dependent on vendor response time and resource "
     "availability."),
    ("Translations",
     "Align will load pre-defined translated codes, titles, and descriptions. "
     "The Client team must provide any custom translations in an approved "
     "template."),
]

STANDARD_ADDITIONAL_TERMS = [
    "Work on this project will be completed at the offices of Align, the "
    "platform vendor, and/or Client. Assigned resources are not 100% dedicated "
    "to this project unless previously stated, and as such last-minute "
    "scheduling of meetings cannot always be accommodated. It may take up to 48 "
    "hours for a response to emails and inquiries.",
    "Standard hours are 8:00 AM to 6:00 PM Eastern Time, Monday through Friday. "
    "Any request for time outside of this period must be approved by the Align "
    "Executive Sponsor two weeks prior to the required dates.",
    "Signoffs document the Client-provided requirements and the Client's "
    "acceptance of the system delivered against them. Sign-off requires an "
    "identified signee on the Client team capable of deliverable acceptance. An "
    "escalation will occur if a response is not provided within five (5) "
    "business days from delivery. Signoff will be considered accepted if no "
    "response is provided within two (2) business days from the escalation. "
    "Denials will be addressed and adjustments made by the Align team, allowing "
    "for an additional iteration before final acceptance.",
    "If a Client is unwilling to provide sign-offs during the project, Align "
    "reserves the right to terminate the engagement and/or not support the "
    "Client once they are live with payroll.",
    "The Client is responsible for coordinating and scheduling partners and "
    "vendors required for project activities in advance to ensure no impact on "
    "timelines.",
    "Align will have access to Client subject matter experts as necessary and "
    "appropriate during pre-approved times to validate project assumptions, "
    "data, requirements, and content.",
    "During the project, the platform vendor will release product updates and "
    "features that were not available during scoping. Implementation of these "
    "features is considered out of scope but will be assessed by the team on a "
    "case-by-case basis.",
    "This estimate is based on the current understanding of the Client's "
    "requirements. Align reserves the right to request additional fees should "
    "the scope of work be significantly different from the initial assumptions "
    "presented by the Client team, including any acquisitions, mergers, or "
    "additional locations.",
    "The Client will be responsible for the actual cost of any travel expenses "
    "associated with the project. All travel must be pre-approved by the Client "
    "and the Align Executive Sponsor.",
]

CLIENT_DETAIL_FIELDS = [
    ("licensed_employees", "Total Licensed Employees"),
    ("target_start", "Target Project Start"),
    ("target_go_live", "Target Project Go-Live"),
    ("business_numbers", "Number of BNs"),
    ("provinces", "Number of Provinces"),
    ("union_cbas", "Number of Union CBAs"),
    ("countries", "Number of Countries"),
    ("locations", "Number of Locations"),
    ("clocks", "Number of Clocks"),
    ("legacy_systems", "Legacy Systems"),
]


def symbol(spec):
    return CURRENCIES[spec.get("currency", "USD")]


def money(spec, n):
    return "{}{:,.0f}".format(symbol(spec), n)


def load_spec(path):
    with open(path, encoding="utf8") as fh:
        spec = json.load(fh)

    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        raise ValueError("spec is missing required field(s): " + ", ".join(missing))

    if spec["align_entity"] not in ENTITIES:
        raise ValueError(
            "align_entity must be exactly one of {}; got {!r}. Which entity "
            "signs is a legal decision and this tool will not guess it."
            .format(" or ".join(repr(e) for e in ENTITIES), spec["align_entity"]))

    if spec["pricing_model"] not in PRICING_MODELS:
        raise ValueError("pricing_model must be one of " + ", ".join(PRICING_MODELS))

    if spec.get("currency", "USD") not in CURRENCIES:
        raise ValueError("currency must be one of " + ", ".join(CURRENCIES))

    if not isinstance(spec["scope_items"], list) or not spec["scope_items"]:
        raise ValueError("spec needs at least one entry in scope_items")
    for i, item in enumerate(spec["scope_items"], 1):
        for key in ("application", "assumptions"):
            if key not in item:
                raise ValueError(f"scope_items[{i}] is missing '{key}'")
        if not isinstance(item["assumptions"], list) or not item["assumptions"]:
            raise ValueError(
                f"scope_items[{i}] ({item['application']}) has no assumptions. "
                f"An application in scope with no stated assumptions is how a "
                f"fixed fee becomes an argument.")

    if spec["pricing_model"] == "fixed_fee":
        if not spec.get("milestones"):
            raise ValueError("a fixed_fee SOW needs 'milestones': "
                             "[{'label': ..., 'amount': ...}, ...]")
        for i, ms in enumerate(spec["milestones"], 1):
            if "label" not in ms or "amount" not in ms:
                raise ValueError(f"milestones[{i}] needs 'label' and 'amount'")
    else:
        if not spec.get("rate"):
            raise ValueError("a time_and_materials SOW needs 'rate'")
        if not spec.get("workstreams"):
            raise ValueError("a time_and_materials SOW needs 'workstreams'")
        for i, ws in enumerate(spec["workstreams"], 1):
            for key in ("name", "hours"):
                if key not in ws:
                    raise ValueError(f"workstreams[{i}] is missing '{key}'")
    return spec


def fee_table(spec):
    """Return (headers, rows, widths, total). Computed, never typed."""
    if spec["pricing_model"] == "fixed_fee":
        rows, total = [], 0.0
        for ms in spec["milestones"]:
            amount = float(ms["amount"])
            total += amount
            rows.append([ms["label"], money(spec, amount)])
        rows.append(["Total", money(spec, total)])
        return ["Payment Milestone", "Amount"], rows, [6600, 2600], total

    rate = float(spec["rate"])
    rows, hours_total, total = [], 0.0, 0.0
    for ws in spec["workstreams"]:
        hours = float(ws["hours"])
        amount = hours * rate
        hours_total += hours
        total += amount
        rows.append([ws["name"], f"{hours:,.0f}",
                     f"{symbol(spec)}{rate:,.0f}/hr", money(spec, amount)])
    rows.append(["Total", f"{hours_total:,.0f}", "", money(spec, total)])
    return (["Workstream", "Hours", "Rate", "Investment"], rows,
            [4000, 1500, 1600, 2100], total)


def build_blocks(spec):
    client = spec["client_legal_name"]
    entity = spec["align_entity"]
    today = spec.get("date") or datetime.date.today().strftime("%B %Y")
    headers, rows, widths, total = fee_table(spec)
    model_phrase = ("a fixed fee proposal" if spec["pricing_model"] == "fixed_fee"
                    else "a time and materials proposal")

    blocks = [
        D.title("Statement of Work",
                f"{spec['platform']} {spec['engagement_title']}",
                meta=[("Prepared for", client),
                      ("Prepared by", entity),
                      ("Date", today),
                      ("Status", spec.get("status", "Draft for review"))]),

        # The preamble carries the MSA subordination and the change-order
        # promise. Every Align SOW opens with it; losing it is what turns a
        # scope dispute into a billing dispute.
        D.para(f"This Statement of Work (SOW) is a proposal for {entity} "
               f"(\"Align\") to provide {spec['platform']} "
               f"{spec['engagement_title'].lower()} to {client} (\"Client\") and "
               f"is subject to the terms and conditions set forth in the Align "
               f"Master Services Agreement (MSA) or such other existing "
               f"underlying agreement between the Parties. The pricing in this "
               f"SOW is based on the deliverables listed below. This is "
               f"{model_phrase}."),
        D.para("Align reserves the right to request additional fees for any work "
               "not included in the deliverables listed below but required by "
               "Client. This additional work will only proceed after a "
               "supplemental Change Order is reviewed and approved by Client in "
               "advance."),

        D.heading("1. Client Details"),
    ]

    details = spec.get("client_details", {})
    detail_rows = [[label, str(details.get(key, "To be confirmed"))]
                   for key, label in CLIENT_DETAIL_FIELDS
                   if key in details or spec.get("show_all_client_details")]
    if detail_rows:
        blocks.append(D.table(["Item", "Value"], detail_rows, widths=[4600, 4600]))
    else:
        blocks.append(D.para("Client details to be confirmed before execution."))

    blocks += [
        D.heading("2. Services in Scope"),
        D.para(spec.get("scope_summary",
                        f"Implementation of the following {spec['platform']} "
                        f"products is in scope and will be configured in "
                        f"accordance with the launch methodology and assumptions "
                        f"described in this document.")),
        D.bullets([item["application"] for item in spec["scope_items"]]),

        D.heading("3. Service Assumptions"),
    ]
    for item in spec["scope_items"]:
        blocks.append(D.heading(item["application"], 2))
        blocks.append(D.para("Align will:"))
        blocks.append(D.bullets(item["assumptions"]))

    blocks.append(D.heading("4. Project Management Process"))
    blocks.append(D.table(["Process", "Description"],
                          [[name, text] for name, text in PM_PROCESS],
                          widths=[2900, 6300]))

    blocks += [
        D.heading("5. Launch Methodology"),
        D.para(spec.get("methodology_framing",
                        "Align utilizes a launch methodology framework that "
                        "provides proven and repeatable processes, enabling "
                        "project teams to measure progress and results. Align "
                        "partners with the Client throughout the launch process "
                        "and provides solid knowledge transfer from the "
                        "consultants to the Client system administrators.")),
        D.table(["Phase", "Phase Description"],
                [[name, text] for name, text in LAUNCH_PHASES],
                widths=[2200, 7000]),

        D.heading("6. Launch Parameters"),
    ]
    params = spec.get("launch_parameters") or []
    if params:
        blocks.append(D.table(["Launch Item", "Assumptions"],
                              [[p["item"], p["detail"]] for p in params],
                              widths=[2600, 6600]))
    else:
        blocks.append(D.para(
            "Launch parameters covering training, change management, data "
            "conversion, dual maintenance, and integrations are to be confirmed "
            "with the Client before execution."))

    blocks += [
        D.heading("7. Roles, Responsibilities, and Deliverables"),
        D.para("A successful launch assumes Client participation throughout each "
               "phase of the project. Roles and responsibilities for both Align "
               "and Client are described below, along with the primary launch "
               "deliverables and acceptance criteria."),
    ]
    phases = spec.get("phase_deliverables") or []
    if phases:
        blocks.append(D.table(["Launch Phase", "Align HCM Deliverables",
                               "Client Deliverables"],
                              [[p["phase"], "\n".join(p.get("align", [])),
                                "\n".join(p.get("client", []))] for p in phases],
                              widths=[1800, 3700, 3700]))

    blocks += [
        D.heading("8. Resources"),
        D.para("Align will provide experienced resources and subject matter "
               "experts specializing in specific areas of the launch associated "
               "with the services purchased."),
        D.table(["Align Resource", "Key Responsibilities"],
                [[name, text] for name, text in ALIGN_ROLES],
                widths=[2600, 6600]),
        D.para("Client will provide resources and subject matter experts as "
               "described below, or as otherwise mutually agreed in the project "
               "plan."),
        D.table(["Client Resource", "Key Responsibilities"],
                [[name, text] for name, text in CLIENT_ROLES],
                widths=[2600, 6600]),

        D.heading("9. Out of Scope"),
        D.para("Additional consulting services outside the scope of this "
               "Statement of Work shall be quoted to the Client for a fee. Said "
               "services will not be provided without a Change Order executed by "
               "both parties."),
    ]
    out_rows = [[name, text] for name, text in STANDARD_OUT_OF_SCOPE]
    out_rows += [[e["item"], e["detail"]] for e in spec.get("out_of_scope", [])]
    blocks.append(D.table(["Service", "Detail"], out_rows, widths=[2600, 6600]))

    blocks.append(D.heading("10. Change Requests"))
    change = []
    if spec.get("change_order_rate"):
        change.append(
            f"The hourly rate for Change Orders is "
            f"{symbol(spec)}{float(spec['change_order_rate']):,.0f} per hour "
            f"{spec.get('currency', 'USD')}.")
    change += [
        "Go-live date changes: a timeline extension triggered by the Client for "
        "convenience, Client resource capacity restriction, or the Client's "
        "ability to meet deliverables in a timely manner, except those beyond "
        "the control of the Client, will incur a cost determined at the time of "
        "the change. Align will notify Client at least two weeks before a change "
        "request is issued, and a discussion will be held to determine if the "
        "situation can be remedied.",
        "Change to requirements after scope sign-off: if a significant change to "
        "the system design is brought forward after scope sign-off, the level of "
        "effort estimated to accommodate the change will be presented to the "
        "Client for approval prior to revisiting the system design.",
        "Change to configuration post build: if a significant change to the "
        "system build is brought forward after the system is configured, the "
        "level of effort estimated will be presented to the Client for approval "
        "prior to revisiting the system design.",
    ]
    blocks.append(D.bullets(change))

    blocks += [
        D.heading("11. Additional Terms"),
        D.bullets(STANDARD_ADDITIONAL_TERMS + list(spec.get("additional_terms", []))),

        D.heading("12. Fees, Payment Terms, Expenses and Billing"),
        D.table(headers, rows, widths=widths),
        D.para("The pricing indicated is not inclusive of applicable taxes where "
               "required by law. All deliverables will be provided to the Client "
               "electronically."),
        D.para("Align acknowledges and agrees that all worldwide right, title and "
               "interest in and to any and all work product, designs, works of "
               "authorship, deliverables, improvements, innovations, discoveries "
               "and inventions conceived, made or reduced to practice while "
               "performing services under this Agreement shall be the sole "
               "property of Client effective upon payment by Client."),
    ]

    valid_through = spec.get("pricing_valid_through")
    if valid_through:
        blocks.append(D.para(
            f"The pricing outlined in this Statement of Work is valid through "
            f"{valid_through}. If the SOW is not fully executed by this date, "
            f"Align reserves the right to revise the pricing, delivery timeline, "
            f"and resource availability based on current rates and capacity."))

    if spec.get("investment_notes"):
        blocks.append(D.para(spec["investment_notes"], size=19, color=D.MUTED))

    blocks += [
        D.page_break(),
        D.heading("13. Acknowledgements"),
        D.para("The terms and conditions of the Master Services Agreement "
               "executed by the Parties contemporaneously with this Statement of "
               "Work apply in full to the services and products provided under "
               "this Statement of Work. All capitalized terms used herein shall "
               "have the meaning assigned in the Master Services Agreement. If "
               "there is any conflict in terms between the MSA and this or any "
               "other document signed by the parties, the terms of the MSA will "
               "prevail."),
        D.para("IN WITNESS WHEREOF, the parties hereto, each acting with proper "
               "authority, have executed this Statement of Work."),
        D.signature_block([
            f"{entity}\nSignature, name, title, and date",
            f"{client}\nSignature, name, title, and date"]),
    ]
    return blocks, total


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

    client = spec["client_legal_name"]
    blocks, total = build_blocks(spec)

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
    facts.check(report, args.allow_contested)
    facts.scan_forbidden_claims(parts, report)

    # A SOW whose numbers do not add up is worse than one that is late.
    stated = spec.get("expected_total")
    if stated is not None and abs(float(stated) - total) > 0.5:
        report.error("fees",
                     f"the fee table totals {money(spec, total)} but the spec "
                     f"states an expected total of {money(spec, float(stated))}")

    # The other document that names a price is the proposal. If they disagree,
    # someone finds out at signature.
    if not spec.get("pricing_valid_through"):
        report.warn("fees", "no pricing_valid_through date, so the quote never "
                            "expires and stale pricing can be executed months later")

    moved = []
    if not args.no_supersede and report.passed:
        moved = core.supersede_previous(args.out_dir, client, "SOW", ".docx", name)

    print(f"wrote {path}")
    print(f"  {len(spec['scope_items'])} application(s) in scope, "
          f"{spec['pricing_model']}, {money(spec, total)}")
    if moved:
        print(f"  moved {len(moved)} earlier version(s) to _superseded/")
    print()
    print(report.render())

    if args.json:
        print(json.dumps({"path": path, "version": version,
                          "pricing_model": spec["pricing_model"],
                          "total": total, "superseded": moved,
                          **report.as_dict()}, indent=2))

    if not report.passed and not args.allow_invalid:
        print("\nValidation failed. Fix the spec and rebuild, or pass "
              "--allow-invalid to keep the file anyway.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
