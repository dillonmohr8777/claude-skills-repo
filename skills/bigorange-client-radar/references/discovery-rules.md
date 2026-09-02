# Discovery rules

What counts as evidence that BigOrange Marketing presents a company as a
client, what gets suppressed, and why.

## What counts

A candidate is added to the roster when its name is found in one of these
contexts on bigorange.marketing:

- **A case-study post or page.** A WordPress post/page whose title, URL, or
  heading names a company alongside "case study" language, or lives in a
  category/tag matching `case-study|casestudy|portfolio|client|testimonial|
  results|success|work`.
- **A testimonial.** A blockquote of praise followed by an attribution line
  (name, title, company) -- the company in that attribution is the client.
- **A client logo strip.** An `<img>` whose `alt`/`title` text, class, or
  filename references "logo", "client", "customer", or "partner", with a
  plausible company name in the alt/title text.
- **Media library filenames.** Files uploaded with "logo" in the search hit
  and a company-looking alt/title text.
- **"For <Company>" phrasing.** Case-study titles or blurbs of the shape
  "... for Acme Roofing" or "Case Study: Acme Roofing".

## What is suppressed

The following never appear in the roster, even if matched:

1. **Dillon's own clients.** Loaded from
   `/home/user/client-operations-canonical/registry/clients.json` --
   `displayName`, every `aliases` entry, and every `emailDomains` entry are
   checked (name or domain match, case-insensitive, substring-tolerant).
   These are Dillon's clients, never BigOrange's, and a name collision here
   is a false positive, not a rival win.
2. **Built-in suppress set.** BigOrange itself and its known name variants,
   platform/tool vendors it might mention (HubSpot, Google, WP Engine,
   Clutch, Expertise, Semrush, Moz, Yoast, WordPress), social platforms
   (Facebook, LinkedIn, Instagram), and generic location words (Cincinnati,
   Ohio) that show up in footers and schema markup, not client mentions.
3. **Generic navigation/section words.** "Case Studies", "Portfolio", "Our
   Work", "Testimonials", "Services", etc. -- section labels, not company
   names.
4. **Names under 3 characters** after trimming, and anything that fails to
   resolve to a real name once cleaned.

## Why this shape

BigOrange doesn't publish a client list. The roster is inferred from public
marketing content, so every entry needs to justify itself with evidence
(see `evidence-and-confidence.md`) and every entry needs a suppress check
against Dillon's own client registry, because a shared client (or a false
match on a common word) would otherwise look like a lead or a threat that
isn't real.

This script never asks bigorange.marketing to prove anything and never
writes back to it. It only reads what's already public (or, with an
Application Password, what's already visible to a read-only editor account).
