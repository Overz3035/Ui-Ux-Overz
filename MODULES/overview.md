# MODULES — overview

Each module is one pipeline stage. Status: **implemented** unless noted.

| Module | Code | Doc |
|---|---|---|
| discovery | `CLI/uiux/ingest.py :: discover` | MODULES/ingest.md |
| image analysis | `CLI/uiux/imagefeat.py` | MODULES/image-analysis.md |
| video analysis | `CLI/uiux/videofeat.py` | MODULES/video-analysis.md |
| classification | `CLI/uiux/classify.py` + CONFIG/taxonomy.yaml | MODULES/classification.md |
| naming | `CLI/uiux/naming.py` | MODULES/naming.md |
| dedup | `CLI/uiux/dedupe.py` + `hashing.py` | MODULES/dedup.md |
| clustering | `CLI/uiux/cluster.py` | MODULES/clustering.md |
| embeddings | `CLI/uiux/embed.py` | MODULES/embeddings.md |
| search | `CLI/uiux/search.py` | MODULES/search.md |
| patterns | `CLI/uiux/patterns.py` + taxonomy §design_patterns | MODULES/patterns.md |
| design DNA | `CLI/uiux/dna.py`, `projectctx.py` | ENGINE/design-dna-engine.md |
| project init | `CLI/uiux/projectctx.py` | MODULES/project-init.md |
| review/polish | `CLI/uiux/review.py` | ENGINE/quality-engine.md |
| resource router | `CONFIG/resources.yaml` + `CLI/uiux/promax.py` | ENGINE/resource-router.md |

Convention: each module degrades gracefully (capability_gaps recorded),
caches by content hash + analyzer fingerprint, and never mutates originals.
