#!/usr/bin/env python3
"""
Prove this package works. Run before sharing it, and after any edit to it.

Every check corresponds to a real failure this package has had. They run against
the bundled assets using the documented commands, so a pass means the workflow in
SKILL.md actually works rather than merely reading as though it should.

    python3 scripts/selftest.py            # run everything
    python3 scripts/selftest.py -v         # show detail for passing checks too

Exit code 0 if every check passes, 1 otherwise, so it can gate a release.
Stdlib only, and it builds its own fixtures, so there is nothing to install and
no test assets to keep in the repo.
"""

import argparse
import hashlib
import importlib.util
import io
import os
import pathlib
import re
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATE = ROOT / "assets" / "templates" / "Align-HCM-Primary-Deck-Reference.pptx"
LOCKUP = ROOT / "assets" / "logos" / "align-hcm-deck-lockup.png"

# The lockup is the one artwork file that must never change. Pinned here so an
# accidental re-export is caught immediately.
EXPECTED_LOCKUP_SHA = "3A0340D27BFE44B21277F4A689796B1C31338F5FD74134786209F5B736D22A07"

# All 15 template placeholders. Four are covered by named flags.
REPLACE_ARGS = [
    "{{ALIGN_CONTACT}}=Jordan Reyes",
    "{{CONTACT_EMAIL}}=jordan.reyes@alignhcm.com",
    "{{CONTACT_PHONE}}=(555) 010-4477",
    "{{COUNT}}=1,200",
    "{{FEE}}=$18,000",
    "{{GO_LIVE}}=January 2027",
    "{{PHASE_2_SCOPE}}=Benefits and Recruiting",
    "{{PRICE}}=$142,000",
    "{{SOURCE_PLATFORM}}=ADP Workforce Now",
    "{{TARGET_PLATFORM}}=UKG Pro",
    "{{WORKSTREAM}}=Core HR and Payroll",
]

EXPECTED_PLACEHOLDER_COUNT = 15

STDLIB_ALLOWED = {
    "argparse", "collections", "hashlib", "importlib", "io", "json", "os",
    "pathlib", "re", "struct", "subprocess", "sys", "tempfile", "zipfile",
    "zlib", "xml",
}

results = []


def check(name):
    """Register a check. The wrapped function returns (ok, detail)."""
    def wrap(fn):
        def run():
            try:
                ok, detail = fn()
            except Exception as exc:  # a crashing check is a failing check
                ok, detail = False, f"raised {type(exc).__name__}: {exc}"
            results.append((name, ok, detail))
        run.__name__ = fn.__name__
        return run
    return wrap


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest().upper()


def make_png(path, w=200, h=80):
    raw = b"".join(b"\x00" + bytes([30, 60, 120]) * w for _ in range(h))

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    pathlib.Path(path).write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b""))


def make_bad_docx(path):
    """A minimal Word file carrying two banned colours and an off-stack font."""
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document xmlns:w="{ns}"><w:body>'
           '<w:p><w:r><w:rPr><w:color w:val="E8760A"/>'
           '<w:rFonts w:ascii="Papyrus"/></w:rPr><w:t>banned</w:t></w:r></w:p>'
           '<w:p><w:r><w:rPr><w:color w:val="414042"/></w:rPr>'
           '<w:t>banned grey</w:t></w:r></w:p>'
           '<w:p><w:r><w:rPr><w:color w:val="232E3E"/>'
           '<w:rFonts w:ascii="Calibri"/></w:rPr><w:t>fine</w:t></w:r></w:p>'
           '</w:body></w:document>')
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)


def run(script, *args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *[str(a) for a in args]],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def rewrite_pptx(src, dst, part, old, new):
    with zipfile.ZipFile(src) as zi:
        items = [(i.filename, zi.read(i.filename)) for i in zi.infolist()]
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, data in items:
            if name == part:
                data = data.replace(old, new)
            zo.writestr(name, data)


def load_linter():
    spec = importlib.util.spec_from_file_location("bl", SCRIPTS / "brand_lint.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Integrity of the bundled assets
# ---------------------------------------------------------------------------

@check("bundled assets present")
def _assets_present():
    missing = [str(p.relative_to(ROOT)) for p in (TEMPLATE, LOCKUP) if not p.exists()]
    return not missing, f"missing: {missing}" if missing else "template and lockup present"


@check("lockup artwork unchanged")
def _lockup_hash():
    actual = sha256_file(LOCKUP)
    return actual == EXPECTED_LOCKUP_SHA, (
        f"{actual[:16]}..." if actual == EXPECTED_LOCKUP_SHA
        else f"expected {EXPECTED_LOCKUP_SHA[:16]}... got {actual[:16]}...")


@check("recorded template hash matches the file")
def _template_hash_recorded():
    actual = sha256_file(TEMPLATE)
    doc = (ROOT / "references" / "powerpoint-deck-system.md").read_text()
    recorded = re.findall(r"\b([0-9A-F]{64})\b", doc)
    if actual not in recorded:
        return False, (f"file is {actual[:16]}... but powerpoint-deck-system.md "
                       f"records {[r[:16] + '...' for r in recorded]}")
    return True, f"{actual[:16]}... recorded correctly"


@check("template placeholder count")
def _placeholder_count():
    code, out = run("prepare_client_deck.py", "--list-placeholders",
                    "--output", "x", "--client-name", "x", "--client-logo", "x",
                    "--engagement-title", "x", "--date", "x")
    found = len(re.findall(r"\{\{[A-Z0-9_]+\}\}", out))
    return found == EXPECTED_PLACEHOLDER_COUNT, f"{found} found, expected {EXPECTED_PLACEHOLDER_COUNT}"


# ---------------------------------------------------------------------------
# The documented workflow
# ---------------------------------------------------------------------------

@check("documented deck workflow passes validation")
def _workflow():
    with tempfile.TemporaryDirectory() as tmp:
        logo = os.path.join(tmp, "logo.png")
        deck = os.path.join(tmp, "deck.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods",
                "--client-logo", logo, "--engagement-title", "UKG Pro Implementation",
                "--deck-type", "Client Presentation", "--date", "September 2026"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        code, out = run("prepare_client_deck.py", *args)
        if code != 0:
            return False, f"prepare exited {code}: {out.strip()[:200]}"
        code, out = run("validate_client_deck.py", deck,
                        "--client-name", "Acme Foods", "--client-logo", logo)
        return code == 0, (f"prepare 0, validate {code}"
                           + ("" if code == 0 else f": {out.strip()[:200]}"))


@check("missing placeholders reported and rejected")
def _unresolved_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        logo = os.path.join(tmp, "logo.png")
        deck = os.path.join(tmp, "deck.pptx")
        make_png(logo)
        code, out = run("prepare_client_deck.py", "--output", deck,
                        "--client-name", "Acme Foods", "--client-logo", logo,
                        "--engagement-title", "E", "--date", "September 2026")
        if code == 0:
            return False, "exited 0 despite 11 unresolved placeholders"
        if "{{PHASE_2_SCOPE}}" not in out:
            return False, "did not name {{PHASE_2_SCOPE}} in the report"
        if "slide 5" not in out:
            return False, "did not group findings by slide"
        return True, f"exited {code} and named the missing tokens by slide"


@check("--allow-unresolved accepts a partial deck")
def _allow_unresolved():
    with tempfile.TemporaryDirectory() as tmp:
        logo = os.path.join(tmp, "logo.png")
        deck = os.path.join(tmp, "deck.pptx")
        make_png(logo)
        code, out = run("prepare_client_deck.py", "--output", deck,
                        "--client-name", "A", "--client-logo", logo,
                        "--engagement-title", "E", "--date", "D",
                        "--allow-unresolved")
        return code == 0, f"exited {code}"


@check("no possessive artifact in output text")
def _no_possessive():
    with tempfile.TemporaryDirectory() as tmp:
        logo = os.path.join(tmp, "logo.png")
        deck = os.path.join(tmp, "deck.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods",
                "--client-logo", logo, "--engagement-title", "E",
                "--deck-type", "T", "--date", "D"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        run("prepare_client_deck.py", *args)
        with zipfile.ZipFile(deck) as z:
            text = z.read("ppt/slides/slide5.xml").decode("utf8", "replace")
        bad = [m for m in ("Foods's", "Foods&#8217;s", "Foods’s") if m in text]
        return not bad, f"found {bad}" if bad else "no double possessive"


# ---------------------------------------------------------------------------
# The linter
# ---------------------------------------------------------------------------

@check("linter catches banned colours in a .docx")
def _opc_docx():
    with tempfile.TemporaryDirectory() as tmp:
        bad = os.path.join(tmp, "bad.docx")
        make_bad_docx(bad)
        code, out = run("brand_lint.py", "--surface", "document", bad)
        errors = out.count("error ")
        if code == 0:
            return False, "exited 0 on a document containing two banned colours"
        if errors < 2:
            return False, f"found {errors} error(s), expected 2"
        return True, f"{errors} errors, exit {code}"


@check("linter reads the reference deck cleanly")
def _deck_clean():
    code, out = run("brand_lint.py", "--surface", "deck", TEMPLATE)
    if code != 0:
        return False, f"exit {code}: {out.strip()[-200:]}"
    m = re.search(r"(\d+) error\(s\), (\d+) warning\(s\)", out)
    if not m:
        return False, "could not parse summary"
    errs, warns = int(m.group(1)), int(m.group(2))
    return errs == 0 and warns == 0, f"{errs} errors, {warns} warnings"


@check("linter rejects a binary Office file it cannot parse")
def _opc_broken():
    with tempfile.TemporaryDirectory() as tmp:
        fake = os.path.join(tmp, "broken.docx")
        pathlib.Path(fake).write_bytes(b"PK\x03\x04" + b"\x00" * 64)
        code, out = run("brand_lint.py", "--surface", "document", fake)
        return code != 0, f"exit {code}"


@check("ledger in tokens.md matches brand_lint.py")
def _ledger_consistent():
    bl = load_linter()
    md = (ROOT / "references" / "tokens.md").read_text()
    sections, cur = {}, None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            sections[cur] = set()
        elif cur:
            sections[cur].update("#" + h.upper()
                                 for h in re.findall(r"#([0-9A-Fa-f]{6})\b", line))
    pairs = {"Web and HubSpot": "web", "LinkedIn carousel and social": "social",
             "Video and motion": "motion", "Blog and editorial HTML": "editorial",
             "PowerPoint decks": "deck"}
    drift = []
    banned = set(bl.KNOWN_BAD)
    for section, surface in pairs.items():
        doc = sections.get(section, set()) - banned
        code = set(bl.SURFACES[surface]["colours"])
        if doc - code:
            drift.append(f"{surface}: in doc only {sorted(doc - code)}")
        if code - doc:
            drift.append(f"{surface}: in code only {sorted(code - doc)}")
    doc_banned = sections.get("Never use", set())
    if doc_banned != banned:
        drift.append(f"never-use mismatch: doc {sorted(doc_banned)} vs code {sorted(banned)}")
    return not drift, "; ".join(drift) if drift else "all surfaces and never-use list agree"


# ---------------------------------------------------------------------------
# Validator behaviour
# ---------------------------------------------------------------------------

@check("geometry tolerance accepts a nominal rebuild")
def _geometry_nominal():
    with tempfile.TemporaryDirectory() as tmp:
        logo, deck = os.path.join(tmp, "l.png"), os.path.join(tmp, "d.pptx")
        nominal = os.path.join(tmp, "n.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods", "--client-logo", logo,
                "--engagement-title", "E", "--deck-type", "T", "--date", "D"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        run("prepare_client_deck.py", *args)
        rewrite_pptx(deck, nominal, "ppt/presentation.xml",
                     b'cx="12191969"', b'cx="12192000"')
        code, out = run("validate_client_deck.py", nominal,
                        "--client-name", "Acme Foods", "--client-logo", logo)
        return code == 0, f"exit {code}" + ("" if code == 0 else f": {out.strip()[:160]}")


@check("geometry still rejects a genuinely wrong canvas")
def _geometry_wrong():
    with tempfile.TemporaryDirectory() as tmp:
        logo, deck = os.path.join(tmp, "l.png"), os.path.join(tmp, "d.pptx")
        wrong = os.path.join(tmp, "w.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods", "--client-logo", logo,
                "--engagement-title", "E", "--deck-type", "T", "--date", "D"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        run("prepare_client_deck.py", *args)
        rewrite_pptx(deck, wrong, "ppt/presentation.xml",
                     b'cx="12191969"', b'cx="9144000"')
        code, out = run("validate_client_deck.py", wrong, "--client-name", "Acme Foods")
        return code != 0 and "geometry" in out, f"exit {code}"


@check("swapped Align icon is detected")
def _icon_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        logo, deck = os.path.join(tmp, "l.png"), os.path.join(tmp, "d.pptx")
        tampered = os.path.join(tmp, "t.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods", "--client-logo", logo,
                "--engagement-title", "E", "--deck-type", "T", "--date", "D"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        run("prepare_client_deck.py", *args)
        # Overwrite an icon media part that the client logo does not occupy.
        with zipfile.ZipFile(deck) as z:
            parts = {n: z.read(n) for n in z.namelist()}
        client_bytes = pathlib.Path(logo).read_bytes()
        victim = next((n for n in sorted(parts)
                       if n.startswith("ppt/media/") and n.endswith(".png")
                       and parts[n] != client_bytes), None)
        if victim is None:
            return False, "no icon media part available to tamper with"
        parts[victim] = make_png(os.path.join(tmp, "x.png")) or \
            pathlib.Path(os.path.join(tmp, "x.png")).read_bytes()
        with zipfile.ZipFile(tampered, "w", zipfile.ZIP_DEFLATED) as o:
            for n, d in parts.items():
                o.writestr(n, d)
        code, out = run("validate_client_deck.py", tampered,
                        "--client-name", "Acme Foods", "--client-logo", logo)
        caught = "does not match the bundled reference" in out or \
                 "does not match the bundled master artwork" in out
        return code != 0 and caught, f"exit {code}, detected={caught}"


@check("client logo distortion is detected")
def _logo_ratio():
    with tempfile.TemporaryDirectory() as tmp:
        logo, deck = os.path.join(tmp, "l.png"), os.path.join(tmp, "d.pptx")
        stretched = os.path.join(tmp, "s.pptx")
        make_png(logo)
        args = ["--output", deck, "--client-name", "Acme Foods", "--client-logo", logo,
                "--engagement-title", "E", "--deck-type", "T", "--date", "D"]
        for r in REPLACE_ARGS:
            args += ["--replace", r]
        run("prepare_client_deck.py", *args)
        with zipfile.ZipFile(deck) as z:
            slide = z.read("ppt/slides/slide1.xml").decode()
        # Scope to the CLIENT_LOGO picture. The first a:ext in the part is the
        # slide extent, and ElementTree writes a space before the self-close.
        start = slide.find("CLIENT_LOGO")
        block = slide[start:slide.find("</p:pic>", start)] if start != -1 else ""
        m = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"\s*/>', block)
        if not m:
            return False, "could not find the client logo extent on the cover"
        squashed = f'<a:ext cx="{m.group(1)}" cy="{int(int(m.group(2)) * 0.5)}" />'
        rewrite_pptx(deck, stretched, "ppt/slides/slide1.xml",
                     m.group(0).encode(), squashed.encode())
        code, out = run("validate_client_deck.py", stretched,
                        "--client-name", "Acme Foods", "--client-logo", logo)
        return code != 0, f"exit {code}"


# ---------------------------------------------------------------------------
# Portability and house rules
# ---------------------------------------------------------------------------

@check("scripts are stdlib only")
def _stdlib_only():
    third_party = set()
    for path in sorted(SCRIPTS.glob("*.py")):
        for line in path.read_text().splitlines():
            m = re.match(r"^\s*(?:import|from)\s+([A-Za-z_][\w.]*)", line)
            if m:
                top = m.group(1).split(".")[0]
                if top not in STDLIB_ALLOWED:
                    third_party.add(f"{path.name}:{top}")
    return not third_party, f"found {sorted(third_party)}" if third_party else \
        f"{len(list(SCRIPTS.glob('*.py')))} scripts, no third-party imports"


@check("scripts compile")
def _compile():
    bad = []
    for path in sorted(SCRIPTS.glob("*.py")):
        proc = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            bad.append(f"{path.name}: {proc.stderr.strip()[:80]}")
    return not bad, "; ".join(bad) if bad else "all scripts compile"


@check("no em dashes in prose")
def _no_em_dash():
    offenders = []
    for path in sorted(ROOT.glob("*.md")) + sorted((ROOT / "references").glob("*.md")):
        n = path.read_text().count("\u2014")
        if n:
            offenders.append(f"{path.name}:{n}")
    return not offenders, "; ".join(offenders) if offenders else \
        "0 across every markdown file"


@check("no machine-specific or personal dependencies")
def _portable():
    patterns = (r"C:\\Users", r"/Users/[a-z]", r"\bDillon\b")
    offenders = []
    targets = ([ROOT / "SKILL.md"] + sorted((ROOT / "references").glob("*.md"))
               + sorted(SCRIPTS.glob("*.py")) + sorted((ROOT / "agents").glob("*")))
    for path in targets:
        text = path.read_text(errors="replace")
        for pattern in patterns:
            if re.search(pattern, text):
                offenders.append(f"{path.name}~{pattern}")
    return not offenders, "; ".join(offenders) if offenders else \
        "operative files name a role, not a person or a machine"


@check("SKILL.md frontmatter is well formed")
def _frontmatter():
    text = (ROOT / "SKILL.md").read_text()
    if not text.startswith("---\n"):
        return False, "does not open with a frontmatter block"
    end = text.find("\n---", 4)
    if end == -1:
        return False, "frontmatter is not closed"
    block = text[4:end]
    if not re.search(r"^name:\s*alignhcm-brand-system\s*$", block, re.M):
        return False, "name field missing or wrong"
    m = re.search(r"^description:\s*(.+)$", block, re.M | re.S)
    if not m:
        return False, "description field missing"
    length = len(" ".join(m.group(1).split()))
    if length > 1024:
        return False, f"description is {length} chars, over the 1024 limit"
    return True, f"name ok, description {length} chars"


@check("every referenced file exists")
def _links_resolve():
    missing = set()
    # CHANGELOG.md is history: it cites files in other repositories and files
    # this package has deliberately removed, so it is not a link source.
    targets = [ROOT / "SKILL.md"] + \
        [p for p in sorted(ROOT.glob("*.md")) if p.name != "CHANGELOG.md"] + \
        sorted((ROOT / "references").glob("*.md"))
    for path in targets:
        for ref in re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`",
                              path.read_text()):
            candidate = ROOT / ref
            if any(ch in ref for ch in "<>*"):
                continue
            if not candidate.exists():
                missing.add(f"{path.name} -> {ref}")
    return not missing, "; ".join(sorted(missing)) if missing else \
        "all referenced paths resolve"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="show detail for passing checks too")
    args = ap.parse_args()

    checks = [v for k, v in sorted(globals().items())
              if k.startswith("_") and callable(v) and not k.startswith("__")]
    for fn in checks:
        fn()

    width = max(len(name) for name, _, _ in results)
    print()
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        line = f"  {mark}  {name:<{width}}"
        if not ok or args.verbose:
            line += f"  {detail}"
        print(line)

    failed = [name for name, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        print("failed: " + ", ".join(failed))
        print("\nNot ready to share. Fix the above and re-run.")
        return 1
    print("Package is internally consistent and the documented workflow runs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
