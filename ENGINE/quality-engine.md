# ENGINE — Quality Engine (§26)

Quality is reviewed across eight dimensions. `uiux review` automates what is
statically checkable and writes `.uiux/quality-report.md`; `uiux polish`
turns findings into a prioritized plan. The rest is a manual checklist.

## 1. Dimensions

| Dimension | Automated | Manual |
|---|---|---|
| UX | — | task-flow walk, error states, empty states, wayfinding |
| UI | DNA token drift (planned) | alignment rhythm, visual hierarchy, taste (`KNOWLEDGE/principles/taste-and-visual-quality.md`) |
| Responsive | media-query presence | 320→1920 matrix, navigation reflow (`responsive-engine.md` §6) |
| Accessibility | contrast pairs, alt, labels, div-onClick, heading skips, focus/reduced-motion presence | SR smoke test, keyboard-only run, 200% zoom |
| Motion | reduced-motion coverage, duration ceilings | easing consistency, stagger restraint, interruptibility |
| Frontend | — | token discipline, dead code, bundle sanity |
| Consistency | — | one signature easing, one accent, density uniformity |
| Performance | — | LCP element, image sizes, font payload, WebGL budget (`3d-engine.md` §5) |

## 2. Severity model

- **HIGH** — a11y hard stop, broken task flow, shipping blocker.
- **MEDIUM** — usability friction, consistency debt, perf risk.
- **LOW** — polish, taste refinement.

`uiux polish` maps severities to P0/P1/P2. Accessibility always outranks
visual polish (priority 4 > 9).

## 3. Review ritual (per release or per feature)

1. `uiux review <project>` — triage HIGHs immediately.
2. Manual checklist per dimension above (30–60 min honest pass).
3. Compare against 2–3 retrieved references (`uiux search "<concept>"`) —
   not to copy, but to notice what they solve that this design doesn't.
4. Re-run after fixes; record deltas in `.uiux/quality-report.md`.

## 4. Report format (quality-report.md)

Per finding: `[SEVERITY] area — title`, evidence (file/token), concrete fix.
Report closes with the automated/manual split made explicit so nobody
mistakes a clean static pass for "quality achieved".

## 5. What automation will never judge

- Whether the hero claim earns the scroll.
- Whether the information density matches the audience's expertise.
- Whether the design feels inevitable or assembled.

For those, use the taste card and the pattern library's
use_when/avoid_when rules (`KNOWLEDGE/patterns/INDEX.md`).
