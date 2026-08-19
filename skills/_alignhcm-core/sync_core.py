#!/usr/bin/env python3
"""
Vendor the shared core into every Align document skill.

A Claude skill is installed standalone and cannot import a sibling, so the core
is copied into each skill rather than shared by reference. Copying without
discipline rots, so this also writes `scripts/_core/CORE_MANIFEST.json` holding
the SHA-256 of every vendored file. Each skill's self-test compares its copies
against that manifest and fails if someone edited a vendored file directly.

    python3 sync_core.py           # copy and report
    python3 sync_core.py --check   # verify only, non-zero if drifted
"""

import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
SKILLS = HERE.parent

# Which core files each skill needs. Keeping this explicit means a deck skill
# does not ship a Word writer it never calls.
TARGETS = {
    "alignhcm-sow": ["alignhcm_core.py", "alignhcm_docx.py", "company-facts.md", "selftest_common.py"],
    "alignhcm-proposal": ["alignhcm_core.py", "alignhcm_pptx.py", "company-facts.md", "selftest_common.py"],
    "alignhcm-intro-deck": ["alignhcm_core.py", "alignhcm_pptx.py", "company-facts.md", "selftest_common.py"],
    "alignhcm-pm-runbook": ["alignhcm_core.py", "alignhcm_docx.py", "company-facts.md", "selftest_common.py"],
}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    check_only = "--check" in sys.argv
    drifted, copied = [], 0

    for skill, files in TARGETS.items():
        root = SKILLS / skill
        if not root.exists():
            print(f"skip {skill}: not present")
            continue
        core_dir = root / "scripts" / "_core"
        core_dir.mkdir(parents=True, exist_ok=True)
        manifest = {"core_version": _core_version(), "files": {}}

        for name in files:
            src = HERE / name
            dst = core_dir / name
            digest = sha(src)
            manifest["files"][name] = digest
            if check_only:
                if not dst.exists() or sha(dst) != digest:
                    drifted.append(f"{skill}/scripts/_core/{name}")
            else:
                shutil.copy2(src, dst)
                copied += 1

        if not check_only:
            (core_dir / "CORE_MANIFEST.json").write_text(
                json.dumps(manifest, indent=2) + "\n")
            (core_dir / "__init__.py").write_text(
                '"""Vendored Align core. Do not edit here; edit '
                '_alignhcm-core/ and run sync_core.py."""\n')

    if check_only:
        if drifted:
            print("DRIFTED:")
            for d in drifted:
                print(f"  {d}")
            return 1
        print("all vendored copies match the canonical core")
        return 0

    print(f"vendored {copied} file(s) into {len(TARGETS)} skill(s)")
    return 0


def _core_version():
    text = (HERE / "alignhcm_core.py").read_text()
    for line in text.splitlines():
        if line.startswith("CORE_VERSION"):
            return line.split("=", 1)[1].strip().strip('"')
    return "unknown"


if __name__ == "__main__":
    sys.exit(main())
