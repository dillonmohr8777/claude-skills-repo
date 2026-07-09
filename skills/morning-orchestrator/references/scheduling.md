# Scheduling the Morning Run (unattended steps 1–5)

Goal: the run wakes on its own each morning, completes pre-flight + scouts + board, and sends **one**
push — all before Dillon engages. He only touches it at the approval step.

## What runs unattended vs. what waits

- **Unattended (no human):** wake → pre-flight → parallel scouts → synthesize board → push.
- **Waits for the one approval:** execute Tier-1 batch (parallel tabs) → readback → ledger.
- **Never unattended:** any Tier-2 write.

## Local trigger (64GB machine — has the logged-in Chrome)

The authenticated pulls need local Chrome, so the scheduler lives on the 64GB machine.

**Windows Task Scheduler** — daily at e.g. 06:30, wake the machine, start Chrome debug, run the pass:

```powershell
# register once
$action  = New-ScheduledTaskAction -Execute "pwsh" -Argument '-File "C:\Users\<User>\.codex\tools\Run-MorningOrchestrator.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 6:30am
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable
Register-ScheduledTask -TaskName "MorningOrchestrator" -Action $action -Trigger $trigger -Settings $settings
```

`Run-MorningOrchestrator.ps1` should: start the CDP profile (`Start-ChromeDebug.ps1`), confirm
`127.0.0.1:9222` responds, then invoke the `morning-orchestrator` skill for the scouts+board (steps
1–5) and send the push. It must **not** execute Tier-1 until approval returns.

## Push + approval channel

- Send the push when the board is ready; deep-link to `automation-runs/morning-orchestrator/<date>/approval-board.md`.
- Approval can come back by whatever channel is wired (a reply, a checkbox file the run polls, a mobile
  action). On approval, the local runtime executes the Tier-1 batch per `parallel-execution.md`.
- If no approval by a cutoff (e.g. noon), leave the batch unexecuted and note it in `run-state.json` —
  never auto-apply on timeout.

## Cloud half (optional, complementary)

A hosted session can run the cloud-safe parts (scouts against the vault/Drive/public pages, board
synthesis, report artifacts) on a schedule and hand the board to the local machine for execution. Keep
one commander though — don't run two boards for the same morning.

## Cadence notes carried from the 64GB handoff

- Momentum + Align orchestrator runs **Sundays**; don't run Momentum reporting before Align calendar
  blockers clear unless Dillon approves draft-only.
- Align social calendar upload is monthly (1st) unless Dillon changes the rule.
