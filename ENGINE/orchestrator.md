# ENGINE — Master Orchestrator

The orchestrator turns a request into a routed, token-efficient execution
plan. It is the entry card for any agent session using this engine. Load
**only** the sections referenced by the current task.

## 0. Hard rules (always in force)

1. **Progressive context loading (§29).** Never load the whole KNOWLEDGE/,
   SKILLS/, or reference library. Load a card only when routed to it.
2. **Reference retrieval is local-first (§14).** Use `uiux search "<task
   concept>" --context-pack` for references. Only the returned compact JSON
   enters model context — never media, never full JSON exports.
3. **No template reuse (§3).** Every project gets a generated Design DNA.
   References supply principles; the DNA supplies decisions.
4. **Priority hierarchy (§4)** resolves every conflict. See
   `ENGINE/priority-hierarchy.md`.
5. **Never overwrite project files** without being asked (§27).
6. **Accessibility is a floor, not a trend** (§25). See
   `ENGINE/accessibility-engine.md`.

## 1. Intake classification

Determine, from the user request and (when attached) the project:

| Question | Where it comes from | Routed to |
|---|---|---|
| Project type (landing / dashboard / app / ecommerce / editorial / 3D …) | request + project detection | design-dna-engine |
| Audience & industry | request, brand, `.uiux/context.json` | design-dna-engine |
| Required skills | task verbs (implement / audit / redesign / animate) | resource-router |
| Relevant modules | ingest state, project state | MODULES/<name>.md |
| Motion needs | motion vocabulary in request; reduced-motion constraints | motion-engine |
| 3D/WebGL needs | explicit 3D/spatial/shader requirements only | 3d-engine |
| Responsive scope | target viewports in request | responsive-engine |
| Accessibility scope | always required | accessibility-engine |
| Implementation strategy | existing stack detection | frontend-engine |

## 2. State checks (run before planning)

```powershell
uiux status        # is the index populated? pending INBOX?
uiux doctor        # capabilities present? (ffmpeg, OCR, embeddings)
```

- If a project is attached but has no `.uiux/design-dna.md` → run
  `uiux init <project>` first (it never overwrites).
- If the reference index is empty → tell the user to run `uiux ingest`;
  continue with knowledge-only mode (KNOWLEDGE/ cards) instead of failing.

## 3. Execution recipes by task kind

**New design / redesign**
1. Read `.uiux/design-dna.md` if present — it outranks external skills.
2. If absent: gather requirements → `uiux design --answers '<json>' --out`.
3. `uiux search "<core concept>" --context-pack` → ≤ 12 references.
4. Route to UI UX Pro Max when installed (resource-router), else fall back.
5. Implement via `ENGINE/frontend-engine.md` + stack-appropriate library.

**Implementation on an existing project**
1. `ENGINE/priority-hierarchy.md` — the existing design system is priority 6.
2. `ENGINE/frontend-engine.md` for the stack; adapt, do not impose.
3. Any new visual decision must be recorded in the DNA (append, don't rewrite).

**Audit / polish**
1. `uiux review <project>` → `.uiux/quality-report.md`
2. `uiux polish <project>` → prioritized plan.
3. `ENGINE/quality-engine.md` for the manual checklist that static analysis
   cannot cover (taste, hierarchy, content rhythm).

**Motion work** → `ENGINE/motion-engine.md` first; GSAP/Framer Motion only
when the technique requires it (resource-router decides).

**3D / shader work** → `ENGINE/3d-engine.md`; 3D must add information, not
decoration. If a gradient or still image achieves the goal, no WebGL.

## 4. Context budget rules

- References per task: ≤ `search.max_context_references` (default 12).
- One context pack ≈ a few hundred tokens. Never paste INDEX/*.json exports.
- Skills/cards: load at most 3 per task; cite which ones in the plan.
- External engines (UI UX Pro Max): invoke natively, summarize the result
  into the plan — do not pipe its full output into context.

## 5. Output contract

Every plan states:
1. Task classification (one line)
2. Design DNA source (existing / generated) + direction name
3. Routed resources (engine, skills, libraries) with the reason
4. References used (generated names only)
5. Accessibility requirements that apply
6. Implementation steps with file targets
