# WORKFLOW — Ingest & Index

Purpose: turn a folder of reference images/videos into a searchable,
deduplicated, pattern-extracted knowledge index.

## 1. Drop assets

```
INBOX/
  sources/source-001/          <- known groups (keep folder structure)
    images/ videos/
  images/  videos/  loose/     <- loose assets (grouped by filename stems)
```

## 2. Run

```powershell
uiux ingest          # full pipeline
uiux status          # pending count / totals
uiux update          # incremental: new/changed files only
```

## 3. What happens per asset

| Step | Detail |
|---|---|
| cache check | content hash + analyzer fingerprint; unchanged files skip analysis |
| analysis | images: features/palette/hashes (+OCR if tesseract); videos: ffprobe, keyframes, motion metrics |
| classification | taxonomy rules → ui_category, components, style, layout, motion |
| naming | descriptive generated name (`dashboard-bento-grid-dark-ui-015.jpg`) |
| materialize | hardlink into REFERENCES/ (originals untouched) |
| sources | folder groups = high confidence; stem groups = medium; else low |
| dedupe | exact (sha256) + perceptual (phash) → duplicate_of / similar_to |
| clustering | tag-space threshold clustering → cluster_id + labels |
| patterns | taxonomy design_patterns → evidence + KNOWLEDGE/patterns/INDEX.md |
| embeddings | visual + text vectors → INDEX/embeddings/*.f32 |
| exports | INDEX/{images,videos,sources,patterns,clusters}.json |

## 4. Guarantees

- Originals are never modified, moved, or deleted (`dedup.delete_originals=false`).
- Re-ingest is idempotent; changed files re-analyze automatically.
- Missing ffmpeg/tesseract degrade gracefully and record capability_gaps.
