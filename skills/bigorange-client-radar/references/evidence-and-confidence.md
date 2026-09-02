# Evidence and confidence scoring

Every candidate carries an `evidence` list:

```json
{
  "url": "https://bigorange.marketing/case-study-acme-roofing/",
  "kind": "case-study-title",
  "text": "Case Study: Acme Roofing",
  "seen_at": "2026-09-02T14:03:00Z"
}
```

## Evidence kinds

| kind | source |
|---|---|
| `rest-post` | A post returned by the WP REST API matching a client-shaped category, tag, or search term, with a company name pulled from its title |
| `testimonial` | A blockquote of praise plus a following attribution line ("Name, Title, Company") |
| `case-study-title` | A heading or "for &lt;Company&gt;" phrase naming a case study |
| `figcaption` | Text under an image, e.g. a captioned client photo or logo |
| `logo-alt` | `alt`/`title` text on an `<img>` in a logo-strip-shaped context |
| `media-library` | A filename or alt/title text from a `/wp-json/wp/v2/media?search=logo` hit |

## Confidence

- **high** -- 2 or more distinct evidence kinds, OR at least one `rest-post`
  / dedicated case-study post. A company that BigOrange wrote a whole post
  about, or that shows up in more than one place (e.g. testimonial + logo),
  is confidently a client.
- **medium** -- exactly one `testimonial` or one `case-study-title` hit and
  nothing else. Plausible, but resting on a single loosely-parsed mention.
- **low** -- only a `logo-alt` or `media-library` hit. Logo strips are the
  noisiest source (partner badges, awards, tool logos all look the same in
  markup), so a bare logo mention alone stays low confidence until something
  else corroborates it.

## Why this matters downstream

`references/access-request.md` and the `bigorange-client-decks` follow-on
only fire a human-facing action ("draft a kickoff deck") on a `new_client`
event where confidence is `high`. Medium and low confidence entries stay in
the roster for a human to eyeball, but they don't trigger outreach-adjacent
suggestions on their own -- a stray logo-strip match shouldn't imply BigOrange
just landed a new client.
