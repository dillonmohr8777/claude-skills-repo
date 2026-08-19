"""
Checks every Align document skill runs, plus the scaffolding to add its own.

Each skill's `scripts/selftest.py` imports this, registers whatever is specific
to it, and calls `run()`. The shared checks are the ones that protect the
package properties: vendored core integrity, no third-party imports, no em
dashes, valid frontmatter, and every referenced file present.
"""

import ast
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

STDLIB_ALLOWED = {
    "argparse", "ast", "collections", "datetime", "functools", "hashlib", "http",
    "importlib", "io", "json", "os", "pathlib", "re", "shutil", "socketserver",
    "struct", "subprocess", "sys", "tempfile", "threading", "urllib", "zipfile",
    "zlib", "xml",
    # The vendored core, imported by sibling scripts.
    "alignhcm_core", "alignhcm_docx", "alignhcm_pptx", "alignhcm_media",
    "selftest_common", "client_mark", "logo_image", "fetch_client_logo",
}

RESULTS = []
CHECKS = []


def check(name):
    def wrap(fn):
        def run_one():
            try:
                ok, detail = fn()
            except Exception as exc:
                ok, detail = False, f"raised {type(exc).__name__}: {exc}"
            RESULTS.append((name, ok, detail))
        CHECKS.append(run_one)
        return run_one
    return wrap


def _root():
    return pathlib.Path(sys.argv[0]).resolve().parent.parent


def run_script(script, *args, cwd=None):
    root = _root()
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / script), *[str(a) for a in args]],
        capture_output=True, text=True, cwd=cwd, timeout=600)
    return proc.returncode, proc.stdout + proc.stderr


def write_json(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=2))
    return str(path)


# ---------------------------------------------------------------------------
# Shared checks
# ---------------------------------------------------------------------------

@check("vendored core matches the canonical manifest")
def _core_integrity():
    """
    The core is copied into each skill rather than imported, because a skill is
    installed standalone. Copying rots unless someone checks, so this is that
    check: edit a vendored file directly and the suite fails.
    """
    core = _root() / "scripts" / "_core"
    manifest_path = core / "CORE_MANIFEST.json"
    if not manifest_path.exists():
        return False, "scripts/_core/CORE_MANIFEST.json is missing"
    manifest = json.loads(manifest_path.read_text())
    bad = []
    for name, expected in manifest["files"].items():
        target = core / name
        if not target.exists():
            bad.append(f"{name} missing")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            bad.append(f"{name} edited in place")
    return not bad, ("; ".join(bad) if bad else
                     f"core {manifest.get('core_version')}, "
                     f"{len(manifest['files'])} file(s) intact")


@check("scripts are stdlib only")
def _stdlib_only():
    """
    No hard third-party dependency, so nothing needs installing.

    An import guarded by try/except ImportError is allowed: logo_image uses
    Pillow when it happens to be present for better resampling and falls back
    to its own codec when it is not. That is an accelerator, not a dependency,
    and banning it would mean deleting working code for a rule it does not break.
    """
    third, optional = set(), set()
    for path in sorted((_root() / "scripts").rglob("*.py")):
        tree = ast.parse(path.read_text())
        guarded = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try) and any(
                    _catches_import_error(h) for h in node.handlers):
                for child in ast.walk(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        guarded.add(id(child))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                if not root or root in STDLIB_ALLOWED:
                    continue
                (optional if id(node) in guarded else third).add(
                    f"{path.name}:{root}")
    if third:
        return False, f"hard third-party import(s): {sorted(third)}"
    detail = "no third-party imports"
    if optional:
        detail = f"none required; optional and guarded: {sorted(optional)}"
    return True, detail


def _catches_import_error(handler):
    exc = handler.type
    if exc is None:
        return False
    names = [exc] if not isinstance(exc, ast.Tuple) else list(exc.elts)
    return any(getattr(n, "id", None) in ("ImportError", "ModuleNotFoundError")
               for n in names)


@check("scripts compile")
def _compile():
    bad = []
    for path in sorted((_root() / "scripts").rglob("*.py")):
        proc = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            bad.append(f"{path.name}: {proc.stderr.strip()[:70]}")
    return not bad, "; ".join(bad) if bad else "all compile"


@check("no em dashes in prose")
def _no_em_dash():
    offenders = []
    for path in sorted(_root().rglob("*.md")):
        if "_core" in path.parts:
            continue
        n = path.read_text().count("\u2014")
        if n:
            offenders.append(f"{path.name}:{n}")
    return not offenders, ("; ".join(offenders) if offenders else
                           "0 across every markdown file")


@check("SKILL.md frontmatter is well formed")
def _frontmatter():
    text = (_root() / "SKILL.md").read_text()
    if not text.startswith("---\n"):
        return False, "no frontmatter block"
    end = text.find("\n---", 4)
    if end == -1:
        return False, "frontmatter not closed"
    block = text[4:end]
    if not re.search(r"^name:\s*\S+", block, re.M):
        return False, "name field missing"
    m = re.search(r"^description:\s*(.+)$", block, re.M | re.S)
    if not m:
        return False, "description field missing"
    length = len(" ".join(m.group(1).split()))
    if length > 1024:
        return False, f"description is {length} chars, over the 1024 limit"
    return True, f"description {length} chars"


@check("every referenced file exists")
def _links():
    missing = set()
    root = _root()
    for path in sorted(root.glob("*.md")):
        for ref in re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`",
                              path.read_text()):
            if any(ch in ref for ch in "<>*"):
                continue
            if not (root / ref).exists():
                missing.add(f"{path.name} -> {ref}")
    return not missing, ("; ".join(sorted(missing)) if missing else
                         "all referenced paths resolve")


@check("no machine-specific or personal paths")
def _portable():
    offenders = []
    for path in sorted(_root().rglob("*")):
        if path.is_dir() or path.suffix not in (".md", ".py", ".json"):
            continue
        text = path.read_text(errors="replace")
        for pattern in (r"C:\\Users", r"/Users/[a-z]", r"/home/[a-z]+/"):
            if re.search(pattern, text):
                offenders.append(f"{path.name}~{pattern}")
    return not offenders, ("; ".join(offenders) if offenders else
                           "no absolute or personal paths")


@check("the vendored Align lockup is the approved mark")
def _lockup_pinned():
    """
    Shipping the exact artwork and proving it is still the exact artwork are
    the same problem. This is the byte-for-byte mark from ppt/media/image1.png
    of the Align master deck.
    """
    core = _root() / "scripts" / "_core"
    sys.path.insert(0, str(core))
    import importlib
    media = importlib.import_module("alignhcm_media")
    try:
        path = media.align_lockup(str(core))
    except media.ImageError as exc:
        return False, str(exc)
    size = media.size(media.register(path))
    return True, f"sha256 pinned, {size[0]}x{size[1]}"


@check("a substituted lockup is refused")
def _lockup_tamper():
    core = _root() / "scripts" / "_core"
    sys.path.insert(0, str(core))
    import importlib, shutil
    media = importlib.import_module("alignhcm_media")
    target = core / media.LOCKUP_NAME
    backup = target.read_bytes()
    try:
        # A visually similar but different PNG is exactly the failure mode:
        # someone re-exports the logo and the deck quietly changes.
        target.write_bytes(backup[:-40] + b"\x00" * 40)
        try:
            media.align_lockup(str(core))
            return False, "a modified lockup was accepted"
        except media.ImageError:
            return True, "modified artwork rejected"
    finally:
        target.write_bytes(backup)


@check("company facts carry a review date")
def _facts_dated():
    facts = _root() / "scripts" / "_core" / "company-facts.md"
    if not facts.exists():
        return False, "company-facts.md not vendored"
    text = facts.read_text()
    if not re.search(r"^review_by:\s*\d{4}-\d{2}-\d{2}", text, re.M):
        return False, "no review_by date, so staleness cannot be detected"
    values = len(re.findall(r"^\|\s*`[A-Z0-9_]+`", text, re.M))
    return values >= 10, f"{values} canonical values with a review date"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run(title):
    for fn in CHECKS:
        fn()
    width = max(len(n) for n, _, _ in RESULTS)
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    print(f"\n{title}")
    for name, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        line = f"  {mark}  {name:<{width}}"
        if not ok or verbose:
            line += f"  {detail}"
        print(line)
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print("failed: " + ", ".join(failed))
        return 1
    return 0
