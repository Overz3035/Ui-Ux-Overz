---
name: problem-space
description: Map what we're optimizing and what constraints we treat as real. Use before jumping to solutions, when hitting repeated blockers, or when patches keep accumulating.
---

# /problem-space

Map the terrain where solutions live: objective, constraints, systems, assumptions, and what would prove the map wrong.

Problem space precedes solution space. Jump to code too early and you build the wrong thing fast.

## When to Use

- Starting new work before implementation
- Repeated blockers or patches keep appearing
- Estimates are badly off
- Constraints are being hand-waved away

**Skip when:** The problem is well-understood and you are in execution.

## The Problem Space Process

### Step 1: State the Objective

> "We are optimizing for [outcome]."

Name the behavior change, metric, or problem disappearance that indicates success. Features are not objectives.

### Step 2: Map Constraints

List what is treated as fixed:

```markdown
Constraint: [boundary]
Type: [hard | soft | assumed]
Reason: [why it exists]
Questioning: [could this be false?]
```

Hard constraints do not bend. Soft and assumed constraints can be questioned. Do not talk yourself out of real constraints because implementation feels easy.

### Step 3: Identify Terrain

Capture only terrain that changes decisions:
- systems involved;
- affected users/operators/downstream systems;
- blast radius if wrong;
- precedents or local metis.

If RNA/OH context tools are available, surface guardrails and metis as candidates with provenance; the human selects what carries forward.

### Step 4: Build the Situation Model

Connect objective, terrain, constraints, assumptions, evidence quality, and open questions. Facts with no decision impact are noise.

### Step 5: Stress the Map

Make hidden assumptions visible. Check for X-Y mismatch. Name frame-stress signals: evidence that constraints, terrain, assumptions, or precedents were wrong.

If constraints, assumptions, or open questions remain implicit, you are not ready for `/solution-space`.

## Output Format

```markdown
## Problem Space

**Scope:** [what area this covers]

### Objective
[Outcome, not feature]

### Constraints
| Constraint | Type | Reason | Question? |
|------------|------|--------|-----------|
| [boundary] | hard/soft/assumed | [why] | [could this be false?] |

### Terrain
- **Systems:** [what's involved]
- **Stakeholders:** [who's affected]
- **Blast radius:** [what breaks if wrong]
- **Precedents/metis:** [existing local knowledge]

### Situation Model
- **Explains:** [why these elements matter]
- **May hide:** [blind spots]
- **Evidence quality:** [observed / inferred / assumed]

### Assumptions and Open Questions
- [assumption or unknown] — [risk if false / when to answer]

### Frame-Stress Signals
- [evidence that should trigger problem-space revision]

### Ready for Solution Space?
[yes/no] - [why or what's missing]
```

## Session Handoff

If a session file is in use, read prior `Aim`, then replace or append `## Problem Space`. Later phases carry forward explicit constraints, assumptions, evidence quality, frame-stress signals, and open questions.
