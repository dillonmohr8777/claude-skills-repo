# Align HCM voice, for generated documents

The subset of Align's voice rules that a document generator has to obey. The
full brand voice, including motion, carousel, and social surfaces, lives in
`alignhcm-brand-system/references/voice-and-copy.md`. Where the two overlap,
they must agree; this file is vendored into each document skill so a generated
SOW and a generated deck sound like the same company.

## Audience

Decision-makers and implementation leaders who already understand UKG, Workday,
Dayforce, HiBob, and payroll operations. Do not explain what an HRIS is. Do not
define go-live. Write to a peer.

## Tone

Professional, consultative, expert-level. Never salesy. The posture is a senior
practitioner explaining what actually happens after go-live, not a vendor
pitching. Credibility comes from specificity, not enthusiasm.

## Hard rules

1. **No em dashes. Anywhere.** Use periods, commas, colons, or restructure. The
   self-tests enforce this across every markdown file in every skill.
2. **Use contractions** in prose. "You'll", not "you will". Contract language in
   a SOW is the exception: it is written formally on purpose.
3. **Bullet character only.** Never a dash as a list marker.
4. **Headlines run 8 to 15 words.**

## Recurring phrases

Established. Reuse rather than inventing synonyms:

- "Go-live"
- "Proactive"
- "No queue, no chatbot"
- "Post-go-live support"
- "Ongoing expert access"
- "Platform optimization"

## SmartCare naming has one source

SmartCare tier names are **not** listed here, deliberately. Two vocabularies are
live at Align and a third and fourth phrasing exist in older copy decks. Every
skill reads the tier table from
`alignhcm-intro-deck/references/smartcare-tiers.md`, which carries the evidence
and the ruling. Restating the ladder in a voice file is how the conflict spread
in the first place.

What is safe to say about SmartCare in any document: it is Align's
post-implementation service line, positioned on ongoing expert access, platform
optimization, and post-go-live support, with a dedicated executive sponsor,
project manager, and advisor.

## Two things never to write

**Approved-sounding copy that was never approved.** If a document needs
something not covered by a reference, say so and mark it net-new. Do not
fabricate a headline and present it as house copy. The SmartCare go-to-market
document that held the approved wording is missing and has never been recovered.

**A claim Align's own documents contradict.** The banned phrases live in
`company-facts.md` and the builders fail on them. The current list concerns
delivery geography.
