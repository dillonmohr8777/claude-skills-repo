# SmartCare tiers

SmartCare is Align's post-go-live service line. Two naming systems are live at
the same time, and one client-facing deck already ships both at once.

## What the sources actually say

| Source | Date | Names used |
|---|---|---|
| `SmartCare Services Catalog - Unified.docx` (Sales, General) | March 2026 | Stabilize (recovery engagement) · **Essentials · Accelerate · Transform** (ongoing plans) |
| `SmartCare Services Overview- Unified v4.docx` (New Rep Training) | June 2026 | Same as the catalog |
| `Align_HCM_SmartCare_Proposal_City of Portsmouth.pptx` (client-facing) | August 2026 | **Stabilize · Optimize · Optimize Plus** |
| `AlignHCM-Company-Bio-Homewood-Living-Ministries.docx` (client-facing) | August 2026 | **Stabilize · Optimize · Optimize Plus** |

Two corrections to what was previously recorded here:

**"Thrive" is not a tier.** It is the second half of the catalog's cover
tagline, "Stabilize. Optimize. Thrive." Reading it as a tier name invented a
third conflict that does not exist.

**"Stabilize" is not a peer of the others.** In the catalog it is a time-bound
recovery engagement: six months, roughly 20 hours per week, about 480 hours,
fixed fee, for organizations within about twelve months of launch or recovering
from system neglect. The catalog is explicit that it is "not a required starting
point" and that clients who do not need recovery begin directly on an ongoing
plan. Presenting it as tier one of three misdescribes what is being sold.

## The live defect

The August 2026 City of Portsmouth proposal contains both vocabularies. Its
overview slide offers "Stabilize / Optimize / Optimize Plus", and a later slide
lifted from the catalog describes Stabilize as a recovery engagement whose
clients "typically transition into Optimize or Optimize Plus" where the catalog
says Essentials, Accelerate, or Transform. The same deck also misspells the tier
as "Stablize" twice.

That is the failure worth preventing. Which vocabulary Align chooses is a
commercial decision; a single document using both is a defect under either
choice, because the deck and the catalog that sets pricing, hour bands, and exit
terms then describe different products.

## What this skill renders

The **client-facing vocabulary**, because that is what two independent August
2026 documents put in front of clients and this deck is client-facing.

| Tier | When it applies | What it covers |
|---|---|---|
| Stabilize | The first months after go-live, or recovery from a period of system neglect. Time-bound: about six months at roughly 20 hours per week | Close out what the first live payroll cycles surface, resolve configuration gaps, remediate security, document the system as built, and get your administrators self-sufficient. Named account manager, project manager, and SMEs, with weekly status tracking. |
| Optimize | Steady-state operation | Everything in Stabilize, plus monthly performance and adoption reviews, daily support ticket management, weekly office hours, a key events calendar, and quarterly business reviews covering tax variance and security roles. |
| Optimize Plus | Added capacity, not just coverage | Everything in Optimize, plus proactive release management, new module implementation and activation, managed services where our team runs payroll, HRIS, or WFM operations alongside yours, and an annual executive business review with a one to three year platform roadmap. |

Every SmartCare engagement includes a dedicated executive sponsor, project
manager, and advisor, available Monday through Friday. Engagements are
hours-based and move between tiers as the client matures.

## Mixing is a build failure

The builder reads this table and checks the names against both known
vocabularies. If a row from one generation appears alongside a row from the
other, the build fails rather than shipping a Portsmouth-style deck. Stabilize
is allowed in either, because it means the same thing in both.

## To change this

Edit the table above. The build script reads it rather than carrying tiers in
code, so a decision reaches every deck without a code change. If the ruling is
to adopt the catalog vocabulary, replace all three rows with Essentials,
Accelerate, and Transform, keep or drop Stabilize as a separate recovery
engagement, and the vocabulary check will accept it.

Whichever way it goes, the catalog and the client decks need to end up saying
the same thing. Right now they do not, and the pricing, hour bands, rollover
terms, and exit terms all live in the catalog.
