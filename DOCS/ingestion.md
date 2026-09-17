# Reference Library (Ingestion) Guide

## Layout

```
INBOX/
├─ sources/
│  ├─ source-001/
│  │  ├─ images/    47 images
│  │  └─ videos/    12 videos      ← same source, relationship preserved
│  └─ source-002/ ...
├─ images/           loose
├─ videos/           loose
└─ loose/            loose (images/, videos/, anything)
```

Supported: png, jpg, jpeg, webp, gif, bmp, tiff, avif · mp4, webm, mov,
m4v, mkv, avi (gif counts as both; analyzed as image + video).

## What you get after `uiux ingest`

- **SOURCES/&lt;id&gt;/source.json** — per-source metadata: label, kind
  (folder/inferred), confidence, counts, visual/motion language, every
  asset's original name + generated name.
- **REFERENCES/images|videos/&lt;generated&gt;** — descriptive names
  (dashboard-bento-grid-dark-ui-015.jpg, motion-scroll-parallax-003.webm)
  via hardlinks; originals keep their names in INBOX.
- **INDEX/** — SQLite (source of truth), JSON exports, embeddings, caches.

## Duplicate & cluster behavior

- exact dup ⇒ duplicate_of (first id wins); near-dup ⇒ perceptual threshold;
  similar-but-distinct ⇒ similar_to links. Nothing is ever deleted.
- Clusters group visually-related assets with dominant-tag labels.

## Confidence semantics

| confidence | meaning |
|---|---|
| high | real folder group under INBOX/sources (or auto-folder) |
| medium | filename-stem inference with ≥ N siblings |
| low | ungrouped loose asset (kept individually; never force-grouped) |

## Re-ingesting

- New/changed files only (content hash + analyzer fingerprint cache).
- Moving a file within INBOX creates a new asset row (path-keyed) — move
  before first ingest for best results.
- `uiux status` shows the pending count.
