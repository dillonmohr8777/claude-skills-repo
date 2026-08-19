# Align HCM company facts

review_by: 2027-02-19

The numbers every client-facing document uses. One file, because they currently
disagree in documents that already went to prospects.

## Why this file exists

Two decks shipped in 2026 with different facts about the same company:

| Fact | Partner introduction deck | Proposal deck |
|---|---|---|
| Team size | 60+ certified team members | 100+ Aligners |
| Reviews | 4.9 / 5 across 115+ reviews | 111 reviews & 4.9 / 5 |
| Projects | 300+ projects delivered | not stated |

Both are Align documents. Both went to prospects. A reader who saw both would
notice. Every skill that produces a client-facing document pulls from the table
below instead of from whichever deck the author happened to copy.

## Canonical values

| Token | Value |
|---|---|
| `FOUNDED` | 2018 |
| `HQ` | St. Petersburg, Florida |
| `SECOND_OFFICE` | Toronto, Ontario |
| `GEOGRAPHIES` | United States, Canada, and the Philippines |
| `TEAM_SIZE` | 100+ |
| `TEAM_DESCRIPTOR` | certified team members across the US, Canada, and the Philippines |
| `CUSTOMERS_SERVED` | 200+ |
| `PROJECTS_DELIVERED` | 300+ |
| `CLIENT_RATING` | 4.9 / 5 |
| `REVIEW_COUNT` | 115+ |
| `RATING_SOURCE` | independently verified by Raven Intelligence |
| `ACADEMY_INVESTMENT` | $2.0M+ |
| `GROWTH` | 30%+ year over year, organic |
| `UKG_STATUS` | UKG Certified Implementation and Services Partner |
| `DAYFORCE_STATUS` | Dayforce Certified Implementation and Managed Services Partner |
| `UKG_AWARD` | UKG White Glove Service and Collaboration Partner of the Year |
| `FOUNDER` | Maher El-Abdallah, Co-Founder and CEO |
| `FOUNDER_CREDENTIAL` | led Dayforce's own Services organization as VP of Implementation from 2011 to 2014 |
| `ESCALATION_PATH` | project manager, then practice lead, then our President and COO |
| `WEBSITE` | alignhcm.com |

> **`TEAM_SIZE` and `REVIEW_COUNT` are the two contested values.** The larger,
> more recent figure is used here. The brand owner should confirm both, and set
> a new `review_by` date when they do.

## Where these numbers came from

- Partner introduction deck for a senior living prospect, August 2026
- Phased UKG optimization proposal, February 2026
- Align Academy PM onboarding deck, May 2024

## The rule

Never type one of these numbers into a document by hand. If a document needs a
fact that is not in this table, add it here first, then use it. That is how the
table stays the single source rather than becoming a fourth version.
