# SOW spec reference

Every field the build reads. Required fields are marked.

## Required

| Field | Type | Notes |
|---|---|---|
| `client_legal_name` | string | The legal entity, not the trading name. This is a contract |
| `align_entity` | string | `Align HCM Services, LLC` or `Align HCM Inc.`, matching the governing agreement |
| `platform` | string | `Dayforce`, `UKG Pro`, `UKG WFM`, `HiBob`, `Paylocity` |
| `engagement_title` | string | `Full Suite Launch`, `Managed Payroll`, `UKG to Dayforce Migration` |
| `rate` | number | Blended hourly rate |
| `workstreams` | array | At least one. Each needs `name`, `hours`, `description`; `deliverables` is optional |

## Strongly recommended

| Field | Type | Why |
|---|---|---|
| `expected_total` | number | The build fails if the workstream table does not reach it. This is the check that catches the error a client always finds |
| `scope_summary` | string | One sentence naming the platform, the modules, and what is being migrated from |
| `investment_notes` | string | Assumption caveats. A number without its assumptions gets quoted back at you |
| `forbid_terms` | array | Extra names to treat as residue, for example the incumbent vendor or a sister entity |

## Optional overrides

Each has an Align default. Override when the deal differs.

| Field | Type |
|---|---|
| `align_responsibilities` | array of strings |
| `client_responsibilities` | array of strings |
| `assumptions` | array of strings |
| `term` | string |
| `status` | string, defaults to `Draft for review` |
| `date` | string, defaults to the current month and year |

## Worked example

```json
{
  "client_legal_name": "Northwind Traders, Inc.",
  "align_entity": "Align HCM Services, LLC",
  "platform": "Dayforce",
  "engagement_title": "Full Suite Launch",
  "date": "September 2026",
  "status": "Draft for review",
  "rate": 200,
  "expected_total": 360000,
  "scope_summary": "Align will implement Dayforce HCM, Payroll, and Workforce Management for Northwind Traders, migrating from ADP Workforce Now.",
  "workstreams": [
    {
      "name": "Core HR and Payroll",
      "hours": 680,
      "description": "Company structure, demographics, pay and tax codes, and payroll configuration through two parallel cycles.",
      "deliverables": [
        "Configured company structure and org levels",
        "Pay and tax code configuration",
        "Two parallel payroll cycles"
      ]
    },
    {
      "name": "Workforce Management",
      "hours": 880,
      "description": "Time collection, pay rules, pay groups, accruals, and business structure alignment with Payroll."
    },
    {
      "name": "Data Conversion",
      "hours": 240,
      "description": "Extract, translate, and load employee data from ADP Workforce Now."
    }
  ],
  "investment_notes": "Blended rate across all resource types."
}
```

## Flags

| Flag | Effect |
|---|---|
| `--out-dir` | Where to write. Defaults to the working directory |
| `--allow-invalid` | Keep the document and exit 0 even if validation failed |
| `--no-supersede` | Leave older versions in place instead of moving them to `_superseded/` |
| `--json` | Print a machine-readable summary after the human one |
