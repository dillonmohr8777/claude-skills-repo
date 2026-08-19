#!/usr/bin/env python3
"""
Build the upload-ready zip for each Align skill, and prove each one works.

    python3 package_skills.py --out-dir ../dist
    python3 package_skills.py --out-dir ../dist alignhcm-sow

Every zip is built from the working tree, then extracted into a clean directory
and tested there. A package that has never been unpacked and run is a package
nobody has actually checked.

Each zip carries a PROVENANCE.json naming the commit it came from, so an
installed copy can be traced back to a revision rather than to a memory of who
uploaded what.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent

SKILLS = ["alignhcm-brand-system", "alignhcm-intro-deck", "alignhcm-proposal",
          "alignhcm-sow", "alignhcm-pm-runbook"]

SKIP_PARTS = {"__pycache__", ".git"}
SKIP_NAMES = {".DS_Store", ".gitignore"}


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=HERE, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def files_of(root):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in SKIP_NAMES or path.suffix == ".pyc":
            continue
        if SKIP_PARTS & set(path.parts):
            continue
        yield path


def provenance(name, root, commit, dirty):
    digests = {str(p.relative_to(root)):
               hashlib.sha256(p.read_bytes()).hexdigest()
               for p in files_of(root)}
    return {
        "skill": name,
        "commit": commit or "unknown",
        "working_tree": "dirty" if dirty else "clean",
        "packaged": datetime.date.today().isoformat(),
        "file_count": len(digests),
        "sha256": digests,
    }


def build(name, out_dir, commit, dirty):
    root = HERE / name
    zip_path = out_dir / f"{name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    prov = provenance(name, root, commit, dirty)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files_of(root):
            z.write(path, f"{name}/{path.relative_to(root)}")
        z.writestr(f"{name}/PROVENANCE.json", json.dumps(prov, indent=2) + "\n")
    return zip_path, prov


def verify(name, zip_path):
    """Extract into an empty directory and run the skill's own self-test."""
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)
        skill_dir = pathlib.Path(tmp) / name
        selftest = skill_dir / "scripts" / "selftest.py"
        if not selftest.exists():
            return False, "no self-test in the package"
        proc = subprocess.run([sys.executable, str(selftest)],
                              cwd=skill_dir, capture_output=True, text=True,
                              timeout=1800)
        tail = [ln for ln in proc.stdout.splitlines() if "checks passed" in ln]
        return proc.returncode == 0, (tail[-1].strip() if tail
                                      else proc.stdout.strip()[-90:])


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*", help="skills to package (default: all)")
    ap.add_argument("--out-dir", default="dist", help="where to write the zips")
    ap.add_argument("--skip-verify", action="store_true",
                    help="build without extracting and testing. Not recommended")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commit = git("rev-parse", "--short", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    if dirty:
        print("note: working tree has uncommitted changes; PROVENANCE.json "
              "will say so\n", file=sys.stderr)

    failures = 0
    for name in (args.skills or SKILLS):
        if not (HERE / name).is_dir():
            print(f"skip {name}: not in this repository", file=sys.stderr)
            continue
        zip_path, prov = build(name, out_dir, commit, dirty)
        size = zip_path.stat().st_size / 1024
        if args.skip_verify:
            print(f"{name:24} {size:7.0f} KB  {prov['file_count']:>3} files  "
                  f"(not verified)")
            continue
        ok, detail = verify(name, zip_path)
        failures += 0 if ok else 1
        print(f"{name:24} {size:7.0f} KB  {prov['file_count']:>3} files  "
              f"{'OK ' if ok else 'FAIL'}  {detail}")

    print(f"\nwrote {out_dir}  (commit {commit or 'unknown'}"
          f"{', dirty' if dirty else ''})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
