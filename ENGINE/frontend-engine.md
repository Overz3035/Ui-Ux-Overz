# ENGINE — Frontend Engine

Adapt to the project's stack; never force one (§23). The engine's
implementation layer is stack-agnostic guidance plus per-stack playbooks.

## 1. Stack detection (automated)

`uiux init` detects framework, styling, libraries, tokens, and component
folders into `.uiux/context.json`. Priority rule 6: **existing conventions
outrank engine preferences.**

| Detected | Playbook |
|---|---|
| Next.js / React | components + server/client split; Framer Motion if present |
| Vue / Nuxt | SFCs; CSS transitions + @vueuse/motion when present |
| Svelte | built-in transitions; svelte-spring for physics |
| plain HTML/CSS/JS | CSS-first motion; GSAP only for choreography |
| Tailwind present | utility-first, tokens as CSS vars in `@theme`/config |
| CSS vars present | map DNA tokens onto existing var names — do not rename |

## 2. Tokenization contract

The DNA (`design-dna.md`, `tokens.json`) maps onto any stack:

- **CSS vars** (universal): `--color-*`, `--space-*`, `--radius-*`,
  `--motion-*`, `--font-*`.
- **Tailwind**: extend theme with the same names; keep scale values exact.
- **Existing system**: if names differ, add an alias layer, do not fork
  values. Two sources of truth is how systems rot.

```css
:root {
  --color-bg: #0b0f14;      /* from DNA */
  --color-surface: #121820;
  --color-text: #e8edf2;
  --color-accent: #5b8cff;
  --space-1: 4px;  --space-2: 8px;  /* …full scale */
  --radius-md: 6px;
  --motion-fast: 120ms; --motion-ease: cubic-bezier(0.2, 0, 0, 1);
}
```

## 3. Component architecture

- Tokens → primitives (Button, Input, Card) → composed sections → pages.
- Primitives accept variants, not booleans soup: `<Button intent="primary"
  size="md">`.
- Every primitive ships its focus, hover, active, disabled, and
  reduced-motion state in the same file as its rest state.
- Density variants from the DNA (`compact|balanced|spacious`) are a prop on
  layout primitives, not ad-hoc padding.

## 4. Responsive implementation

Follow `ENGINE/responsive-engine.md` for the breakpoint strategy; implement
with mobile-adaptation, not desktop-shrink: reflow navigation, collapse
grids by information priority, and move from hover to touch affordances.

## 5. Content first, chrome second

- Semantic HTML before styling: landmarks, headings, lists, buttons, labels.
- Loading: skeletons only where shape is predictable; else button-level
  busy states.
- Empty and error states are designed states — same density, same type
  scale, actionable copy.

## 6. Performance defaults

- Images: explicit dimensions, `loading="lazy"` below fold, modern formats.
- Fonts: `font-display: swap`, subset to Latin (+used ranges), ≤ 2 families.
- JS: route-level code splitting; animation libs dynamically imported when
  only used below the fold.
- Ship CSS-first whenever the effect is achievable in CSS (cheaper, robust).

## 7. Hand-off checklist (per feature)

1. Tokens used, zero hard-coded hex/px for color/spacing.
2. Keyboard path walked; focus visible; reduced motion verified.
3. 320 / 768 / 1440 / 1920 checked (`responsive-engine.md` matrix).
4. `uiux review` clean on changed files (or findings triaged into the plan).
