# Browserbase agents

Five small, **read-only** browser agents for agency checks. Each one opens a single
Browserbase session, visits its targets, and writes a JSON receipt plus PNG screenshots.

| Agent | What it does | Login needed? |
|---|---|---|
| `ad_ui_check.py` | Opens Google Ads / Meta Ads Manager pages and captures policy/disapproval banners, billing warnings and account status text | **Yes** (persistent context) |
| `gbp_watch.py` | Reads the public Google knowledge panel for each business (rating, reviews, hours, phone, website, address, "Suggest an edit" / "Own this business?") and diffs against the last run | No |
| `lp_qa.py` | Landing-page QA at 390 / 768 / 1440px: HTTP status, horizontal overflow, console errors, broken images, form, tel:/mailto:, tap targets under 44px, title, meta description | No |
| `lead_enrich.py` | Reads a lead CSV, finds missing websites via DuckDuckGo's HTML results, pulls phone, email, socials and contact page. Respects robots.txt, rate limited, hard cap 50 rows | No |
| `listing_audit.py` | Checks Yelp and Apple Maps for presence and name/address/phone consistency, and gives the claim URL | No |

## Safety rules (all agents)

- **Read-only.** Agents only navigate and read. They never click, type, submit forms,
  edit, buy, post, or create or claim listings.
- **One failure never hides the rest.** Each target runs in its own try/except. A failed
  target is recorded as `status: "error"` with its error and printed to stderr.
- **Caps.** `--max-targets` (default 25; lead_enrich is hard-capped at 50) and
  `--max-minutes` (default 15). Whichever hits first ends the run cleanly.
- **Kill switch.** Create a file named `STOP` in this folder (`touch STOP`). The current
  target finishes, then the run stops and says so in the receipt. Delete it to run again.
- **Session always released.** The Browserbase session is released in a `finally`
  block, even when a target or the connection fails.

## Setup

```bash
cd browserbase-agents
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Only needed for --local smoke tests (Browserbase runs need no local browser):
python -m playwright install chromium
```

### Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `BROWSERBASE_API_KEY` | yes | Sent as `X-BB-API-Key` |
| `BROWSERBASE_PROJECT_ID` | yes | Browserbase project |
| `BB_CONTEXT_ID` | for `ad_ui_check` | Persistent context that holds your Google / Meta login (`persist: true`) |
| `BB_LOCAL_CHROMIUM` | no | Chromium executable for `--local` runs |

Never commit keys. On the Mac, `~/.local/bin/with-browserbase` injects them:

```bash
~/.local/bin/with-browserbase python lp_qa.py
```

### Targets (real ones stay on the Mac)

- `targets.example.json` is committed and only has fake `example.com` targets.
- Copy it to **`targets.local.json`** (gitignored) and put real targets there. Agents use
  it automatically when it exists; otherwise they print a note and use the example file.
- For leads, put the real CSV at **`leads.local.csv`** (gitignored) or pass `--csv path`.
  Columns: `business_name,city,website` (website optional).

## Running

```bash
~/.local/bin/with-browserbase python ad_ui_check.py
~/.local/bin/with-browserbase python gbp_watch.py
~/.local/bin/with-browserbase python lp_qa.py --max-targets 10
~/.local/bin/with-browserbase python lead_enrich.py --csv ~/Desktop/leads.csv --min-interval 4
~/.local/bin/with-browserbase python listing_audit.py --max-minutes 10

# Free smoke test on a local Chromium (no Browserbase minutes, no login):
python lp_qa.py --local --targets my-test-targets.json
```

Common flags: `--targets FILE`, `--max-targets N`, `--max-minutes M`, `--out DIR`, `--local`.
Exit code is 0 when every target ran, 1 if any target errored or the session failed.

### Logging in for `ad_ui_check`

Create a Browserbase context once, open a session with it and `persist: true`, log in to
Google Ads and Meta by hand through the Browserbase live view, then release the session.
Set `BB_CONTEXT_ID` to that context. If a target lands on a login page later, the agent
reports `needs_login` for that target and moves on. It never types credentials.

## Running on GitHub Actions

`.github/workflows/browserbase-agents.yml` runs one agent per run. Start it from
**Actions → Browserbase agents → Run workflow** and pick the agent.

- **Secrets to add** (Settings → Secrets and variables → Actions → New repository secret):
  `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`, `BB_CONTEXT_ID`, `TARGETS_JSON` (the whole
  contents of your `targets.local.json`) and `ARTIFACT_PASSPHRASE`. `LEADS_CSV` (CSV text) is
  optional, for `lead_enrich`.
- **Quiet hours:** runs that start between 01:30 and 09:30 ET skip themselves.
- **The repo is public**, so Actions logs and artifacts can be read by any GitHub user. The
  log shows only the one-line summary. `out/` is uploaded as `out.tar.gz.gpg`, encrypted with
  `ARTIFACT_PASSPHRASE`, and kept for 14 days. Without that secret, the upload step fails
  rather than publish plain output. To decrypt it after downloading:

  ```bash
  gpg -d out.tar.gz.gpg | tar xzf -
  ```

- **Schedule:** the `schedule:` block is commented out. Uncomment it once the secrets are in.

## Receipts

Everything lands in `out/<agent>/<YYYY-MM-DD>/` (gitignored):

```
out/lp_qa/2026-10-13/
  receipt-152227.json
  152227-example-home-390.png
  152227-example-home-768.png
  152227-example-home-1440.png
```

Each run prints one line:

```
lp_qa: 4 target(s) [error=1, fail=2, ok=1] | receipt out/lp_qa/2026-10-13/receipt-152227.json
```

Receipt shape (trimmed):

```json
{
  "agent": "lp_qa",
  "read_only": true,
  "caps": {"max_targets": 25, "max_minutes": 15.0},
  "stopped_reason": null,
  "fatal": null,
  "counts": {"ok": 1, "fail": 2, "error": 1},
  "results": [
    {"target": "Example landing page", "status": "fail",
     "failed": ["meta_description", "tap_targets_44px@390"],
     "checks": {"http_status": {"pass": true, "detail": 200}, "...": "..."},
     "widths": {"390": {"no_horizontal_overflow": {"pass": true, "detail": "0px wider than viewport"}}},
     "screenshots": ["152227-example-landing-page-390.png"]},
    {"target": "Broken page", "status": "error", "error": "Error: Page.goto: net::ERR_NAME_NOT_RESOLVED"}
  ]
}
```

Statuses: `ok`, `warn` (something to look at), `fail` (lp_qa check failed), `changed`
(gbp_watch diff), `needs_login`, `partial` / `no_website` / `robots_blocked` (lead_enrich),
`error`. `lead_enrich` also writes `enriched-<time>.csv` next to the receipt.

## Tests

Offline, no network, no browser. A fake page serves fixture HTML from `tests/fixtures/`.

```bash
pytest -q
ruff check . && ruff format --check .
```
