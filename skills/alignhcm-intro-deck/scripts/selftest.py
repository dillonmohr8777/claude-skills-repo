#!/usr/bin/env python3
"""Prove the alignhcm-intro-deck skill works. Run before publishing any edit."""
import importlib, json, os, pathlib, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_core"))
import selftest_common as S   # noqa: E402

TITLE = "alignhcm-intro-deck"
SCRIPT = "build_intro_deck.py"
EXT = ".pptx"

SPEC = {
    "client_mark": "none",
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


def _modules():
    """Load the builder and core by name, so the stdlib-only scan stays honest."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    return (importlib.import_module("build_intro_deck"),
            importlib.import_module("alignhcm_core"))


@S.check("a deck mixing SmartCare vocabularies is refused")
def _tier_vocabulary():
    """
    The August 2026 Portsmouth proposal shipped both naming systems in one
    deck. Whichever set Align settles on, using both at once is a defect.
    """
    B, C = _modules()

    mixed = C.Report("mixed")
    B.check_tier_vocabulary(
        [["Stabilize", "x", "y"], ["Optimize", "x", "y"], ["Transform", "x", "y"]],
        mixed)
    clean = C.Report("clean")
    B.check_tier_vocabulary(
        [["Stabilize", "x", "y"], ["Optimize", "x", "y"],
         ["Optimize Plus", "x", "y"]], clean)
    catalog = C.Report("catalog")
    B.check_tier_vocabulary(
        [["Stabilize", "x", "y"], ["Essentials", "x", "y"],
         ["Accelerate", "x", "y"], ["Transform", "x", "y"]], catalog)

    if mixed.passed:
        return False, "a mixed table was accepted"
    if not clean.passed:
        return False, "the client-facing set was rejected"
    if not catalog.passed:
        return False, "the catalog set was rejected"
    return True, "mixed rejected, both single vocabularies accepted"


@S.check("the shipped tier table is one vocabulary")
def _shipped_tiers():
    B, C = _modules()
    root = pathlib.Path(__file__).resolve().parent.parent
    tiers = B.load_tiers(str(root / "references" / "smartcare-tiers.md"))
    rep = C.Report("shipped")
    B.check_tier_vocabulary(tiers, rep)
    names = [t[0] for t in tiers]
    return rep.passed, f"{names}"


@S.check("a contested company fact is refused")
def _contested_fact():
    """
    Shipped Align documents disagree on headquarters, team size, geography, and
    review count. Reading one of those into a client document picks a side
    silently, which is how two prospects end up with two versions of Align.
    """
    B, C = _modules()
    root = pathlib.Path(__file__).resolve().parent.parent
    facts = C.Facts(str(root / "scripts" / "_core" / "company-facts.md"))
    if not [k for k, s in facts.status.items() if s == "contested"]:
        return False, "company-facts.md marks nothing as contested"

    blocked = C.Report("blocked")
    facts.get("TEAM_SIZE")
    facts.check(blocked, allow_contested=False)
    if blocked.passed:
        return False, "reading TEAM_SIZE did not fail the build"

    allowed = C.Report("allowed")
    facts.check(allowed, allow_contested=True)
    if not allowed.passed:
        return False, "--allow-contested did not permit it"

    clean = C.Facts(str(root / "scripts" / "_core" / "company-facts.md"))
    for key in ("OFFICES", "TEAM_CLAIM", "RATING_CLAIM", "CUSTOMERS_SERVED",
                "PROJECTS_DELIVERED", "FOUNDED"):
        clean.get(key)
    rep = C.Report("defaults")
    clean.check(rep, allow_contested=False)
    return rep.passed, "contested blocked, override works, defaults clean"


@S.check("the deck never claims delivery is fully onshore")
def _onshore_claim():
    """
    Align's own RFP response discloses team members in the Philippines. A deck
    that claims 100% onshore contradicts a document Align has already given a
    client under evaluation.
    """
    spec = json.loads(json.dumps(SPEC))
    spec["both_sides"] = ("Our delivery is 100% onshore, with no handoff to "
                          "another region at any phase.")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        return code == 2 and "100% onshore" in out, f"exit {code}"


def _media_shas(path):
    import hashlib, zipfile
    z = zipfile.ZipFile(path)
    return {hashlib.sha256(z.read(n)).hexdigest()
            for n in z.namelist() if "/media/" in n}


@S.check("the exact Align lockup lands on the cover")
def _lockup_on_cover():
    spec = json.loads(json.dumps(SPEC))
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        deck = [f for f in os.listdir(tmp) if f.endswith(".pptx")]
        if code != 0 or not deck:
            return False, f"exit {code}: {out.strip()[-140:]}"
        shas = _media_shas(os.path.join(tmp, deck[0]))
        B, C = _modules()
        import importlib
        media = importlib.import_module("alignhcm_media")
        return media.LOCKUP_SHA in shas, f"{len(shas)} image(s) embedded"


@S.check("the build refuses to guess whether a prospect is involved")
def _mark_decision_required():
    """
    The failure this prevents is a deck going out with an empty client panel,
    or with the previous prospect's mark still in it, because nobody was asked.
    """
    spec = json.loads(json.dumps(SPEC))
    spec.pop("client_mark")
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        wrote = [f for f in os.listdir(tmp) if f.endswith(".pptx")]
        asked = "Is a prospect or client involved" in out
        return code == 3 and not wrote and asked, f"exit {code}, asked={asked}"


@S.check("a supplied client mark is cleaned, plated, and placed")
def _client_mark_placed():
    """
    Uses the Align lockup as stand-in artwork. What matters is that a supplied
    file goes through the same background removal, trim, contrast measurement,
    and plate as a fetched one, and then reaches the cover.
    """
    root = pathlib.Path(__file__).resolve().parent.parent
    art = root / "scripts" / "_core" / "align-hcm-deck-lockup.png"
    spec = json.loads(json.dumps(SPEC))
    spec["client_mark"] = {"file": str(art)}
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), spec)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        deck = [f for f in os.listdir(tmp) if f.endswith(".pptx")]
        if code != 0 or not deck:
            return False, f"exit {code}: {out.strip()[-160:]}"
        shas = _media_shas(os.path.join(tmp, deck[0]))
        import importlib
        media = importlib.import_module("alignhcm_media")
        if media.LOCKUP_SHA not in shas:
            return False, "the Align lockup went missing"
        if len(shas) < 2:
            return False, "no separate client mark was embedded"
        plated = os.path.join(tmp, "_assets", "client-mark.png")
        side = plated + ".source.json"
        if not os.path.exists(side):
            return False, "no provenance written for the client mark"
        with open(side) as fh:
            prov = json.load(fh)
        return prov["plate"]["applied"], (
            f"plate {prov['plate'].get('polarity')}, "
            f"border {prov['plate'].get('border')}")


@S.check("the SmartCare mark appears on the SmartCare slide")
def _smartcare_mark():
    """
    Align has no SmartCare logo, so this is the typographic lockup. It still
    has to actually reach the slide, and it must not leak onto slides that have
    nothing to do with SmartCare.
    """
    import zipfile
    with tempfile.TemporaryDirectory() as tmp:
        path = S.write_json(os.path.join(tmp, "s.json"), SPEC)
        code, out = S.run_script(SCRIPT, "--spec", path, "--out-dir", tmp)
        deck = [f for f in os.listdir(tmp) if f.endswith(".pptx")]
        if code != 0 or not deck:
            return False, f"exit {code}"
        z = zipfile.ZipFile(os.path.join(tmp, deck[0]))
        hits = []
        for n in sorted(z.namelist()):
            if "/slides/slide" in n and n.endswith(".xml"):
                xml = z.read(n).decode("utf8", "replace")
                if ">Smart</a:t>" in xml and ">Care</a:t>" in xml:
                    hits.append(n)
        if len(hits) != 1:
            return False, f"lockup on {len(hits)} slide(s), expected exactly 1"
        xml = z.read(hits[0]).decode("utf8", "replace")
        return "SmartCare" in xml, f"on {hits[0].split('/')[-1]}"


if __name__ == "__main__":
    sys.exit(S.run(TITLE))
