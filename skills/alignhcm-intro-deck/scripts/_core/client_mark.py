"""
The client mark: whether a document carries the other party's logo, and how.

The rule Align asked for is that a prospect's mark is fetched from their own
site, cleaned, background removed, and plated, exactly as the brand system does
it, every time. The part that is easy to get wrong is not the fetching. It is
that nobody remembers to decide. A deck ships with an empty right panel, or
worse, with the previous prospect's mark still in it.

So the decision is required rather than optional. A builder that supports a
client mark refuses to run until the spec says one of:

    "client_mark": {"domain": "acme.com"}      fetch it, clean it, plate it
    "client_mark": {"file": "acme-logo.png"}   same pipeline, supplied file
    "client_mark": {"ready": "acme-plated.png"} already produced by the pipeline
    "client_mark": "none"                       deliberately no client mark

"none" is a real answer and is meant to be used. An internal readout or a
template does not need the prospect's logo. What is not allowed is silence.
"""

import json
import os
import subprocess
import sys

DECISION_HELP = """A client mark decision is required and the spec does not have one.

Is a prospect or client involved in this document?

  Yes, and I have their domain
      "client_mark": {"domain": "acme.com"}
      Fetches the mark from their own site, removes the background, upscales,
      and puts it on a bordered plate in their own brand colour.

  Yes, and I already have a logo file
      "client_mark": {"file": "path/to/acme.png"}
      Same cleanup, plate, and quality gate as the fetched path.

  Yes, and it has already been through the pipeline
      "client_mark": {"ready": "path/to/acme-plated.png"}
      Used as is. Only do this with output from fetch_client_logo.py.

  No
      "client_mark": "none"
      A deliberate choice, and a normal one for internal documents."""


class MarkError(ValueError):
    pass


def _fetcher():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fetch_client_logo.py")


def resolve(spec, out_dir, *, name=None, log=print, allow_low_quality=False):
    """
    Turn the spec's decision into a path, or None.

    Returns (path_or_None, provenance_dict). Raises MarkError when the decision
    is missing or the pipeline rejects the artwork, because a cover with a
    broken mark on it is worse than a build that stopped.
    """
    decision = spec.get("client_mark")
    if decision is None:
        raise MarkError(DECISION_HELP)

    if decision == "none" or decision is False:
        return None, {"decision": "none"}

    if not isinstance(decision, dict):
        raise MarkError('client_mark must be "none" or an object with one of '
                        '"domain", "file", or "ready"')

    if "ready" in decision:
        path = decision["ready"]
        if not os.path.exists(path):
            raise MarkError(f"client_mark.ready points at a missing file: {path}")
        side = path + ".source.json"
        prov = {"decision": "ready", "path": path}
        if os.path.exists(side):
            with open(side, encoding="utf8") as fh:
                prov["source"] = json.load(fh)
        else:
            log("note: no .source.json beside the supplied mark, so it cannot "
                "be confirmed as pipeline output")
        return path, prov

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "client-mark.png")
    cmd = [sys.executable, _fetcher(), "--out", out, "--json"]
    if name:
        cmd += ["--name", name]
    if allow_low_quality:
        cmd.append("--allow-low-quality")

    if "domain" in decision:
        cmd += ["--domain", decision["domain"]]
        what = decision["domain"]
    elif "file" in decision:
        if not os.path.exists(decision["file"]):
            raise MarkError(f"client_mark.file is missing: {decision['file']}")
        cmd += ["--from-file", decision["file"]]
        what = decision["file"]
    else:
        raise MarkError('client_mark needs one of "domain", "file", or "ready"')

    for key, flag in (("plate", "--plate"), ("cover_bg", "--cover-bg"),
                      ("min_width", "--min-width")):
        if key in decision:
            cmd += [flag, str(decision[key])]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if proc.returncode == 5:
        raise MarkError(
            f"the network refused every download while fetching {what}. This is "
            f"an egress problem, not a company without a logo. Run "
            f"fetch_client_logo.py --domain {what} --doctor, or supply the file "
            f'with "client_mark": {{"file": "..."}}.')
    if proc.returncode != 0 or not os.path.exists(out):
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        tail = "\n  ".join(detail[-6:]) if detail else "no output"
        raise MarkError(
            f"could not produce a usable mark for {what} (exit "
            f"{proc.returncode}):\n  {tail}")

    prov = {"decision": "fetched" if "domain" in decision else "file",
            "path": out}
    try:
        prov["source"] = json.loads(proc.stdout[proc.stdout.index("{"):])
    except (ValueError, json.JSONDecodeError):
        pass
    return out, prov


def describe(prov):
    """One line for the build log."""
    if prov.get("decision") == "none":
        return "no client mark, by decision"
    src = prov.get("source") or {}
    plate = (src.get("plate") or {})
    bits = [prov.get("decision", "?")]
    if src.get("source_url"):
        bits.append(src["source_url"][:60])
    if plate.get("applied"):
        bits.append(f"{plate.get('polarity')} plate, border {plate.get('border')}")
    if src.get("final_size"):
        bits.append("x".join(str(v) for v in src["final_size"]))
    return "client mark: " + ", ".join(bits)
