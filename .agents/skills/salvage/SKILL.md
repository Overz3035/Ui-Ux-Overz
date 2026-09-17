---
name: salvage
description: Extract learning before restarting. Code is a draft; learning is the asset. Use when work is drifting, approach has reversed 3+ times, or scope is expanding while "done" keeps fuzzing.
---

# /salvage

Extract learning before restarting. **Code is cheap; learning is the asset.**

## When to Use

Invoke `/salvage` when work is drifting, approach reversed multiple times, scope keeps expanding, the finish line keeps moving, or starting over feels right.

**Do not use when:** Work is on track. Salvage is extraction before restart, not routine reflection.

## JIT References

Load [references/extraction.md](references/extraction.md) only when a salvage needs deeper learning extraction than the core report.

## The Salvage Process

### Step 1: Acknowledge the State

> "This session/approach is being salvaged because [reason]. The original aim was [aim]. What happened was [reality]."

### Step 2: Extract What Matters

Extract only what is present; do not pad empty categories.

Core categories:
- **Learnings:** what changed your understanding?
- **Frame shifts:** what story stopped explaining reality?
- **Guardrails:** what constraint was discovered the hard way?
- **Missing context:** what should have been found or asked earlier?
- **Ownership / coordination:** what authority, owner, handoff, review, dissent, or verification boundary blurred?
- **Reusable fragments:** what code, pattern, or partial approach is worth keeping?

If RNA/OH tools are available, check existing metis/guardrails before writing new ones. Update or strengthen existing entries rather than creating near-duplicates.

### Step 3: Package for Fresh Start

Synthesize a restart kit: original aim, why salvaged, key learnings, frame shift, new guardrails, ownership/coordination breakdown, context for restart, and reusable fragments.

### Step 4: Persist Learning

Persist metis, not noise. Record only non-obvious constraints, anomalies, trade-offs, and local patterns that would change a later decision. Generic best-practice advice adds context cost without local leverage.

If repeated salvages surface the same learning, run `/distill`; the corpus has knowledge but it is not being consulted.

## Output Format

```markdown
## Salvage

### Salvage Report

**Salvaged:** [date/session identifier]
**Reason:** [why this work is being salvaged]
**Original Aim:** [what we were trying to do]

### Learnings
[Numbered list of key insights]

### Frame Shifts
[Old frame → new frame, with evidence]

### New Guardrails
[Explicit constraints with reason and trigger]

### Missing Context
[What would have helped]

### Ownership / Coordination Breakdowns
[Authority boundary, missing owner, or handoff rule]

### Reusable Fragments
[Code or patterns worth keeping]

### Fresh Start Recommendation
[How to approach this next time]
```

## Session Handoff

If a session file is in use, read prior phase sections, then replace or append `## Salvage`. Later attempts use the salvage report as restart context, not as a mandate to preserve failed code.
