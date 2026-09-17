# MODULE — Knowledge Extraction (patterns, clusters, sources)

Code: `CLI/uiux/patterns.py`, `cluster.py`, `ingest.py :: summarize_source_languages`.

## Patterns (§15)

Taxonomy `design_patterns` entries declare `requires: {facet: [tags]}` plus
the transferable knowledge triple: principle / use_when / avoid_when. At
ingest end, evidence = assets whose tags satisfy the requirement map.

Outputs:
- `patterns` table + `pattern_evidence` (pattern ⇄ asset scores)
- knowledge graph edges (`pattern:X evidences asset:N`) in nodes/edges tables
  (Obsidian-inspired, no dependency — RESOURCE-LIST §6)
- `KNOWLEDGE/patterns/INDEX.md` — progressive-loadable cards with counts

The contract: references produce "persistent sidebar", "dense data table",
"scroll choreography", "reduced-motion fallback" — never "copy this site".

## Clusters

Tag-space cosine threshold clustering (config `cluster.threshold`).
Clusters get labels from dominant member tags and land in
`clusters` table + INDEX/clusters.json. Exact/near duplicates never lead a
cluster (they are excluded first).

## Source languages (§15)

Per source: visual_language (top style/category/layout tags), motion_language
(motion tags), counts, technology hints (registry-backed), usage categories —
written to the DB and to `SOURCES/<id>/source.json` for humans and adapters.
