# Design DNA Guide

What it is, how it is generated, how to use and evolve it.

## Definition

`design-dna.md` is a project's design constitution: direction, audience,
visual direction, WCAG-checked color table, typography, spacing/density,
motion ladder, accessibility contract, and explicit things-to-avoid. Two
projects never share one: every axis derives from project inputs
(see ENGINE/design-dna-engine.md for the derivation table).

## Generation paths

```powershell
# attach a project (detects stack, writes .uiux/)
uiux init .\my-app

# greenfield / standalone
uiux design --answers '{\"name\":\"vira-control\",\"industry\":\"industrial\",
  \"product_type\":\"dashboard\",\"audience\":\"plant operators\",
  \"dark_mode\":true,\"data_heavy\":true,\"motion_appetite\":\"low\"}'
```

Complex projects: the generator internally scores 8 directions and records
rejected alternatives in one line; the deliberation itself stays internal.

## Machine-readable companions

- `.uiux/tokens.json` — palette/type/space/radius/motion for tooling
- `.uiux/motion.json` — duration ladder + easing

Map onto Tailwind theme or CSS vars (ENGINE/frontend-engine.md §2); when the
project already has tokens, alias them — never fork values.

## Evolution rules

1. Requirements change → regenerate via `uiux init` (a proposal file is
   written if a DNA exists; compare, then adopt deliberately).
2. Session decisions → append a dated changelog line; the DNA is append-
   friendly, never silently rewritten.
3. Conflicts → resolved by priority hierarchy and recorded as one-line
   notes in the DNA.

## Anti-goals

- Not a theme file (themes pick values; DNA records reasoning + values).
- Not a template (nothing here is a page layout to copy).
- Not optional for UI work: agents treat it as the visual law once present.
