# BigOrange deck system

The deck kit (`lib/deck-kit.js`) is the visual authority. The bundled
`assets/templates/BigOrange-Primary-Deck-Reference.pptx` is the rendered proof
of what the kit produces (the 15-slide Thursday review of 2026-09-03). Build
new decks from the kit through a recipe; do not hand-edit the reference.

## Slide grammar

Every content slide has the same chrome: logo top-left (orange on white,
white on dark), eyebrow in orange caps, a 30 pt title, a footer line, the
orange square and slide number bottom-right. Dark slides open and close the
deck (sandwich); one dark slide mid-deck is allowed for the single most
important number.

## Blocks

| Block | Use it for | Data shape |
|---|---|---|
| `coverDark` | Opening slide, BigOrange-only | `{eyebrow,title,sub,date,badge}` |
| `coverClient` | Opening slide with a client logo zone (`CLIENT_LOGO`) | `{eyebrow,title,sub,date,clientName,clientLine,clientLogo:{path,verified}}` |
| `twoUp` | Up to four stats plus one card, optional takeaway | `{stats:[{v,l,hot}],card:{kicker,title,body},cardDark,takeaway}` |
| `columns` | Two to four columns with a big value each (agreement, team, offer) | `{items:[{kicker,big,body,hot}]}` |
| `grid` | Numbered small cards, 3 or 5 per row (contract layers, plays, access list) | `{cols,items:[{n,title,body,hot}]}` |
| `flow` | Left-to-right process with orange connectors, optional bar or takeaway | `{items:[{title,body}],hotIndex,light,bar,takeaway}` |
| `timeline` | Four phases, first hot | `{items:[{label,body}],takeaway}` |
| `bigNumbers` | Two oversized numbers and an explanation (dark slide) | `{items:[{v,l}],body}` |
| `features` | 2x2 icon cards (method, readiness) | `{items:[{icon,kicker,title,body}]}` (react-icons Fi names) |
| `decisions` | Numbered decision cards, last one hot | `{items:[string or {title}],takeaway}` |
| `textBullets` | Intro plus bullets, optional dark side card | `{intro,bullets:[],card}` |
| `table` | Native table with orange caps header | `{header:[],rows:[[]],colW:[],takeaway}` |
| `chart` | Native line or bar chart plus side card | `{type,labels:[],series:[{name,values}],chartTitle,card}` |
| `closeDark` | Closing slide with CTA and contact | `{title,body,cta,contact}` |

Empty required values render as `[[slot]]` text so `validate_deck.py` fails.

## Draft banner

When a brief has `sampleData: true` (the default), every slide carries the
orange "DRAFT · FIGURES PENDING VALIDATION" banner top-right and the validator
requires it. Turn it off only when every figure in the deck has a granted,
dated source.

## Client logos

Only `coverClient` places a client logo, in a fixed 3.5 x 1.3 in zone under
"PREPARED FOR", sized to contain, never stretched. The brief must carry
`logo.path`, `logo.source` (URL or asset locator) and `logo.verified: true`.
Without all three the zone renders a dashed placeholder and the deck fails
validation. Sources in order: an asset the client supplied, the client's brand
kit, the client's own website. Record the source in the brief.

## QA gate

1. `node scripts/build_deck.js brief.json out.pptx` (runs the validator).
2. `python3 scripts/brand_lint.py --surface deck <generator or brief>` when copy or code changed.
3. LibreOffice render to PDF, `pdftoppm` to JPEG, look at every slide: overflow, logo fidelity, contrast, banner present, no `[[slot]]`.
4. `markitdown out.pptx` and read the text once as the audience would.
