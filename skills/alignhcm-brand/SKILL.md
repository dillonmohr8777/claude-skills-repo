---
name: alignhcm-brand
description: DEPRECATED. Superseded by `alignhcm-brand-system`, which consolidates Align HCM brand tokens, the PowerPoint master template system, carousel and motion specs, and voice rules into one package. Use `alignhcm-brand-system` instead.
---

# Deprecated — use `alignhcm-brand-system`

This skill has been folded into **`alignhcm-brand-system`**.

## Why

It was pointer-only. It instructed the reader to load
`C:\Users\DillonMohr\.claude\clients\align-hcm\brand.md`, which does not exist
in any repository and was independently recorded as missing on 2026-07-16 in
`align-hcm-august-2026-content/master-template-reference/SOURCE-NOTES.md`.

The usable tokens carried in its prose have been salvaged into the new package,
reconciled against production files, and split by surface — because the single
`#FF6B2B` "primary" this skill named is in fact the *blog* accent, not the web,
deck, social, or motion orange.

It also noted that a deck skill was still "pending". That gap is now closed.

## Where things went

| Was here | Now |
|---|---|
| Colour tokens | `alignhcm-brand-system/references/tokens.md` |
| Signature effects | `alignhcm-brand-system/references/carousel-and-motion.md` |
| Voice rules | `alignhcm-brand-system/references/voice-and-copy.md` |
| Deck system (was pending) | `alignhcm-brand-system/references/powerpoint-deck-system.md` |
| Audit of what conflicted | `alignhcm-brand-system/references/provenance-and-conflicts.md` |

Safe to delete once nothing references the old name.
