---
name: teach-oh
description: Project setup. Explore the codebase, ask about strategy and aims, write persistent context to AGENTS.md. Run when starting or when aims shift.
---

# /teach-oh

Gathers project context and writes it to AGENTS.md. Run when starting on a project or when strategy, aims, or constraints shift.

## When to Use

- Starting on a new project
- Context keeps getting lost across sessions
- Major strategic aims or constraints changed

**Do not use when:** You are mid-task. This is setup, not execution.

## JIT References

- Load [references/examples.md](references/examples.md) only when the user asks what AGENTS.md output should look like.
- Load [references/install.md](references/install.md) only after AGENTS.md context is drafted and the user wants optional OMP or Claude Code hooks/agents.
- If RNA setup is needed, use `/setup`; do not inline install commands here.

## The Process

### Step 1: Explore Before Asking

Discover what tools and files can answer:
- structure and stack;
- package/build/CI configuration;
- existing AGENTS.md, CLAUDE.md, README, CONTRIBUTING, `.oh/`, ADRs;
- patterns, conventions, recent commits;
- sensitive areas or documented constraints.

Do not ask for information you can discover.

### Step 2: Ask Only What Matters

Ask targeted questions about what could not be inferred:

#### Purpose & Aims
- What is this project trying to achieve?
- Who uses it? What behavior change indicates success?
- What is the current priority?

#### Strategic Constraints
- What constraints never bend?
- What trade-offs were made intentionally?
- What is explicitly out of scope?

#### Decision Context
- How are decisions made here?
- What does "done" mean here?
- What patterns or practices are sacred?

#### Sensemaking & Reorientation
- What signals mean the current story has stopped fitting reality and needs a pause/reframe?
- Who or what can call drift, dissent, salvage, or a reframe?
- What decisions require dissent before commitment?
- What failures should trigger salvage rather than more execution?
- What role boundaries should stay distinct (implementer, reviewer, dissenter, domain expert, final decision-maker)?
- What evidence overrides the plan (tests, stakeholder feedback, operational signals, domain expertise)?
- What local metis or guardrails should carry across sessions?

#### What to Avoid
- Past mistakes that should not repeat
- Tempting patterns that do not fit
- Sensitive areas of the codebase

### Step 3: Draft Persistent Context

Offer to append or update AGENTS.md. Keep it working-context sized, not documentation sized.

Include:
- **Open Horizons Framework** if the user wants OH skills documented in the repo;
- **Project Context** always: purpose, aims, constraints, patterns, anti-patterns, decision context, and sensemaking norms.

Present the draft for user approval before writing.

## Output Format

```markdown
## Teach-OH Summary

### What I Discovered
- Stack: [technologies found]
- Structure: [key patterns observed]
- Existing context: [what docs already exist]
- Current focus: [what recent code/docs imply]

### Questions I Have
1. [Question about aims/strategy]
2. [Question about constraints]
3. [Question about decision practices]

---

After your answers, I'll draft an AGENTS.md section for your approval.
```

After user answers:

```markdown
## Proposed AGENTS.md Addition

[Draft the requested Open Horizons Framework section, if applicable]

[Draft the Project Context section]

---

**Write to AGENTS.md?** [Yes/No - show what will be added/updated]
```

## Completion Notes

After AGENTS.md is approved and written, optionally offer install help only when the environment supports it. Context lives in AGENTS.md; keep it focused and re-run when aims shift, constraints change, or context feels stale.
