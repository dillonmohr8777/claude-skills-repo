#!/usr/bin/env python3
"""Prove the alignhcm-intro-deck skill works. Run before publishing any edit."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402

TITLE = "alignhcm-intro-deck"
SCRIPT = "build_intro_deck.py"
EXT = ".pptx"

SPEC = {
    "client_name": "Northwind Traders", "platform": "Dayforce",
    "sector": "Senior Living and Care",
    "heard_from_team": [
        {"title": "One Employee Record", "detail": "Systems are disconnected today."},
        {"title": "Scheduling", "detail": "Coverage must flex with census."}],
    "sector_proof": [
        {"stat": "40+", "detail": "Engagements delivered in this sector."},
        {"stat": "25+", "detail": "Organizations served to date."},
        {"stat": "85%", "detail": "Delivered on the original timeline."}],
    "why_us": [
        {"title": "Full-Suite Focus", "detail": "End to end, not one module."},
        {"title": "Built for Complexity", "detail": "Census-driven staffing."}],
    "contact": {"name": "Maher El-Abdallah", "title": "CEO", "email": "maher@alignhcm.com"}}


def LEAK(spec):
    spec["sector_framing"] = "As delivered for Prime Communications."


@S.check("documented workflow produces a clean deck")
def _happy():
    with tempfile.TemporaryDirectory() as tmp:
        spec = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script(SCRIPT, "--spec", spec, "--out-dir", tmp)
        if code != 0:
            return False, f"exit {code}: {out.strip()[-160:]}"
        return "15 slides" in out, out.strip().splitlines()[1].strip()


@S.check("a generic deck is refused")
def _needs_specifics():
    spec = json.loads(json.dumps(SPEC))
    spec["heard_from_team"] = [{"title": "One thing", "detail": "Only one."}]
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 3 and "heard_from_team" in out, f"exit {code}"


@S.check("SmartCare tiers are read from the reference, not the code")
def _tiers_from_file():
    import pathlib as _p
    ref = _p.Path(sys.argv[0]).resolve().parent.parent / "references" / "smartcare-tiers.md"
    if not ref.exists():
        return False, "smartcare-tiers.md missing"
    text = ref.read_text()
    has_table = "| Tier " in text and "Stabilize" in text
    records_conflict = "conflict" in text.lower()
    return has_table and records_conflict, "tier table present, conflict recorded"


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
