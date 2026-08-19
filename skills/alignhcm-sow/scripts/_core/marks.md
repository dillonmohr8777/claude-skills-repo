# Marks: which logo goes on what, and why

Three marks can appear on an Align document. Each has one rule.

## The Align lockup

The exact mark, taken byte for byte from `ppt/media/image1.png` of the Align
master deck. It is vendored into every document skill as
`scripts/_core/align-hcm-deck-lockup.png` and pinned by SHA-256, so a
re-export, a resize, or a well-meaning substitution fails the build instead of
quietly changing what goes out.

| Surface | Placement |
|---|---|
| Deck cover | The master's `AlignHCM_Logo` zone: 0.900 in from the left, 0.780 in from the top, inside a 2.750 x 1.275 in box |
| Word documents | A navy masthead band across the top of the first page |

The lockup is a **reverse** mark: the wordmark is light grey, drawn for dark
backgrounds. Dropped onto white paper it is washed out and off-brand. That is
why Word gets a navy band rather than a bare logo. The band is not decoration.

Where the real mark appears, the typographic "ALIGN HCM" eyebrow is suppressed,
because two lockups on one page reads as a mistake.

## The client mark

A prospect's or client's own logo, fetched from their own site, background
removed, trimmed, upscaled, measured for contrast, and placed on a bordered
plate in their own brand colour. The full pipeline and the plate rule belong to
`alignhcm-brand-system`; the document skills vendor it rather than reimplement
it.

| Document | Client mark | Why |
|---|---|---|
| `alignhcm-intro-deck` | **Required decision** | A first-meeting deck is co-branded by nature |
| `alignhcm-proposal` | **Required decision** | Same |
| `alignhcm-pm-runbook` status report | Optional | Goes to a client who has already signed. Ordinary and welcome, but nobody needs to be stopped for it |
| `alignhcm-sow` | **Never** | A SOW is a contract. Putting the counterparty's logo on a document you drafted is presumptuous, and in procurement it raises a trademark-use question nobody wants mid-deal. Their legal name goes in the parties block. The self-test asserts the only image in a generated SOW is Align's own mark, even when the spec supplies one |

"Required decision" means the build stops until the spec says one of:

```json
"client_mark": {"domain": "acme.com"}        fetch, clean, plate
"client_mark": {"file": "acme-logo.png"}     same pipeline, supplied file
"client_mark": {"ready": "acme-plated.png"}  already pipeline output
"client_mark": "none"                        deliberately none
```

`"none"` is a real answer and a normal one. What is not allowed is silence,
because silence is how a deck ships with an empty client panel, or with the
previous prospect's mark still sitting in it.

The mark is always fitted, never stretched. A distorted logo is not the
client's logo.

## The SmartCare mark

**Align has no SmartCare logo.** Not in the master deck, not in SharePoint, not
in any brand kit reachable from here. The client decks set it as type.

So the skills draw a typographic lockup: "Smart" in the document's ink, "Care"
in Align orange, with a short orange rule. That is type, not a trademark
invented on the spot, and it matches what the shipped decks already do.

It appears once, on the SmartCare slide, right-aligned against the title so it
reads as a service mark rather than competing with the Align lockup. The
self-test asserts it lands on exactly one slide.

If a real SmartCare mark exists, drop it in as
`scripts/_core/smartcare-lockup.png` and it is used instead, with no other
change and no code edit.

## What is checked

| Check | Where |
|---|---|
| The vendored lockup is the approved mark | Every document skill |
| A substituted lockup is refused | Every document skill |
| The lockup reaches the cover | `alignhcm-intro-deck` |
| The client mark decision cannot be skipped | `alignhcm-intro-deck`, `alignhcm-proposal` |
| A supplied client mark is cleaned and plated | `alignhcm-intro-deck` |
| A contract carries no client mark | `alignhcm-sow` |
| The SmartCare mark lands on exactly one slide | `alignhcm-intro-deck` |
