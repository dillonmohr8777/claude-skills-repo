# Release readiness

What has to be true before this skill is shared across AlignHCM, and who can do
each part. Re-run this list before any rollout.

## Automated gate

```bash
python3 scripts/selftest.py
```

22 checks, stdlib only, builds its own fixtures. Every check corresponds to a
real failure this package has had:

| Group | Covers |
|---|---|
| Bundled assets | Lockup artwork byte-identical, recorded template hash matches the file, template still carries 15 placeholders |
| Documented workflow | The `SKILL.md` command sequence runs and validates, missing placeholders are reported by slide and rejected, `--allow-unresolved` works, no possessive artifact in output |
| Linter | Banned colors caught inside a `.docx`, reference deck reads clean, unparseable Office file rejected, ledger in `tokens.md` matches `brand_lint.py` |
| Validator | Geometry tolerance accepts a nominal rebuild and still rejects a wrong canvas, swapped icon detected, distorted client logo detected |
| Portability | Stdlib only, all scripts compile, no em dashes, no personal or machine-specific paths, frontmatter valid, every referenced path resolves |

Exit 0 means the package is internally consistent and the documented workflow
actually runs. It does **not** mean the brand facts are correct; that is the
human review below.

Verified to pass from an isolated copy of the skill folder with nothing else
present, so it works for someone who receives only this directory.

## Blocking, and not automatable

### 1. Publish the fixed version to the account skill store

**This is the gate that matters most.** The copy people load today is the
account-synced one, not this repository. As of the last check, that copy still
contains every blocker:

| Check | Account-synced copy | This repository |
|---|---|---|
| `.docx` gate | `0 error(s)`, exit 0 on a banned color | 2 errors, exit 1 |
| Personal dependencies | 2 in `SKILL.md` | 0 |
| Em dashes in references | 23 | 0 |
| Deck workflow | Fails validation every run | Passes |

Merging the pull request does not change what anyone loads. The fixed package
has to be uploaded wherever account skills are managed. Until then, sharing the
skill name distributes the broken version.

### 2. Fix `rfp-responder`

It hardcodes `#F5A623` as "Align orange" and `#404040` as "Align dark gray".
Neither appears in any audited Align production file. Every RFP response
produced so far carries the unverified color. See `INTEGRATION.md` for the
replacement lines. It is an account skill, so it cannot be fixed from this
repository.

### 3. Decide what happens to the five skills that do not exist

`sow-generator`, `alignhcm-loi`, `alignhcm-legal-review`,
`alignhcm-weekly-sales-report`, and `alignhcm-monthly-forecast-review` were
named in review as consumers of this package but are not in this repository, the
eight Align repositories, or the account skills. Either they live somewhere not
yet searched, they are planned rather than built, or the names are wrong. The
composition table in `SKILL.md` currently promises integrations that cannot be
verified.

### 4. Human brand review

The self-test proves internal consistency, not correctness. A person who knows
the brand should confirm:

- The deck token table matches what the master actually renders. Open the
  bundled reference, compare against `references/powerpoint-tokens.md`.
- Retiring `#E8832A` is right. It was retired on evidence of zero shipped usage,
  which is a judgment call the brand owner can reverse.
- The web tokens are still current. They were observed 2026-07-15 and carry a
  review date of 2027-01-15.
- One real client deck produced end to end reads correctly at full size.

### 5. Decide the SmartCare and carousel disclosure

The historical SmartCare GTM document and the original carousel HTML are
unrecoverable, so those two surfaces produce net-new copy requiring review.
`SKILL.md` states this. Confirm that is acceptable for org-wide use, or recover
the sources.

## Recommended before wider rollout

- **Pilot with one person outside the brand owner's team.** Have them produce a
  real client deck using only `SKILL.md`, with no verbal help. Anything they ask
  about is a documentation gap.
- **Decide the update path.** This package has now been revised twice by
  different routes. Pick one home, repository or account store, and make the
  other a mirror, or the two will diverge again.
- **Consider marketplace packaging.** Several skills in this repository carry
  `.claude-plugin/plugin.json`; this one does not. Adding it would make
  installation and versioning explicit rather than manual.

## After any future edit

Run `python3 scripts/selftest.py` before publishing. If you changed a token,
update both `references/tokens.md` and `scripts/brand_lint.py`; the ledger check
will fail if you update only one. If you replaced the master, re-run
`extract_pptx_theme.py` and update the SHA-256 in
`references/powerpoint-deck-system.md`; the hash check will fail if you do not.
