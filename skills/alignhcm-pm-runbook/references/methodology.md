# Align HCM project methodology

Compiled from the Align Academy PM onboarding deck. This is what Align actually
does, not a generic PMI summary.

## The five phases

| Phase | Align team | Client team |
|---|---|---|
| **Project Readiness / Planning** | Sales-to-service transition, welcome call, readiness meetings, review approach and roles, establish system access, define meeting cadence, review the requirements-gathering process, conduct kickoff | Review the SOW, complete the pre-analysis requirements exercise, gather and provide requested documentation |
| **Analysis and Design** | Lead the client in defining business processes and rules, recommend solution design, create scope design documents | Participate in analysis meetings, define processes and rules, facilitate rapid review, feedback, and sign-off |
| **Configuration and Build** | Share configuration responsibilities with the client, knowledge transfer, facilitate integration needs, review configuration with client SMEs, complete internal configuration QA | Manage downstream and upstream vendors, sign off on configuration, sign off on data conversion |
| **Acceptance and Parallel Testing** | Support the client through test execution, coordinate test results, manage and deliver fixes, provide input to change management and train-the-trainer | Participate in test planning, assist with test cases for unique requirements, participate in UAT, sign off on testing |
| **Go-Live and Support Transition** | Provide production and post-live support, transition to ongoing support, perform project wrap-up | Deliver end user training, finalize the open issues list, deliver people data and opening balances |

## Client level of effort by phase

This belongs in the SOW and the kickoff, because schedule risk follows directly
from availability. Understating it is the most common cause of a slipped
go-live.

| Workstream | Analysis | Build | System test | Parallel | Go-live |
|---|---|---|---|---|---|
| HR / Payroll | 10+ hrs/wk | 10+ | 10+ | 20+ | 20+ |
| Workforce Management | 10+ | 10+ | 20+ | 20+ | 20+ |
| Benefits | 10+ | 10+ | 10+ | 10+ | 10+ |
| Data Conversion | 20+ | 20+ | 20+ | 20+ | 20+ |
| Integration | 15+ | 15+ | 15+ | 20+ | 20+ |
| Payment Services | 3+ | 5+ | 3+ | 5+ | 5+ |

## Phase dependencies that stop a project

Each of these is a hard gate. A phase that opens before its dependency is met
is the most reliable way to lose the timeline.

- **Build** requires requirements signed off and the launch data collection tool
  complete.
- **System test** requires configuration completed and signed off, and test data
  files received.
- **Parallel test** requires dual maintenance complete, and authorization to
  proceed to testing signed off.
- **Go-live** requires UAT signed off, final data conversion complete and signed
  off, and the Go/No-Go readiness decision.
- **Integration go-live** additionally requires vendor and client approval to
  move the file to production, and respects vendor SLAs and blackout periods.
- **Payment Services** requires all tax jurisdictions registered, the bank
  authorization in place, POAs signed, and the company tax profile reviewed and
  returned.

## Client sign-offs

Different depending on whose paper the project runs on. See
`paper-differences.md`. On Align paper the list is: Pro requirements, WFM
requirements, Pro configuration, initial data conversion for people, initial
data conversion for opening balances, UAT 1, UAT 2, WFM authorization to proceed
to cutover, final data conversion, WFM authorization to proceed to go-live.

## Quality assurance

Pro configuration QA, Pro system test QA, Pro final QA, tax team QA, WFM
business structure approval, and WFM deployment review. The PM schedules each,
confirms the passing score before the next phase opens, and submits the
deployment review case seven days before the first punch date.

## The process before the project

| Step | Who drives | When | Tool |
|---|---|---|---|
| Sale closed | Sales rep | On signature | Contracting, CRM update |
| Client welcome | Sales rep | Within 3 days | Welcome email, first steps guide |
| Internal sales transition | Sales rep and practice lead | Within 7 days | Internal transition deck |
| Client sales transition | PM schedules, sales introduces | Within 2 weeks | Transition deck |
| Readiness workshops | PM | Within 3 weeks, or 1 week before kickoff | Workshop decks |
| Kickoff | PM | Per plan | Kickoff deck |

Readiness is two to three one-hour workshops covering best practices, training,
testing, data and integrations, and risks. The client starts gathering
requirements after the first session, and carries action items out of each one.

## Known challenges, and what works

| Challenge | What actually helps |
|---|---|
| Complex deployments stretch client bandwidth | Discuss resources, level of effort, and contingencies before signature, not at kickoff |
| Product-to-product integration is hard to troubleshoot | Discuss the integration timeline early; name which elements are quick wins and which need more time |
| Additional testing responsibilities land on the client | Have team members collaborate during testing so the end-to-end process is exercised |
| Client training does not get completed | Set expectations at readiness and kickoff about what training is required and by when. Be honest that this is a real challenge |
