# SOW spec reference

Every field the builder reads. Required fields are marked; everything else has
Align's standard language as a default.

## Required

| Field | Type | Notes |
|---|---|---|
| `client_legal_name` | string | The signing entity's legal name, not the trading name. It goes on the signature page |
| `platform` | string | `UKG Pro`, `UKG Pro WFM`, `Dayforce`, `HiBob`, `Paylocity` |
| `engagement_title` | string | `Full Suite Launch`, `Managed Payroll`, `Leave Assessment` |
| `align_entity` | string | Exactly `Align HCM, Inc.` or `Align HCM Services LLC`. Nothing else is accepted |
| `pricing_model` | string | `fixed_fee` or `time_and_materials` |
| `scope_items` | array | One entry per application in scope, each with `application` and a non-empty `assumptions` list |

### `scope_items`

```json
{"application": "UKG Pro Workforce Management (Timekeeping and Accruals)",
 "assumptions": [
   "Configure up to 6 employee pay rules.",
   "Configure up to 4 accrual policies.",
   "Provide setup and advisory guidance for up to 5 data collection devices.",
   "Load accrual balances once during testing and once for go-live."]}
```

Write limits as numbers. "Configure pay rules" is a promise without a boundary;
"configure up to 6 employee pay rules" is a scope line. The builder rejects an
application with an empty assumptions list for exactly this reason.

## Pricing

### Fixed fee

```json
"pricing_model": "fixed_fee",
"milestones": [
  {"label": "Contract Execution", "amount": 1000},
  {"label": "Month 2 Fees", "amount": 89750},
  {"label": "Month 3 Fees", "amount": 89750}
]
```

### Time and materials

```json
"pricing_model": "time_and_materials",
"rate": 200,
"workstreams": [
  {"name": "Core HR and Payroll", "hours": 900},
  {"name": "Workforce Management", "hours": 900}
]
```

Either way the total is summed by the builder. `expected_total` is checked
against it and fails the build on a mismatch.

## Optional

| Field | Type | Default |
|---|---|---|
| `currency` | string | `USD`. `CAD` renders `CA$` throughout |
| `expected_total` | number | Unset. Set it to what the deal team agreed |
| `pricing_valid_through` | string | Unset, and warned about. A quote with no expiry can be executed months later at stale rates |
| `change_order_rate` | number | Unset. Adds the hourly change-order rate line to section 10 |
| `client_details` | object | Any of `licensed_employees`, `target_start`, `target_go_live`, `business_numbers`, `provinces`, `union_cbas`, `countries`, `locations`, `clocks`, `legacy_systems` |
| `show_all_client_details` | bool | `false`. When true, unfilled rows render as "To be confirmed" rather than being omitted |
| `launch_parameters` | array | `[{"item": ..., "detail": ...}]` for training, change management, data conversion, dual maintenance, integrations, travel |
| `phase_deliverables` | array | `[{"phase": ..., "align": [...], "client": [...]}]` |
| `out_of_scope` | array | `[{"item": ..., "detail": ...}]`, appended to the five standard exclusions |
| `additional_terms` | array of strings | Appended to the nine standard terms |
| `scope_summary` | string | The framing paragraph above the application list |
| `methodology_framing` | string | The paragraph above the launch phase table |
| `investment_notes` | string | Small muted note under the fee table |
| `status` | string | `Draft for review` |
| `date` | string | Today, formatted `August 2026` |
| `forbid_terms` | array of strings | Extra names the residue scan must not find. Use it when reworking a spec copied from another deal |

## Worked example

```json
{
  "client_legal_name": "Northwind Traders, Inc.",
  "align_entity": "Align HCM Services LLC",
  "platform": "UKG Pro",
  "engagement_title": "Full Suite Launch",
  "pricing_model": "fixed_fee",
  "currency": "USD",
  "pricing_valid_through": "31 December 2026",
  "change_order_rate": 225,
  "expected_total": 360000,
  "client_details": {
    "licensed_employees": 650,
    "target_start": "March 2027",
    "target_go_live": "January 2028",
    "countries": 2,
    "locations": 14,
    "legacy_systems": "ADP Workforce Now"
  },
  "scope_items": [
    {"application": "UKG Pro Pay and People Center - US",
     "assumptions": [
       "Implement HR, Payroll, Benefits, ESS/MSS, and standard interfaces.",
       "Support one launch of UKG Pro Pay and UKG Pro People Center."]},
    {"application": "UKG Pro Workforce Management (Timekeeping and Accruals)",
     "assumptions": [
       "Configure up to 6 employee pay rules.",
       "Configure up to 4 accrual policies."]}
  ],
  "launch_parameters": [
    {"item": "Data Conversion",
     "detail": "1 x Employee Master File Conversion and 2 x Payroll Balance Conversion per region."}
  ],
  "milestones": [
    {"label": "Contract Execution", "amount": 1000},
    {"label": "Month 2 Fees", "amount": 89750},
    {"label": "Month 3 Fees", "amount": 89750},
    {"label": "Month 4 Fees", "amount": 89750},
    {"label": "Month 5 Fees", "amount": 89750}
  ]
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Written and clean |
| 2 | Written, but a check failed. The file is left so you can look at it |
| 3 | The spec is incomplete or contradictory. Nothing is written |
