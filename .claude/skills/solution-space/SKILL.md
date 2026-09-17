---
name: solution-space
description: Explore candidate solutions before committing. Use when you have a problem statement and need to evaluate approaches - band-aid, optimize, reframe, or redesign.
---

# /solution-space

Explore candidate solutions before committing. The trap is defending the first workable idea.

Solution space is plausibility-driven: create a coherent enough story to choose the next action, not a perfect map of every possible option. Detail earns its place only when it changes the recommendation.

## When to Use

- Problem is framed and more than one approach is viable
- You are about to start coding
- Patches or flags are accumulating
- You feel attached to the first idea

**Skip when:** Still clarifying the problem. Use `/problem-statement` first.

## JIT References

Load [references/depth.md](references/depth.md) only when options are high-stakes, too similar, or the recommendation feels overconfident.

## The Process

### Step 1: Confirm the Frame

> "The problem we're solving is: [statement]. The binding constraint is: [constraint]. The working story is: [plausible frame]. Success would look like: [signal]."

If you cannot state this clearly, return to `/problem-statement`. Do not add detail to compensate for an unclear frame.

If `## Problem Weave` exists, read its candidate S&T steps and sufficiency groups. Treat them as hypotheses, not preselected work. Keep their IDs so the recommendation can select, reject, or defer each step.

### Step 2: Generate Candidates

List 3-4 materially different candidates before evaluating. Include the obvious option, status quo when real, and at least one option that changes altitude: band-aid, local optimum, reframe, or redesign.

### Step 3: Evaluate Only Decision-Changing Differences

Before scoring, name the decision criteria, critical assumptions, and constraints that eliminate options early. Then prune aggressively.

For each candidate, answer:
1. Does it solve the stated problem?
2. What frame does it assume?
3. What is the main implementation or maintenance cost?
4. What second-order problem or future option does it create?


For any candidate that names a second-order problem, hidden assumption, or plausible alternate frame, decide its risk-retirement disposition using `/execute` vocabulary: **Retired by evidence**, **Accepted with rationale**, or **Triggered**. For every **Retired by evidence** item, name the tempting wrong patch or local maximum that the check must fail. A named risk may not disappear in handoff.

### Step 4: Check Interpretive Variety

Make sure the option set is not one frame in costumes. Name which option assumes the current frame, which tests it, and what failure would teach.

If every candidate shares the same hidden frame, generate one different-frame candidate or return to `/problem-statement`.

### Step 4.5: Build the Risk Retirement Plan

Convert uncertainty into action before recommending. For each critical assumption, plausible alternate frame, and stop/pivot trigger, choose one planned disposition: **Retired by evidence** with an adversarial check, **Accepted with rationale** because it is outside scope or requires human/domain judgment, or **Triggered** if evidence would invalidate the selected approach.

An adversarial check must be able to fail the first workable idea, tempting band-aid, or local optimum that would leave the named risk alive. If the check would also pass the patch you are worried about, it is not a retirement check; strengthen it or route to `/problem-statement`.

Do not defer the choice to `/execute`. If the selected option depends on ignoring a plausible alternate frame that is model-checkable now or cheaply during execution, add an adversarial check to the handoff. If no credible evidence path exists for a critical assumption, return to `/problem-statement` because the frame is not ready.

### Step 5: Recommend

Select the approach that is plausible enough under current constraints. If the recommendation is a one-way door — architecture, public API, data model, external commitment — run `/dissent` before `/execute`.

When a Problem Weave exists, map the chosen approach back to its S&T steps:

- mark only steps required by the recommendation `selected`;
- mark disproven tactics `rejected` and unneeded-but-still-plausible tactics `deferred`;
- preserve parent step, sufficiency group, owner, review trigger, and accepted trade-offs;
- do not select a child whose required parent or sibling sufficiency set is absent without naming the gap;
- route only selected step IDs to `/oh-plan`; candidate and deferred steps remain visible but unplanned.

## Output Format

```markdown
## Solution Space

### Solution Space Analysis

**Problem:** [One sentence]
**Key Constraint:** [The binding constraint]
**Working Story:** [The plausible frame that makes this recommendation sensible]
**Success Signal:** [What later phases should verify]
**Decision Criteria:** [What matters most and how options were compared]
**Critical Assumptions:** [Premises the selected approach depends on]

### Candidates Considered
| Option | Level | Approach | Main Trade-off |
|--------|-------|----------|----------------|
| A | [Band-Aid / Local Optimum / Reframe / Redesign] | [Brief] | [Cost] |
| B | [Level] | [Brief] | [Cost] |
| C | [Level] | [Brief] | [Cost] |

### Interpretive Variety Check
- Same frame or different frames? [brief answer]
- Current-frame test: [which option most assumes/tests the current frame]
- Failure would teach: [what failure would mean and where learning routes]

### Risk Retirement Plan
| Risk / Assumption / Alternate Frame | Planned Disposition | Tempting Patch This Must Fail | Required Evidence or Rationale | Stop/Pivot If |
|-------------------------------------|---------------------|-------------------------------|--------------------------------|---------------|
| [Named uncertainty] | [Retired by evidence / Accepted with rationale / Triggered] | [wrong-but-plausible local patch, or "N/A — accepted/triggered"] | [adversarial test/check/rationale/human decision] | [trigger] |

### Recommendation
**Selected:** Option [X] - [Name]
**Level:** [Band-Aid / Local Optimum / Reframe / Redesign]

**Rationale:** [Why this approach is plausible enough under current constraints]

**Accepted trade-offs:**
- [Trade-off 1]
- [Trade-off 2]

### S&T Selection
| Step ID | Disposition | Parent | Sufficiency group | Why this disposition | Owner | Review trigger |
|---|---|---|---|---|---|---|
| [id] | [selected/rejected/deferred] | [root/id] | [group id] | [connection to recommendation/evidence] | [role] | [when to reassess] |

**Selected-step sufficiency:** [why the selected set covers the chosen strategy, or the explicit gap that blocks planning]

### Execution Handoff
- Preserve: [criterion or behavior later phases must preserve]
- Verify via: [signal `/execute` and `/ship` should be able to check]
- Decision criteria: [comparison basis `/execute` should preserve]
- Critical assumptions: [premises to monitor during execution]
- Accepted trade-offs: [costs consciously accepted]
- Risk retirement checks: [planned disposition plus adversarial tests/inspections/rationales required for every named risk or alternate frame; each evidence check names the tempting patch it must fail]
- Invalidated if: [what evidence would make this direction wrong]
- Stop/pivot triggers: [conditions that require pause, escalation, or strategy change]
- Needs human verification: [claim or decision the model cannot self-check, or "none"]
```

## Session Handoff

If a session file is in use, read `Aim`, `Problem Statement`, `Problem Space`, and optional `Problem Weave`, then replace or append `## Solution Space`.

- `/execute` reuses the selected approach, working story, success signal, criteria, assumptions, trade-offs, risk-retirement checks, invalidation signal, stop/pivot triggers, and S&T dispositions.
- `/oh-plan` consumes only `selected` S&T step IDs and their lineage.
