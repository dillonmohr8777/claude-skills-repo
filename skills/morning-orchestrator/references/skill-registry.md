# Skill & Plugin Registry — routing the swarm to Dillon's toolkit

The point: the orchestrator should **use the skills and plugins Dillon already built and relies on**, not
reinvent them. Every worker, before it builds anything, checks `skill-map.json` for a matching skill and
invokes it. Build-from-scratch is the fallback, not the default.

## How routing works
1. A worker gets a job (`lane` + `objective`).
2. It looks up the lane in `skill-map.json` → gets `primary`, then `supporting`, then `pinned_most_used`.
3. **Pinned skills win ties** — the ones Dillon reaches for most.
4. If nothing matches, it logs the job to `Morning Directives` for Dillon to route/name, and does the minimal safe version.

## Lane → skill routing (populate `pinned` as you confirm)

| Lane | Reach for first | Also | Dillon's most-used? |
|------|-----------------|------|---------------------|
| **Ads** | `campaign-intel`, `paid-ads` | ab-test-setup, campaign-analytics, marketing-psychology, analytics-tracking | _confirm_ |
| **Ads creative** | `ad-creative` | content-creator, copywriting | _confirm_ |
| **Web / design** | `mirror`, `landing-page-generator`, `page-cro` | form-cro, ui-design-system, a11y-audit, schema-markup, site-architecture, apple-hig-expert | _confirm_ |
| **Web automation** | `browser-automation`, `playwright-pro` | — | _confirm_ |
| **SEO / AEO** | `ai-seo`, `seo-audit` | seo-auditor, programmatic-seo, schema-markup | _confirm_ |
| **Reporting** | `client-report`, `metrics-pull` | product-analytics, social-media-analyzer | _confirm_ |
| **Comms** | `inbox-brief` | cold-email, email-sequence, team-communications, churn-prevention | _confirm_ |
| **Research** | `deep-research`, `autoresearch-agent` | research-summarizer, competitive-intel, competitive-teardown | _confirm_ |
| **Command / meta** | `am-report`, `plan-today`, `client-pulse` | self-improving-agent, agent-designer, orchestration, prompt-engineer-toolkit | _confirm_ |

## Your action (5 min, one time)
In `skill-map.json → pinned_most_used`, set the **skills and plugins you actually use most**. Prune the
placeholder list to reality. That's the only manual step — after that the swarm routes itself, and the
`self-improving-agent` skill can promote new recurring jobs into new pinned skills over time.

## Plugins
The map can't see which plugins are installed on the machine — resolve those at boot and reconcile
against `pinned_most_used.plugins`. Skills packaged as plugins (they have a `.claude-plugin/plugin.json`,
e.g. `self-improving-agent`, `research-summarizer`, `behuman`) route the same as any skill.

## Keeping it current
- New skill added to the repo → add it to the relevant lane here + in `skill-map.json`.
- A job type keeps recurring with no matching skill → `agent-designer` / `self-improving-agent` drafts a new skill for it, and it gets pinned.
- Mirror skill: now captured at `skills/mirror/` (was local-only). If the local version is richer, merge it in.
