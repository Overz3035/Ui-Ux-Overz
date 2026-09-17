# MODULE — Project Init

Code: `CLI/uiux/projectctx.py` (`uiux init <project>`).

## Detection

| Signal | Method |
|---|---|
| framework | package.json deps (next/nuxt/remix/astro/react/vue/svelte/angular) |
| styling | tailwindcss dep → "tailwind"; CSS custom props in src styles → "css-vars"; else unknown |
| libraries | framer-motion/motion, gsap, three, @react-three/fiber, lenis |
| tokens | tailwind.config.*, tokens.json, design-tokens*, theme.* |
| components | src/components, components, app/components, lib/components |
| data_heavy | table/chart/grid markers in first 40 tsx/jsx files |
| industry | name heuristics (bank/pay/… → fintech, health/med/… → healthcare) |

## Writes (never overwriting existing files)

| File | Content |
|---|---|
| .uiux/context.json | detection results |
| .uiux/design-dna.md | generated DNA (existing → design-dna.proposed.md) |
| .uiux/tokens.json | palette/type/space/radius/motion as machine tokens |
| .uiux/motion.json | motion ladder |
| .uiux/README.md | agent contract (DNA is law; search first; priority rules) |

Registers the project in the engine DB (`projects` table).

## Extension points

- Answers JSON (industry/audience/brand/dark_mode/motion_appetite) overrides
  inference.
- New detectors: add pure functions returning context keys; keep them cheap
  (bounded rglob, head-limited reads).
