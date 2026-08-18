# Align HCM primary PowerPoint system

## Authority and implementation model

`assets/templates/Align-HCM-Primary-Deck-Reference.pptx` is the privacy-scrubbed
clone of the exact visual authority supplied by the brand owner on
2026-08-13. Its
geometry, styles, colors, type, icons, Align artwork, and client-logo zone are
unchanged. Prior-client branding, contacts, pricing, and engagement facts were
removed before committing it to the public repository. It is a designed seven-
slide deck, not a mature `.potx` theme.

The file retains the stock Office theme internally. Its real Align identity is
hand-painted into slide shapes and text:

- primary navy `#232E3E`
- primary orange `#E97722`
- contrast orange `#B05512`
- paper `#F6F8FA`
- light text/rules `#C5CEDA` and `#E3E8EE`
- direct type overrides: Calibri, Arial, and Cambria

Therefore:

- Do not use the Office `accent1` through `accent6` slots as Align colors.
- Do not rebuild the design from the reported stock Office layouts.
- Clone a designed slide and edit its existing shapes.
- Treat `powerpoint-tokens.md` as measurement evidence and the rendered deck as
  the visual authority.

## Exact file and artwork

- Scrubbed reference deck SHA-256:
  `BA3CD30112BC9EFB2A9D18483A2188559FD97BCD08CF47E02B0C9BEA675F18EA`
  (updated 2026-08-17; see `CHANGELOG.md` for what changed and why)
- Exact Align deck lockup SHA-256:
  `3A0340D27BFE44B21277F4A689796B1C31338F5FD74134786209F5B736D22A07`
- Canvas: 13.333 x 7.5 inches, 16:9

Never reconstruct or recolor the Align lockup. Use the embedded image or the
bundled exact copy.

## Client co-branding

The cover has two distinct brand zones:

| Zone | Named picture | Position and box |
|---|---|---|
| Align lockup | `AlignHCM_Logo` | x 0.900 in, y 0.780 in, 2.750 x 1.275 in |
| Client logo | `CLIENT_LOGO` after preparation | x 9.667 in, y 3.460 in, maximum 2.900 x 0.997 in |

The client logo belongs below `PREPARED FOR` on the navy panel. Contain it
inside the maximum box, center it on both axes, preserve aspect ratio, and do
not crop, trace, recolor, add effects, or place it on a white card unless the
official mark is unreadable on navy. Prefer the client's official reverse or
white mark. If only a dark mark exists, use the approved light-background logo
variant and a restrained clear-space field.

Normalize by optical height, not bounding-box width. A wide wordmark should
not visually overpower the Align logo. Client branding does not enter the
footer and does not replace Align ownership.

## Slide recipes in the supplied authority

1. **Dual-brand cover**: navy split field, Align lockup upper left, client mark
   centered in the right panel, orange vertical divider, serif title, compact
   eyebrow, short engagement line, date, and three-zone footer.
2. **Executive answer**: white field, title and one-sentence answer, four navy
   proof cards in a two-by-two grid. Use one claim per card.
3. **Timeline**: white field, six restrained navy phase blocks, one orange
   go-live marker, and one dark explanatory callout.
4. **Milestone table**: white field, dark header, alternating pale rows, orange
   duration column. Keep the body readable; move overflow to an appendix.
5. **Investment or focal proof**: full navy field, one dominant value, one
   secondary conditional callout, and one full-width scope note.
6. **Client responsibility matrix**: white field, compact matrix plus one dark
   interpretation callout. Use words and color together.
7. **Close/contact**: navy split field, Align lockup on the left, one clear next
   step and verified contact details on the right.

These are visual archetypes, not permission to preserve the sample content.
Delete irrelevant slides and duplicate the closest archetype when more pages
are needed.

## Content and evidence rules

- Read the current brief before touching the deck.
- Resolve the client and engagement from current source evidence.
- Replace every sample client, person, price, scope, date, timeline, and claim.
- Keep one primary idea per slide and one accent behavior per field.
- Use precise source notes for claims, tables, pricing, and timelines.
- Keep body text at a readable presentation size. Split dense pages instead of
  shrinking text.
- Preserve the footer sequence: `alignhcm.com`, confidentiality, `Align HCM`,
  and zero-padded slide number.

## Build and delivery gate

1. Run `prepare_client_deck.py` with a verified client name and PNG logo.
2. Rewrite the deck from the current brief.
3. Run `validate_client_deck.py` with the same client name and logo.
4. Render all slides at 16:9 and review them as images.
5. Confirm the Align logo hash, client logo fidelity and aspect ratio, no sample
   residue, no unresolved placeholders, no overflow, and sequential footers.
6. Check body contrast at 4.5:1 and large display text at 3:1.
7. Deliver both the editable `.pptx` and a reviewed PDF when requested.

Run `extract_pptx_theme.py` only when onboarding a replacement master or
auditing drift. Extraction is not required for ordinary deck creation.
