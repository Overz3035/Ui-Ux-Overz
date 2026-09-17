# ENGINE — Accessibility Engine (§25)

Accessibility is priority 4: overridable only by explicit user/product
requirements — never by visual trends, external skills, or references.

## 1. Contrast

| Pair | Minimum |
|---|---|
| Body text | 4.5:1 |
| Large text (≥ 24 px / 18.66 px bold) | 3:1 |
| UI components & graphical objects | 3:1 |
| Disabled controls | exempt, but pair with aria-disabled |

The DNA generator pre-checks `text`, `muted`, `on_accent` against
`background`. During review, run `uiux review` — it computes ratios for
declared CSS var pairs.

## 2. Keyboard (every surface)

- Full tab order; no positive `tabindex`; skip link as first tab stop.
- All functionality operable: Enter/Space activate; Esc closes; arrows for
  composite widgets (menus, tabs, lists) per ARIA APG.
- Visible focus: `:focus-visible` with the accent token, ≥ 2 px, offset ≥ 2 px,
  never `outline: none` without replacement.
- No keyboard traps (modals return focus on close).

## 3. Semantics

- Landmarks: `header/nav/main/aside/footer`; one `<main>`.
- Heading order logical, no skips; the page has an `<h1>`.
- Buttons are `<button>`, links are `<a href>`; `<div onClick>` is a defect.
- Every `<input>` has a programmatic label; error text linked via
  `aria-describedby`; invalid state via `aria-invalid`.
- Decorative media: `alt=""`; informative media: concise alt; complex media:
  adjacent description.
- Icons that carry meaning get `aria-label` or `title`.

## 4. Touch targets

≥ 44 × 44 px (WCAG 2.2 target size) on coarse pointers; adjacent targets
separated ≥ 8 px.

## 5. Motion & vestibular safety

`prefers-reduced-motion` handling is mandatory
(`motion-engine.md` §5). Ambient/parallax/3D loops: pausable, static
equivalent, never convey unique information through motion alone.

## 6. Screen reader compatibility

- Dynamic regions announced politely: `aria-live="polite"` (toasts, results
  count), never `"assertive"` for non-emergencies.
- Loading states: `aria-busy`; progress: role/aria-valuenow.
- Charts: text summary or data table alternative; do not leave an `<svg>`
  silent and essential.

## 7. Forms & errors

- Labels visible (placeholder is not a label).
- Validate on submit-first; on error, focus the first invalid field,
  announce message, keep user input intact.
- Error copy states what happened and how to fix it (no "invalid input").

## 8. Automated + manual split

- **Automated** (`uiux review`): contrast pairs, missing alt, label-less
  inputs, div-onClick, heading skips, missing reduced-motion, missing focus
  styles.
- **Manual (checklist)**: screen-reader smoke test of one critical flow,
  keyboard-only run, zoom to 200%, drag alternatives for sliders, color
  blindness spot check (never color-only status).

## 9. Hard stops (a review finding of these blocks shipping)

Missing reduced-motion handling · body contrast < 4.5:1 · focus removed ·
unlabeled form controls · keyboard-inaccessible primary action.
