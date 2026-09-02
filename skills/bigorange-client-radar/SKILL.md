---
name: bigorange-client-radar
description: Discover which companies BigOrange Marketing (bigorange.marketing) presents as clients via public case studies, testimonials, portfolio pages, and client logo strips, keep a roster, and flag new ones. Triggers on find BigOrange's clients, new client detection, client roster, who does BigOrange work with.
---

# bigorange-client-radar

## Purpose

BigOrange Marketing is a competitor agency. This skill builds and maintains a
roster of the companies BigOrange publicly presents as clients, using only
public web content (and, once granted, a read-only WordPress Application
Password). It never guesses -- every roster entry carries evidence with a
source URL, an evidence kind, and a confidence level. On each run it diffs
against the previous roster and emits events for new clients, new evidence
on existing clients, and clients that have dropped off the site.

## Guardrails

- **Read-only, always.** Every network call in this skill is a GET request.
  Nothing is ever written to bigorange.marketing, with or without
  credentials.
- **Never sends anything.** No email, no Slack, no outbound message of any
  kind. `references/access-request.md` drafts requests for a human to review
  and send; the skill itself stops at the draft.
- **Suppresses Dillon's own clients.** Every candidate is checked against
  `/home/user/client-operations-canonical/registry/clients.json`
  (`displayName`, `aliases`, `emailDomains`) plus a built-in suppress list
  (see `references/discovery-rules.md`). A name collision with Dillon's own
  roster is dropped, not reported as a BigOrange client.
- **Fails closed without access.** With no credentials, it runs on public
  REST + HTML only and records what it couldn't reach in the output's
  `errors` list rather than guessing. It never fabricates a client.
- **Polite crawling.** 0.5s between requests, 20s timeout per request, one
  User-Agent identifying the script and a contact.

## Commands

```bash
# Real run against bigorange.marketing, print a table, write nothing
python3 scripts/discover_clients.py --dry-run --limit 60

# Write the roster and diff against a previous snapshot in one pass
python3 scripts/discover_clients.py \
  --diff 12_Brain/state/bigorange-client-roster.json \
  --out 12_Brain/state/bigorange-client-roster.json

# Diff two existing roster snapshots directly
python3 scripts/diff_roster.py <previous roster.json> <current roster.json>

# Verify a WordPress Application Password (read-only; never writes)
export BIGORANGE_WP_USER=...
export BIGORANGE_WP_APP_PASSWORD=...
python3 scripts/wp_auth_probe.py

# Offline test (no network)
python3 scripts/test_radar.py
```

Flags on `discover_clients.py`: `--out`, `--dry-run`, `--limit N`,
`--auth-user`/`--auth-pass` (or env `BIGORANGE_WP_USER`/
`BIGORANGE_WP_APP_PASSWORD`), `--diff <previous roster.json>`,
`--fixture <dir>` (offline testing), `--quiet`.

## State paths (dillon-os vault)

- `12_Brain/state/bigorange-client-roster.json` -- current roster snapshot
- `12_Brain/state/bigorange-client-events.json` -- events from the last diff
  (also carries the `_missing_runs` counters used to debounce `removed`
  events)

Inside this skill's own directory, `state/roster.json` is the default `--out`
target for local testing; the automation always passes the vault paths above
explicitly.

## Automation registration

Add this entry to `dillon-os/12_Brain/registry/automations.json`:

```json
{
  "id": "bigorange-client-radar",
  "name": "BigOrange client radar",
  "lane": "clients",
  "tier": 1,
  "cadence": "daily",
  "command": "python3 <skills>/bigorange-client-radar/scripts/discover_clients.py --diff 12_Brain/state/bigorange-client-roster.json --out 12_Brain/state/bigorange-client-roster.json",
  "inputs": ["https://bigorange.marketing/wp-json/", "registry/clients.json"],
  "outputs": [
    "12_Brain/state/bigorange-client-roster.json",
    "12_Brain/state/bigorange-client-events.json"
  ],
  "external_actions": false,
  "status": "implemented"
}
```

## Follow-on

On a `high`-confidence `new_client` event, a human (not this skill) runs
`bigorange-client-decks` with recipe `client-kickoff` (`sampleData: true`) to
draft a kickoff-competitor deck. This skill only detects and reports; it
never triggers that follow-on itself.

## References

- `references/discovery-rules.md` -- what counts as a client, what is
  suppressed, and why
- `references/evidence-and-confidence.md` -- evidence kinds and how
  confidence is scored
- `references/access-request.md` -- ready-to-send (human-approved) requests
  for deeper read-only access
