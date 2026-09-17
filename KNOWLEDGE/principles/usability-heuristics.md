# KNOWLEDGE — Usability Heuristics

Condensed from Nielsen's heuristics + task-surface practice. Consult during
review (quality-engine) and design (DNA application).

1. **System status** — always answer "did that work?" within 100 ms
   (optimistic UI) or show progress; never leave a silent gap.
2. **Match the real world** — use the audience's vocabulary (operator:
   "deviation", not "variance anomaly").
3. **User control** — exits visible (undo, cancel, back); destructive
   actions are two-step and typed where irreversible.
4. **Consistency** — same object = same behavior across views; the DNA is
   the arbiter.
5. **Error prevention over messages** — constrain inputs, confirm rarely,
   make the right action the default.
6. **Recognition, not recall** — labels visible, history visible, no
   memorized codes; icons always paired with labels on first use.
7. **Flexibility** — keyboard paths for frequent users; pointer paths for
   first-timers; remember defaults per user.
8. **Aesthetic minimalism** — every element competes with the primary
   content; density is earned by need (data_heavy projects) not by habit.
9. **Error recovery** — say what happened, why, and the way out; keep
   user input intact.
10. **Help when needed** — contextual hints at the point of friction, not a
    docs detour.

## Task-surface additions

- First answer above the fold: "is anything wrong?" (kpi_summary_row).
- Comparison needs adjacency; analysis needs zoom; monitoring needs glance-
  ability. Choose table vs chart by the job, not by fashion.
- Persistent global navigation only when pivoting between 5+ peer sections
  (`persistent_sidebar` pattern); otherwise it is chrome tax.
- Empty states teach: show the shape of the content to come, plus the
  single action that creates it.
