# ENGINE — Design DNA Engine

**Purpose:** produce a project-unique design constitution. Reuse principles;
never reuse a visual template (§2, §3, §16).

## When to run

- `uiux init <project>` — attaches a project, generates the DNA once.
- `uiux design --answers '<json>' [--out path]` — standalone generation.
- Regenerate only when requirements materially change; append a changelog
  line instead of silently rewriting history.

## Input answers schema

```json
{
  "name": "acme-control",
  "industry": "industrial",          // or fintech | healthcare | ...
  "product_type": "dashboard",
  "audience": "plant operators, 40-60, gloves, wall displays",
  "brand": "VIRA Control",
  "dark_mode": true,
  "motion_appetite": "low",          // low | medium | high
  "data_heavy": true,
  "accessibility_first": true
}
```

Unknown fields are inferred (framework detection, name heuristics) and marked
as inferred in the DNA.

## What the generator decides (and why each axis is free, not templated)

| Axis | How it is derived | Diversity mechanism |
|---|---|---|
| Direction | scored fit over 8 archetypes (industry, audience, data density, motion appetite) | 8 archetypes × project inputs |
| Palette | HSL strategy (mono/analogous/split/duotone) seeded by project name hash; every text token WCAG-nudged ≥ 4.5:1 | hue/saturation/strategy all parameterized |
| Typography | pairing chosen within the direction's radius family | 5–6 pairings per family |
| Spacing & density | base 4 vs 8, scale, row/pad/gap from density class | 3 density classes |
| Radius | sm/md/lg triple from family | 3 families |
| Motion | duration ladder + signature easing from motion profile, capped by `design.max_motion_ms` | 5 profiles |
| Layout | navigation + grid + hero composition from direction + data density | combinatorial |
| Imagery | style family matched to direction | per-direction lists |

Deterministic per project (name-seeded) so regenerated DNA is stable, but two
different projects derive different values on every axis above.

## Internal direction evaluation (§17)

For complex projects the engine internally scores all 8 directions and keeps
the top-2 rejected candidates as one line in the DNA ("alternatives
considered … rejected on fit"). The full scoring is internal; the artifact
exposes the decision and rationale, not the deliberation.

## DNA file contract (design-dna.md)

1. Product identity & direction
2. Audience & industry
3. Visual direction (density/motion/radius/layout/imagery)
4. Color strategy table (token, value, role — all WCAG-checked)
5. Typography (display/body/mono, scale ratio, tabular numerals rule)
6. Spacing & density
7. Motion (durations, easing, intensity, reduced-motion clause)
8. Accessibility contract
9. Things to avoid (anti-decisions)

## Relationship to other engines

- `ENGINE/motion-engine.md` elaborates §7 into implementation tokens.
- `ENGINE/accessibility-engine.md` enforces §8 during review.
- `ENGINE/frontend-engine.md` maps the DNA onto the project stack.
- The DNA never overrides priority ranks 1–6 (`priority-hierarchy.md`).
