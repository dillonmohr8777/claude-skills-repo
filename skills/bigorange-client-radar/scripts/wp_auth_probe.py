#!/usr/bin/env python3
"""
wp_auth_probe.py -- verify a WordPress Application Password grants read-only
access to bigorange.marketing, without writing anything.

Reads credentials from env:
  BIGORANGE_WP_USER
  BIGORANGE_WP_APP_PASSWORD

GETs /wp-json/wp/v2/users/me and /wp-json/wp/v2/posts?status=private&per_page=1.
Prints the reported capabilities and whether private-post listing works.
Exits 0 if auth succeeds and read access is confirmed, 1 otherwise.

This script performs GET requests only. It never creates, updates, or
deletes anything in WordPress.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

USER_AGENT = "bigorange-client-radar/1.0 (+dillon@momentum360)"
BASE = "https://bigorange.marketing"
TIMEOUT = 20


def fetch_json(url, auth_header):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    req.add_header("Authorization", auth_header)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            body = {}
        return e.code, body
    except urllib.error.URLError as e:
        return None, {"error": str(e.reason)}


def main():
    user = os.environ.get("BIGORANGE_WP_USER")
    pw = os.environ.get("BIGORANGE_WP_APP_PASSWORD")

    if not user or not pw:
        print("BIGORANGE_WP_USER and BIGORANGE_WP_APP_PASSWORD must both be set in the environment.")
        print("This is a read-only probe: it will not write to WordPress.")
        return 1

    token = base64.b64encode(f"{user}:{pw}".encode("utf-8")).decode("ascii")
    auth_header = f"Basic {token}"

    print(f"Probing {BASE} as {user} (read-only GET requests only)...\n")

    status, me = fetch_json(f"{BASE}/wp-json/wp/v2/users/me?context=edit", auth_header)
    ok_identity = status == 200
    print(f"GET /wp-json/wp/v2/users/me -> HTTP {status}")
    if ok_identity:
        caps = me.get("capabilities", {})
        active_caps = sorted(k for k, v in caps.items() if v)
        print(f"  name: {me.get('name')}")
        print(f"  roles: {me.get('roles')}")
        print(f"  capabilities granted: {', '.join(active_caps) if active_caps else '(none reported)'}")
    else:
        print(f"  response: {me}")

    status2, posts = fetch_json(f"{BASE}/wp-json/wp/v2/posts?status=private&per_page=1", auth_header)
    ok_private_read = status2 == 200
    print(f"\nGET /wp-json/wp/v2/posts?status=private&per_page=1 -> HTTP {status2}")
    if ok_private_read:
        print(f"  private-post listing works ({len(posts) if isinstance(posts, list) else 0} returned)")
    else:
        print(f"  private-post listing NOT available: {posts}")

    print("\nSummary:")
    print(f"  identity confirmed: {ok_identity}")
    print(f"  read-only private listing: {ok_private_read}")
    print("  writes attempted: none (this probe never writes)")

    return 0 if ok_identity else 1


if __name__ == "__main__":
    sys.exit(main())
