#!/usr/bin/env python3
"""Prove the alignhcm-pm-runbook skill works. Run before publishing any edit."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402

TITLE = "alignhcm-pm-runbook"
SCRIPT = "build_status_report.py"
EXT = ".docx"

SPEC = {
    "client": "Northwind Traders", "project": "Dayforce Full Suite Launch",
    "pm": "Joann Scolaro, CPP", "reporting_period": "Week 12",
    "overall_status": "yellow", "go_live": "January 2027",
    "workstreams": [{"name": "HR/Payroll", "phase": "System Test",
                     "status": "green", "note": "Signed off."}],
    "accomplishments": ["Payroll configuration signed off"],
    "risks": [{"item": "Carrier feed format unconfirmed", "severity": "high",
               "owner": "Client", "mitigation": "Escalated to vendor."}]}


def LEAK(spec):
    spec["status_narrative"] = "Tracking as it did for Prime Communications."


@S.check("documented workflow produces a clean status report")
def _happy():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        if code != 0:
            return False, f"exit {code}: {out.strip()[-160:]}"
        return "status YELLOW" in out, out.strip().splitlines()[1].strip()


@S.check("green is refused while a high risk is open")
def _honest_status():
    spec = json.loads(json.dumps(SPEC))
    spec["overall_status"] = "green"
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 2 and "GREEN" in out, f"exit {code}"


@S.check("green is refused while a decision is overdue")
def _overdue_decision():
    spec = json.loads(json.dumps(SPEC))
    spec["overall_status"] = "green"
    spec["risks"] = []
    spec["decisions_needed"] = [{"decision": "Confirm accrual policy",
                                 "owner": "Client", "needed_by": "2020-01-01"}]
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 2 and "has passed" in out, f"exit {code}"


@S.check("an invalid status value is rejected")
def _bad_status():
    spec = json.loads(json.dumps(SPEC))
    spec["overall_status"] = "amber"
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 3, f"exit {code}"


@S.check("the file opens in a real renderer")
def _renders():
    from shutil import which
    if not which("soffice"):
        return True, "skipped, LibreOffice not installed"
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        made = [f for f in os.listdir(tmp) if f.endswith(EXT)]
        if not made:
            return False, "nothing was written"
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/lo",
                        "--headless", "--norestore", "--convert-to", "pdf",
                        "--outdir", tmp, os.path.join(tmp, made[0])],
                       capture_output=True, timeout=500)
        pdfs = [f for f in os.listdir(tmp) if f.endswith(".pdf")]
        return bool(pdfs), f"rendered {pdfs[0] if pdfs else 'nothing'}"


@S.check("a previous client's name is caught")
def _residue():
    spec = json.loads(json.dumps(SPEC))
    LEAK(spec)
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 2 and "Prime Communications" in out, f"exit {code}"


@S.check("an incomplete spec is rejected before writing")
def _incomplete():
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), {"client_name": "X"})
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        wrote = [f for f in os.listdir(tmp) if f.endswith(EXT)]
        return code == 3 and not wrote, f"exit {code}, wrote {len(wrote)} file(s)"


@S.check("second build supersedes the first")
def _supersede():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        live = [f for f in os.listdir(tmp) if f.endswith(EXT)]
        arch = os.path.join(tmp, "_superseded")
        archived = os.listdir(arch) if os.path.isdir(arch) else []
        return (len(live) == 1 and live[0].endswith("_v2" + EXT)
                and len(archived) == 1), f"{len(live)} live, {len(archived)} archived"


if __name__ == "__main__":
    sys.exit(S.run(TITLE))
