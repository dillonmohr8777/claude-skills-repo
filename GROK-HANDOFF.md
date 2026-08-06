# Grok handoff: skills and design systems

Snapshot: 2026-08-06  
Repository: `dillonmohr8777/claude-skills-repo`  
Reviewed `main`: `36f709e88562d7ae50ba8b582b4776f477948c4a`

This repository is a reusable skill, brand-asset, IMMOHRTAL, and vault-content source. A skill's `SKILL.md` is its contract. Read the complete file before using the skill, follow its linked references/scripts, and do not merge similarly named skills by assumption.

## Website-design load order

1. `skills/brand-guidelines` for client-specific identity, asset, voice, and composition rules.
2. `skills/ui-design-system` for tokens, components, responsive behavior, and design-system consistency.
3. `skills/senior-frontend` for implementation architecture and production-quality frontend work.
4. `skills/landing-page-generator` for bounded landing-page structure and conversion flow.
5. `skills/ux-researcher-designer` for user/task evidence and interaction decisions.
6. `skills/epic-design` only when a highly art-directed surface is justified.
7. `skills/browser-automation` / `skills/browserstack` for deterministic browser verification.
8. `skills/copywriting`, `skills/copy-editing`, and `skills/content-humanizer` for final copy craft.
9. `skills/seo-audit`, `skills/seo-auditor`, `skills/ai-seo`, and `skills/programmatic-seo` when search/AEO scope is explicit.

The installed Impeccable workflow is the current craft floor for substantive UI work even though the canonical Impeccable package is installed outside this repository. Preserve `PRODUCT.md` and `DESIGN.md`, run the production build, inspect the real page at desktop/mobile widths, and use `npx impeccable detect` where applicable.

## Dillon OS skills

- `agent-designer`, `agent-workflow-designer`, `agent-protocol`, and `agents` for bounded agent roles and handoffs.
- `agenthub` and `autoresearch-agent` for explicitly orchestrated multi-step work, not as a second canonical queue.
- `self-improving-agent` only with reviewable evidence and without silent durable-memory writes.
- `mcp-server-builder` for MCP implementation behind the project's acceptance/security gate.
- `api-design-reviewer`, `api-test-suite-builder`, `ci-cd-pipeline-builder`, and `tdd-guide` for system hardening.

For Dillon OS itself, its repository-local `AGENTS.md`, `CLAUDE.md`, `12_Brain/` rules, and `.claude/skills/` override generic skill guidance.

## Align HCM source skills

- `skills/alignhcm-brand`: primary Align voice, visual, logo, color, and brand constraints.
- `skills/alignhcm-smartcare`: SmartCare positioning and content/creative system.
- `skills/alignhcm-carousel-video`: Align carousel/video production workflow.
- `skills/content-production`, `skills/content-strategy`, `skills/social-content`, and `skills/video-content-strategist`: supporting production lanes.

Use the exact Align logo and current approved references. The live canonical client context and portal/account evidence in Client Operations outrank cached examples in a generic skill.

## UI, motion, and frontend rules

- Existing codebase and client design system win over framework preference.
- Preferred greenfield stack: React/Next.js with TypeScript, Tailwind, shadcn-style accessible primitives, and Framer Motion for purposeful state explanation.
- Use Three.js/R3F only when 3D materially supports the concept; always provide reduced-motion and non-WebGL fallbacks.
- Avoid generic gradient dashboards, repeated rounded cards, excessive pills, template symmetry, and decorative motion.
- Do not reconstruct logos or fabricate wordmarks when verified assets are unavailable.

## Assets and vault

- `brand-logos/` currently contains product/vendor logos used by spa/beauty work: Amika, Circadia, Dermalogica, FarmHouse Fresh, GrandeLASH-MD, Image Skincare, K18, Medik8, Obagi Medical, Olaplex, Redken, Skinbetter Science, and SkinCeuticals.
- These assets are not a universal client logo library. Verify provenance, trademark context, and the exact client relationship before use.
- `immohrtal/` contains IMMOHRTAL-specific material. It is exclusive to the IMMOHRTAL artist/site lane.
- `vault/01_Clients/` is supporting historical context. Current Client Operations registry, queue, evidence, and approvals outrank it.

## Custom workflow truth

Treat the following as source-of-truth categories only within their exact contracts: Align HCM brand/SmartCare/video skills; the repository's brand-guideline and UI design-system skills; agent protocol/workflow skills; and any project-local skill in Dillon OS. Do not let a generic web, content, or agent skill override an exact client route, current evidence, approval gate, or project-local instruction.

## Grok: next 48 hours

1. Load the exact project-local rules first, then the smallest relevant skill set above.
2. Audit the 16 open draft PRs. Merge only current capabilities/artifacts; close superseded session branches after preserving unique work.
3. Verify Align-specific skills against the current brand and Client Operations context.
4. Keep IMMOHRTAL and client assets isolated.
5. Do not copy secrets, raw communications, or stale vault state into a skill or handoff.
