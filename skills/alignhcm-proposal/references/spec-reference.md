# Proposal spec reference

## Required

| Field | Type | Notes |
|---|---|---|
| `client_name` | string | Trading name is fine here; this is not a contract |
| `platform` | string | `UKG Pro`, `Dayforce`, `HiBob`, `Paylocity` |
| `engagement_title` | string | `Optimization Program`, `Full Suite Launch` |
| `rate` | number | Blended hourly rate |
| `current_state` | array | At least two categories. Each needs `category` and `items` |
| `phases` | array | At least one. Each needs `name`, `window`, `hours`, `summary` |
| `contact` | object | `name`, and ideally `title` and `email` |

`current_state` needs two categories because one bullet of discovery is not
discovery, and the section is what separates a proposal from a brochure.

## Phase fields

| Field | Required | Notes |
|---|---|---|
| `name` | yes | `Phase 1: CBAs and Total Rewards` |
| `window` | yes | `Mar - Jul 2026` |
| `hours` | yes | Drives the investment table |
| `summary` | yes | Used when the phase has no workstreams |
| `workstreams` | no | Array of `{name, detail}`. Renders as a card grid |
| `deliverables` | no | Array of strings. Feeds the deliverables table |

## Optional

| Field | Type | Notes |
|---|---|---|
| `expected_total` | number | Build fails if phase hours do not reach it |
| `drivers` | array of `{title, detail}` | Why now |
| `risks` | array of `{title, detail}` | Named honestly, it builds credibility |
| `outcomes` | array of `{value, label}` | Big-number outcome cards |
| `next_steps` | array of `{what, when}` | Renders as a table |
| `why_us` | array of `{title, detail}` | Has an Align default |
| `investment_notes` | string | Assumption caveats |
| `approach_framing`, `current_state_framing` | string | Section divider framing lines |
| `closing_title`, `closing_body` | string | Final slide |
| `date` | string | Defaults to current month and year |
| `forbid_terms` | array | Extra residue terms |

## The arithmetic

The investment table is computed as hours times rate per phase, then totalled.
You cannot produce a proposal whose phases disagree with its total. Set
`expected_total` to the agreed number and the build fails if the phases do not
reach it.

## Flags

| Flag | Effect |
|---|---|
| `--out-dir` | Where to write |
| `--allow-invalid` | Keep the deck and exit 0 despite validation failure |
| `--no-supersede` | Leave older versions in place |
| `--json` | Machine-readable summary |
