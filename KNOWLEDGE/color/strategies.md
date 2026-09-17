# KNOWLEDGE — Color Strategies

How the DNA palette generator thinks. Use when evaluating or extending a
generated palette.

## Strategies

| Strategy | Structure | Use when |
|---|---|---|
| mono-accent | neutral base + single hue accent | clarity-first products, dashboards, editorial |
| analogous | accent + neighbor hue (~24–28°) | depth without tension; hero gradients |
| split-complement | accent + two balanced counter-hues (~150–210°) | expressive brands, category/segment coding |
| duotone | accent + complement (~180°), both controlled | bold identity, creative audiences |

## Surfaces & neutrals

- Neutrals are tinted, never pure grey: carry 4–14% of the accent hue.
- Dark UI: layered surfaces (bg < surface < border-lightness) replace
  shadows; elevation = lightness steps, not blur.
- Light UI: shadows stay warm-grey; borders appear before shadows.
- Dark mode is a re-lighting, not an inversion: lower saturation ~10–20%,
  raise accent lightness, keep text ≤ pure-white minus a step (#e8edf2 not
  #ffffff for large fields).

## WCAG contract (enforced in generator)

- text on background ≥ 4.5:1 (nudged automatically)
- muted ≥ 4.5:1 (secondary is not low-quality)
- on_accent ≥ 4.5:1
- accent as UI (borders, icons) ≥ 3:1 vs its backdrop
- status colors ≥ 4.5:1 when carrying text, ≥ 3:1 as dots/bars

## Semantic layer

- success/warning/danger are vocabulary, not decoration: one meaning each,
  used identically everywhere (status dots, badges, chart series).
- Charts reserve accent for the series that answers the question; others
  step down the neutral ramp.

## Anti-patterns

- accent-on-accent gradients (vibration, no hierarchy)
- low-contrast grey-on-grey "premium" (fails 4.5:1 — the reference library
  contains examples; they are studied, not copied)
- neon accents on white (halation); neons need dark surfaces
- a status color doing brand work (danger-red CTA next to error badges)
