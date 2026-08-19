#!/usr/bin/env python3
"""
Build an Align HCM partner introduction deck.

    python3 build_intro_deck.py --spec homewood.json --out-dir ./decks

This is the deck that goes out with every new deal: who Align is, why
implementations fail, how we implement, governance, change management,
SmartCare, and why us. The narrative order is fixed because it is an argument,
not a list. What changes per prospect is the sector, what their team told us,
and the closing.

The three sections that must be rewritten per prospect are checked. A deck that
still carries the previous prospect's concerns is worse than no deck.

Exit codes:
    0  written and clean
    2  written but failed validation
    3  the spec is incomplete
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

REQUIRED = ["client_name", "platform", "sector", "heard_from_team",
            "why_us", "contact"]

# Failure patterns and the counter for each. These are Align's own, taken from
# the shipped deck, and they do not change per prospect.
FAILURE_PATTERNS = [
    ("A rotating cast of implementation teams",
     "One project manager and a named consultant team, identified at contract "
     "signature and unchanged through go-live."),
    ("Inconsistent or absent project management",
     "Weekly status calls, a shared project plan, RAID log, and health "
     "dashboard, visible to your team throughout."),
    ("Compliance and adoption slip once the builders roll off",
     "SmartCare adds a dedicated HCM admin SME after go-live. The people who "
     "build a system are not always the people who should run it."),
    ("Not enough hands-on participation in testing",
     "We lead unit testing before UAT and schedule collaborative testing "
     "early, so gaps surface before go-live rather than after."),
    ("Slow or unclear decision-making",
     "Decision owners named on both sides at kickoff, backed by a written "
     "change order and a three-step escalation path."),
]

METHODOLOGY = [
    ("Project Readiness", "Before the clock starts"),
    ("Analysis & Design", "You approve the design"),
    ("Configuration & Build", "Your team in the room"),
    ("Acceptance & Parallel", "Twice, on our time"),
    ("Go-Live & Transition", "Documented handoff"),
]

GOVERNANCE = [
    ("Single Point of Accountability",
     "One project manager and a named consultant team, unchanged through go-live."),
    ("Weekly Cadence",
     "Weekly status calls, PM-to-PM calls, and monthly executive check-ins."),
    ("Full Visibility",
     "A shared project plan, RAID log, and health dashboard throughout."),
    ("Protected Capacity",
     "Consultant capacity is tracked centrally, so no one is overbooked."),
    ("Controlled Scope",
     "Scope changes go through a written change order, signed before work begins."),
    ("Clear Escalation",
     "Three steps: project manager, practice lead, then our President and COO."),
]

CHANGE_STAGES = [
    ("1 ALIGN", "Confirm executive sponsor and governance. Identify change leads."),
    ("2 ENGAGE", "Launch the communication plan. Awareness campaigns by role."),
    ("3 TRAIN", "Train-the-trainer delivery. Role-based hands-on sessions."),
    ("4 ADOPT", "Supervisor enforcement, usage tracking, super-user check-ins."),
    ("5 SUSTAIN", "Go-live command centre, escalation paths, refresher cycles."),
]


def load_spec(path):
    with open(path, encoding="utf8") as fh:
        spec = json.load(fh)
    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        raise ValueError("spec is missing required field(s): " + ", ".join(missing))
    if len(spec["heard_from_team"]) < 2:
        raise ValueError("heard_from_team needs at least two points; this section "
                         "is what makes the deck theirs rather than generic")
    if len(spec["why_us"]) < 2:
        raise ValueError("why_us needs at least two points")
    return spec


def load_tiers(path):
    """SmartCare tiers, read from the reference rather than hardcoded."""
    rows = []
    if not os.path.exists(path):
        return rows
    started = False
    for line in open(path, encoding="utf8"):
        if line.startswith("| Tier "):
            started = True
            continue
        if started:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and not set(cells[0]) <= set("- "):
                rows.append(cells[:3])
    return rows


# Two SmartCare vocabularies are live at once. Which one Align chooses is a
# commercial decision; a single document using both is a defect under either
# choice, and that has already shipped once. See references/smartcare-tiers.md.
CLIENT_VOCABULARY = {"optimize", "optimize plus"}
CATALOG_VOCABULARY = {"essentials", "accelerate", "transform"}


def check_tier_vocabulary(tiers, report):
    """
    Fail a deck that mixes the client-facing tier names with the catalog's.
    Stabilize is exempt: it means the same thing in both.
    """
    names = {row[0].strip().lower() for row in tiers}
    client_side = sorted(names & CLIENT_VOCABULARY)
    catalog_side = sorted(names & CATALOG_VOCABULARY)
    if client_side and catalog_side:
        report.error(
            "smartcare",
            f"the tier table mixes vocabularies: {client_side} are client-deck "
            f"names and {catalog_side} are SmartCare Services Catalog names. "
            f"A deck that uses both describes two different products. Pick one "
            f"set in references/smartcare-tiers.md.")
        return
    unknown = sorted(names - CLIENT_VOCABULARY - CATALOG_VOCABULARY - {"stabilize"})
    if unknown:
        report.warn(
            "smartcare",
            f"tier name(s) {unknown} match neither the client-facing set nor "
            f"the catalog set. If this is a deliberate rename, add it to "
            f"references/smartcare-tiers.md and to this check.")


def build_slides(spec, facts, tiers):
    client = spec["client_name"]
    sector = spec["sector"]
    today = spec.get("date") or datetime.date.today().strftime("%B %Y")
    slides, dark = [], []

    def add(shapes, is_dark=False):
        slides.append(shapes)
        dark.append(is_dark)

    add(P.cover(client, f"{spec['platform']} Implementation Services",
                "Partner Introduction",
                [f"Prepared for {client}", today]), True)

    add(P.cards(
        "Who we are", "Who Is Align HCM",
        # Deliberately uses OFFICES / TEAM_CLAIM / RATING_CLAIM rather than
        # HQ, TEAM_SIZE, or REVIEW_COUNT. Those three are contested across
        # shipped Align documents; these formulations are true under all of
        # them. See the contested section of company-facts.md.
        [(f"Founded {facts.get('FOUNDED', '2018')}",
          f"Offices in {facts.get('OFFICES')}."),
         ("Certified team",
          f"{facts.get('TEAM_CLAIM')}. Delivery is "
          f"{facts.get('DELIVERY_MODEL')}."),
         (f"{facts.get('CUSTOMERS_SERVED')} customers",
          f"Served since founding. {facts.get('PROJECTS_DELIVERED')} projects "
          f"delivered."),
         ("Client rating",
          f"{facts.get('RATING_CLAIM')}.")]))

    add(P.statement(
        "The partner", "The Partner Who Understands Both Sides",
        spec.get("both_sides",
                 f"Align's founder, {facts.get('FOUNDER')}, "
                 f"{facts.get('FOUNDER_CREDENTIAL')}. Our consultants are "
                 f"certified across platforms, so we understand what you are "
                 f"leaving as well as where you are going.")))

    add(P.section(1, "What We Heard From Your Team",
                  f"Direct answers to the priorities raised across our "
                  f"conversations with {client}."))
    add(P.cards("What we heard", f"Priorities Raised by {client}",
                [(h["title"], h["detail"]) for h in spec["heard_from_team"]],
                columns=2 if len(spec["heard_from_team"]) > 2 else 1))

    add(P.section(2, "Why Implementations Fail",
                  "The same handful of patterns show up across almost every "
                  "troubled HCM implementation."))
    add(P.data_table("Pattern recognition", "How We Build Against It",
                     ["Common failure pattern", "How Align builds against it"],
                     [[a, b] for a, b in FAILURE_PATTERNS],
                     widths=[0.38, 0.62]))

    add(P.section(3, f"Our Depth in {sector}",
                  spec.get("sector_framing",
                           f"Where a meaningful share of our practice already "
                           f"lives.")))
    if spec.get("sector_proof"):
        add(P.cards("Where we have built our depth",
                    f"Deep Experience in {sector}",
                    [(p["stat"], p["detail"]) for p in spec["sector_proof"]],
                    columns=3 if len(spec["sector_proof"]) >= 3 else 2))

    add(P.phases("Our methodology", f"How We Implement {spec['platform']}",
                 METHODOLOGY, marker_index=4))

    add(P.cards("How we run a project", "Governance and Cadence",
                GOVERNANCE, columns=3))

    add(P.phases("Change management", "Adoption Is the Real Deliverable",
                 CHANGE_STAGES))

    if tiers:
        add(P.data_table("After go-live", "SmartCare: What Happens After Go-Live",
                         ["Tier", "When it applies", "What it covers"],
                         tiers, widths=[0.16, 0.26, 0.58]))

    add(P.cards("Why Align HCM", f"Why Organizations Like {client} Choose Align",
                [(w["title"], w["detail"]) for w in spec["why_us"]],
                columns=3 if len(spec["why_us"]) >= 3 else 2))

    contact = spec["contact"]
    add(P.closing(spec.get("closing_title", "Built for the Work You Do Every Day."),
                  spec.get("closing_body",
                           f"We would welcome the chance to talk with your team "
                           f"about what a {spec['platform']} implementation could "
                           f"look like at {client}."),
                  [contact["name"], contact.get("title", ""),
                   contact.get("email", "")]), True)

    return P.with_footers(slides, dark_flags=dark), len(slides)


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

    core_dir = os.path.join(SKILL_ROOT, "scripts", "_core")
    facts = core.Facts(os.path.join(core_dir, "company-facts.md"))
    tiers = load_tiers(os.path.join(SKILL_ROOT, "references", "smartcare-tiers.md"))

    client = spec["client_name"]
    slides, count = build_slides(spec, facts, tiers)

    os.makedirs(args.out_dir, exist_ok=True)
    version = core.next_version(args.out_dir, client, "Introduction", ".pptx")
    name = core.build_name(client, "Introduction", ".pptx", version)
    path = os.path.join(args.out_dir, name)
    P.build(slides, path, title=f"Align HCM Introduction for {client}")

    report = core.Report(name)
    parts = core.read_parts(path)
    core.scan_residue(parts, client, report, extra_terms=spec.get("forbid_terms", ()))
    core.scan_banned_colours(parts, report)
    core.check_filename(name, report)
    facts.check(report, args.allow_contested)
    facts.scan_forbidden_claims(parts, report)
    if not tiers:
        report.warn("smartcare",
                    "references/smartcare-tiers.md has no tier table, so the "
                    "SmartCare slide was omitted")
    else:
        check_tier_vocabulary(tiers, report)

    moved = []
    if not args.no_supersede and report.passed:
        moved = core.supersede_previous(args.out_dir, client, "Introduction",
                                        ".pptx", name)

    print(f"wrote {path}")
    print(f"  {count} slides")
    if moved:
        print(f"  moved {len(moved)} earlier version(s) to _superseded/")
    print()
    print(report.render())

    if args.json:
        print(json.dumps({"path": path, "slides": count, "version": version,
                          "superseded": moved, **report.as_dict()}, indent=2))

    if not report.passed and not args.allow_invalid:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
