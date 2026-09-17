---
name: aim
description: Clarify the outcome you want - a change in user behavior, not a feature shipped. Use at the start of any work to ground the session in strategic intent.
---

# /aim

Clarify the outcome you want. An aim is a change in user behavior, not a feature shipped. First step in Intent-Execution-Review.

**The aim IS the abstraction.** Clarifying what behavior to change abstracts the business domain itself. Features are mechanism; the aim is why they matter.

## When to Use

- **Starting new work** — before problem-statement or problem-space
- **Scope feels fuzzy** — you can describe what but not why
- **Multiple solutions seem valid** — aim reveals which moves the needle
- **Work has drifted** — check alignment
- **Stakeholders are misaligned** — surfaces hidden assumptions

**Skip when:** You already have a crisp aim. Move to `/problem-statement` or `/problem-space`.

## The Aim Process

### Step 1: State the Desired Behavior Change

Start with the user, not the system.

> "Users will [specific behavior] instead of [current behavior]."

Bad: "Add dark mode toggle"
Good: "Users can work comfortably at night without eye strain"

Bad: "Improve onboarding flow"
Good: "New users reach their first value moment within 5 minutes"

**Key distinction:** Features are outputs. Behavior changes are outcomes. If users don't become more capable, shipping more output doesn't rescue the work.

### Step 2: Identify the Mechanism

The mechanism is your hypothesis — the causal lever you believe produces the behavior change.

```
Mechanism: [What you're changing]
Hypothesis: [Why you believe it will produce the outcome]
Assumptions: [What must be true for this to work]
```

If you listed zero assumptions, that is a red flag, not a clean bill of health. Every mechanism rests on premises. Name at least one or explain why none exist.

Watch for abstract qualities (simplicity, speed, clarity) posing as aims — these are mechanisms, not outcomes. Ask what they enable that their absence blocks.
### Step 3: Define the Feedback Signal

How will you know if the aim is achieved?

> "We'll know it's working when [observable signal]."

Signals must be **observable**, **timely**, and **attributable** to your mechanism.

### Step 4: Check Shared Intent

Before guardrails, protect the aim from premature mechanism:
- Can each stakeholder restate the same behavior change and why it matters?
- Is the mechanism still a hypothesis, not the aim itself?
- What evidence would show the aim was misunderstood?

### Step 5: Set Guardrails

What constraints bound this work? What would cause you to stop?

```
Guardrail: [boundary]
Reason: [why this matters]
Trigger: [when to revisit]
```

## Output Format

```
## Aim

**Aim:** [One sentence: the behavior change you want]
**Why it matters:** [User or business consequence if this behavior does not change]

**Current State:** [What users do now]
**Desired State:** [What users will do after]

### Mechanism
**Change:** [What you're building/changing]
**Hypothesis:** [Why you believe this produces the outcome]
**Assumptions:** [What must be true]
**Misunderstanding Signal:** [What you'd see if people understood the feature but missed the aim]

### Feedback
**Signal:** [How you'll know it's working]
**Timeframe:** [When you'll have signal]

### Guardrails
- [Guardrail 1]
- [Guardrail 2]
```

Later phases carry forward the aim's explicit fields — outcome, why it matters, mechanism as hypothesis, assumptions, feedback signal, guardrails, and misunderstanding signal — as the contract the rest of the workflow preserves.

## Session Handoff

If a session file is in use, replace or append `## Aim`. Later phases read this section as the canonical aim contract.
