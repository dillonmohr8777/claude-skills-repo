# Align HCM company facts

review_by: 2026-11-19

The numbers every client-facing document uses. One file, because they currently
disagree in documents that already went to prospects.

## Why this file exists

Documents that have all shipped, all from Align, all about Align:

| Fact | Jamieson RFP response (Apr 2026) | Hemlo / master template (Jun-Jul 2026) | Homewood company bio (Aug 2026) |
|---|---|---|---|
| Headquarters | Toronto, with an additional office in St. Petersburg | not stated | St. Petersburg, with a second office in Toronto |
| Team size | 100+ full-time professionals | 75+ certified HCM and Dayforce experts | 60+ employees |
| Geography | Canada and the US, plus a small international group including the Philippines | not stated | "all work in the United States and Canada", "100% onshore" |
| Reviews | not stated | not stated | 4.9 / 5 across 115+ reviews |
| Customers | 200+ | not stated | 200+ |
| Engagements | 300+ | not stated | 300+ |

A prospect who saw two of these would notice. A prospect who saw the RFP answer
and the company bio would notice something worse: they disagree about whether
any delivery happens outside North America.

## Canonical values

Status meanings: **verified** means two or more independent Align documents
agree. **single source** means one document says it and nothing contradicts it.
**contested** means shipped Align documents disagree, and the builders refuse to
render it into a client-facing file until someone rules.

| Token | Value | Status |
|---|---|---|
| `FOUNDED` | 2018 | verified |
| `OFFICES` | St. Petersburg, Florida and Toronto, Ontario | verified |
| `TEAM_CLAIM` | a certified delivery team across Canada and the United States | verified |
| `DELIVERY_MODEL` | primarily onshore-led, with a small international group supporting specific functions | single source |
| `RATING_CLAIM` | 4.9 / 5, independently verified by Raven Intelligence | verified |
| `HQ` | St. Petersburg, Florida | contested |
| `SECOND_OFFICE` | Toronto, Ontario | contested |
| `GEOGRAPHIES` | the United States and Canada | contested |
| `TEAM_SIZE` | 100+ | contested |
| `TEAM_DESCRIPTOR` | full-time professionals across Canada and the United States | contested |
| `CUSTOMERS_SERVED` | 200+ | verified |
| `PROJECTS_DELIVERED` | 300+ | verified |
| `ON_TIME_RATE` | 85% of projects delivered on the original timeline | single source |
| `CLIENT_RATING` | 4.9 / 5 | verified |
| `REVIEW_COUNT` | 115+ | contested |
| `RATING_SOURCE` | independently verified by Raven Intelligence | verified |
| `ACADEMY_INVESTMENT` | $2.0M+ | single source |
| `GROWTH` | 30%+ year over year, organic | single source |
| `UKG_STATUS` | UKG Certified Implementation and Services Partner | verified |
| `DAYFORCE_STATUS` | Dayforce Certified Implementation and Managed Services Partner | single source |
| `UKG_AWARD` | UKG White Glove Service and Collaboration Partner of the Year | single source |
| `FOUNDER` | Maher El-Abdallah, Co-Founder and CEO | verified |
| `FOUNDER_CREDENTIAL` | led Dayforce's own Services organization as VP of Implementation from 2011 to 2014 | single source |
| `ESCALATION_PATH` | project manager, then practice lead, then our President and COO | verified |
| `TYPICAL_ENGAGEMENT` | CAD $150,000 to $1,500,000 depending on scope and complexity | single source |
| `WEBSITE` | alignhcm.com | verified |

## Default formulations, which is why builds still pass

Blocking every document until someone rules would turn a documentation dispute
into an outage. Instead the builders default to formulations that are true under
every source, and leave the disputed numbers unused:

| Instead of | The builders use | Why it is safe |
|---|---|---|
| `HQ` and `SECOND_OFFICE` | `OFFICES` | Every source agrees both offices exist. Only which one is "headquarters" is disputed, and a client deck does not need to say |
| `TEAM_SIZE` and `TEAM_DESCRIPTOR` | `TEAM_CLAIM` | True whether the team is 60, 75, or 100. A headcount that three documents disagree on is worth less than the claim it supports |
| `GEOGRAPHIES` | `DELIVERY_MODEL` | The RFP's own wording, which is compatible with everything except the banned onshore claim |
| `REVIEW_COUNT` | `RATING_CLAIM` | The rating is stable and verified. The count only goes up, so any number stated without a date is already stale |

The contested tokens stay in the table. A builder that reads one fails with the
disagreement printed, so using a disputed number is a deliberate act with
`--allow-contested` rather than an accident.

## The four contested values, and what has to be decided

**Headquarters.** The Jamieson RFP response says Align is headquartered in
Toronto with an additional office in St. Petersburg. The Homewood company bio
says the reverse. Both were written in 2026. One of them is wrong on a fact that
appears on contracts and in vendor-registration forms.

**Team size.** 100+ full-time professionals in April, 75+ certified experts in
June, 60+ employees in August. These may be three different metrics rather than
a shrinking company: employees, certified consultants, and "Aligners" are not
necessarily the same population. If so, say which metric each number counts.
Right now the documents use them interchangeably.

**Geography and the onshore claim.** The RFP response discloses "a small group
of international team members, including in the Philippines, who support
specific functions" and describes delivery as "primarily onshore-led". The
company bio, four months later, says employees "all work in the United States
and Canada" and that delivery is "100% onshore, with no handoff to another
region at any phase". These cannot both be true. The RFP answer is the more
carefully written of the two and the one a client could hold Align to.

**Review count.** 111 in one deck, 115+ in another. Raven Intelligence publishes
the real number and it only goes up, so this needs a date attached, not just a
value.

## Claims these skills will never generate

Some sentences are not facts to be corrected but claims to be avoided until the
underlying question is settled. The builders scan output for these and fail.

| Phrase | Why |
|---|---|
| `100% onshore` | Contradicted by Align's own RFP disclosure of Philippines-based team members |
| `no handoff to another region` | Same |
| `all onshore` | Same |
| `entirely in the United States and Canada` | Same |

If Align's delivery model changes, or the RFP answer was wrong, remove the row
and record which document settled it.

## Where these numbers came from

- Align HCM response to the Jamieson Wellness HRIS RFP, April 2026, Schedule A
- Align HCM company bio prepared for Homewood Living Ministries, August 2026
- Hemlo Mining Dayforce optimization proposal, June 2026
- Align HCM new master template, July 2026
- Align Academy PM onboarding deck, May 2024

## The rule

Never type one of these numbers into a document by hand. If a document needs a
fact that is not in this table, add it here first, then use it. That is how the
table stays the single source rather than becoming a fourth version.
