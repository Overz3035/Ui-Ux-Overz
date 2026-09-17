---
description: Run UIUX ENGINE quality review and produce a prioritized polish plan.
---
# UIUX Review

Project: $ARGUMENTS (default: current directory)

Steps:

1. Run `uiux review "<project>"` → writes `.uiux/quality-report.md`.
2. Run `uiux polish "<project>"` → writes `.uiux/polish-plan.md` (P0/P1/P2).
3. Read the report. Fix P0 (HIGH) findings now, especially accessibility
   hard stops: missing reduced-motion handling, contrast < 4.5:1, removed
   focus, unlabeled inputs, keyboard-inaccessible actions.
4. Re-run review to confirm. Report deltas.
5. Manual pass reminder: static review cannot judge taste, task flow, or
   performance — list which manual checks from `ENGINE/quality-engine.md`
   still apply for the changed surfaces.
