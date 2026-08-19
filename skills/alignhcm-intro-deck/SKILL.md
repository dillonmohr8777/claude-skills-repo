---
name: alignhcm-intro-deck
description: Generate the Align HCM partner introduction deck for a new prospect as a branded 15-slide PowerPoint. Use whenever a new deal needs a company introduction, capabilities overview, partner intro, "who is Align HCM" deck, or first-meeting presentation, on any platform (Dayforce, UKG Pro, UKG WFM, HiBob, Paylocity) and in any sector. Builds the fixed Align narrative (who we are, why implementations fail, our methodology, governance, change management, SmartCare, why us) around the three sections that must be rewritten per prospect. Do not use for a priced proposal (use alignhcm-proposal) or a contract (use alignhcm-sow).
---

# Align HCM partner introduction deck

The deck that goes out with every new deal. One per prospect: the folder for a
recent one already holds today's version and yesterday's in `/OLD/`.

The narrative order is fixed because it is an argument, not a list. Align earns
the right to talk about methodology by first naming the failure patterns the
prospect has lived through. Reordering it breaks the argument.

## Build one

```bash
python3 scripts/build_intro_deck.py --spec <prospect>.json --out-dir <folder>
```

## Two claims it will not let you make

**A contested company fact.** Align's April 2026 RFP response and its August
2026 company bio disagree about headquarters, team size, and whether any
delivery happens outside North America. The deck therefore states offices
rather than a headquarters, a certified team rather than a headcount, and a
verified rating rather than a review count. Each of those is true under every
source. Reading a disputed value instead fails the build and prints the
disagreement; `--allow-contested` overrides it deliberately.

**That delivery is fully onshore.** Align's own RFP answer discloses team
members in the Philippines. Any wording to the contrary fails the build,
whatever the spec says. The banned phrases are listed in
`scripts/_core/company-facts.md`.

## SmartCare tiers come from a file, and cannot be mixed

`references/smartcare-tiers.md` holds the table the deck renders, so a ruling
reaches every deck without a code change. Two vocabularies are live at Align
right now, the catalog's Essentials/Accelerate/Transform and the client decks'
Optimize/Optimize Plus, and one August 2026 client proposal shipped both at
once. A table drawing from both fails the build. That reference explains the
evidence and what has to be decided.

## The three sections that are actually yours to write

Everything else is Align's standing story and is filled from
`scripts/_core/company-facts.md`. These three make the deck theirs, and the
build refuses to run without them:

| Field | What it is | Why it matters |
|---|---|---|
| `heard_from_team` | What their people told you, in their words | Proves you listened. A generic version of this slide is worse than omitting it |
| `sector` and `sector_proof` | Where Align has depth in their world | Turns a claim into evidence |
| `why_us` | Why Align specifically, for them | The close |

`heard_from_team` needs at least two points and `why_us` at least two. That is a
deliberately low bar that still stops the deck being shipped generic.

### Minimum spec

```json
{
  "client_name": "Northwind Traders",
  "platform": "Dayforce",
  "sector": "Senior Living and Care",
  "heard_from_team": [
    {"title": "One Employee Record, Not Six Systems",
     "detail": "Recruiting, onboarding, HR, and benefits run across disconnected systems today."}
  ],
  "why_us": [
    {"title": "Full-Suite Focus",
     "detail": "We implement end to end, not a single module."}
  ],
  "contact": {"name": "Maher El-Abdallah", "title": "Co-Founder and CEO",
              "email": "maher@alignhcm.com"}
}
```

Optional: `sector_proof`, `sector_framing`, `both_sides`, `closing_title`,
`closing_body`, `date`, `forbid_terms`.

## Slide order

1. Cover
2. Who Is Align HCM
3. The partner who understands both sides
4. Section: What we heard from your team
5. Their priorities **(yours to write)**
6. Section: Why implementations fail
7. Failure patterns and how Align builds against each
8. Section: Depth in their sector
9. Sector proof **(yours to write)**
10. How we implement, five phases
11. Governance and cadence
12. Change management, five stages
13. SmartCare tiers
14. Why organizations like them choose Align **(yours to write)**
15. Close and contact

## SmartCare tiers are contested

Three Align documents name them three different ways: Stabilize/Optimize/Optimize
Plus, Stabilize/Optimize/Thrive, and Stabilize/Essentials/Accelerate/Transform.
Only the first word agrees.

`references/smartcare-tiers.md` records the conflict, states which version this
skill renders and why, and is read at build time. Change the table there and
every future deck follows. Do not hardcode tiers into a spec.

## What it refuses to ship

Another client's name, unresolved placeholders, a deck that never mentions the
prospect, or an off-brand colour. Exits 2 with the reason; `--allow-invalid`
overrides.

Naming and superseding work exactly as in `alignhcm-sow`.

## Marks

Every document carries the exact Align lockup, vendored and SHA-256 pinned, so
a re-exported or substituted logo fails the build rather than shipping. Full
rules, including where a client mark belongs and where it does not:
`scripts/_core/marks.md`.

### The client mark decision cannot be skipped

The build stops until the spec answers whether a prospect or client is
involved:

```json
"client_mark": {"domain": "acme.com"}        fetch, clean, remove background, plate
"client_mark": {"file": "acme-logo.png"}     same pipeline, file you already have
"client_mark": {"ready": "acme-plated.png"}  already pipeline output
"client_mark": "none"                        deliberately none
```

`"none"` is a normal answer. Silence is not, because silence is how a deck goes
out with an empty client panel or the previous prospect's mark still in it.

A fetched mark goes through the brand system's pipeline: background removed,
trimmed, upscaled, contrast measured, then placed on a bordered plate in the
client's own brand colour. It is fitted, never stretched.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_intro_deck.py` | The generator |
| `scripts/_core/marks.md` | Which logo goes on what, and why |
| `scripts/_core/brand-voice.md` | Voice rules every Align document shares |
| `scripts/_core/` | Shared Align document engine, vendored |
| `references/smartcare-tiers.md` | Tier table, read at build time, plus the conflict record |
| `references/narrative.md` | Why the slide order is what it is |
| `scripts/selftest.py` | Proves the documented workflow runs |

## Composition

- **`alignhcm-brand-system`** carries the exact deck master and the client-logo
  plate rule. When the prospect's logo belongs on the cover, fetch it there.
- **`alignhcm-proposal`** is the next document in the deal.
