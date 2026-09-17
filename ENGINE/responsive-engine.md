# ENGINE — Responsive Engine (§24)

Responsive is per-breakpoint **design**, not desktop shrinkage. Each class
gets its own navigation model, hierarchy, and interaction mode.

## 1. Breakpoint classes

| Class | Width | Role |
|---|---|---|
| mobile | 320–767 px | primary for most audiences; thumb-reach design |
| tablet | 768–1023 px | 2-column adaptations; larger touch targets |
| desktop | 1024–1439 px | canonical layout |
| large | 1440 px+ | max-width containers, not stretched content |

Anchor points (min-width by default): `sm 640, md 768, lg 1024, xl 1280,
2xl 1536` — align with the project's existing Tailwind/vars when present
(priority 6).

## 2. What changes per class (never just scale)

| Aspect | mobile | tablet | desktop | large |
|---|---|---|---|---|
| Navigation | bottom tabs or drawer | drawer or condensed top | persistent sidebar/topbar | sidebar + secondary rail |
| Typography | fluid clamp(), same ratio | same | scale locks in | +1 step display |
| Grid | 1-col, priority order | 2–4 col | 12-col | 12-col + gutters grow |
| Density | relaxed rows | balanced | DNA density | DNA density |
| Interaction | touch 44 px targets, no hover dependency | touch | hover + keyboard | multi-pane possible |
| Media | art-directed crops | standard | full-bleed ok | full-bleed + ambient |
| Motion | T1/T2 only | T1–T3 | full | full, scroll-linked |

## 3. Fluid typography

```css
font-size: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
```
Type scale ratio comes from the DNA; line-height ≥ 1.5 body, ≤ 1.1 display.

## 4. Content priority = layout order

Decide per page: what must be visible at 320 px before scroll? That order —
not the desktop order reversed — drives the mobile hierarchy. Tables on
mobile become stacked cards (sticky first column or key-field row) rather
than horizontal-scroll traps.

## 5. Touch & pointer

- `@media (pointer: coarse)` → larger hit areas, visible pressed states,
  no hover-only affordances; reveal via tap/expand instead.
- Hover styling must be additive on desktop, never load-bearing
  (`motion_category: hover` → `subtle_hover_elevation` pattern).

## 6. Verification matrix (review uses this)

320 / 375 / 768 / 1024 / 1440 / 1920 × light/dark × reduced-motion on/off.
No horizontal scroll at any anchor; no clipped focus rings at any size.
