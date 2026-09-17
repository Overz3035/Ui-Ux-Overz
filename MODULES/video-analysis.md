# MODULE — Video Analysis

Code: `CLI/uiux/videofeat.py` (ffprobe + ffmpeg; optional otherwise).

## Outputs per video

| Field | How |
|---|---|
| duration, width, height, fps, codec, bit_rate | ffprobe JSON |
| aspect | width/height |
| keyframes (default 8) | ffmpeg timestamp seeks, scaled to ≤ 640 px, saved under INDEX/cache/video/<hash>/ |
| contact sheet | 4×2 PIL grid of keyframes (contact-sheet.jpg) |
| scene_cuts | ffmpeg scene-change detection (gt(scene,0.30)) |
| motion_energy | mean frame difference over 24 decoded 96×54 grayscale frames (normalized) |
| vertical_flow | ratio of vertical to horizontal difference energy (scroll vs lateral motion) |
| kf_hashes | per-keyframe ahash → aggregated phash (majority vote) for dedup |
| descriptor | mean of per-keyframe 288-D visual descriptors |
| palette, feats | from the middle keyframe |
| motion_category | taxonomy rules over motion features + filename/OCR |

## Motion categories (§10)

hover · scroll · parallax · page_transition · navigation · card · button ·
cursor · micro_interaction · loading · hero · three_d · shader · liquid ·
text_animation · background · misc

## Rules

- Entire videos are never sent to any model. Keyframe thumbnails stay on
  disk; only compact metadata enters indices/context packs.
- Missing ffmpeg ⇒ capability_gap `ffmpeg_missing`; the asset still indexes
  with basic probe data (and works if ffprobe-only tasks need it).
- Keyframe extraction cost is bounded (≤ 8 seeks + 24-frame decode).
