# Access request (approval-gated -- draft only, never sent automatically)

Two ways to get deeper, still-read-only visibility into BigOrange's WordPress
content (private/draft case studies not yet public). Sending either request
is a human decision -- append the drafted message to the approval queue and
stop. This skill never sends anything itself.

## Option A -- WordPress Application Password

Ask BigOrange (or whoever administers bigorange.marketing) to create a
dedicated user for this purpose:

> Subject: Read-only WordPress access for content research
>
> Hi -- could you create a WordPress user on bigorange.marketing scoped to
> the Editor role (or lower, if a custom read-only role exists), and issue it
> an Application Password under Users > Profile > Application Passwords?
>
> This account is only ever used for read-only GET requests against the
> `/wp-json/wp/v2/` REST API -- listing posts, pages, and media, including
> drafts and private posts, so we can see published and in-progress case
> studies. It never creates, edits, or deletes anything. You can revoke the
> Application Password at any time from the same screen with no other
> impact.
>
> Once issued, please share the username and the generated Application
> Password (a space-separated code, not your login password) through a
> secure channel.

Once received, set:

```bash
export BIGORANGE_WP_USER="<username>"
export BIGORANGE_WP_APP_PASSWORD="<app password>"
python3 scripts/wp_auth_probe.py
```

`wp_auth_probe.py` only performs GET requests and reports whether the
credentials work and what read access they grant. It never writes.

## Option B -- Abency brand connection

If BigOrange is willing to be connected as a brand inside Abency (the
agency's own MCP-based marketing platform), the same read-only surface
becomes available through `mcp__Abency__wp_list_posts` and friends, without
managing a separate WordPress user or password at all. This is the lighter
option if Abency already has a relationship with BigOrange or their agency
of record.

> Subject: Connecting bigorange.marketing as an Abency brand
>
> Would you be open to connecting bigorange.marketing as a brand inside
> Abency? It would let us pull read-only post/page listings (including
> drafts, if you choose to expose them) the same way we do for our other
> tracked brands, without a separate login or password to manage. Fully
> revocable from your side at any time.

## Guardrails either way

- Read-only. This skill has no write path to WordPress or to Abency.
- Revocable. Application Passwords and Abency brand connections can both be
  removed unilaterally by BigOrange at any time.
- Nothing is sent without a human approving it first. Draft the message,
  append it to `System/approval-queue.md`, and stop.
