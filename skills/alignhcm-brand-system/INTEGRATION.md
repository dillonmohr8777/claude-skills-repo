# Downstream skill integration

Blocker 4 of the org-readiness review asked for a cross-reference line in each
of the six Align skills that produce client-facing files. Half of that work
could be done in this repository; half could not. This file records the exact
change to make and where.

## Status

Rechecked 2026-08-19 against this repository, the attached Align repositories,
and the synced account skills.

| Skill | Where it lives | Status |
|---|---|---|
| `rfp-responder` | Account skill store, synced to `~/.claude/skills/synced/` | **Exists, and the colour fix has landed there.** The live copy uses `#E97722` and `#232E3E`; no `#F5A623` or `#404040` remains. Still needs the cross-reference line below |
| `sow-generator` | Superseded | Does not exist and does not need to. `alignhcm-sow` covers it, against Align's real thirteen-section template |
| `alignhcm-loi` | Never existed | Not in this repository, the Align repositories, or the account skills. Nothing claims it |
| `alignhcm-legal-review` | Never existed | Same |
| `alignhcm-weekly-sales-report` | Never existed | Same. `alignhcm-pm-runbook` produces a weekly *project* status report, which is a different document from a sales report |
| `alignhcm-monthly-forecast-review` | Never existed | Same |

Treat the four that never existed as never built rather than as missing, and
stop looking for them. If one turns up somewhere unsearched, wire it up with the
block below.

The composition tables in each `SKILL.md` name the skills that do exist, so the
pointer outward from this package is in place. What remains is the pointer
inward, from `rfp-responder` back to this one.

`rfp-responder` cannot be edited from this repository as a matter of policy: it
is an account skill, and a local edit is overwritten whenever the account store
syncs. Make the edit wherever account skills are managed, then confirm with
`python3 skills/verify_install.py`.

## The line to add

Paste this near the top of each skill's `SKILL.md`, before any document-building
step:

```markdown
## Step 0: Load Align brand tokens

Before building the .docx, load the Align brand system:

- `alignhcm-brand-system/references/tokens.md`, the **Formal documents** section
- the bundled Align lockup at `alignhcm-brand-system/assets/logos/align-hcm-deck-lockup.png`

Use those tokens for every color and typeface. Do not hardcode hex values in
this skill. Gate the finished file with:

    python3 alignhcm-brand-system/scripts/brand_lint.py --surface document <file>.docx
```

## `rfp-responder` also ships off-brand color

Independent of the cross-reference, `rfp-responder` currently hardcodes:

```
- H1 color: Align orange #F5A623
- Body color: dark gray #404040
```

Neither value appears in any audited Align production file. `#F5A623` is a
seventh distinct orange; `#404040` is a near-duplicate of the already-rejected
`#414042`. Both are now on the never-use list in `references/tokens.md` and are
errors in `brand_lint.py`.

Replace those two lines with:

```
- H1 color: Align orange #E97722 (see alignhcm-brand-system/references/tokens.md)
- Body color: primary navy #232E3E
```

Every RFP response produced before this fix carries the unverified orange.

## `cool-data-elements`

Not one of the six, but the same failure: it hardcodes `#E8760A` and `#414042`
in eight places, including its own description. Both are rejected. Either
retarget it at the formal-document palette or stop using it for Align work.
