#!/usr/bin/env python3
"""Prove the SOW skill works. Run before publishing any edit."""
import json, os, pathlib, re, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402
import alignhcm_core as core  # noqa: E402

SPEC = {
    "client_legal_name": "Northwind Traders, Inc.",
    "align_entity": "Align HCM Services LLC",
    "platform": "UKG Pro",
    "engagement_title": "Full Suite Launch",
    "pricing_model": "fixed_fee",
    "currency": "USD",
    "pricing_valid_through": "31 December 2026",
    "change_order_rate": 225,
    "expected_total": 360000,
    "client_details": {
        "licensed_employees": 650,
        "target_start": "March 2027",
        "target_go_live": "January 2028",
        "countries": 2,
        "locations": 14,
        "legacy_systems": "ADP Workforce Now",
    },
    "scope_items": [
        {"application": "UKG Pro Pay and People Center - US",
         "assumptions": [
             "Implement HR, Payroll, Benefits, ESS/MSS, and standard interfaces.",
             "Support one launch of UKG Pro Pay and UKG Pro People Center."]},
        {"application": "UKG Pro Workforce Management (Timekeeping and Accruals)",
         "assumptions": [
             "Configure up to 6 employee pay rules.",
             "Configure up to 4 accrual policies.",
             "Load accrual balances once during testing and once for go-live."]},
    ],
    "launch_parameters": [
        {"item": "Data Conversion",
         "detail": "Align will complete 1 x Employee Master File Conversion and "
                   "2 x Payroll Balance Conversion per region."},
    ],
    "milestones": [
        {"label": "Contract Execution", "amount": 1000},
        {"label": "Month 2 Fees", "amount": 89750},
        {"label": "Month 3 Fees", "amount": 89750},
        {"label": "Month 4 Fees", "amount": 89750},
        {"label": "Month 5 Fees", "amount": 89750},
    ],
}


def _text_of(directory):
    doc = [f for f in os.listdir(directory) if f.endswith(".docx")][0]
    return core.visible_text(core.read_parts(os.path.join(directory, doc)))


@S.check("documented workflow produces a clean SOW")
def _happy():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        if code != 0:
            return False, f"exit {code}: {out.strip()[-200:]}"
        made = [f for f in os.listdir(tmp) if f.endswith(".docx")]
        return len(made) == 1, f"wrote {made[0] if made else 'nothing'}"


@S.check("all thirteen template sections are present, in order")
def _sections():
    want = ["1. Client Details", "2. Services in Scope", "3. Service Assumptions",
            "4. Project Management Process", "5. Launch Methodology",
            "6. Launch Parameters", "7. Roles, Responsibilities, and Deliverables",
            "8. Resources", "9. Out of Scope", "10. Change Requests",
            "11. Additional Terms",
            "12. Fees, Payment Terms, Expenses and Billing",
            "13. Acknowledgements"]
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        text = _text_of(tmp)
    missing = [w for w in want if w not in text]
    if missing:
        return False, f"missing {missing}"
    positions = [text.index(w) for w in want]
    return positions == sorted(positions), f"{len(want)} sections, correct order"


@S.check("the MSA clauses survive into the document")
def _msa_clauses():
    """
    These four are the load-bearing legal sentences in Align's template. A SOW
    that loses them reads fine and protects nobody.
    """
    needles = {
        "MSA subordination": "Master Services Agreement (MSA) or such other "
                             "existing underlying agreement",
        "change order gate": "only proceed after a supplemental Change Order",
        "MSA precedence": "the terms of the MSA will prevail",
        "IP on payment": "sole property of Client effective upon payment",
        "signoff escalation": "within two (2) business days from the escalation",
    }
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        text = " ".join(_text_of(tmp).split())
    missing = [name for name, needle in needles.items()
               if " ".join(needle.split()) not in text]
    return not missing, ("missing " + ", ".join(missing) if missing
                         else f"all {len(needles)} present")


@S.check("an invented signing entity is rejected")
def _entity():
    """
    The old spec said "Align HCM Services, LLC" with a comma. Align signs as
    "Align HCM Services LLC" or "Align HCM, Inc." and nothing else.
    """
    spec = dict(SPEC, align_entity="Align HCM Services, LLC")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        wrote = [f for f in os.listdir(tmp) if f.endswith(".docx")]
        return code == 3 and not wrote, f"exit {code}, wrote {len(wrote)} file(s)"


@S.check("an application in scope with no assumptions is rejected")
def _bare_scope():
    spec = json.loads(json.dumps(SPEC))
    spec["scope_items"][1]["assumptions"] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 3 and "assumptions" in out, f"exit {code}"


@S.check("time and materials pricing computes from hours")
def _tandm():
    spec = json.loads(json.dumps(SPEC))
    spec.pop("milestones")
    spec["pricing_model"] = "time_and_materials"
    spec["rate"] = 200
    spec["workstreams"] = [{"name": "Core HR and Payroll", "hours": 900},
                           {"name": "Workforce Management", "hours": 900}]
    spec["expected_total"] = 360000
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 0 and "$360,000" in out, f"exit {code}: {out.strip()[-160:]}"


@S.check("filename follows the convention")
def _naming():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        made = [f for f in os.listdir(tmp) if f.endswith(".docx")][0]
        ok = re.fullmatch(r"Northwind-Traders-Inc_SOW_\d{4}-\d{2}-\d{2}_v1\.docx", made)
        return bool(ok), made


@S.check("second build supersedes the first")
def _supersede():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        live = [f for f in os.listdir(tmp) if f.endswith(".docx")]
        archived = os.listdir(os.path.join(tmp, "_superseded")) if \
            os.path.isdir(os.path.join(tmp, "_superseded")) else []
        if len(live) != 1 or not live[0].endswith("_v2.docx"):
            return False, f"live folder holds {live}"
        return len(archived) == 1, f"v2 live, {len(archived)} archived, nothing deleted"


@S.check("a previous client's name is caught")
def _residue():
    spec = dict(SPEC, scope_summary="Implementation for Prime Communications.")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 2 and "Prime Communications" in out, f"exit {code}"


@S.check("residue scan does not fire on ordinary words")
def _no_false_positive():
    spec = dict(SPEC, scope_summary="Scope changes go through a written change order.")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 0, f"exit {code}: 'changes' must not match the entity GES"


@S.check("fee arithmetic is enforced")
def _math():
    spec = dict(SPEC, expected_total=999999)
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 2 and "360,000" in out, f"exit {code}"


@S.check("a missing price expiry is flagged")
def _expiry():
    spec = json.loads(json.dumps(SPEC))
    spec.pop("pricing_valid_through")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return "never expires" in out, "warned about open-ended pricing"


@S.check("Canadian dollars render as CA$")
def _currency():
    spec = json.loads(json.dumps(SPEC))
    spec["currency"] = "CAD"
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        text = _text_of(tmp)
        return "CA$" in text and code == 0, f"exit {code}"


@S.check("an incomplete spec is rejected before writing")
def _incomplete():
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), {"client_legal_name": "X"})
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        wrote = [f for f in os.listdir(tmp) if f.endswith(".docx")]
        return code == 3 and not wrote, f"exit {code}, wrote {len(wrote)} file(s)"


@S.check("the .docx opens in a real renderer")
def _renders():
    from shutil import which
    if not which("soffice"):
        return True, "skipped, LibreOffice not installed"
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        doc = [f for f in os.listdir(tmp) if f.endswith(".docx")][0]
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/lo",
                        "--headless", "--norestore", "--convert-to", "pdf",
                        "--outdir", tmp, os.path.join(tmp, doc)],
                       capture_output=True, timeout=500)
        pdfs = [f for f in os.listdir(tmp) if f.endswith(".pdf")]
        return bool(pdfs), f"rendered {pdfs[0] if pdfs else 'nothing'}"


if __name__ == "__main__":
    sys.exit(S.run("alignhcm-sow"))
