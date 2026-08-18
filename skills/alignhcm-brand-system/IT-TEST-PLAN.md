# Test plan for this skill

For whoever is validating `alignhcm-brand-system` before it goes to the wider
team. Budget about 30 minutes. You do not need to know the brand to run this.

Everything here runs on a stock Python 3. There is nothing to install.

---

## 1. Automated check, 2 minutes

From the skill folder:

```bash
python3 scripts/selftest.py
```

**Expect:** `36/36 checks passed` and exit code 0.

This runs the documented workflow against the bundled assets, builds a real
deck, lints a real Word file, and exercises the logo fetcher against a local
fixture site. It builds its own test files and cleans up after itself.

If any check fails, stop and send the output. A failure here means the package
is broken, not that you did something wrong.

One check reports `skipped` where LibreOffice is not installed. That is expected
and fine.

---

## 2. Build a deck, 10 minutes

Ask Claude, with the skill enabled:

> Build an Align HCM client presentation for Acme Foods, a UKG Pro
> implementation, 1,200 employees migrating off ADP Workforce Now, go-live
> January 2027, priced at $142,000.

**Expect:**

- A seven-slide `.pptx`, not a deck built from scratch
- The Align lockup on slides 1 and 7
- Navy `#232E3E` fields, orange `#E97722` accents, serif titles
- No `{{PLACEHOLDER}}` text anywhere
- Footer on every slide reading `alignhcm.com`, `Confidential`, `Align HCM · NN`

**Red flags worth reporting:**

- Any visible `{{` or `}}`
- A deck that looks generic rather than like the bundled reference
- Text reading `Acme Foods's` with a double possessive
- Any slide missing the footer

Then verify it mechanically:

```bash
python3 scripts/validate_client_deck.py <the-deck>.pptx --client-name "Acme Foods"
```

**Expect:** `passed=True` and exit 0.

---

## 3. Fetch a client logo, 10 minutes

Pick any company with a public website:

```bash
python3 scripts/fetch_client_logo.py --domain <company>.com --name "<Company>" --out /tmp/logo.png
```

**Expect one of these, all of which are correct behaviour:**

| Exit | Meaning |
|---|---|
| 0 | A logo was written, plus a `.source.json` recording where it came from |
| 2 | Found a logo but it failed the quality bar, with a reason given |
| 3 | Nothing usable on that site |
| 4 | Site unreachable |

**The point of this test is that it refuses bad input.** A non-zero exit with a
clear reason is a pass, not a failure. What would be a real defect is a blurry,
stretched, or invisible logo written with exit 0.

On success, open `/tmp/logo.png`. It should be the company's mark on a plate:
white plate with a coloured border for a dark logo, near-black plate for a light
one, with the border colour taken from the logo itself.

Open `/tmp/logo.png.source.json` and confirm it names the source URL.

This step needs outbound web access. If your network blocks it you will get exit
4, which tells you about the network rather than the skill.

---

## 4. Confirm the brand gate actually bites, 5 minutes

Create a Word document containing the colour `#E8760A`, then:

```bash
python3 scripts/brand_lint.py --surface document <file>.docx
```

**Expect:** at least one `error` line and exit code 1.

This colour is on the never-use list. If this returns clean, the gate is broken
and that is worth reporting immediately.

---

## Known limits, please do not file these

- The logo fetcher has never run against a live corporate site from inside our
  network. Messy real-world markup is the most likely source of surprises, and
  finding those is part of what this test is for.
- SmartCare copy and LinkedIn carousels produced from this skill are net-new and
  need review. The source documents for both are unrecoverable, which is stated
  in the skill.
- The bundled deck is a designed reference on the stock Office theme, not a
  normalised `.potx`. That is deliberate; the skill clones designed slides
  rather than rebuilding from layouts.
- Five skills named in an earlier draft (`sow-generator`, `alignhcm-loi`,
  `alignhcm-legal-review`, and the two report skills) do not exist. They are no
  longer referenced.

---

## Reporting

For anything that fails, the most useful report is:

1. Which numbered step
2. The exact command
3. The full output
4. For a deck or logo problem, the file itself

Send findings to the brand owner named in `SKILL.md`.
