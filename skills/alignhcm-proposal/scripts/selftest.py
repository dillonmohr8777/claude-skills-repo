#!/usr/bin/env python3
"""Prove the alignhcm-proposal skill works. Run before publishing any edit."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402

TITLE = "alignhcm-proposal"
SCRIPT = "build_proposal.py"
EXT = ".pptx"

SPEC = {
    "client_name": "Northwind Traders", "platform": "UKG Pro",
    "engagement_title": "Optimization Program", "rate": 200,
    "expected_total": 536400,
    "current_state": [
        {"category": "Core HR", "items": ["Manual hire date updates"]},
        {"category": "Benefits", "items": ["EOI needs manual work"]}],
    "phases": [
        {"name": "Phase 1", "window": "Mar - Jul 2026", "hours": 1560,
         "summary": "Configure new terms.",
         "deliverables": ["Configured terms"]},
        {"name": "Phase 2", "window": "Jul - Oct 2026", "hours": 1122,
         "summary": "Remediate pain points."}],
    "contact": {"name": "Rich Hennessey", "title": "Director", "email": "r@alignhcm.com"}}


def LEAK(spec):
    spec["approach_framing"] = "The approach we used at Prime Communications."


@S.check("documented workflow produces a clean proposal")
def _happy():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        if code != 0:
            return False, f"exit {code}: {out.strip()[-160:]}"
        return "2 phase(s)" in out, out.strip().splitlines()[1].strip()


@S.check("investment total is computed, not trusted")
def _math():
    spec = json.loads(json.dumps(SPEC))
    spec["expected_total"] = 999999
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 2 and "536,400" in out, f"exit {code}"


@S.check("thin discovery is refused")
def _needs_discovery():
    spec = json.loads(json.dumps(SPEC))
    spec["current_state"] = [{"category": "Only one", "items": ["x"]}]
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 3 and "current_state" in out, f"exit {code}"


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
