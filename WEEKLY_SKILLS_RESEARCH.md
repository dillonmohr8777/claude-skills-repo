# Weekly Claude Skills Research Brief

> Ranked scan of the most popular Claude skills on GitHub, filtered to what this
> library is **missing**. Refreshed weekly (see [Refresh cadence](#refresh-cadence)).

**Last refreshed:** 2026-07-10
**Maintainer:** dillon-mohr
**Scope:** `dillonmohr8777/claude-skills-repo`

---

## How this list is built

GitHub does not publish a per-skill popularity metric, so "most popular" is ranked
by a blend of:

1. **Source-collection popularity** — stars / install counts of the repo the skill
   ships in.
2. **Gap relevance** — how well it fills a capability this library does **not**
   already have.

### Explicitly excluded

This library already has deep coverage of **marketing, CRO, growth, advisors, product,
and engineering** skills (e.g. `landing-page-generator`, `ui-design-system`,
`page-cro`, `form-cro`, `ad-creative`, `playwright-pro`, `a11y-audit`,
`ux-researcher-designer`, the full advisor/eng roster). Skills that only duplicate
those are **filtered out**. Where a recommendation partially overlaps an existing
skill, the overlap is called out in the notes.

### Prioritized gaps

Missing / thin areas this brief prioritizes:

- **Landing pages** beyond the generator we already have (showcase pages, full site setup)
- **Visual design** (design systems, theming, artifact design)
- **Motion / animation** (web animation, scroll effects, physics)
- **Interactive web** (3D / WebGL / Rive / Spline)
- **Testing** (E2E, visual regression, responsiveness, WCAG, unit)

---

## Ranked top 15 (this week)

| # | Skill / collection | Source | Gap it fills | Notes |
|---|---|---|---|---|
| 1 | **frontend-design** | `anthropics/claude-code` (official, 277k+ installs) | Visual design | The default visual-design skill; rewritten Feb 2026 to avoid "AI-overused" fonts and generic purple gradients. Highest-reach recommendation. |
| 2 | **Superpowers** | `obra/superpowers` (~94k★) | Testing / quality | TDD-enforced dev framework; its UI audit checks code against the Web Interface Guidelines (a11y, focus states, touch targets, reduced-motion, semantic HTML). |
| 3 | **claudedesignskills** | `freshtechbro/claudedesignskills` (~496★) | Interactive web + motion | 22 skills + 5 bundles: `threejs-webgl`, `react-three-fiber`, `gsap-scrolltrigger`, `motion-framer`, `babylonjs`, `lottie`, `react-spring`. Biggest single interactive/3D gap-filler. |
| 4 | **landing-page + product-showcase** | `jezweb/claude-skills` (~911★) | Landing pages | Marketing one-pagers and app/product showcase pages. Complements our `landing-page-generator` with showcase-specific layouts. |
| 5 | **motion-dev-animations-skill** | `199-biotechnologies/motion-dev-animations-skill` | Motion | 120fps GPU animations via Motion.dev (Framer Motion successor): hero fade-up, staggered entrances, scroll reveal, parallax layers. |
| 6 | **claude-design-skill** | `jiji262/claude-design-skill` | Visual design | Portable skill adapted from Claude.ai's internal Design system prompt — decks, landing pages, prototypes, animations, posters as HTML artifacts. |
| 7 | **website-builder-setup** | `tenfoldmarc/website-builder-setup` | Landing pages + motion | One install → UI/UX Pro Max + Framer Motion + 21st.dev for animated marketing sites. |
| 8 | **playwright-skill** | `lackeyjb/playwright-skill` | Testing (E2E + visual regression) | Model-invoked Playwright: selectors, network interception, auth, visual regression, mobile emulation. *Overlaps `playwright-pro` — adopt whichever is more current.* |
| 9 | **Theme Factory** | listed in `ComposioHQ/awesome-claude-skills` | Visual design | Applies pro font/color themes (10 presets) to slides, docs, reports, and HTML landing pages. |
| 10 | **anydesign** | listed in `ComposioHQ/awesome-claude-skills` | Visual design | Reverse-engineers an image / URL / Figma file into a structured `design.md` (design system + component inventory). |
| 11 | **design-review + responsiveness-check** | `jezweb/claude-skills` (~911★) | Testing (visual / responsive) | Visual quality assessment + multi-viewport layout testing. |
| 12 | **accessibility-axe-pa11y** | `qaskills.sh` (Claude Code QA pack) | Testing (WCAG 2.2 AA) | Runs axe-core inside Playwright, parses violations, files them as GitHub issues. *Overlaps `a11y-audit` — compare depth before adopting.* |
| 13 | **rive-interactive + spline-interactive** | `freshtechbro/claudedesignskills` | Interactive web | Rive motion graphics + Spline interactive 3D authoring for hero sections and product visuals. |
| 14 | **vitest** | `jezweb/claude-skills` (~911★) | Testing (unit) | Vitest setup and Jest→Vitest migration — fills the unit-testing gap (we have E2E, not unit). |
| 15 | **claude-directory** | `pulkitxm/claude-directory` | Interactive web (reference) | Open gallery of Claude-generated landing pages, hero sections, GLSL shaders, design systems, and 3D scenes — an inspiration/reference source rather than an installable skill. |

---

## Sources

- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — curated index
- [anthropics/claude-code — frontend-design](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md)
- [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills)
- [jezweb/claude-skills](https://github.com/jezweb/claude-skills)
- [199-biotechnologies/motion-dev-animations-skill](https://github.com/199-biotechnologies/motion-dev-animations-skill)
- [jiji262/claude-design-skill](https://github.com/jiji262/claude-design-skill)
- [tenfoldmarc/website-builder-setup](https://github.com/tenfoldmarc/website-builder-setup)
- [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill)
- [pulkitxm/claude-directory](https://github.com/pulkitxm/claude-directory)
- [Best Claude Code Skills for Testing and QA in 2026 — qaskills.sh](https://qaskills.sh/blog/best-claude-code-skills-for-testing-2026)

---

## Refresh cadence

This brief is meant to be refreshed **weekly (Mondays)**. Nothing is installed
automatically — each refresh only re-ranks and rewrites this file, then opens a PR
for review.

In this cloud environment the refresh runs as a **scheduled Routine** (the
web/remote equivalent of the desktop Task Scheduler job), not a local PowerShell
script. See the research log below for each run.

---

## Research log

### 2026-07-10 — Initial brief
- Established methodology (source popularity + gap relevance) and exclusion rules.
- Confirmed existing library already covers marketing/CRO/advisor/eng deeply (~250 skills).
- Ranked the top 15 gap-filling skills across landing-page, visual-design, motion,
  interactive-web, and testing.
- Key finds: official `frontend-design` (277k+ installs), `Superpowers` (~94k★),
  `freshtechbro/claudedesignskills` (3D/motion bundle), `jezweb/claude-skills` (~911★),
  `199-biotechnologies/motion-dev-animations-skill` (Motion.dev).
