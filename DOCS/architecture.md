# Architecture

```
UIUX-ENGINE/
├─ INBOX/            raw intake (sources/<group>/, images/, videos/, loose/)
├─ SOURCES/          per-source metadata (source.json per group)
├─ REFERENCES/       renamed hardlinks of indexed assets (originals untouched)
├─ INDEX/            uiux.db (SQLite), embeddings/, cache/, JSON exports,
│                    uiux.log, resource-state.json
├─ KNOWLEDGE/        reusable knowledge cards + generated pattern library
├─ ENGINE/           the intelligence contracts: orchestrator, motion, 3d,
│                    frontend, responsive, accessibility, quality, DNA,
│                    resource router, priority hierarchy, token efficiency
├─ SKILLS/           agent-facing skill cards (uiux-engine/SKILL.md)
├─ PROMPTS/          session bootstrap / design / implementation prompts
├─ WORKFLOWS/        end-to-end runbooks (new project, ingest, design, audit)
├─ MODULES/          per-pipeline-stage docs (what/why/config/failure modes)
├─ ADAPTERS/         claude-code, opencode, kilocode, ui-ux-pro-max
├─ SCRIPTS/          uiux.cmd / uiux.ps1 launchers, install.ps1/bat
├─ CLI/uiux/         the Python package (all pipeline code)
├─ CONFIG/           config.default.yaml + config.yaml + taxonomy/concepts/resources
├─ DOCS/             these documents
└─ VERSION           engine/analyzer/index/schema/naming/embedding/knowledge
```

## Data flow

```
INBOX ──discover──▶ jobs ──analyze (cached)──▶ features/palette/hashes/keyframes
        │                                          │
        ├─ sources (folder/stem)                   ▼
        │                                    classify (taxonomy)
        │                                          ▼
        └────────────────────────▶ naming ──▶ REFERENCES (hardlinks)
                                                   │
       dedupe (sha256 + phash) ─▶ duplicate_of/similar_to/cluster_id
       clusters (tag-space cosine) ─▶ cluster_id + labels
       patterns (requires-maps) ─▶ patterns table + KNOWLEDGE/patterns
       embeddings (visual/text) ─▶ INDEX/embeddings
       exports ─▶ INDEX/*.json          SQLite = source of truth
                   │
                   ▼
      uiux search --context-pack ─▶ TOP-N compact JSON ─▶ agent context
```

## Design decisions

1. **SQLite primary, JSON exports secondary** — one consistent store for
   10k+ assets; exports stay human-diffable for portability.
2. **Cache keyed by content + analyzer fingerprint** — config or analyzer
   bumps re-analyze; unchanged bytes never do.
3. **Rule-based classification** — inspectable, editable via taxonomy.yaml,
   zero model cost; the model is reserved for judgment tasks.
4. **Annotate-only dedup** — originals are sacred; duplicates carry
   `duplicate_of`/`similar_to`/`cluster_id`.
5. **Provider seams** — embeddings and OCR degrade or swap without touching
   pipeline code (`capability_gaps` records what was skipped).
6. **DNA = decisions, templates = none** — see ENGINE/design-dna-engine.md.
