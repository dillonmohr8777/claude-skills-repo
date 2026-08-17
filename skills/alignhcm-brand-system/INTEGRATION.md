# Downstream skill integration

Blocker 4 of the org-readiness review asked for a cross-reference line in each
of the six Align skills that produce client-facing files. Half of that work
could be done in this repository; half could not. This file records the exact
change to make and where.

## Status

| Skill | Where it lives | Status |
|---|---|---|
| `rfp-responder` | Account skill store, synced to `~/.claude/skills/synced/` | **Exists. Needs the edit below, plus a color fix.** |
| `sow-generator` | Not found | Does not exist in this repository, in any of the eight Align repositories, or in the synced account skills |
| `alignhcm-loi` | Not found | Same |
| `alignhcm-legal-review` | Not found | Same |
| `alignhcm-weekly-sales-report` | Not found | Same |
| `alignhcm-monthly-forecast-review` | Not found | Same |

The composition table in `SKILL.md` already names all six, so the pointer from
this package outward is in place. What remains is the pointer inward, from each
of those skills back to this one.

`rfp-responder` cannot be edited from this repository: it is an account skill,
synced read-only into the session, and a local edit would be overwritten on the
next sync. It has to be edited wherever account skills are managed.

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
