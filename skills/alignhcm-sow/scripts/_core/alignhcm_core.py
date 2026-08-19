"""
Align HCM document engine. Shared by every Align document skill.

Four skills produce four different artifacts from the same underlying problem:
take an approved template, fill it with this deal's facts, prove nothing from
the last deal survived, and write it somewhere a colleague can find. This module
is that problem solved once.

Vendored into each skill at `scripts/_core/alignhcm_core.py`. Do not edit a
vendored copy; edit the canonical one and re-run `sync_core.py`.

Stdlib only. An Office file is a zip of XML, which is all this needs.
"""

import datetime
import json
import os
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET

CORE_VERSION = "1.0.0"

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

class Finding:
    """One problem with a document. Level is 'error' or 'warn'."""

    __slots__ = ("level", "where", "message")

    def __init__(self, level, where, message):
        self.level = level
        self.where = where
        self.message = message

    def __repr__(self):
        return f"{self.level:5} {self.where}: {self.message}"

    def as_dict(self):
        return {"level": self.level, "where": self.where, "message": self.message}


class Report:
    """Findings plus a pass/fail verdict. Errors fail; warnings do not."""

    def __init__(self, subject):
        self.subject = subject
        self.findings = []

    def error(self, where, message):
        self.findings.append(Finding("error", where, message))

    def warn(self, where, message):
        self.findings.append(Finding("warn", where, message))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.level == "warn"]

    @property
    def passed(self):
        return not self.errors

    def render(self):
        lines = [f"{self.subject}"]
        for f in self.findings:
            lines.append(f"  {f.level:5} {f.where}: {f.message}")
        lines.append(f"  {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return "\n".join(lines)

    def as_dict(self):
        return {
            "subject": self.subject,
            "passed": self.passed,
            "findings": [f.as_dict() for f in self.findings],
        }


# ---------------------------------------------------------------------------
# OPC helpers
# ---------------------------------------------------------------------------

def read_parts(path):
    """Every part of an Office package, as a name to bytes mapping."""
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


def write_parts(path, parts, source=None):
    """
    Write a package back out.

    When `source` is given, per-entry timestamps and attributes are carried
    across so a diff between input and output shows only the parts that really
    changed. That matters when the template is hash-pinned.
    """
    info = {}
    if source and os.path.exists(source):
        with zipfile.ZipFile(source) as zf:
            info = {i.filename: i for i in zf.infolist()}
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            src = info.get(name)
            entry = zipfile.ZipInfo(name, date_time=src.date_time if src
                                    else (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            if src:
                entry.external_attr = src.external_attr
            out.writestr(entry, data)
    os.replace(tmp, path)


def text_parts(parts):
    """The parts whose visible text a reader would see, by package family."""
    out = []
    for name in sorted(parts):
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
            out.append(name)
        elif re.fullmatch(r"word/(document|header\d*|footer\d*)\.xml", name):
            out.append(name)
    return out


def _text_tag(part):
    return f"{{{W}}}t" if part.startswith("word/") else f"{{{A}}}t"


def _para_tag(part):
    return f"{{{W}}}p" if part.startswith("word/") else f"{{{A}}}p"


def visible_text(parts):
    """All visible text in the document, joined. Used for residue scanning."""
    chunks = []
    for name in text_parts(parts):
        try:
            root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        for node in root.iter(_text_tag(name)):
            if node.text:
                chunks.append(node.text)
    return " ".join(chunks)


# ---------------------------------------------------------------------------
# Placeholders
# ---------------------------------------------------------------------------

def discover_placeholders(parts):
    """
    Every `{{TOKEN}}` in the document, mapped to where it appears.

    Runs are joined per paragraph before matching, because an editor may split
    a token across runs and a naive per-run scan would miss it entirely.
    """
    found = {}
    for name in text_parts(parts):
        try:
            root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        ttag, ptag = _text_tag(name), _para_tag(name)
        for para in root.iter(ptag):
            joined = "".join(n.text or "" for n in para.iter(ttag))
            for token in PLACEHOLDER_RE.findall(joined):
                found.setdefault(token, set()).add(_where(name))
    return {token: sorted(places) for token, places in found.items()}


def _where(part_name):
    m = re.search(r"slide(\d+)\.xml", part_name)
    if m:
        return f"slide {int(m.group(1))}"
    if part_name.startswith("word/document"):
        return "body"
    if "header" in part_name:
        return "header"
    if "footer" in part_name:
        return "footer"
    return part_name


def _apply(text, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def fill_placeholders(parts, replacements):
    """
    Substitute tokens throughout the document.

    Per-run replacement is preferred because it preserves mixed formatting
    inside a paragraph. When a token straddles a run boundary the per-run pass
    cannot see it, so that paragraph is collapsed into its first run instead.
    """
    changed_parts = 0
    for name in text_parts(parts):
        try:
            root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        ttag, ptag = _text_tag(name), _para_tag(name)
        dirty = False
        for para in root.iter(ptag):
            nodes = list(para.iter(ttag))
            if not nodes:
                continue
            originals = [n.text or "" for n in nodes]
            joined = "".join(originals)
            if "{{" not in joined:
                continue
            per_run = [_apply(t, replacements) for t in originals]
            whole = _apply(joined, replacements)
            if "".join(per_run) == whole:
                for node, new, old in zip(nodes, per_run, originals):
                    if new != old:
                        node.text = new
                        dirty = True
            else:
                nodes[0].text = whole
                for node in nodes[1:]:
                    node.text = ""
                dirty = True
        if dirty:
            parts[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            changed_parts += 1
    return changed_parts


def parse_replacements(pairs):
    """Turn `--replace OLD=NEW` strings into pairs, rejecting malformed input."""
    out = []
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"invalid --replace value {item!r}; expected OLD=NEW")
        old, new = item.split("=", 1)
        if not old:
            raise ValueError("--replace OLD may not be empty")
        out.append((old, new))
    return out


def report_unresolved(remaining, allow=False, out=print):
    """
    Print what is still unfilled, grouped by location.

    The script teaches the contract so documentation cannot drift from it: the
    list of tokens comes from the template, not from a list someone maintained
    by hand and forgot to update.
    """
    if not remaining:
        out("all placeholders resolved")
        return 0
    by_place = {}
    for token, places in remaining.items():
        for place in places:
            by_place.setdefault(place, []).append(token)
    out(f"\n{len(remaining)} unresolved placeholder(s):")
    for place in sorted(by_place):
        out(f"  {place}: {' '.join(sorted(by_place[place]))}")
    out("\nSupply each with --replace, for example:")
    out(f"  --replace '{sorted(remaining)[0]}=<value>'")
    if allow:
        out("\n--allow-unresolved set: continuing anyway.")
        return 0
    out("\nThe document was written but will fail validation until these are "
        "filled. Re-run with the missing values, or pass --allow-unresolved.")
    return 1


# ---------------------------------------------------------------------------
# Residue
#
# The single most damaging failure in a reused template is the previous
# client's name surviving into the next one. It has to be checked by looking
# for what should NOT be there, not by trusting that every field was filled.
# ---------------------------------------------------------------------------

# Names that appear in Align's own sample and reference material. Any of these
# in a document prepared for someone else means the template was not cleaned.
KNOWN_SAMPLE_ENTITIES = [
    "Acme Foods", "Homewood", "REI", "Prime Communications", "Kearney",
    "Sage Hospitality", "World Central Kitchen", "Hydro Extrusion", "Leyad",
    "Miner's", "St Lukes", "St Luke's", "GES", "Vancity", "Diversified Energy",
    "Troon", "Peco Foods", "Burnco", "Driscoll's", "Kimberly-Clark", "Alsco",
    "TPI Composites",
]

MONEY_RE = re.compile(r"\$\s?[\d,]+(?:\.\d{2})?(?:\s?[KMB])?")


def scan_residue(parts, client_name, report, extra_terms=()):
    """
    Look for anything that belongs to a different engagement.

    Checks, in order of how badly each one lands with a client:
      1. Another company's name in a document addressed to this one
      2. Any surviving `{{TOKEN}}`
      3. The client's own name absent entirely, which means nothing was filled
    """
    text = visible_text(parts)
    lowered = text.lower()

    for entity in list(KNOWN_SAMPLE_ENTITIES) + list(extra_terms):
        if client_name and entity.lower() in client_name.lower():
            continue  # this really is the client
        # Whole-word only. A short name like GES matches inside "changes" and a
        # naive substring scan makes the check cry wolf on every document.
        pattern = r"(?<!\w)" + re.escape(entity.lower()) + r"(?!\w)"
        if re.search(pattern, lowered):
            report.error(
                "residue",
                f"'{entity}' appears in a document prepared for "
                f"{client_name or 'this client'}. A previous engagement's "
                f"content survived the template fill.")

    leftovers = PLACEHOLDER_RE.findall(text)
    if leftovers:
        uniq = sorted(set(leftovers))
        report.error("placeholders",
                     f"unresolved: {' '.join(uniq[:8])}"
                     + (f" and {len(uniq) - 8} more" if len(uniq) > 8 else ""))

    if client_name and client_name.lower() not in lowered:
        report.error("client",
                     f"the client name '{client_name}' does not appear anywhere "
                     f"in the document")
    return report


# ---------------------------------------------------------------------------
# Deterministic naming
#
# SharePoint currently carries files like `Prime_Communications_SOW2.docx`,
# `Prime_Communications_SOW_revisedMoe15Aug2025.docx`, and an `/OLD/` folder
# holding three more. Nobody can tell which is real. Every skill writes through
# this so the newest version is always obvious and superseded ones move aside.
# ---------------------------------------------------------------------------

BANNED_NAME_TOKENS = re.compile(
    r"\b(final|FINAL|latest|new|old|OLD|copy|revised|rev\d*|draft\d+|v?\d+\s*-\s*copy|"
    r"use\s*this|current)\b|\(\d+\)")


def slugify(value):
    """A filename-safe form of a company name that stays readable."""
    cleaned = re.sub(r"[^\w\s-]", "", value or "").strip()
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    return cleaned or "Unnamed"


def next_version(directory, client, artifact, ext, today=None):
    """
    The next version number for this client and artifact in this directory.

    Derived by looking at what is already on disk rather than asking the author
    to remember, because asking is exactly how `SOW2` and `SOW_revised` happen.
    """
    stem = f"{slugify(client)}_{artifact}_"
    highest = 0
    if os.path.isdir(directory):
        for name in os.listdir(directory):
            if not name.startswith(stem) or not name.endswith(ext):
                continue
            m = re.search(r"_v(\d+)" + re.escape(ext) + r"$", name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def build_name(client, artifact, ext, version, date=None):
    """`Client_Artifact_YYYY-MM-DD_v3.docx`. Sorts correctly, reads correctly."""
    stamp = (date or datetime.date.today()).isoformat()
    return f"{slugify(client)}_{artifact}_{stamp}_v{version}{ext}"


def supersede_previous(directory, client, artifact, ext, keep):
    """
    Move older versions into `_superseded/` so the live folder holds one file.

    Nothing is deleted. The history stays available, it simply stops competing
    for attention with the current version.
    """
    if not os.path.isdir(directory):
        return []
    stem = f"{slugify(client)}_{artifact}_"
    moved = []
    archive = os.path.join(directory, "_superseded")
    for name in sorted(os.listdir(directory)):
        if name == keep or not name.startswith(stem) or not name.endswith(ext):
            continue
        os.makedirs(archive, exist_ok=True)
        shutil.move(os.path.join(directory, name), os.path.join(archive, name))
        moved.append(name)
    return moved


def check_filename(name, report):
    """Flag a filename that reintroduces the ambiguity this convention removes."""
    bad = BANNED_NAME_TOKENS.findall(name)
    if bad:
        report.warn("filename",
                    f"'{name}' contains version-ambiguous wording. Use the "
                    f"Client_Artifact_Date_vN convention so the current file is "
                    f"obvious.")
    if re.search(r"\b(?:[A-Z][a-z]+\d{1,2}[A-Z][a-z]{2}\d{4})\b", name):
        report.warn("filename",
                    f"'{name}' looks like it carries an editor's name and date. "
                    f"Version numbers belong in the filename; authorship belongs "
                    f"in the document history.")
    return report


# ---------------------------------------------------------------------------
# Company facts
# ---------------------------------------------------------------------------

class Facts:
    """
    Align's own numbers, loaded from one file.

    These disagree across shipped client documents: one deck says 60+ team
    members and 115+ reviews, another says 100+ and 111. Both went to
    prospects. A single loader plus a staleness date is the fix.
    """

    def __init__(self, path):
        self.path = path
        self.values = {}
        self.status = {}
        self.forbidden = {}
        self.review_by = None
        self.used = set()
        self._load()

    # The file is prose with several tables in it. Parse by section rather than
    # by shape: a "| `TOKEN` | value |" pattern also matches rows in the
    # explanatory tables, and matching those silently corrupts the ledger.
    VALUES_HEADING = "## canonical values"
    CLAIMS_HEADING = "## claims these skills will never generate"

    def _load(self):
        if not os.path.exists(self.path):
            return
        section = None
        for line in open(self.path, encoding="utf8"):
            stripped = line.strip()
            if stripped.startswith("## "):
                low = stripped.lower()
                if low.startswith(self.VALUES_HEADING):
                    section = "values"
                elif low.startswith(self.CLAIMS_HEADING):
                    section = "claims"
                else:
                    section = None
                continue

            m2 = re.match(r"^review_by:\s*(\S+)", line)
            if m2:
                self.review_by = m2.group(1)
                continue

            if section == "values":
                m = re.match(
                    r"^\|\s*`([A-Z0-9_]+)`\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|",
                    line)
                if m:
                    self.values[m.group(1)] = m.group(2).strip()
                    self.status[m.group(1)] = (m.group(3).strip().lower()
                                               or "single source")
            elif section == "claims":
                f = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|", line)
                if f:
                    self.forbidden[f.group(1).strip().lower()] = f.group(2).strip()

    def get(self, key, default=None):
        """Record the read, so the builder can report what it actually used."""
        self.used.add(key)
        return self.values.get(key, default)

    def contested_used(self):
        """(key, value) for every contested fact this build actually rendered."""
        return sorted((k, self.values[k]) for k in self.used
                      if self.status.get(k) == "contested")

    def single_source_used(self):
        return sorted((k, self.values[k]) for k in self.used
                      if self.status.get(k) == "single source")

    def check(self, report, allow_contested=False):
        """
        A contested fact is one that shipped Align documents disagree about.
        Rendering it into a client-facing file picks a side silently, which is
        how two prospects end up holding two different versions of Align.
        """
        if self.stale():
            report.warn("facts",
                        f"company facts were due for review on {self.review_by}")
        contested = self.contested_used()
        if contested:
            detail = "; ".join(f"{k} = {v}" for k, v in contested)
            if allow_contested:
                report.warn("facts",
                            f"rendered {len(contested)} contested fact(s): {detail}")
            else:
                report.error(
                    "facts",
                    f"this document renders {len(contested)} contested fact(s) "
                    f"({detail}). Shipped Align documents disagree on these; see "
                    f"the contested section of company-facts.md. Settle the value "
                    f"and change its status to verified, or pass "
                    f"--allow-contested to ship it anyway.")
        return report

    def scan_forbidden_claims(self, parts, report):
        """Fail on claims Align's own documents contradict."""
        text = " ".join(visible_text(parts).split()).lower()
        for phrase, why in self.forbidden.items():
            if phrase in text:
                report.error("claims",
                             f'the document asserts "{phrase}": {why}')
        return report

    def as_replacements(self):
        return [("{{" + k + "}}", v) for k, v in self.values.items()]

    def stale(self, today=None):
        if not self.review_by:
            return False
        try:
            due = datetime.date.fromisoformat(self.review_by)
        except ValueError:
            return False
        return (today or datetime.date.today()) > due


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------

# Measured from the supplied Align deck master. Kept here so every skill gates
# on the same values without depending on the brand skill being installed.
DECK_NAVY = "#232E3E"
DECK_ORANGE = "#E97722"
CONTRAST_ORANGE = "#B05512"
PAPER = "#F6F8FA"

NEVER_USE = {
    "#E8760A": "not present in any audited Align production file",
    "#414042": "not present in any audited Align production file",
    "#E8832A": "retired 2026-08-17; documentation only, never shipped",
    "#F5A623": "not present in any audited Align production file",
    "#404040": "not present in any audited Align production file",
}

OFFICE_COLOUR_RE = re.compile(
    rb'(?:<w:color[^>]*w:val="|<w:shd[^>]*w:fill="|srgbClr[^>]*val=")([0-9A-Fa-f]{6})')


def scan_banned_colours(parts, report):
    """Reject the colours that are wrong wherever they appear."""
    for name, data in parts.items():
        if not name.endswith(".xml"):
            continue
        for raw in set(OFFICE_COLOUR_RE.findall(data)):
            hexv = "#" + raw.decode().upper()
            if hexv in NEVER_USE:
                report.error(name, f"{hexv} is off-brand: {NEVER_USE[hexv]}")
    return report


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf8") as fh:
        return json.load(fh)
