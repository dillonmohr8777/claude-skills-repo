# The thirteen sections, and why each exists

This is not an invented skeleton. It is Align's real SOW template, section for
section, from `AlignHCM-Sales/Shared Documents/General/1 - All Things Sales/
Templates/SOWs/Align HCM UKG Pro Launch SOW Template v1.docx`, cross-checked
against executed contracts for World Central Kitchen, Interfor, CHFA, Ashley
Furniture, and Redberry.

Knowing what each section is for makes it obvious which need real attention per
deal and which take the standard language.

| # | Section | Purpose | Per-deal attention |
|---|---|---|---|
| - | Preamble | Names the parties and subordinates the SOW to the MSA. Also states the pricing model and the change-order gate | Fixed |
| 1 | Client Details | Licensed employees, target dates, BNs, provinces, CBAs, countries, locations, clocks, legacy systems | **High** |
| 2 | Services in Scope | Which applications are being implemented | **High** |
| 3 | Service Assumptions | Per application, exactly what Align will do and to what limit | **Highest** |
| 4 | Project Management Process | Planning, schedule, action log, status meetings, risk, closure | Fixed |
| 5 | Launch Methodology | WELCOME, REQUIREMENTS, BUILD, TEST, GO-LIVE | Fixed |
| 6 | Launch Parameters | Training, change management, data conversion, dual maintenance, integrations, travel | **High** |
| 7 | Roles, Responsibilities, and Deliverables | Per phase, what Align delivers and what the Client delivers | Medium |
| 8 | Resources | Named Align roles and named Client roles | Fixed |
| 9 | Out of Scope | Customizations, non-platform hardware, training, vendor requests, translations, plus anything deal-specific | Medium |
| 10 | Change Requests | Change order rate, go-live push cost, post-signoff design and build changes | **High** |
| 11 | Additional Terms | Working location, standard hours, the sign-off escalation clock, vendor coordination, travel | Fixed |
| 12 | Fees, Payment Terms, Expenses and Billing | The money, plus the IP assignment and the pricing expiry | **High** |
| 13 | Acknowledgements | MSA precedence and the signature blocks | Fixed |

## Section 3 is the document

Every quantity in Service Assumptions is a future change order avoided. The real
template writes limits explicitly: "configure up to 5 attestation workflows each
containing up to 4 questions", "up to 20 data views", "1 x Employee Master File
Conversion and 2 x Payroll Balance Conversion per region". A scope line without
a number is a scope line the client will read generously.

The builder refuses an application listed in scope with an empty assumptions
list, for that reason.

## Two legal entities, and the tool will not guess

Align signs as **Align HCM, Inc.** or **Align HCM Services LLC**. Both appear in
executed contracts. Which one applies is a legal decision that depends on the
contracting arrangement, so `align_entity` is required and validated against
exactly those two strings. A near-miss such as "Align HCM Services, LLC" is
rejected rather than quietly printed onto a signature page.

## Load-bearing sentences

Five sentences do the legal work. The self-test asserts each one survives into
the rendered file:

1. The SOW is subject to the Align Master Services Agreement or other existing
   underlying agreement.
2. Additional work proceeds only after a supplemental Change Order approved in
   advance.
3. Where the MSA and the SOW conflict, the MSA prevails.
4. Work product becomes the Client's property effective upon payment.
5. Sign-off escalates after five business days and is deemed accepted two
   business days after that.

Losing any of them produces a document that reads fine and protects nobody.

## Phase names differ from the PM runbook on purpose

A SOW uses the UKG Launch labels: WELCOME, REQUIREMENTS, BUILD, TEST, GO-LIVE.
`alignhcm-pm-runbook` uses Align's internal five-phase names: Project Readiness,
Analysis and Design, Configuration and Build, Acceptance and Parallel Testing,
Go-Live and Transition. They map one to one. Do not "fix" one to match the other.

## What this document is not

It is not the proposal. The proposal argues; the SOW records what was agreed. If
the SOW's scope and fees do not match the accepted proposal, one of the two is
wrong, and it is worth finding out which before signature rather than after.
