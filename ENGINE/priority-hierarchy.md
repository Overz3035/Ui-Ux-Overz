# ENGINE — Priority Hierarchy (§4)

When two instructions conflict, the higher number on this list wins. Nothing
below rank 4 may override accessibility; nothing below rank 2 may override
explicit user requirements.

| # | Authority | Examples | Loses to |
|---|---|---|---|
| 1 | **User requirements** | "no purple", "must be keyboard-only operable", "keep it boring" | nothing |
| 2 | **Project requirements** | documented feature goals, platform constraints, SLOs | 1 |
| 3 | **Product / audience requirements** | healthcare seniors vs creative teens; density needs | 1–2 |
| 4 | **Accessibility** | WCAG contrast, keyboard, reduced motion, semantics | 1–3 |
| 5 | **UX usability** | task efficiency, error prevention, wayfinding | 1–4 |
| 6 | **Existing project design system** | tokens, components, conventions already in the repo | 1–5 |
| 7 | **Brand requirements** | logo, palette, voice — when the project has one | 1–6 |
| 8 | **Technical constraints** | bundle budget, browser matrix, device performance | 1–7 |
| 9 | **UIUX ENGINE core principles** | this engine's knowledge, motion/3D philosophy | 1–8 |
| 10 | **External skills** | UI UX Pro Max, taste/frontend-design knowledge | 1–9 |
| 11 | **External libraries** | GSAP, Framer Motion, Three.js defaults | 1–10 |
| 12 | **Visual references** | retrieved reference library entries | 1–11 |

## Practical consequences

- A reference showing a low-contrast grey-on-grey hero does **not** license
  shipping it (12 < 4).
- UI UX Pro Max suggests a palette; the project already has tokens → keep the
  project tokens, note the conflict in the DNA (10 < 6).
- The brand demands an animation-heavy hero; a user requirement says reduced
  motion → provide the reduced-motion state (4 > 7).
- The engine's motion engine says "no animation for decoration on task
  surfaces" and the task surface is a data table → decorative stagger stays
  out (9 > 12).

## Recording conflicts

When ranks conflict materially, the Design DNA gains a one-line note:
`Conflict: brand accent #7c3aed (7) vs contrast 3.1:1 (4) → lightened to
#6d34e0 keeping hue.` This keeps future sessions from re-litigating.
