---
name: "ponytail"
description: "Minimal-code discipline — write the least code that works, like the laziest senior dev in the room. Use before generating new code, adding a dependency, or building a feature, and when the user says 'keep it simple', 'don't over-engineer', 'ponytail', 'minimal', 'no bloat', or asks for a lean implementation. The best code is the code you never wrote."
license: MIT
metadata:
  version: 1.0.0
  author: dillonmohr8777
  category: engineering
  updated: 2026-07-10
---

# Ponytail

Think like the laziest senior dev in the room. The best code is the code you never wrote. Every line is a line someone has to read, test, and maintain at 3am. Inspired by ponytail.dev, rebuilt for this repo.

## The Ladder — climb it in order, stop at the first rung that works

Before writing ANY new code, walk down this list and stop as soon as one answers the need:

1. **Do we even need it?** — YAGNI. Skip speculative features, config knobs, and abstractions for one caller. Ask: does the user need this now, or am I guessing they might later?
2. **Does the codebase already do this?** — Reuse an existing function, component, util, or pattern. Grep first.
3. **Does the standard library do this?** — Built-in language features beat hand-rolled code.
4. **Does the platform do this?** — Native browser/OS/runtime features (CSS, HTML form validation, `Intl`, `URL`, `fetch`) before any library.
5. **Does a current dependency do this?** — Use packages already in `package.json` / requirements before adding new ones.
6. **Can it be one line / one small function?** — If a tiny inline solution is clear and safe, ship that.
7. **Only now: write the minimum working code.** — Smallest change that fully solves it. No scaffolding for imagined futures.

## Hard rules

- **No new dependency** without justifying why rungs 3–5 can't cover it. A dependency is a permanent liability.
- **No new abstraction for a single caller.** Inline it. Abstract on the *third* repetition, not the first.
- **No speculative flexibility.** Config options, plugin hooks, and "just in case" params are debt until proven needed.
- **Delete-first mindset.** If a change lets you remove code, that's the win. Prefer diffs that are net-negative lines.
- **Match the existing code.** Fewer new patterns = less to learn. Consistency over cleverness.

## Never sacrifice

Lazy about *volume*, never about *correctness*. Do NOT skimp on:
- Input validation and error handling on real boundaries
- Security (authz, injection, secrets)
- Correctness and edge cases
- Tests for logic that can break

Minimal ≠ fragile. Write the least code that is still *safe and complete*.

## Intensity

- **lite** — flag obvious over-engineering, still helpful with scaffolding
- **full** (default) — enforce the ladder on new code
- **ultra** — aggressively push back; refuse to add code/deps without clearing the ladder out loud

## When reviewing existing code

Hunt for: dead code, unused deps, one-caller abstractions, hand-rolled stdlib/platform equivalents, copy-paste that wants one helper, config nobody sets. Propose deletions first.

## Litmus test before shipping

> "If a senior dev who hates writing code saw this diff, would they say 'why is this so big?' — or nod?"

Aim for the nod.
