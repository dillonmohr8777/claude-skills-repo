#!/usr/bin/env python3
"""Scaffold a BigOrange deck brief with every slot a recipe references.

    python3 new_brief.py --recipe industry-pitch --industry msp --out brief.json
    python3 new_brief.py --recipe client-kickoff --client "Acme Homes" --out brief.json

Every referenced {{vars.x}} becomes "[[TODO x]]" (or an empty list when the
recipe uses it as an array), so build_deck.js fails until it is filled.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECIPES = os.path.join(HERE, "..", "recipes")
TOKEN = re.compile(r"\{\{\s*([\w.\-]+)\s*\}\}")


def walk(node, found):
    if isinstance(node, str):
        whole = re.fullmatch(r"\{\{\s*([\w.\-]+)\s*\}\}", node.strip())
        for p in TOKEN.findall(node):
            found.setdefault(p, "string")
        if whole:
            found[whole.group(1)] = "whole"
    elif isinstance(node, list):
        for x in node:
            walk(x, found)
    elif isinstance(node, dict):
        for k, v in node.items():
            walk(v, found)
            if isinstance(v, str) and k in ("items", "stats", "bullets", "rows", "labels", "series", "decisions", "whoBullets", "playItems", "brokenItems", "journeySteps", "proofStats", "investmentBullets", "accessItems", "scopeRows"):
                m = re.fullmatch(r"\{\{\s*([\w.\-]+)\s*\}\}", v.strip())
                if m:
                    found[m.group(1)] = "array"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipe", required=True)
    ap.add_argument("--industry", choices=["home-builders", "msp", "manufacturing", "landscaping"])
    ap.add_argument("--client")
    ap.add_argument("--presenter", default="Margee Moore")
    ap.add_argument("--date", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    path = os.path.join(RECIPES, f"{a.recipe}.json")
    if not os.path.exists(path):
        sys.exit(f"no recipe at {path}")
    recipe = json.load(open(path))
    found = {}
    walk(recipe, found)
    brief = {"recipe": a.recipe, "date": a.date or "[[TODO date]]", "presenter": a.presenter, "sampleData": True}
    if a.client:
        brief["client"] = {"name": a.client, "line": "[[TODO one line about the client]]"}
        brief["logo"] = {"path": "", "source": "", "verified": False}
    if a.industry:
        brief["industry"] = a.industry
        brief.setdefault("vars", {})["industryLabel"] = {"home-builders": "Home builders", "msp": "IT and MSPs", "manufacturing": "Manufacturing", "landscaping": "Landscaping"}[a.industry]
        brief["vars"]["industryHubUrl"] = {"home-builders": "https://bigorange.marketing/marketing-agency-for-builders/", "msp": "https://bigorange.marketing/msp-it-services-marketing-agency/", "manufacturing": "https://bigorange.marketing/manufacturing-services-marketing-agency/", "landscaping": "https://bigorange.marketing/landscaping-marketing-services/"}[a.industry]
    vars_ = brief.setdefault("vars", {})
    metrics = {}
    for p, kind in sorted(found.items()):
        root, _, key = p.partition(".")
        if root == "vars" and key not in vars_:
            vars_[key] = [] if kind == "array" else f"[[TODO {key}]]"
        elif root == "metrics":
            metrics[key] = [] if kind == "array" else f"[[TODO {key}]]"
        elif root in ("date", "presenter", "periodLabel") and root not in brief:
            brief[root] = f"[[TODO {root}]]"
    if metrics:
        brief["metrics"] = metrics
    with open(a.out, "w") as fh:
        json.dump(brief, fh, indent=2)
    print(f"wrote {a.out} with {len(vars_)} vars; fill every [[TODO]] before building")


if __name__ == "__main__":
    main()
