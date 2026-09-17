---
name: review
description: Check work and detect drift before committing. A second opinion that catches misalignment early. Use at natural pause points, before PRs, or when something feels off.
---

# /review

A second opinion before committing. Checks alignment between intent and execution, detects drift, and decides: continue, adjust, or salvage.

Part of the **Intent → Execution → Review** loop at every scale — from a single commit to a multi-week project. Review closes the loop.

## When to Use

Invoke `/review` when: before committing, at natural pause points, something feels off, scope seems to have grown, or before PRs.

**Do not use when:** You're in deep flow and making progress. Review at natural breaks, not arbitrary intervals.

## Review Lenses

Default to the core workflow review in this file. When the artifact being reviewed needs a sharper domain lens, load the matching supporting reference:

- Code, PRs, technical plans, or implementation work: [references/code.md](references/code.md)
- Prose, documentation, essays, prompts, or release notes: [references/writing.md](references/writing.md)
- Tutorials, explanations, onboarding, or teaching behavior: [references/learning.md](references/learning.md)

Use these as lenses, not replacement workflows. The final review still answers the core `/review` questions: aim, alignment, sufficiency, mechanism, drift, completion, and next action.

## The Review Process

### Step 1: State the Original Aim

> "The aim was: [original intent in one sentence]"

If you can't state the aim clearly, that's the first finding.

### Step 2: Check Alignment

Ask six questions. Keep them artifact-neutral; load a review lens only when the artifact needs domain-specific judgment.

1. **Necessary?** — Does this still need to exist now, or did speculative work creep in?
2. **Aligned?** — Does the current work still serve the original aim?
3. **Sufficient?** — Is this enough for the aim without unnecessary scope, abstraction, or entanglement?
4. **Mechanism clear?** — Can you state why this approach should produce the intended outcome?
5. **Risks retired?** — Did every named risk, alternate frame, invalidation signal, and stop/pivot trigger get tested, accepted with evidence, or triggered?
6. **Complete?** — Are promised characteristics, dependencies, verification, and handoff covered?

If RNA MCP is available, check work against guardrails (`oh_search_context` with `artifact_types: ["guardrail"]`) and declared outcomes (`outcome_progress`).

### Step 3: Check the Frame

Before naming ordinary drift, ask whether the interpretation itself collapsed:

- What situation did we think we were in?
- What evidence no longer fits that story?
- Did the aim, mechanism, or constraints change meaning rather than just change scope?
- Would continuing require pretending the old frame still explains the work?

**Frame Collapse** — the working interpretation no longer explains the evidence, constraints, or aim. Treat this separately from drift. Route it by where the break lives: back to `/problem-statement` for a bad frame, `/problem-space` for a bad situation map, `/aim` for changed intent, or `/salvage` when the session needs learning extraction before restart.

A named alternate frame that remains model-checkable but untested is **incomplete execution**, not automatic frame collapse and not a note for later. A named risk with a non-adversarial check is also incomplete: if the evidence would pass the tempting local patch, the risk was not retired. Route to **Adjust** when the selected approach is still plausible and the missing/adversarial check can be added. Route to **Reframe** only when evidence already invalidates the selected approach or the alternate frame better explains the problem than the current one.

### Step 4: Detect Drift

Drift is the gap between where you started and where you are. Explicitly name any drift found:

**Scope Drift** — task grew beyond original boundaries
**Solution Drift** — approach changed from plan
**Goal Drift** — aim itself shifted without explicit decision
**Frame Collapse** — evidence invalidated the story that made the work make sense

For each drift or frame collapse:
```text
Drift: [type]
Started as: [original frame/plan]
Became: [current evidence/model]
Impact: [what this means]
Route: [continue | adjust | /problem-statement | /problem-space | /aim | /salvage]
```

### Step 5: Decide Next Action

| Decision | When | Action |
|----------|------|--------|
| **Continue** | Aligned, on track, and named risks retired or explicitly accepted | Proceed with confidence |
| **Adjust** | Minor drift, recoverable issue, model-checkable named risk is still untested, or retirement evidence is non-adversarial while the selected approach remains plausible | Add the missing/adversarial check or correction and continue |
| **Reframe** | Frame collapse, invalidation triggered, or evidence shows an alternate frame better explains the problem than the selected approach | Return to `/problem-statement`, `/problem-space`, or `/aim` |
| **Pause** | Unclear aim, major questions, or required human/domain verification | Stop, clarify, then resume |
| **Salvage** | Significant drift or failed frame needs extraction | Extract learning with `/salvage` |

If the review surfaces new hard constraints, record them (`oh_record_guardrail_candidate`).

## Output Format

```markdown
## Review

**Aim:** [original intent]
**Status:** [Continue / Adjust / Reframe / Pause / Salvage]

### Alignment Check
- Necessary: [Yes/No - brief note]
- Aligned: [Yes/No - brief note]
- Sufficient: [Yes/No - brief note]
- Mechanism clear: [Yes/No - brief note]
- Changes complete: [Yes/No - brief note]
- Risks retired: [Yes/No - every named risk/stop trigger is covered by evidence, accepted with rationale, or triggered]

### Frame Check
[State whether the current frame still explains the evidence. If collapsed, name the new frame or route to reframe/salvage.]

### Drift Detected
[List any drift found, or "None detected"]

### Risk Retirement Review
[List each named risk / alternate frame / stop trigger from Solution Space and Execute with its evidence. Mark untested model-checkable items or non-adversarial checks as Adjust unless observed evidence invalidates the selected approach; mark those as Reframe.]

### Needs Human Verification
Claims that cannot be self-checked by the model and require independent human judgment:
- [claim or assumption that needs external confirmation]
- [one-way decision that was not independently challenged]
- [delivered characteristic that was asserted but not externally observed]

If this section is empty, say why. Model-generated review of model-generated work shares the same blindspots. The purpose of this section is to route the right questions to the actual human checkpoint (PR review, stakeholder sign-off, manual test) rather than pretending the model can answer them.

### Decision
[Reasoning for the status decision]

### Next Steps
[Concrete actions to take]
```

## Completion Gate (Before "Done")

When the user or agent claims work is complete, verify:

1. **Intent clear?** — Can you state what changed and why in one sentence?
2. **Work reviewed?** — Has the actual artifact been checked against the stated intent?
3. **Evidence present?** — Are the relevant checks, examples, or observations recorded?
4. **Feedback handled?** — Have review comments or open objections been resolved or explicitly deferred?
5. **Declared criteria delivered?** — Were promised characteristics verified, not merely claimed?
6. **Needs Human Verification surfaced?** — Have claims the model cannot self-check been flagged for human attention?

7. **Risk retirement complete?** — Were all named risks/alternate frames/stop-pivot triggers tested, explicitly accepted, or routed to Adjust/Reframe/Pause?
If incomplete:
 > "Completion gate: [missing step]. Run the check before marking complete."

## Session Handoff

If a session file is in use, replace or append `## Review`. Preserve frame check, verification result, risk-retirement review, human-verification needs, and unresolved objections for later phases.
