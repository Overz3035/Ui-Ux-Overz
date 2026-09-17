# MODULE — Search & Retrieval

Code: `CLI/uiux/search.py`, vectors in `CLI/uiux/embed.py`.

## Hybrid score

```
score = 0.55·lexical + 0.25·concept + 0.20·visual      (configurable)
```

- **lexical**: exact tag matches against the asset_tags table (each asset's
  tags are facet-prefixed like `style:dark_ui`).
- **concept**: CONFIG/concepts.yaml expansion — "premium" pulls
  muted_neutral, minimal_spacious, monochrome… with weights; "industrial"
  pulls data_dense, dashboard, sidebar_content…
- **visual**: feature-space similarity via adjective anchors (dark, dense,
  minimal, colorful, dashboard…) mapped onto the compact feature vector;
  image-based visual queries arrive through the embedding store.

## Providers (replaceable, §14)

| Provider | Needs | Role |
|---|---|---|
| visual-stat | Pillow+numpy | deterministic image descriptors |
| lexical-concept | nothing | text queries → tag-space vectors |
| st-neural | sentence-transformers | richer text embeddings (auto-used when importable) |

Matrices live in `INDEX/embeddings/{visual,text}.f32` + `ids.json` manifests.

## Context pack (the model-facing interface, §29)

`uiux search "<q>" --context-pack` → ≤ 12 entries of: ref name, type,
ui_category, layout, style, motion, 4 palette hexes, score, matched
patterns. A few hundred bytes each. Everything else stays on disk.

## Failure modes

- Empty index → command says so; run ingest.
- Provider changed since build → automatic fallback to lexical vectors.
- No matches → broaden query or lower thresholds; concept expansion already
  widens synonyms.
