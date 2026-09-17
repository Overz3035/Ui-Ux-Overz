# ENGINE — Motion Engine

Motion is information. Every animation must answer: *what changed, where
should I look, what can I do next?* Motion that fails that test is
decoration and must justify itself against the priority hierarchy (§4: it
usually loses).

## 1. Hierarchy of motion

| Tier | Purpose | Examples | Budget |
|---|---|---|---|
| T1 Feedback | confirm the user's own action | button press, toggle, input focus | ≤ 150 ms |
| T2 State | surface a change of state | panel open, toast enter, tab switch | 150–300 ms |
| T3 Reveal | guide attention to new content | list stagger, section reveal on scroll | 300–600 ms, scroll-linked where possible |
| T4 Ambient | brand depth, atmosphere | shader background, hero drift | optional, pausable, reduced-motion safe |

Task surfaces (dashboards, tables, forms) live on T1–T2. T3/T4 belong to
narrative surfaces (landing, story, portfolio).

## 2. Timing tokens (from the Design DNA)

- `--motion-fast` (100–200 ms): hover, press, focus.
- `--motion-base` (160–300 ms): enters/exits, layout.
- `--motion-slow` (240–700 ms): choreography, page transitions.
- `--motion-stagger` (25–80 ms): children offset.
- Never exceed `design.max_motion_ms` (default 900) for anything the user
  must wait for.

## 3. Easing vocabulary

| Curve | Use |
|---|---|
| `cubic-bezier(0.2, 0, 0, 1)` | default enter (decelerate) |
| `cubic-bezier(0.4, 0, 1, 1)` | exits (accelerate out) |
| `cubic-bezier(0.16, 1, 0.3, 1)` | emphatic reveal (expo-out) |
| spring physics (Framer Motion) | interruptible, gesture-driven |
| `linear` | only for scroll-linked scrubbing and loops |

One signature easing per project (the DNA names it). Two is a system
failure; three is a mess.

## 4. Stagger rules

- Stagger communicates sequence, not cuteness. Use when children share one
  event (list enter, card deal).
- Cap visible stagger wave at ~300 ms total: `stagger × min(count, 6)`;
  beyond 6 children, animate in viewport chunks.
- Never stagger task-critical data (tables render, they don't perform).

## 5. Reduced motion is a first-class state

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Every T3/T4 effect needs an equally complete static state: content visible,
hierarchy intact, no information conveyed only through motion.

## 6. Performance rules

- Animate only `transform` and `opacity` (compositor-friendly). Layout-
  animating properties (top/left/width/height) require FLIP or Framer
  Motion's layout animations.
- `will-change` is a scalpel: set it just before the animation, remove after.
- Cap WebGL/DPR (see 3d-engine); pause ambient loops when tab hidden
  (`document.visibilityState`) and off-screen (`IntersectionObserver`).
- Scroll-linked motion scrubs with scroll position — never setTimeout.

## 7. Motion categories (reference vocabulary)

Matches taxonomy `motion_category`: hover, scroll, parallax, page_transition,
navigation, card, button, cursor, micro_interaction, loading, hero, three_d,
shader, liquid, text_animation, background. Retrieve examples with
`uiux search "motion <category>"`.

## 8. Library routing

See `ENGINE/resource-router.md` §Motion. Short version: CSS first; Framer
Motion for React layout/gesture; GSAP for timeline/scroll choreography;
native `Element.animate` for one-offs.
