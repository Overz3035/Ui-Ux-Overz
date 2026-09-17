---
name: execute
description: Do the work. Pre-flight, build, detect drift, salvage if needed. Use when you have a clear aim and are ready to implement.
---

# /execute

Bridge from Solution Space to shipped code: pre-flight, build, detect drift, course-correct or salvage.

## When to Use

Invoke `/execute` when aim is clear, solution is chosen, context is loaded, and you are ready to build.

**Do not use when:** Aim is unclear (`/aim`), options are still open (`/solution-space`), or the problem is ambiguous (`/problem-space`, `/problem-statement`).

## JIT References

Load [references/drift-boundaries.md](references/drift-boundaries.md) when execution starts changing the aim, scope, frame, or decision authority, or when the work may be hard to reverse.

## The Execute Process

### Step 1: Pre-flight

```markdown
Pre-flight Checklist:
[ ] Aim is clear — what outcome am I producing?
[ ] Constraints known — what must I not break?
[ ] Context loaded — do I understand the codebase and handoff?
[ ] Scope bounded — what am I doing and not doing?
[ ] Success criteria clear — how will I know when done?
[ ] Decision basis clear — selected approach, criteria, assumptions, trade-offs, invalidation, and stop/pivot triggers carried forward?
[ ] Authority boundaries clear — review, dissent, and human/domain-owner calls routed correctly?
[ ] Readiness clear — why deepen now, what invalidates this, what triggers stop/pivot?
[ ] Risk retirement clear — every named risk, alternate frame, invalidation signal, and stop/pivot trigger has a concrete check or an explicit evidence-backed reason it is out of scope?
```

If a box cannot be checked, stop and address it first. If the work is a one-way door and `/dissent` has not run, flag it before proceeding.

Declare the phase shift:
> "The task is [task]. The aim is [aim]. This ladders back to [selected approach] because [decision criteria]. Scope is [scope]. Out of scope is [non-goals]. Success is [criteria]. Assumptions are [critical assumptions]. Accepted trade-offs are [trade-offs]. Invalidated if [condition]. Stop/pivot if [trigger]."

Before editing, translate the handoff into an execution checklist: declared success criteria, preservation constraints, adversarial risk-retirement checks, invalidation checks, and stop/pivot triggers. Every model-checkable named risk gets a check before completion; each evidence check must name the tempting wrong patch it would fail. Mark **Accepted with rationale** only when the risk is outside scope, not model-checkable in this environment, or requires human/domain judgment, and state why.

### Step 2: Build

Retire named risks as you build: each risk must become a passing adversarial test/check, an evidence-backed non-issue, or a pause/pivot. A check is adversarial only if it could fail the first workable idea or local patch that would leave the risk alive.

Work in small, testable increments. Stay within declared scope. Verify behavior with the narrowest credible check that can falsify the tempting shortcut, not merely confirm the selected implementation's happy path. Run `/review` or the repo's review workflow when available. Commit logical units with clear messages.

### Step 3: Detect Drift

```markdown
Drift Check:
- Original aim: [aim]
- What I'm doing now: [current work]
- Gap: [divergence]
- Verdict: [aligned | minor drift | significant drift | lost]
- Authority boundary: [clear | ambiguous | crossed]
```

Aligned: continue. Minor drift: note and refocus. Significant drift: pause, refocus, confirm scope change, or salvage. Lost: invoke `/salvage`.

### Step 3.5: Risk Retirement Gate

Before declaring execution complete, review every risk, alternate frame, invalidation signal, and stop/pivot trigger inherited from `/solution-space`.

For each one, record one of:

- **Retired by evidence:** a test, code inspection, runtime check, or documented observation directly covers it and would fail the tempting wrong patch or alternate failure mode.
- **Accepted with rationale:** it is outside scope, not model-checkable in this environment, or requires human/domain verification; the rationale names that boundary explicitly.
- **Triggered:** evidence matched an invalidation or stop/pivot condition; pause and route to `/problem-statement`, `/problem-space`, `/review`, or `/salvage`.

Do not mark execution complete with a model-checkable named risk left untested, and do not downgrade a handed-off check to "accepted" because it is inconvenient. Do not count a non-adversarial check as retirement; if the check would pass the tempting wrong patch, route to Adjust. Naming a risk and then shipping through it is drift.

### Step 4: Salvage if Needed

Stop when the approach has reversed repeatedly, scope keeps expanding, oscillation replaces convergence, or the finish line keeps moving. Extract learning with `/salvage` instead of protecting sunk-cost code.

## Output Format

```markdown
## Execute

### Execution Complete

**Task:** [what was done]
**Aim achieved:** [how it maps to the original aim]

### Declared Success Criteria
- [criterion]

### Delivered Characteristics
- [characteristic/result]: [met | partially met | deferred]

### Changes
- [file/component]: [what changed and why]

### Verification
- [test/check/manual observation]

### Risk Retirement
| Risk / Assumption / Stop Trigger | Status | Tempting Patch This Check Fails | Evidence / Route |
|----------------------------------|--------|---------------------------------|------------------|
| [Named item from handoff] | [retired / accepted / triggered] | [wrong-but-plausible local patch, or "N/A"] | [adversarial test/check/rationale/next route] |

### Needs Human Verification
- [claim the model cannot independently confirm, or "none — because ..."]

### Notes
- [future-relevant note]
```

When drift triggers a pause:

```markdown
## Execute

### Execution Paused - Drift Detected

**Original aim:** [aim]
**Current state:** [where things stand]
**Drift:** [what diverged and why]

### Options
1. [option]
2. [option]
3. Salvage and restart

Recommendation: [assessment]
```

## Session Handoff

If a session file is in use, read `Aim`, `Problem Statement`, and `Solution Space`, then replace or append `## Execute`. `/execute` preserves the selected approach, decision criteria, critical assumptions, accepted trade-offs, invalidation signal, stop/pivot triggers, and risk-retirement results; `/ship` and `/review` use declared success criteria, delivered characteristics, verification, risk-retirement evidence, and authority/frame drift.
