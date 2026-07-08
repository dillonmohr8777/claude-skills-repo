---
name: "mirror"
description: "Faithfully mirror, improve, or migrate a landing page or site across GHL, Wix, Squarespace, WordPress, Netlify, or Vercel. Reads the live page first (URL, forms, scripts, tracking tags, CTAs, copy, disclaimers), preserves everything that matters, builds the smallest faithful version, QAs desktop + mobile, and deploys only after QA. When dashboard control is flaky, produces a paste-ready optimization packet instead. Use for any page rebuild/clone/migration."
---

# Mirror — faithful page rebuild / improve / migrate

> Captured into the repo from Dillon's core workflow #2 (was local-only). If a richer local version
> exists, merge it here so this is the single source of truth.

The web lane's workhorse. Called by `morning-orchestrator` / Web Design Lane, or run standalone.

## First: decide the mode
- **Mirror** — faithful rebuild. Preserve forms, links, phone numbers, tracking tags, CTAs, disclaimers **exactly**.
- **Improve** — keep structure, lift conversion (hero, form friction, proof, mobile).
- **Migrate** — move platforms. Add a move log; preserve tracking + SEO (URLs, titles, 301s).

## Flow
1. **Read the live page** — capture URL, title, screenshots, forms, scripts, tracking tags (GA4/GTM/pixel), CTAs, phone numbers, and visible copy. This is the spec.
2. Confirm the mode (mirror / improve / migrate).
3. Reuse the existing local project lane from `PROJECTS.md`; keep source files untouched.
4. Copy assets only when needed.
5. **Preserve** tracking, forms, links, phone numbers, and legal/disclaimer text — non-negotiable.
6. Build the smallest faithful static or app version. Reuse parts from `08_Assets/web-kit/`.
7. **QA desktop and mobile** (mobile checklist in the Web Design Lane).
8. Deploy only after QA **and** only if a live URL was requested — deploy is Tier 2 (live approval).

## Flaky-dashboard fallback
For GHL or heavy dashboards where direct UI control drops: produce a **paste-ready optimization packet**
from public-page evidence (exact copy blocks, section order, form fields, CTA text), then retry real
Chrome only when the browser surface is healthy. Never guess at content you couldn't read.

## Tiers
- Read live page, capture spec, build, QA → **Tier 0** (autonomous).
- Reversible on-page copy/link/CTA fixes on an existing page → **Tier 1** (morning batch).
- Publish / production deploy / platform migration cutover → **Tier 2** (live approval).

## Rules
- Read before you touch. Preserve tracking/forms/legal. Keep source files untouched.
- Real Chrome for authenticated platforms (local machine, CDP). Public pages fine anywhere.
- Mobile QA gates every deploy.

## Writes to
- `01_Clients/<Client>/Reporting Log.md` (append)
- `02_Campaigns/Landing Page Build Queue.md`
- `08_Assets/web-kit/` (reusable parts extracted during builds)
