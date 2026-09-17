---
name: distill
description: Human-led curation of accumulated metis and guardrails. Surface patterns across sessions, propose what to promote, compact, or dismiss. Use after multiple sessions, before a new phase, or when search results feel noisy.
---

# /distill

Surface patterns in accumulated knowledge. Propose what to keep, promote, compact, or dismiss. The human decides.

Salvage extracts learning from a single session; distill curates the corpus those extractions build. Without distill, metis accumulates but never compounds.

## When to Use

Invoke `/distill` when:

- **After multiple sessions** - The corpus has grown and hasn't been reviewed
- **Before a new phase** - Want to know what's settled before moving forward
- **Search results feel noisy** - `oh_search_context` returning too much loosely-related content
- **Similar learnings keep appearing** - `/salvage` keeps extracting the same insights (the meta-signal)
- **End of a successful session** - Even good sessions produce learnings worth capturing before context is lost

**Use distill (not `/salvage`) when the session went well.** `/salvage` is for stopping because things went wrong. Distill is for pausing because things went right — or finished — and learnings are worth capturing before context is lost.

**Do not use when:** You're in the middle of execution. Distill is a pause point, not a mid-flight activity.

## The Human-Led Curation Principle

LLMs find patterns; humans decide what matters. Auto-promotion is never correct. A theme is not a guardrail until a human writes it.

## The Process

### Step 1: Establish Scope

Decide what corpus to work with:
- **Session scope** (default, no RNA needed): learnings from this conversation
- **Corpus scope** (RNA available): accumulated metis across all sessions, optionally filtered by outcome, phase, or tag

**Filtering (RNA):** Pass outcome ID, phase tag, or recency window to `oh_search_context` to narrow the corpus when only a domain slice needs curation.

### Step 2: Surface Candidates

**Session scope:** Review the conversation. What was learned? What assumptions were validated or invalidated? What constraints were discovered? What would be useful to know at the start of the next session? Exclude generic advice unless it demonstrably changes decisions in this context.

**Corpus scope (RNA):** Call `oh_search_context` broadly. Cluster by semantic similarity. Identify:
- Entries that appear together repeatedly (candidates for compaction)
- Patterns across entries (candidates for guardrail promotion)
- Entries that contradict each other (candidates for resolution)
- Entries that are stale, generic, or overly context-specific (candidates for dismissal)

### Step 3: Myth vs. Metis Check

Before proposing promotion or compaction, test whether the pattern is durable learning or a memorable story:

- **Reality contact:** Did this recur across observations, or is it one vivid incident?
- **Tied conditions:** When does it apply, and when would it mislead?
- **Staleness:** Is the system, context, or constraint still the same?
- **Judgment vs. old fear:** Does it improve current decisions, or preserve anxiety from an old failure?
- **Scope:** Is it local, temporary, or general? Label it honestly.

If the answer is weak, suggest Keep or Dismiss rather than Promote. Distill surfaces candidates; humans still approve every write.

### Step 4: Present for Human Review

Present each candidate group with four possible actions:

```markdown
**Theme: [theme name]**
Entries: [list with source IDs and one-line summaries]
Suggested action: [Keep / Promote / Compact / Dismiss]
Myth vs. metis: [reality contact, tied conditions, staleness, scope]
Reason: [why this action fits]
→ Your call:
```
**Keep** — leave as individual metis entries, no change.
**Promote** — pattern is recurring and stable enough to warrant a guardrail. Distill drafts a stub; human approves the content (editing as needed), then an agent writes the file:
  ```markdown
  ---
  id: [slug]
  outcome: [outcome-id]
  severity: soft
  title: [one-line constraint]
  ---
  [drafted body — human refines, agent writes to .oh/guardrails/]
  ```
**Compact** — multiple entries say the same thing. Human approves a merged version; originals archived or deleted.
**Dismiss** — stale, generic, superseded, or so context-specific it misleads more than it helps.

### Step 5: Write Results

Only write what the human approved. No auto-promotion, no auto-deletion.

- New metis entries → `.oh/metis/<slug>.md`
- Guardrail candidates → draft for human to write to `.oh/guardrails/<slug>.md`
- Compactions → new merged entry + note which originals can be removed
- Session file compaction → offer to remove stale planning artifacts, keep settled decisions as brief anchors

## Output Format

```markdown
## Distill Summary

**Scope:** [session | corpus — filtered by: outcome/phase/tag]
**Entries reviewed:** [N]

### Proposals

**[Theme or entry title]**
- Source(s): [file paths or conversation reference]
- Suggested: [Keep / Promote to guardrail / Compact / Dismiss]
- Reason: [one sentence]
- Myth vs. metis: [why this is durable situated learning, or why it may be myth/stale]
→ Decision: [human fills this in]

[repeat for each proposal]

### Results Written
- [what was written, with file paths]
```

## Guardrails

- **Never auto-promote.** A theme proposal is not a guardrail until a human writes it.
- **Never auto-delete.** Dismissal proposals require human confirmation.
- **Preserve provenance.** Every proposal links to source metis IDs or conversation context.
- **Prefer situated metis over generic advice.** If a note does not add local leverage beyond what a foundation model would already know, treat it as dismissal or compaction candidate.
- **Check myth before metis.** A memorable incident is not a pattern unless repeated reality contact and tied conditions make it decision-changing.
- **Phase-aware.** Corpus-mode clustering must surface phase tags — cross-phase metis often misleads. A solution-space learning is not automatically relevant in problem-space.
- **Graceful with sparse corpus.** With fewer than 5 entries, surface what exists without manufacturing false patterns. Don't cluster noise.
- **Metis is contextual, not universal.** What worked in one context doesn't carry everywhere. The human selects what applies; distill surfaces candidates.

## Session Handoff

Distill is corpus/session curation, not execution. Use after multiple salvages or after a session that produced reusable local learning. Human approval is required before promoting, compacting, or deleting anything.
