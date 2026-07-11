# Multi-Agent Workflow Patterns: Claude + Codex

How to combine Claude and Codex productively. Each pattern below has a concrete trigger ("use this when…"), a concrete recipe, and an explicit failure mode to watch for.

The mental model: Claude and Codex are not interchangeable. They have different strengths, different blind spots, and (usefully) different training. The patterns below exploit those differences instead of pretending they don't exist.

---

## Pattern 1: Implement-Claude / Review-Codex

**Use when:** Claude wrote the change. Before committing, you want a non-author review.

**Recipe:**
1. Claude implements.
2. Stop before staging.
3. Run `/codex:review` (or `/codex:review --base main` for branch review).
4. Address every MEDIUM-or-higher finding.
5. Re-run `/codex:review` if the fix was non-trivial.
6. Then commit.

**Failure mode:** dismissing findings as "Codex didn't see the conversation." That's exactly the perspective shift you wanted — the conversation is the *bias*, not the *context*.

---

## Pattern 2: Plan-Claude / Execute-Codex

**Use when:** Design needs nuanced discussion (Claude is good at this), but execution is mechanical and repetitive (Codex is good at this, and won't drift).

**Recipe:**
1. Discuss the plan with Claude. Iterate until you have a written spec — a `PLAN.md` file or a numbered list in chat.
2. Save the spec to a file in the repo.
3. Hand off:
   ```
   /codex:rescue --background --fresh implement the design in PLAN.md exactly as written. do not deviate from file/function names listed in section 3. open questions: ask as TODO comments rather than guessing.
   ```
4. While Codex executes, keep working on something else in Claude.
5. `/codex:status` → `/codex:result <id>` when done.
6. Review the output yourself or with Pattern 1.

**Why:** Long Claude sessions drift from their own plan as context fills up. Codex starting fresh from a written spec doesn't have that problem.

**Failure mode:** Under-specifying the plan. Codex will guess; the guesses won't match your unstated assumptions. The spec needs file paths, function signatures, and acceptance criteria.

---

## Pattern 3: Adversarial Layered Review

**Use when:** A change is load-bearing (auth, data model, public API, security boundary) and you want maximum critical scrutiny before merge.

**Recipe:**
1. Run the local `adversarial-reviewer` skill (`/adversarial-review` if installed, or the skill prompt). This produces three hostile-persona reviews from Claude itself.
2. Run `/codex:adversarial-review` with steering text pointing at the same surface area. Codex produces an independent design critique.
3. Diff the two reviews. **Findings that appear in both** are highest priority — independent agents converging is strong signal.
4. Address those first. Then address Codex-only and Claude-only findings.

**Why:** Same-model adversarial review (just Claude playing personas) catches less than cross-model adversarial review. The personas trick reduces but doesn't eliminate Claude's own blind spots.

**Failure mode:** Treating "Codex agreed with Claude" as a green light. Two agents can be wrong in correlated ways — both trained on similar internet code, both miss similar edge cases. Convergence is *evidence*, not *proof*.

---

## Pattern 4: Background Bug Rescue

**Use when:** A bug is going to take >15 minutes of investigation and you have other work to do.

**Recipe:**
1. Frame the bug clearly: symptom, repro steps, suspected area, what you've already ruled out.
2. ```
   /codex:rescue --background --fresh <framed bug description>
   ```
3. Note the job ID.
4. Switch back to Claude for unrelated work.
5. `/codex:status` periodically.
6. When done: `/codex:result <id>`. If the fix landed in the working tree, run Pattern 1 on it before committing.

**Failure mode:** Vague prompts. "Fix the failing tests" gives Codex no investigative direction; it'll thrash. Frame what you already know.

**Anti-pattern:** Background-and-forget. If you don't intend to come back and reap the result, don't kick it off — you're just burning quota.

---

## Pattern 5: Disagreement-Driven Decision

**Use when:** You're about to make a call that the team will live with for a long time, and you suspect Claude has been agreeing with you too easily.

**Recipe:**
1. State the proposed decision in one paragraph.
2. Ask Claude: "Argue *against* this proposal."
3. Run `/codex:adversarial-review` with the same proposal.
4. Compare. If both agents oppose the same way, you should probably reconsider.
5. If they oppose for different reasons, you have a richer picture of the risk surface than you'd have had from either alone.

**Why:** Most "the AI agreed with me" moments are sycophancy, not signal. Forcing structured disagreement from two independent agents extracts real signal.

**Failure mode:** Selecting the more agreeable agent's verdict because you'd already decided. If you're going to ignore both, save the API calls.

---

## Pattern 6: Long-Running Loop

**Use when:** A task is "investigate until you find it" — flaky test root cause, intermittent crash, performance regression bisect.

**Recipe:**
1. Set up the repro mechanically: a script that exercises the bug, ideally with a clear pass/fail signal.
2. ```
   /codex:rescue --background --effort high <task with repro script reference>
   ```
3. Codex can iterate locally — running tests, reading output, modifying code, re-running — without consuming your Claude context window.
4. Periodically check `/codex:status`.
5. When Codex declares done, verify the fix yourself and run Pattern 1 review on the change.

**Why:** Long investigative loops are the worst use of Claude's context — every retry burns tokens and the context fills up with old runs. Codex sessions are isolated from Claude's, so the cost of "another iteration" stays bounded.

**Failure mode:** No clear stopping condition. If Codex doesn't know what "done" looks like, it will declare done at the wrong time. Spell out the success criterion.

---

## Choosing Between Patterns

| Trigger | Pattern |
|---|---|
| About to commit Claude's code | 1: Implement-Claude / Review-Codex |
| Long task, want to keep working | 4: Background Bug Rescue or 2: Plan-Claude / Execute-Codex |
| Architectural decision that's expensive to reverse | 3: Adversarial Layered Review |
| Suspicion Claude has been agreeable | 5: Disagreement-Driven Decision |
| Iterative debugging with a repro script | 6: Long-Running Loop |
| Trivial change | None — just commit |

---

## Cost and Latency Considerations

- Each `/codex:*` call hits OpenAI and counts against your ChatGPT plan.
- Latency is real: a `/codex:review` of a 200-line diff is not free in wall time.
- Background jobs (`--background`) decouple latency from the Claude session but still cost the same.
- For trivial changes, the round-trip is dominant cost. Reserve patterns for non-trivial work.

---

## Composing With Other Skills in This Repo

- `adversarial-reviewer` → Pattern 3 (use both, compare findings).
- `agent-workflow-designer` → for codifying these patterns into a documented team workflow.
- `code-to-prd` → if you want Codex to write the PRD from Claude's plan.
- `tech-debt-tracker` → run `/codex:review` on the largest debt-cluster diffs before committing fixes.
