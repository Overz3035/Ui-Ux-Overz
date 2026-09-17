# MODULE — Image Analysis

Code: `CLI/uiux/imagefeat.py` (Pillow + numpy only; no model calls).

## Outputs per image

| Field | How |
|---|---|
| dimensions / aspect / megapixels | header + verified load |
| brightness, contrast, dark/light ratio | luminance stats (Rec.709 luma) |
| saturation, colorfulness (Hasler–Süsstrunk), hue spread, warm/cool/neutral ratios | HSV + opponent channels |
| unique_colors | 15-level RGB quantization |
| edge_density | Sobel magnitude above adaptive threshold |
| text_density | fine/coarse detail ratio gated by local bimodality (glyph-scale speck detection) |
| vertical/horizontal structure, grid_score | edge-energy peakiness + autocorrelation periodicity |
| panel_score | flat-region share + rectilinearity of long straight runs (UI chrome vs photo clutter) |
| corner_radius_hint | curved strong edges not on straight runs |
| palette | k-means in OKLab (deterministic seeding), top-6 with ratios |
| ahash / dhash / phash | 64-bit perceptual hashes (numpy DCT) |
| descriptor | 288-D visual-stat vector (colour identity, composition, rhythm, palette, text bands, aspect) |
| ocr_text | tesseract via pytesseract when installed; else capability_gap |

## Classification contract

Features feed CONFIG/taxonomy.yaml rules (`when` predicates). Every tag is
traceable to a rule — edit taxonomy.yaml to teach the engine, no code change.

## Cache

Cache key = sha256(content)[:24] + analyzer fingerprint [:12] + kind, stored
under INDEX/cache/. Re-analysis happens only when content, analyzer version,
or analyzer-relevant config changes.

## Limits (honest)

No semantic understanding of what text says (without tesseract), no brand
detection, no layout-tree extraction. Those are optional future providers;
the interface (`analyze_image(path) -> dict`) is the boundary.
