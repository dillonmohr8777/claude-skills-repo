# Output Templates

Consistent formats for the agent's responses. Fill from live data; never invent values. Keep customer PII in the conversation (not in any saved file). In BUILD mode, any action ends in the **Proposed Write** block.

---

## 1. Ticket triage summary

```
🎫 Ticket #<id> — <subject>
Account:    <company> · Contact: <name> (<email>)
Source:     <Chat|Email|Form|Phone>   Opened: <date>
——
Classify:   Category <…>  ·  Priority <LOW|MEDIUM|HIGH|URGENT>
Route:      <owner/queue + why>
Stage:      <current> → <proposed>
Context:    <1–3 lines from customer-360: open deals, past tickets, health>
Next:       <reply / internal note / follow-up task>
```

---

## 2. Ticket reply draft (customer-facing)

```
Subject: Re: <subject>

Hi <first name>,

<Acknowledge the issue in one line.>
<What we found / what we're doing — grounded in the record.>
<Clear next step + realistic timeframe. No over-promising.>

<If waiting on them: the specific thing you need.>

Best,
<Owner name> — Align HCM
```
Voice: professional, warm, concise. Pull exact tone tokens from `alignhcm-brand` for polished customer copy.

---

## 3. Customer-360 brief

```
🏢 <Company>  ·  <industry>  ·  Owner: <owner>
   Lifecycle: <stage>   Type: <type>   NA2: <record URL>

👥 Contacts (<n>)
   • <name> — <title> — <email>  (primary)
   • …

💼 Deals
   Open:   <name> — <stage> — $<amount> <cur> — close <date>
   History:<renewals / change orders / closed won-lost>

🎫 Support
   Open <n> / Closed <n>   Highest priority open: <…>

🕑 Recent activity
   • <date> <note/call/email/meeting one-liner>

❤️ Health: <Green|Yellow|Red> — <one-line why>
▶️ Next best action: <…>
```

---

## 4. Health / renewal-risk summary (per account or portfolio)

```
Account        Health   Open tickets   Renewal        Signal
<company>      🟡       1 (aging)      in 60d, Qual   thin multi-threading
<company>      🔴       2 (1 URGENT)   past close     escalation open
<company>      🟢       0              —              recent QBR, engaged
```
Portfolio note: for weighted scoring across many accounts, feed the assembled per-account JSON to the `customer-success-manager` skill's tools.

---

## 5. SmartCare onboarding status

```
🚀 <Company> — SmartCare <tier>
   Advisor: SmartCare Advisor (162168981)   Go-live: <date>
   Stage:   <onboarding stage>   Next milestone: <… by date>
   Open:    <tickets/tasks>      Last touch: <date>
   Status:  <On track | Watch | Stalled>  — <why>
   Next:    <proposed action>
```

---

## 6. Proposed Write block (BUILD-mode action contract)

```
### ⏸ Proposed Write (held — BUILD mode)
- Action:        <create | update | associate | send>
- Object:        <TICKET 12345 | NOTE on COMPANY 678 | TASK for owner …>
- Tool:          manage_crm_objects (would be called)
- Changes:
    <property>: <old> → <new>
- Draft content: |
    <full body, ready to run>
- Why:           <one-line rationale from the record>
- To execute:    say "run this" (requires LIVE mode)
```

Multiple actions → one block each (or a compact table). Nothing executes implicitly.
