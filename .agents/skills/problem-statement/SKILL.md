---
name: problem-statement
description: Define the framing of a problem. Change the statement, change the solution space. Use when starting work, when solutions feel wrong, or when you suspect an X-Y problem.
---

# /problem-statement

Define the framing. **Change the statement, change the solution space.**

A problem statement is a lens, not reality. The goal is a plausible, coherent story that enables action and names what would make it wrong — not an exhaustive account.

## When to Use

- Starting new work before choosing solutions
- Solutions feel forced or workaround-shaped
- Approach keeps oscillating
- Requirements keep expanding
- You suspect an X-Y problem

**Skip when:** You already have a crisp problem statement. Move to `/solution-space`.

## JIT References

Load [references/framing.md](references/framing.md) only when the request may be X-Y shaped, examples would help, or the frame is becoming too detailed.

## The Framing Process

### Step 1: Name the Current Frame

> "The problem is currently framed as: [how it's being described]."

Capture only what changes the next move: stated problem, embedded assumptions, fixed vs. flexible constraints, and the simplest story that would make action sensible.

### Step 2: Separate WHAT from HOW

A good problem statement says what must change, not how to change it.

Test:
- Does it describe a symptom/outcome rather than a proposed solution?
- Could someone unfamiliar with the codebase understand what is wrong?
- Does it leave room for multiple approaches?

### Step 3: Identify Constraints

Name hard constraints, soft constraints, and assumptions. Question soft/assumed constraints; do not negotiate hard ones away.

### Step 4: Craft the Reframe

Use this shape:

> **[Who] needs [what outcome] because [why it matters], but currently [what's blocking].**

Good statements are crisp, outcome-focused, testable, solution-agnostic, and plausible enough to guide the next move.

### Step 5: Pressure-Test Lightly

Ask:
1. Does this frame enable action?
2. What does it reveal or hide?
3. What plausible alternate story would change the solution space?
4. Who would disagree, and what alternate story would they tell?
5. What evidence would show this is only a symptom?

## Output Format

```markdown
## Problem Statement

**Current framing:** [How the problem is currently being described]
**Reframed as:** [Your crisp problem statement]
**The shift:** [What changed in how we see it]

### Working Story
[The plausible story that makes this problem worth acting on now — concise, not exhaustive]

### Constraints
- **Hard:** [Actually immovable constraints]
- **Soft/assumed:** [Constraints that may be flexible]

### Assumptions Being Tested
- [assumption embedded in this framing]

### Frame Pressure Test
- Reveals/enables: [what this framing makes visible or easier]
- Hides/risks: [what this framing may obscure]
- Plausible alternate: [one alternate story that would change the solution space]
- Who disagrees: [stakeholder/role and the alternate story they would tell]

### Signal This Framing Is Wrong
[What evidence would show this frame is misleading or only a symptom]
```

## Session Handoff

If a session file is in use, read prior `Aim` / `Problem Space` and optional `Problem Weave` candidate frames, then replace or append `## Problem Statement`. Treat the weave as evidence and alternatives, not consensus. Later phases carry forward the working story, constraints, assumptions, pressure test, and invalidation signal.
