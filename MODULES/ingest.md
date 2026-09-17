# MODULE — Ingest Pipeline

Code: `CLI/uiux/ingest.py`. Orchestrates discovery → analysis → naming →
sources → indexing. See WORKFLOWS/ingest-and-index.md for the operator view.

## Discovery buckets

| Location | Treatment |
|---|---|
| INBOX/sources/<group>/** | source group (kind=folder, confidence=high) |
| INBOX/<other-folder>/** | source group when `auto_source_from_folder` (default on) |
| INBOX/{images,videos,loose}/** | loose assets |
| INBOX/*.* | loose assets |

## Source inference (loose assets, §8)

- Filename-stem normalization: strip trailing `_N`/`-N` counters.
- ≥ `ingest.infer_source_min_assets` (default 2) sharing a stem ⇒ inferred
  group, confidence=medium.
- Meaningless stems (pure timestamps, "screenshot", empty) are skipped —
  those assets stay ungrouped with `source_confidence: low`.

## Naming & materialization

- Generated names via `naming.py` (category + up to 4 distinguishing tags
  + sequence). `_unknown` tags never reach filenames.
- REFERENCES/<images|videos>/<generated> via hardlink (fallback copy across
  volumes; symlink mode configurable; `none` to index in place).
- Sequence numbers are per-category-prefix and persist across runs through
  collision-avoidance on existing files.

## Concurrency

Thread pool (default `cpu_count-1`) for analysis; ffmpeg/ffprobe calls are
subprocess-isolated. SQLite writes are serialized on the main thread.

## Idempotency & cache

- Cache key: content sha256 + analyzer fingerprint + kind (INDEX/cache).
- Upserts keyed by original_path; source fields always reflect the latest
  discovery pass; changed files re-analyze automatically.
