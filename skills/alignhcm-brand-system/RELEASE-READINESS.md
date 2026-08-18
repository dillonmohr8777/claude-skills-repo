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

## Still open, and genuinely needs a person

### 1. Decide where this package lives

It has now been revised twice by different routes, which is how two copies
diverged in the first place. The live install done here is a local file
replacement. If the account skill store pushes a sync, it will overwrite it. Pick
one home and make the other a mirror:

- **Account skill store as the source.** Upload this package there, and treat the
  repository as the review and history trail.
- **Repository as the source.** Distribute through the marketplace and stop
  editing the account copy.

Until this is decided, a future sync can silently reinstate the broken version.

### 2. Confirm the brand facts

The self-test proves internal consistency, not correctness. Worth a few minutes
from someone who knows the brand:

- The rendered deck matches what the master should look like.
- Retiring `#E8832A` was right. It was retired on evidence of zero shipped usage,
  which is a judgment call and reversible.
- The web tokens are still current. Observed 2026-07-15, review date 2027-01-15.

### 3. The five skills that could not be found

`sow-generator`, `alignhcm-loi`, `alignhcm-legal-review`,
`alignhcm-weekly-sales-report`, and `alignhcm-monthly-forecast-review` are not in
this repository, the eight Align repositories, or the account skills. They are no
longer claimed anywhere. If they exist somewhere unsearched, wire them up with
the block in `INTEGRATION.md`.

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
