# Release readiness

What has to be true before this skill is shared across AlignHCM, and who can do
each part. Re-run this list before any rollout.

## Automated gate

```bash
python3 scripts/selftest.py
```

24 checks, stdlib only, builds its own fixtures. Every check corresponds to a
real failure this package has had:

| Group | Covers |
|---|---|
| Bundled assets | Lockup artwork byte-identical, recorded template hash matches the file, template still carries 15 placeholders, no hardcoded possessive after a token |
| Documented workflow | The `SKILL.md` command sequence runs and validates, missing placeholders are reported by slide and rejected, `--allow-unresolved` works, the deck opens and paginates in a real renderer |
| Linter | Banned colors caught inside a `.docx`, reference deck reads clean, unparseable Office file rejected, ledger in `tokens.md` matches `brand_lint.py` |
| Validator | Geometry tolerance accepts a nominal rebuild and still rejects a wrong canvas, swapped icon detected, distorted client logo detected |
| Portability | Stdlib only, all scripts compile, no em dashes, no personal or machine-specific paths, frontmatter valid, every referenced path resolves |

Exit 0 means the package is internally consistent and the documented workflow
actually runs. It does **not** mean the brand facts are correct; that is the
human review below.

Verified to pass from an isolated copy of the skill folder with nothing else
present, so it works for someone who receives only this directory.

The render check is skipped automatically where LibreOffice is not installed.
Everything else runs anywhere Python 3 runs.

## Done

| Item | State |
|---|---|
| Fixed package installed as the live skill | Done. The synced copy was replaced and verified: the `.docx` gate now errors, zero personal dependencies, zero em dashes, self-test 24/24 against the live copy. A backup of the previous copy is at `/tmp/skill-backup`. |
| `rfp-responder` off-brand color | Fixed. `#F5A623` and `#404040` replaced with `#E97722` and `#232E3E`, and a Step 0 added that loads the formal-document tokens and gates on `brand_lint.py`. Now version-controlled in this repository. |
| Unverifiable integration promises | Removed. `SKILL.md` now claims only `rfp-responder`, which is real and wired. `INTEGRATION.md` keeps the paste-in block for future document skills. |
| Deck renders correctly | Verified visually. A full seven-slide deck was built, rendered to PDF, and the slides were inspected. |
| SmartCare and carousel disclosure | Settled. `SKILL.md` states plainly that both surfaces produce net-new copy requiring review. |

### What the visual render caught

The review flagged a hardcoded possessive on slide 5. Rendering showed the same
bug on slides 2, 4, and 6, which no XML-level check would have found: sentences
read "Acme Foods's existing UKG Pro environment". All six occurrences are fixed,
and the self-test now scans the template itself so the pattern cannot return.

This is the argument for keeping the render check: structural validation passed
on all of them.

## Blockers, and how each was closed

Every item previously listed here as "needs a person" was answerable from
documents Align already has. Two of the answers were different from what this
file used to record.

### 1. Where this package lives: settled, and now checkable

The repository is the source. That was previously a preference nobody could
enforce, because no one could see the difference between the two copies from
either side. `skills/verify_install.py` compares an installed skill against the
repository file by file and names what differs. Running it the first time found
the live install two files behind; those were resynced and it now reports a
match.

`skills/package_skills.py` builds each upload zip, stamps it with a
`PROVENANCE.json` naming the commit it came from, then extracts it into an empty
directory and runs the skill's own self-test there. A package that has never
been unpacked and run is a package nobody has checked.

### 2. Brand facts: partly confirmed, partly worse than "contested"

Align's own documents contradict each other on more than team size:

| Fact | Jamieson RFP response, April 2026 | Homewood company bio, August 2026 |
|---|---|---|
| Headquarters | Toronto, with an additional office in St. Petersburg | St. Petersburg, with a second office in Toronto |
| Team | 100+ full-time professionals | 60+ employees |
| Offshore | "a small group of international team members, including in the Philippines" | "100% onshore, with no handoff to another region at any phase" |

The onshore pair is the one that matters. An RFP answer is the more carefully
written document and the one a client can hold Align to.

Rather than block every build until someone rules, `company-facts.md` now
carries a status per value, the builders default to formulations true under
every source, and a contested value fails the build if actually rendered.
The onshore claim is banned outright. Details and the four open rulings are in
that file.

Retiring `#E8832A` and the currency of the web tokens are unchanged and still
worth a brand owner's eye.

### 3. SmartCare: not the conflict it was recorded as

"Thrive" is half a tagline, not a tier. "Stabilize" is a time-bound recovery
engagement, not tier one of three. There are two live vocabularies, the
catalog's Essentials/Accelerate/Transform and the client decks'
Optimize/Optimize Plus, and the August 2026 Portsmouth proposal ships both in
one deck. The builder now fails on a mixed table.
See `alignhcm-intro-deck/references/smartcare-tiers.md`.

### 4. The five skills that could not be found

`sow-generator` is now covered by `alignhcm-sow`. `alignhcm-loi`,
`alignhcm-legal-review`, `alignhcm-weekly-sales-report`, and
`alignhcm-monthly-forecast-review` do not exist in this repository, the Align
repositories, or the account skills, and nothing claims them any more. Treat
them as never built rather than as missing.

### 5. Logo fetching on a restricted network

Still not tested against a live corporate site, because this environment's
network policy answers 403 to every outbound CONNECT. That is an environment
limit, not a defect, and it is now diagnosable rather than misleading: a page
that loads while every asset download is refused used to report "no decodable
logo candidate found", which reads as "this company has no usable logo". It now
reports an egress restriction and exits 5, and `--doctor` answers the question
directly.

## What still needs a person, and it is not code

- **Rule on the four contested facts.** Headquarters, team size, the offshore
  disclosure, and the review count. The offshore one is worth doing first.
- **Rule on the SmartCare vocabulary**, and align the catalog with the client
  decks either way. The catalog holds the pricing, hour bands, and exit terms.
- **Have Sales read one generated SOW** against a recent executed one. The
  structure and the five load-bearing clauses now match Align's template, but a
  lawyer has not read the output.

## Recommended before wider rollout

- **Pilot with one person outside the brand owner's team.** Have them produce a
  real client deck using only `SKILL.md`, with no verbal help. Anything they ask
  about is a documentation gap.
- **Consider marketplace packaging.** Several skills in this repository carry
  `.claude-plugin/plugin.json`; this one does not. Adding it would make
  installation and versioning explicit rather than manual.

## After any future edit

Run `python3 scripts/selftest.py` before publishing. If you changed a token,
update both `references/tokens.md` and `scripts/brand_lint.py`; the ledger check
will fail if you update only one. If you replaced the master, re-run
`extract_pptx_theme.py` and update the SHA-256 in
`references/powerpoint-deck-system.md`; the hash check will fail if you do not.
