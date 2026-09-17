# WORKFLOW — Audit & Polish

For taking an existing UI to a shippable state.

## 1. Automate

```powershell
uiux review <project>    # .uiux/quality-report.md (8 dimensions)
uiux polish <project>    # .uiux/polish-plan.md (P0/P1/P2)
```

## 2. Triage order (priority hierarchy applies)

1. P0 accessibility hard stops (`ENGINE/accessibility-engine.md` §9).
2. P0 broken task flows (quality-engine UX row, manual walk).
3. P1 usability + consistency + responsive failures.
4. P2 taste/motion polish (`KNOWLEDGE/principles/taste-and-visual-quality.md`).

## 3. Reference comparison (not copying)

`uiux search "<the surface's job>" --context-pack` — ask of each reference:
what does it solve that ours doesn't? Adopt the principle, restyle through
the DNA.

## 4. Fix → verify loop

- Implement fixes; re-run `uiux review`; confirm HIGH = 0.
- Manual checks that remain: keyboard-only run, SR smoke test, 320→1920
  matrix, reduced-motion walk, 200% zoom.
- Append remaining risks to the polish plan (never silently drop).

## 5. Exit criteria

- No P0s; P1s either fixed or scheduled with owner + date.
- Report + plan committed alongside the code for the next session.
