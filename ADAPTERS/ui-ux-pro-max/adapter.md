# Design system generation — routed

When generating a design system for a project, the resource router may
delegate to UI UX Pro Max (native CLI). This adapter file defines how its
output is consumed.

## Invocation patterns

```powershell
# style + palette + typography for a product type
python "<skill>/src/ui-ux-pro-max/scripts/search.py" "<product type>" --domain style -n 3
python "<skill>/src/ui-ux-pro-max/scripts/search.py" "<product type>" --domain color -n 3
python "<skill>/src/ui-ux-pro-max/scripts/search.py" "<audience>" --domain typography -n 3

# tuned design-system dial (variance/motion/density map to DNA axes)
python "<skill>/src/ui-ux-pro-max/scripts/search.py" "<product>" \
  --design-system --variance 7 --motion 4 --density 8

# stack-specific implementation guidance
python "<skill>/src/ui-ux-pro-max/scripts/search.py" "<component>" --stack nextjs -n 2
```

## Consumption rules

1. Summarize: each result becomes 1–3 lines in the plan (style id, key
   tokens, checklist). Never paste full result blocks.
2. Cross-check against the project DNA; conflicts resolve by
   `ENGINE/priority-hierarchy.md` (existing system outranks external skills).
3. Accessibility requirements inside its output (contrast-text-4.5,
   keyboard, visible-focus, reduced-motion) are treated as mandatory
   constraints, not suggestions.
4. If the CLI is missing or fails: fall back to
   `ENGINE/design-dna-engine.md` and record `promax: fallback` in the plan.
