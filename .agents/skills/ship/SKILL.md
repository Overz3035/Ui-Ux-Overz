---
name: ship
description: Deliver code to users. Optimize the path from merged code to working install. Use when execution is complete and you need to get changes into users' hands.
---

# /ship

Optimize the delivery path from completed work to working install. **When execution is cheap, delivery is the work.**

Ship is the final step of the Execution phase. Code that isn't in users' hands isn't delivering value.

## When to Use

Invoke `/ship` when execution is complete, tests pass, review is done, and you need to get changes to users. Also usable as a standalone diagnostic: run `/ship` against a stalled delivery pipeline to surface delivery-path tax without deploying anything.

**Do not use when:** You're still building. Ship is for completed work.

## JIT References

Load [references/reality-contact.md](references/reality-contact.md) only when shipping reveals a different target environment, user behavior, ownership failure, or delivery-path tax than expected.

## The Ship Process

### Step 1: Identify the Delivery Path

Map the path from code to working install:

> "The delivery path for this change is: [local] → [PR/review] → [merge] → [CI/CD] → [staging/prod] → [user install]."

Be specific. Name each step and who/what owns it.

### Step 2: Assess the Delivery-Path Tax

The delivery-path tax is friction that slows velocity. Identify where time is lost across: review queue, merge conflicts/stability, gate/scan time (serial vs parallel, flaky), approval bottlenecks, deploy duration, rollback readiness, and manual steps.

### Step 3: Execute the Ship

#### With CI/CD Context
1. **Reference the pipeline** — point to the specific build/deploy configuration
2. **Trigger the appropriate workflow** — label PRs, push to deploy branches, etc.
3. **Monitor the pipeline** — watch for failures, report status
4. **Verify deployment** — confirm the change is live

#### Without CI/CD Context
1. **List deployment steps** — what needs to happen in order
2. **Execute each step** — or provide commands to execute
3. **Verify each stage** — confirm success before proceeding
4. **Report final status** — confirm user-facing change is live

### Step 4: Post-Ship Verification

Shipping isn't done until you verify:

- **Is it running?** — deployed and executing
- **Is it working?** — intended behavior is present
- **Is it reachable?** — users can access/use it
- **Were the promised characteristics delivered?** — shipped result matches the declared success criteria from `/execute`
- **Did reality match the frame?** — users/operators encountered the problem we thought we solved; hidden constraints or ownership failures are routed to the right learning artifact

Create ad-hoc verification tests if needed — the point is confidence, not permanent infrastructure. Verification ties back to what the work claimed it would deliver, not only whether deployment completed.

Ship remains delivery-focused: route failed verification or rollback learning to `/salvage`; route broader reality-contact learning to `/aim`, `/problem-space`, guardrails, or metis. Do not reopen shipped work unless verification fails.

## Output Format

```
## Ship

### Ship Report

**Shipped:** [what was shipped]
**Target:** [where it was shipped to]
**Path:** [the delivery path taken]

### Delivery-Path Tax Identified
- [Friction point 1]: [time/effort cost]
- [Friction point 2]: [time/effort cost]

### Ship Actions Taken
1. [Action 1 - result]
2. [Action 2 - result]

### Verification
- [x] Deployed successfully
- [x] Running in target environment
- [x] User-facing functionality confirmed

### Delivered Characteristics Validation
- [x] [Declared criterion/characteristic 1]
- [ ] [Declared criterion/characteristic 2, if not yet verified]

### Reality Contact Check
- Frame match: [matched | partially matched | missed]
- Different problem encountered: [none | describe]
- Hidden constraints / ownership failures: [none | describe]
- Learning routed to: [`/salvage` | `/aim` | `/problem-space` | guardrail | metis | none]

### Recommendations
[Any suggestions for reducing delivery-path tax in future]
```

## Session Handoff

If a session file is in use, replace or append `## Ship`. Preserve delivery-path tax, verification status, delivered-characteristic validation, reality-contact result, and learning route.
