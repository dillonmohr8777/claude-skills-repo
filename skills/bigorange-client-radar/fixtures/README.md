# fixtures

Local, offline fixture set for `scripts/test_radar.py`. These files let
`discover_clients.py --fixture <dir>` run without any network access, so the
skill can be tested in CI or on a locked-down machine.

## Layout

- `home.html` -- a fake BigOrange home page with a client logo strip and two
  client testimonials (blockquote + attribution).
- `posts.json` -- a fake `/wp-json/wp/v2/posts` response containing one
  case-study post.
- `categories.json`, `tags.json`, `pages.json`, `media.json` -- minimal or
  empty stand-ins for the other REST endpoints, kept small on purpose.

## Convention

`discover_clients.py --fixture <dir>` reads:

- `categories.json`, `tags.json`, `posts.json`, `pages.json`, `media.json`
  in place of the matching REST calls (missing files behave as an empty
  response).
- every `*.html` file in the directory as one HTML page to scan. The file's
  stem becomes its page path label, e.g. `home.html` -> `/home/`. The industry
  hub mapping only applies to the real hub page paths, so fixture pages
  default to `industry_guess: "unknown"` unless the test asserts otherwise.

## Third fixture client (used by test_radar.py)

The test injects a third fixture client at runtime by writing a copy of this
directory with an extra testimonial appended to `home.html`, then re-running
discovery and diffing against the original roster. It does not ship as a
static file here so the base fixture set stays exactly two clients.
