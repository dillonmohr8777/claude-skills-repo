#!/usr/bin/env python3
"""Regenerate the top-level AGENTS.md catalog from skills/<name>/SKILL.md files.

Run from repo root:

    python3 scripts/generate-agents-md.py

Walks every immediate subdirectory of skills/ that contains a SKILL.md, parses
the YAML frontmatter for `name` and `description`, and writes a Codex-readable
index to ./AGENTS.md.
"""
from __future__ import annotations

import os
import re
import sys

SKILLS_DIR = "skills"
OUTPUT = "AGENTS.md"

NON_SKILL_DIRS = {
    "agents",
    "commands",
    "custom-gpt",
    "docs",
    "documentation",
    "eval-workspace",
    "orchestration",
    "scripts",
    "standards",
    "templates",
    "tests",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    cur_key: str | None = None
    for line in m.group(1).splitlines():
        mk = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if mk:
            cur_key = mk.group(1)
            val = mk.group(2).strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            fm[cur_key] = val
        elif cur_key and line.startswith((" ", "\t")):
            fm[cur_key] = (fm.get(cur_key, "") + " " + line.strip()).strip()
    return fm, text[m.end():]


def extract_skill(skill_dir: str, skill_path: str) -> dict | None:
    with open(skill_path, encoding="utf-8") as f:
        text = f.read()
    fm, _ = parse_frontmatter(text)
    if not fm:
        # No YAML frontmatter — not a real skill, skip.
        return None
    name = fm.get("name") or skill_dir
    desc = fm.get("description", "").strip()
    if not desc:
        return None
    desc = desc.replace("\n", " ").strip()
    if len(desc) > 220:
        desc = desc[:217].rstrip() + "..."
    return {"dir": skill_dir, "name": name, "description": desc}


def main() -> int:
    if not os.path.isdir(SKILLS_DIR):
        print(f"error: {SKILLS_DIR}/ not found (run from repo root)", file=sys.stderr)
        return 1
    rows: list[dict] = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        if entry.startswith(".") or entry in NON_SKILL_DIRS:
            continue
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_dir):
            continue
        skill_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        row = extract_skill(entry, skill_path)
        if row is not None:
            rows.append(row)

    header = (
        "# AGENTS.md — Codex instructions for the Claude skills repo\n\n"
        "This repository is a library of **Claude Skills** (each `skills/<name>/SKILL.md`).\n"
        "Codex CLI sessions running in this repo can use any skill below as a playbook.\n\n"
        "## How to use a skill (Codex)\n\n"
        "1. Match the user's request to a skill in the catalog below by its description.\n"
        "2. Read that skill's full file: `skills/<name>/SKILL.md`.\n"
        "3. Follow the procedure described in that file. If the skill links to\n"
        "   `references/*.md` files inside its own directory, read those as needed.\n"
        "4. The YAML frontmatter at the top of each `SKILL.md` defines the trigger\n"
        "   conditions (`description`) and may pin specific tools (`allowed-tools`).\n"
        "   Treat that frontmatter as authoritative.\n\n"
        "## Conventions\n\n"
        "- Each skill directory is self-contained. Anything it needs (templates,\n"
        "  references, scripts, evaluators) lives under `skills/<name>/`.\n"
        "- Some skills have their own `AGENTS.md` or `.codex/instructions.md` — those\n"
        "  override this top-level file when Codex is run from inside that directory.\n"
        "- Non-skill support directories (`agents/`, `commands/`, `docs/`,\n"
        "  `documentation/`, `scripts/`, `standards/`, `templates/`, `tests/`,\n"
        "  `orchestration/`, `eval-workspace/`, `custom-gpt/`) are tooling, not skills.\n\n"
        "## Adjacent resources Codex can pull from\n\n"
        "Beyond the SKILL.md files indexed below, this repo also contains:\n\n"
        "- `skills/agents/` — agent-persona prompts organized by function\n"
        "  (`business-growth/`, `c-level/`, `engineering/`, `engineering-team/`,\n"
        "  `finance/`, `marketing/`, `personas/`, `product/`, `project-management/`,\n"
        "  `ra-qm-team/`). Use one of these as a system prompt when the user asks\n"
        "  for a domain expert (e.g. \"act as a CTO advisor\" → read\n"
        "  `skills/agents/c-level/cs-cto-advisor.md`).\n"
        "- `skills/commands/` — slash-command-style playbooks (`a11y-audit.md`,\n"
        "  `code-to-prd.md`, `prd.md`, `retro.md`, `rice.md`, `seo-auditor.md`,\n"
        "  `sprint-plan.md`, `tc.md`, etc.). These are reusable prompts; read the\n"
        "  matching file when the user invokes the command by name.\n"
        "- `skills/standards/` — repo-wide quality, communication, git, and\n"
        "  documentation standards. Treat as authoritative house style.\n\n"
        "## Cross-model handoffs\n\n"
        "The `codex` skill itself documents how Claude Code delegates work to Codex\n"
        "(via `codex-plugin-cc` or the `codex` CLI). The reverse direction — Codex\n"
        "delegating back to Claude — isn't wired up here; if you need a Claude opinion\n"
        "from a Codex session, ask the human to run it in Claude Code.\n\n"
        "## Skill catalog\n\n"
        f"Total skills: {len(rows)}.\n\n"
        "| Skill | Description |\n"
        "| --- | --- |\n"
    )

    body_lines = []
    for r in rows:
        desc = r["description"].replace("|", "\\|") or "_(no description in frontmatter)_"
        body_lines.append(f"| [`{r['dir']}`](skills/{r['dir']}/SKILL.md) | {desc} |")

    footer = (
        "\n\n---\n\n"
        "_This file is generated by `scripts/generate-agents-md.py`. "
        "Regenerate after adding or removing skills._\n"
    )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(body_lines) + footer)
    print(f"wrote {OUTPUT}: {len(rows)} skills indexed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
