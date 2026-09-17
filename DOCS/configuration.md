# Configuration Guide

Layers (deep-merged, later wins):

1. `CONFIG/config.default.yaml` — baseline, do not edit
2. `CONFIG/config.yaml` — user overrides
3. `UIUX_<SECTION>__<KEY>` environment variables (e.g. `UIUX_SEARCH__WEIGHT_LEXICAL=0.7`)

## Path rules

All paths are relative to the engine root unless absolute. Portable setups
never need absolute paths; `paths.db/embeddings/cache` default under INDEX/.

## Key sections

| Section | Purpose | Notable keys |
|---|---|---|
| engine | mode | `strict` (fail on missing tools) vs `adaptive` (degrade + record gaps) |
| paths | locations | inbox, sources, references, index, knowledge, db, embeddings, cache |
| ingest | pipeline | materialize (hardlink/copy/symlink/none), max_file_mb, infer_source_min_assets, rename, workers |
| image_analysis | vision | work_size, palette_colors, hash bits, ocr.enabled/max_side |
| video_analysis | ffmpeg | enabled (auto), keyframes, keyframe_max_side, scene_threshold, contact_sheet |
| dedup | similarity | phash_threshold (near-dup), similar_threshold, video_threshold, delete_originals (always false) |
| cluster | grouping | method, distance, threshold (cosine), min_cluster_size |
| embeddings | providers | visual_provider, text_provider order, st_model |
| search | retrieval | weight_lexical/concept/visual, default_limit, max_context_references |
| cache | invalidation | enabled, invalidate_on |
| design | DNA | directions count, contrast floors, max_motion_ms, respect_reduced_motion |
| resources | router | registry path, auto_activate classes, disabled list |
| tools | binaries | pinned paths + search_paths (ffmpeg, ffprobe, tesseract) |
| security | posture | allow_network=false, allow_remote_resources=false |

## taxonomy.yaml

Rule-based classification vocabulary (ui_category, component_category,
visual_style, layout_pattern, motion_category) + design_patterns
(requirement maps with principle/use_when/avoid_when). Edit to teach the
engine; version-bumped entries invalidate the analyzer cache.

## concepts.yaml

Concept ontology powering semantic search without a neural model: aliases →
expands_to (weighted) → implies_tokens. Add your domain vocabulary here.

## resources.yaml

The classified registry of external resources (from RESOURCE-LIST.md) with
detection probes. `uiux doctor` writes live presence to
INDEX/resource-state.json; the loader merges it so `installed:` stays true
to reality without editing the registry.
