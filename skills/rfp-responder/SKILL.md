---
name: rfp-responder
description: >
  Use this skill whenever the user wants help responding to an RFI (Request for Information)
  or RFP (Request for Proposal) on behalf of Align HCM. Trigger when the user uploads or
  pastes content that looks like an RFP or RFI, or says things like "help me respond to this
  RFP", "draft an RFP response", "fill out this RFI", "we got an RFP", "respond to this bid",
  "write a proposal response", or "answer these vendor questions". Also trigger when the user
  shares any document containing sections like "Scope of Work", "Vendor Requirements",
  "Evaluation Criteria", or numbered/bulleted questionnaire-style questions directed at a
  potential vendor. This skill produces a polished Word (.docx) response document that mirrors
  the RFP's structure, draws on Align HCM's company facts for boilerplate content, and
  searches SharePoint for relevant past responses to inform section drafts.
---

# RFP / RFI Responder — Align HCM

This skill helps draft professional, accurate responses to RFPs and RFIs on behalf of Align HCM.
It uses a two-layer knowledge base: bundled company facts (always available) and past winning
RFP responses stored in SharePoint (searched at runtime).

---

## Step 0: Load Align brand tokens

Before building the .docx, load the Align brand system:

- `alignhcm-brand-system/references/tokens.md`, the **Formal documents** section
- the bundled Align lockup at
  `alignhcm-brand-system/assets/logos/align-hcm-deck-lockup.png`

Use those tokens for every color and typeface. Do not hardcode hex values here.
Gate the finished file with:

    python3 alignhcm-brand-system/scripts/brand_lint.py --surface document <file>.docx

## Step 0b: Read Company Facts

Before doing anything else, read the bundled reference file:

  references/company_facts.md

This file contains all authoritative facts about Align HCM — company overview, credentials,
methodology, security posture, insurance, DEI policy, and pre-written boilerplate answers to
common RFP questions. Always use this as your primary source. Never invent facts about Align HCM.

---

## Step 1: Parse the RFP

Read the uploaded RFP/RFI document carefully and extract:

1. **Issuing organization** — Who is asking?
2. **Submission deadline** — Note it prominently if present
3. **Scope / context** — What are they implementing or evaluating? What platform(s) are in scope?
4. **Section structure** — List every major section and sub-question. Preserve the original numbering/lettering exactly.
5. **Evaluation criteria** — If stated, note what they're scoring on
6. **Special requirements** — Attachments requested, page limits, formatting rules, certifications needed

Present this summary to the user before drafting, in this format:

  RFP SUMMARY
  Issuing org: [name]
  Deadline: [date or "not stated"]
  Platform in scope: [e.g., UKG Pro, Dayforce, etc.]
  Sections identified: [count]
  Notable requirements: [any flags]

  Proceeding to draft response...

---

## Step 2: Review Past RFP Responses from the Project

Look at the files uploaded to this Project. Any documents that appear to be past RFP or RFI
responses are your reference library — use them to inform your drafting.

For each section of the new RFP, scan the past responses for:
- Similar questions and how Align answered them previously
- Specific language, phrasing, or positioning that worked well
- Examples, case studies, or data points Align has cited before

Use the most relevant 1–3 past responses as guides. Do not copy them verbatim — adapt the
language to fit the new RFP's specific wording and context.

If no past responses are uploaded to the Project, proceed using company_facts.md alone and
let the user know they can upload past winning RFP responses to this Project to improve future
drafts.

---

## Step 3: Draft the Response Section by Section

Work through every section of the RFP in order. For each question or section:

### Source priority:
1. **company_facts.md** — Check for a direct boilerplate answer first. Adapt to the question's wording.
2. **Past SharePoint responses** — Use for tone and phrasing guidance where company_facts.md is thin.
3. **Draft from context** — Write a professional answer consistent with Align HCM's voice and capabilities.
4. **Flag for human input** — If the question requires info you cannot responsibly answer (specific references, custom pricing, named team members, financial statements), leave a clearly marked placeholder:

  [HUMAN INPUT NEEDED: brief description of what's required]

### Tone and positioning guidelines:
- Write in first person plural: "We", "Our team", "Align HCM"
- Professional but warm — confident and specific
- Use real numbers: 4.9/5 Raven Intel with 115+ reviews, 300+ engagements, 60+ employees, 80-85% on-time rate, 72.45% Microsoft Secure Score
- Highlight key differentiators: Align Academy, SmartCare, total project quality approach, onshore-only delivery, client readiness program
- NEVER describe Align as "100% UKG exclusive" — we support UKG, Dayforce, Paylocity, HiBob, Workday, and ADP
- For security questions: reference BEMO partnership, Microsoft Azure infrastructure, 72.45% Secure Score vs. 43.49% industry average
- For DEI/DEIB questions: use the full policy language from company_facts.md
- For certifications: Align follows SOC 2 and ISO 27001 controls but is NOT formally certified — state this accurately

---

## Step 4: Produce the Word Document

Read /mnt/skills/public/docx/SKILL.md before generating the file.

### Document structure:
- **Cover page**: "Response to [RFP Title]" | Submitted by Align HCM | Date | Contact: mike@alignhcm.com
- **Table of contents** (if more than 5 sections)
- **Response body**: Mirror the RFP's section numbering and titles exactly
- **Final section**: "Items Requiring Review Before Submission" — list every [HUMAN INPUT NEEDED] item with its section reference

### Formatting:
- Page size: US Letter, 1-inch margins
- Font: Arial, 11pt body, 14pt H1, 12pt H2
- H1 color: Align orange #E97722
- Body color: Align primary navy #232E3E

These are the audited Align formal-document tokens. Do not substitute other
values. The full palette is in `alignhcm-brand-system/references/tokens.md`
under **Formal documents**.

---

## Step 5: Deliver

Present the .docx file, then provide a brief chat summary:
- Sections drafted vs. flagged for human input
- Any critical flags the user must address before submitting
- One sentence on what to verify before sending

---

## Hard Rules

- Never invent facts about Align HCM
- Never claim certifications Align does not hold (SOC 2 and ISO 27001: follows controls, not certified)
- Never include pricing without explicit user confirmation — rates in company_facts.md may be outdated
- Never describe Align as UKG-exclusive
- For financial statements: write "Available upon request"
- For client references: flag for human input — never fabricate names or contacts

---

## Reference Files

- references/company_facts.md — Authoritative facts, boilerplate answers, insurance, DEI, security
- Project-uploaded files — Past winning RFP responses (upload PDFs or Word docs to this Project)
