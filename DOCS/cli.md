# CLI Reference

Invocation: `uiux <command> [args]` (shim) or
`PYTHONPATH=<engine>\CLI python -m uiux <command>`. All commands accept
`--json` (before or after the subcommand) for machine-readable output.

## uiux init `<project>` [`--answers file.json`]
Detect framework/styling/tokens/components, generate the Design DNA, write
`.uiux/` (never overwrites existing files), register the project.

## uiux ingest [`--workers N`] [`--no-dedupe`]
Full pipeline: discover → analyze (cached) → classify → name → materialize →
dedupe → cluster → patterns → source languages → embeddings → exports.

## uiux update
Incremental refresh: same pipeline; cached assets are skipped unless
changed. Alias for `ingest --no-dedupe=false`.

## uiux search `<query>` [`-n N`] [`--media image|video`] [`--context-pack`]
Hybrid semantic search. `--context-pack` emits the compact JSON that is
authorized to enter model context.

## uiux analyze `<path>` [`--max N`]
Analyze without ingesting (ad-hoc inspection). Prints features,
classification, palette (images) or probe/keyframes/motion (videos).

## uiux design [`--answers '<json>'|file`] [`--name X`] [`--out path`]
Generate a Design DNA without attaching a project. Writes markdown when
`--out` given; prints it otherwise.

## uiux build `<prompt>` [`--project path`] [`--out path`]
One-shot pipeline: context pack + UI UX Pro Max lookup + Design DNA +
implementation plan in a single command. Writes `.uiux/design-plan.md` and
`.uiux/design-dna.md` into the project (or `INDEX/plans/` for greenfield).
The agent then implements from the plan and runs review.

## uiux review `<project>`
Static quality review (a11y, motion, responsive, consistency) →
`.uiux/quality-report.md`.

## uiux polish `<project>`
Turns review findings into a P0/P1/P2 plan → `.uiux/polish-plan.md`.

## uiux status
Counts, last ingest time, pending INBOX files.

## uiux doctor
Environment + capability checks; resource detection (registry probes);
writes INDEX/resource-state.json. Exit code reflects required failures.

## uiux version
Prints engine/analyzer/index/schema versions (VERSION file).

## Exit codes

0 ok · 1 recoverable failure (errors during command, required doctor
failure, not found) · 2 CLI misuse · 130 interrupted.
