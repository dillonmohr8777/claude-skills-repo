#!/usr/bin/env python3
"""
Compare an installed Align skill against this repository.

    python3 verify_install.py                      # check every Align skill
    python3 verify_install.py alignhcm-sow         # check one
    python3 verify_install.py --installed-root DIR # non-default install location
    python3 verify_install.py --json

Why this exists: this package has been revised by two routes, a repository and
an account skill store, and the copies diverged. Arguing about which one is
"the source" does not help, because nobody can see the difference from either
side. This makes the difference visible, which is the part that was missing.

The repository is the source. Anything this reports as differing means the
installed copy was edited somewhere else, or a sync has not happened yet.

Exit codes:
    0  every installed copy matches the repository
    1  at least one installed copy differs
    2  nothing to compare, no Align skill is installed where expected
"""

import argparse
import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

ALIGN_SKILLS = ["alignhcm-brand-system", "alignhcm-intro-deck",
                "alignhcm-proposal", "alignhcm-sow", "alignhcm-pm-runbook"]

DEFAULT_ROOTS = [
    pathlib.Path.home() / ".claude" / "skills" / "synced",
    pathlib.Path.home() / ".claude" / "skills",
]

# Not content. Regenerated on install or by the packager, so a difference here
# says nothing about whether the skill itself drifted.
IGNORE_NAMES = {"PROVENANCE.json", ".DS_Store", ".gitignore"}
IGNORE_PARTS = {"__pycache__", ".git"}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def tree(root):
    """Relative path -> sha256, skipping generated and editor noise."""
    out = {}
    root = pathlib.Path(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORE_NAMES or path.suffix == ".pyc":
            continue
        if IGNORE_PARTS & set(path.parts):
            continue
        out[str(path.relative_to(root))] = sha(path)
    return out


def find_installed(name, roots):
    for root in roots:
        candidate = pathlib.Path(root) / name
        if candidate.is_dir():
            return candidate
    return None


def compare(name, installed_dir):
    repo_dir = HERE / name
    repo, inst = tree(repo_dir), tree(installed_dir)
    missing = sorted(set(repo) - set(inst))
    extra = sorted(set(inst) - set(repo))
    changed = sorted(f for f in set(repo) & set(inst) if repo[f] != inst[f])
    return {
        "skill": name,
        "installed_path": str(installed_dir),
        "matches": not (missing or extra or changed),
        "repo_files": len(repo),
        "installed_files": len(inst),
        "missing_from_install": missing,
        "not_in_repo": extra,
        "differing": changed,
    }


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*", default=None,
                    help="skill names to check (default: every Align skill)")
    ap.add_argument("--installed-root", action="append", default=None,
                    help="where installed skills live; repeatable")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    roots = ([pathlib.Path(r) for r in args.installed_root]
             if args.installed_root else DEFAULT_ROOTS)
    wanted = args.skills or ALIGN_SKILLS

    results, absent = [], []
    for name in wanted:
        if not (HERE / name).is_dir():
            print(f"skip {name}: not in this repository", file=sys.stderr)
            continue
        installed = find_installed(name, roots)
        if installed is None:
            absent.append(name)
            continue
        results.append(compare(name, installed))

    if args.json:
        print(json.dumps({"results": results, "not_installed": absent,
                          "roots": [str(r) for r in roots]}, indent=2))
    else:
        for r in results:
            mark = "match " if r["matches"] else "DIFFER"
            print(f"{mark}  {r['skill']:24} {r['installed_files']:>3} file(s) "
                  f"at {r['installed_path']}")
            for f in r["differing"]:
                print(f"          differs   {f}")
            for f in r["missing_from_install"]:
                print(f"          missing   {f}")
            for f in r["not_in_repo"]:
                print(f"          extra     {f}")
        for name in absent:
            print(f"absent  {name:24} not installed under "
                  f"{', '.join(str(r) for r in roots)}")

    if not results:
        return 2
    return 0 if all(r["matches"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
