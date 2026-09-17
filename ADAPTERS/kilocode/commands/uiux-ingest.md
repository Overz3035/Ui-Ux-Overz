---
description: Ingest pending INBOX assets into the UIUX ENGINE index (analyze, name, dedupe, cluster, patterns).
---
# UIUX Ingest

1. Verify the engine: `uiux doctor` (report required failures, stop on any).
2. Run `uiux status` and report pending INBOX count. If zero, stop.
3. Run `uiux ingest` (long; up to a few minutes for hundreds of assets).
4. Report: discovered/analyzed/cached/errors, dedupe counts, cluster count,
   pattern count, export files written.
5. Remind: originals in INBOX are never modified; REFERENCES/ holds renamed
   hardlinks; SOURCES/<id>/source.json holds per-source metadata.
