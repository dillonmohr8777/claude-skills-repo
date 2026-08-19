#!/usr/bin/env python3
"""Prove the SOW skill works. Run before publishing any edit."""
import json, os, pathlib, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402
import alignhcm_core as core  # noqa: E402

SPEC = {
    "client_legal_name": "Northwind Traders, Inc.",
    "align_entity": "Align HCM Services, LLC",
    "platform": "Dayforce", "engagement_title": "Full Suite Launch",
    "rate": 200, "expected_total": 360000,
    "workstreams": [
        {"name": "Core HR and Payroll", "hours": 680, "description": "Payroll configuration.",
         "deliverables": ["Configured org levels"]},
        {"name": "Workforce Management", "hours": 880, "description": "Pay rules and accruals."},
        {"name": "Data Conversion", "hours": 240, "description": "Extract and load."}]}


@S.check("documented workflow produces a clean SOW")
def _happy():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        if code != 0:
            return False, f"exit {code}: {out.strip()[-160:]}"
        made = [f for f in os.listdir(tmp) if f.endswith(".docx")]
        return len(made) == 1, f"wrote {made[0] if made else 'nothing'}"


@S.check("filename follows the convention")
def _naming():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        S.run_script("build_sow.py", "--spec", spec, "--out-dir", tmp)
        made = [f for f in os.listdir(tmp) if f.endswith(".docx")][0]
        import re
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


@S.check("investment arithmetic is enforced")
def _math():
    spec = dict(SPEC, expected_total=999999)
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script("build_sow.py", "--spec", path, "--out-dir", tmp)
        return code == 2 and "360,000" in out, f"exit {code}"


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
