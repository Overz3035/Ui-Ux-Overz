---
name: problem-weave
description: Map a cross-layer problem with independent problem statements and Strategy & Tactics trees, then interweave overlap, opposition, dependencies, and gaps. Use when one frame hides distinct work across users, systems, teams, or explanations. Routes durable artifacts to $record and selected tactics to /oh-plan.
---

# /problem-weave

Map what must change across layers before choosing solutions. Independent passes reduce anchoring; synthesis keeps disagreement visible.

Use it when:

- the problem spans user behavior, workflow, organization, technology, or evidence;
- different roles describe different problems or propose fixes that pull in opposite directions;
- a single `/problem-statement` keeps expanding, becoming vague, or collapsing distinct concerns;
- the user asks for multiple agents, S&T trees, “all the things we have to fix,” overlap, or opposition.

Skip it when the problem is already single-layer and crisp; use `/problem-statement` directly. Use `/problem-space` first when the terrain, constraints, or stakeholders are not yet known well enough to partition the work.

## Aim

**Aim:** People facing a multi-layer problem can distinguish the behavior changes and necessary work, see where frames reinforce or contradict one another, and choose a framing before solution design.

**Mechanism:** Run independent, layer-specific framing passes. Each produces a problem statement and S&T tree. Normalize and interweave the results while preserving opposition and uncertainty.

**Hypothesis:** Independent views expose hidden problem statements and cross-layer dependencies that a single framing pass would miss, while a shared tree vocabulary makes the differences comparable.

**Feedback signal:** A human can identify the primary and alternate frames, cross-layer dependencies, unresolved tensions, and invalidation signals without reading the raw agent outputs.

**Guardrails:** Do not turn tactics into implementation requirements; do not merge unlike objectives merely because they share a noun; do not label disagreement as consensus; do not proceed to solution selection while a material framing conflict is hidden.

## Workflow

### 1. Establish the common contract

Read the current session's `## Aim` and `## Problem Space`, if present. Carry forward the aim's behavior change, rationale, mechanism-as-hypothesis, assumptions, feedback signal, and guardrails.

`## Aim` is required. If it is missing, route to `/aim`; do not invent the shared objective. If `## Problem Space` is missing and the layers or constraints are unclear, route there first.

State the current frame in one paragraph, including:

- the request or symptom as currently described;
- the shared objective to preserve across all agents;
- known constraints and evidence quality;
- what is explicitly out of scope.

Do not let one proposed solution become the shared frame.

### S&T semantics to preserve

An S&T tree is a progressively elaborated hierarchy of **steps**, not a flat list of strategy-flavored rows. Preserve these invariants:

- **Strategy (S)** answers what outcome is needed and why.
- **Tactic (T)** answers how that strategy could be advanced.
- **Necessity (N)** explains why the tactic is indispensable to its strategy.
- **Parallel assumption (PA)** explains why this tactic is credible relative to alternatives under current conditions.
- **Sufficiency (Su)** is a claim about a named set of sibling steps collectively covering their parent strategy; it is not proved one row at a time.
- A tactic may be elaborated into a lower-level strategy. Preserve that recursion with `parent_step`, `depth`, and a named sufficiency group.
- Strategy evolves. Mark tactics `candidate`, `selected`, `rejected`, or `deferred`, and name an owner plus a review trigger for selected branches.

Do not expand the whole tree up front. Prioritize branches that are necessary, uncertain, opposed, or decision-changing; defer the rest explicitly and elaborate them as evidence or completed objectives change the next decision.

### 2. Choose the layers

Choose three to six lenses that would change a decision. They are independent views, not levels in the S&T hierarchy. Use lenses present in the situation; do not invent branches to fill a quota. Typical lenses are:

1. **User/outcome:** what people need to do or decide differently.
2. **Workflow/operations:** how work moves, where handoffs or feedback fail.
3. **Organization/coordination:** roles, incentives, ownership, policy, or governance.
4. **System/technical:** capabilities, interfaces, data, reliability, or architecture.
5. **Evidence/measurement:** what is observable, how success is detected, and which claims are weak.

Record why each lens matters and what it must not assume about the others. Start at the root objective. Elaborate only the one or two branches whose absence, uncertainty, or opposition changes the current decision. Stop when a tactic is plan-ready, rejected, or deferred. If only one lens matters, use `/problem-statement` instead.

### 3. Delegate independent framing passes

Spawn one sub-agent per layer in parallel when sub-agents are available. Give every agent the same common contract and only its own layer lens; do not give agents other agents' outputs. Child agents must not write to the shared session file; the coordinator owns the final handoff. Ask each agent to return:

```markdown
## Layer Frame: [layer]

**Who needs what outcome because why, but currently what blocks it?**

### S&T Tree
- **Root objective (S):** [what/why]
  - **Step [id]:**
    - **Parent step:** [root or step id]
    - **Depth:** [0..n]
    - **Strategy (S):** [objective and why]
    - **Tactic (T):** [how this objective could be advanced]
    - **Disposition:** [candidate / selected / rejected / deferred]
    - **Necessity:** [why T is indispensable to S]
    - **Tactic justification / parallel assumption:** [why T is a credible choice now]
    - **Sufficiency group:** [group id containing this and sibling steps]
    - **Owner:** [role or unknown]
    - **Review trigger:** [objective met, evidence changes, or assumption fails]
    - **Evidence:** [observed / inferred / assumed, with source if available]
    - **Invalidation signal:** [what would show this branch is wrong]

### Sufficiency Groups
- **Group [id] for parent strategy [step/root]:**
  - **Child steps:** [ids]
  - **Mode:** [all required / alternatives / conditional]
  - **Coverage claim:** [why this set is enough for now]
  - **Known gap or deferred branch:** [what is not covered]

### Constraints and assumptions
- [hard, soft, or assumed constraint]

### Disagreements or missing branches
- [who might frame this differently and what evidence would decide]
```

The agent is framing a problem, not selecting a final solution. Its tactics remain `candidate` unless evidence already rejects or defers them; `/solution-space` owns `selected`. Tactics should describe enabling changes or necessary moves at the appropriate level, not premature implementation detail. If delegation is unavailable, perform the passes sequentially and mark the loss of independence.

### 4. Normalize before comparing

Convert every returned tree into comparable **steps**. Preserve provenance: layer, agent, evidence quality, and original wording. For each step, separate:

- **S:** objective or behavior change — what/why;
- **T:** enabling action or condition — how;
- **P / D:** parent step and depth — where the step sits in the recursive hierarchy;
- **Disposition:** candidate / selected / rejected / deferred — whether later planning may act on it;
- **N:** necessity — why the tactic is indispensable;
- **Su group:** sibling step IDs plus mode and a collective coverage claim;
- **PA:** tactic justification / parallel assumption — why this tactic is credible;
- **Owner / review trigger:** who reassesses the branch and when;
- **I:** invalidation signal — what would make the branch wrong.

Reject or flag nodes that are only adjectives (“make it simpler”), untestable outcomes, disguised implementation choices, or tactics with no parent objective. Do not silently repair them; record the normalization decision.

### 5. Interweave the trees

Compare nodes by meaning and causal role, not by matching words. Produce a relation map with one of these dispositions:

| Relation | Meaning | Required treatment |
|---|---|---|
| **Overlap** | Same or nearly same objective, constraint, or tactic | Merge only with provenance; retain meaningful wording differences |
| **Complement** | Different branches that jointly support a parent objective | Link them; test collective sufficiency |
| **Dependency** | One branch must precede, enable, or constrain another | Draw the dependency and name the assumption |
| **Opposition** | Objectives, tactics, constraints, or incentives pull apart | Preserve both; name the trade-off and decision owner |
| **Gap** | A parent objective lacks a necessary branch or evidence | Add a missing-branch question, not an invented tactic |
| **Contradiction** | Agents make incompatible factual or causal claims | Keep both claims with evidence status; identify the check needed |

For every proposed merge, answer: “Would a reasonable person choose different actions if these remained separate?” If yes, keep them separate and link them. For every opposition, answer: “Is this a true trade-off, a sequencing issue, a scope difference, or an evidence dispute?”

### 6. Synthesize the framing

Produce a single synthesis with four layers of truth:

1. **Shared core:** what all credible trees agree must change.
2. **Distinct problem statements:** the minimum set of layer-specific frames that should remain separate.
3. **Interwoven S&T hierarchy:** recursive parent/child steps, collective sufficiency groups, dependencies, overlaps, gaps, and opposition.
4. **Decision boundary:** what can move to `/problem-statement` or `/solution-space`, what needs evidence or human judgment first, and what would invalidate the synthesis.

Choose a **recommended working frame** only when it preserves the shared core and makes the major opposition visible. Include alternate frames when they would materially change the solution space. The recommendation is a working lens, not a claim that the other frames are false.

### 7. Offer outcome and capability wiring

When the synthesis identifies more than one durable outcome, objective, capability, signal, or guardrail, offer a follow-up rather than silently creating external records or GitHub issues:

1. Add a bounded `### Wiring Follow-up` table to `## Problem Weave` so the session records what must be wired and which S&T step it belongs to.
2. Suggest `$record` for each durable artifact using the artifact type that fits:
   - behavior change → create or update `outcome`;
   - nested strategic objective → create or update `objective` under a canonical parent outcome;
   - durable ability to establish → create or update `capability` under a canonical parent outcome;
   - measurable feedback or an invalidation check → `signal`;
   - constraint or stop condition → `guardrail`;
   - reusable learning or framing rationale → `metis`.
3. Preserve S&T lineage in outcome-family records: step ID, parent step, sufficiency group, owner, and review trigger. If an objective or capability lacks a canonical parent outcome, keep it as a candidate and ask for or create the parent outcome first.
4. After `/solution-space` records which S&T step IDs are `selected`, suggest `/oh-plan <session>` to turn only those selected tactics into right-sized issues (or a parent epic plus child issues when that workflow is supported). Each issue must retain its parent objective, parent step, sufficiency group, acceptance signal, dependencies, and accepted trade-offs.

`/oh-plan` is a planning/write step, not part of independent framing. Do not recommend it while material opposition remains unresolved or before a solution has been selected, unless the user explicitly wants discovery issues.

### 8. Hand off deliberately

If a session file is in use, replace or append `## Problem Weave` only. Carry forward the recommended frame, distinct problem statements, recursive steps, sufficiency groups, dispositions, owners, review triggers, provenance, relationships, evidence needs, invalidation signals, and wiring table. Do not overwrite `## Aim`, `## Problem Space`, or `## Problem Statement` unless asked.

## Output Format

```markdown
## Problem Weave

**Current frame:** [the shared problem as currently described]
**Layers used:** [layers and why each matters]
**Independence:** [parallel agents / sequential passes; any limitations]
**Status:** [candidate frames / ready for selection / unresolved]
**Inputs:** [Aim / Problem Space anchors used]

### Shared Core
[What the credible trees agree must change]

### Distinct Problem Statements
1. **[Layer]:** [Who] needs [outcome] because [why], but currently [blocker].
2. **[Layer]:** [Who] needs [outcome] because [why], but currently [blocker].

### Interwoven S&T Steps
| ID | Parent | Depth | Layer | Strategy (what/why) | Tactic (how) | Disposition | N | PA | Owner | Review trigger | Evidence | Links |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [id] | [root/id] | [n] | [layer] | [objective] | [enabling move] | [candidate/selected/rejected/deferred] | [why needed] | [why credible] | [role] | [when to reassess] | [status] | [relations] |

### Sufficiency Groups
| Group | Parent strategy | Child steps | Mode | Collective coverage claim | Gap/deferred branch |
|---|---|---|---|---|---|
| [id] | [root/step] | [ids] | [all required/alternatives/conditional] | [why this set is enough for now] | [known gap] |

### Overlap and Complement
- [nodes that reinforce or jointly satisfy a parent objective]

### Opposition and Uncertainty
- **Tension:** [branches in conflict]
  - **Type:** [trade-off / sequence / scope / evidence dispute]
  - **Decision needed:** [choice or experiment]
  - **Owner:** [role, if known]

### Recommended Working Frame
[One solution-agnostic frame that preserves the important distinctions]

### Alternate Frames Worth Keeping
- [alternate frame and how it would change the solution space]

### Evidence and Invalidation
- **Need to learn:** [claim/check]
- **Signal this synthesis is wrong:** [observable evidence]

### Ready for Next Phase?
[yes/no] — [move to `/problem-statement`, `/problem-space`, `/solution-space`, or seek human judgment, with reason]

### Next Route
[one bounded decision, evidence check, or human alignment step]

### Wiring Follow-up
**Offer:** [record durable artifacts now / defer until framing is selected]
**Plan gate:** [after `/solution-space`, run `/oh-plan <session>` / not ready]

| ID | Type | Outcome/objective/capability or artifact | S&T step | Parent step | Disposition | Owner | Record route | Planning route |
|---|---|---|---|---|---|---|---|---|
| [id] | [outcome/objective/capability/signal/guardrail/metis] | [statement] | [S&T id] | [root/id] | [candidate/selected/rejected/deferred] | [role] | [$record type slug / candidate] | [issue/epic candidate or defer] |
```

## Quality Checks

Before finishing, verify:

- Every important strategy has at least one tactic, and every tactic has a parent strategy.
- Every tactic has necessity and parallel-assumption justification—or an explicit “unknown.”
- Every non-root step has `parent_step` and `depth`; a flattened table with free-form links does not count as a tree.
- Every parent strategy has a named sufficiency group whose claim covers a sibling set, mode, and known gap; row-local “sufficiency” does not count.
- Candidate tactics cannot become plan items until `/solution-space` marks their S&T IDs `selected`.
- Selected branches name an owner and review trigger; deferred branches remain visible without forced expansion.
- The shared core is supported by more than one layer or is clearly marked as a single-layer claim.
- Opposing branches are not merged into vague language.
- Missing evidence is distinct from disagreement and from a missing branch.
- The recommended frame remains solution-agnostic and carries forward the aim contract.
- The output is sufficient for the next phase without requiring the reader to inspect raw agent transcripts.
- Every durable outcome/objective/capability is either mapped to a valid `$record` route or explicitly marked as a candidate requiring normalization.
- Every proposed plan item maps to a selected S&T tactic and is gated on solution selection unless explicitly requested for discovery.
