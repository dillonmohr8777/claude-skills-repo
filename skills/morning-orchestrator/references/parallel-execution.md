# Parallel Execution Across Remote Chrome Tabs

The 64GB payoff: after the single morning approval, optimize multiple clients **at the same time**,
one client per Chrome tab, instead of one-by-one.

## The model

```
                 ┌── tab 1: Onsite   (CDP context A) ── apply → screenshot → readback ─┐
approve (once) ──┼── tab 2: NKCDC    (CDP context B) ── apply → screenshot → readback ─┼─► ledger
                 ├── tab 3: Omega    (CDP context C) ── apply → screenshot → readback ─┤
                 └── tab 4: Replenish(CDP context D) ── apply → screenshot → readback ─┘
```

## Hard rules

1. **One tab = one client = one CDP context.** Two tabs must never write to the same ads account or the
   same browser session — that's the one thing that corrupts state. Group by account, not by task.
2. **Attach, don't launch.** Connect over CDP to Dillon's real logged-in Chrome
   (`chromium.connectOverCDP("http://127.0.0.1:9222")`), open a fresh page per client, and
   **disconnect** when done — never close his browser.
3. **Screenshot before and after** every write. The pair is the evidence-log entry.
4. **Read back** the applied change from the platform UI before marking it done. No readback = not done.
5. **Isolate failures.** An expired session or platform error in one tab stops *that* client cleanly
   (`needs-reauth` / `error`) and the other tabs continue. One client never takes down the batch.
6. **Tier-1 only.** Budget/bid/billing/new-campaign/publish never execute here — they're Tier 2, live-only.

## How many at once

The limiter is **not** RAM at 64GB — each authenticated Chrome context is ~0.5–0.7 GB, so memory
comfortably holds 15–25. The real ceilings:

- **API rate limit** — the agents driving the tabs share your model rate limit; that throttles first.
- **Ads-platform rate/UI stability** — hammering the same platform across many tabs risks flakiness.

Practical setting: **3–6 client tabs concurrently.** Start at 3 (Dillon's own baseline: "even 3 at once
would be very helpful"), raise toward 6 if runs stay clean. Queue the rest; they drain as tabs free up.

## Concurrency config

```json
{
  "max_concurrent_client_tabs": 3,
  "cdp_endpoint": "http://127.0.0.1:9222",
  "per_tab_budget_min": 15,
  "screenshot_before_after": true,
  "require_readback": true,
  "stop_client_on_auth_fail": true,
  "tier2_in_batch": false
}
```

Raise `max_concurrent_client_tabs` only after observing clean runs at the current level.
