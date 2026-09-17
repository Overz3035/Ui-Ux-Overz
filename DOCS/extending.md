# Extending the Engine

## 1. Teach the classifier (no code)

Edit `CONFIG/taxonomy.yaml`: add keywords (`any`), feature predicates
(`when`), or whole tags under any facet; add `design_patterns` entries with
principle/use_when/avoid_when. Bump `version:`. Re-run `uiux update`
(fingerprint change triggers re-analysis... only when analysis-relevant
config changes; classification is cheap and re-runs every ingest).

## 2. Teach the search (no code)

Edit `CONFIG/concepts.yaml`: add a concept with aliases and weighted
`expands_to`. Queries containing aliases now expand into your vocabulary.

## 3. Add an embedding provider

Implement `vector(text|image) -> np.ndarray (normalized)` and register the
name in `embeddings.visual_provider`/`text_provider` order. Neural text is
already wired (`st-neural`); images follow `imagefeat.visual_descriptor`.
Keep DIMENSIONS stable or bump `embeddings.dim_visual` + clear INDEX/embeddings.

## 4. Add a resource to the router

1. Classify it honestly (class, confidence — `unknown` stays inert).
2. Add an entry to CONFIG/resources.yaml under the right section with
   `detection` probes.
3. If it has a native CLI: add an adapter module like `CLI/uiux/promax.py`
   (detect/invoke/route), then wire routes in ENGINE/resource-router.md.
4. Security: inspect before storing; never auto-execute remote code.

## 5. Add a review check

`CLI/uiux/review.py`: pattern-based checks append findings
(area, severity, title, detail, fix, file). Keep checks honest — report
what cannot be known as manual-checklist items instead of guessing.

## 6. Add an adapter

Copy `ADAPTERS/opencode/` as a template: README (setup + AGENTS rules) +
optional command files. The adapter contract is CLI + orchestrator card;
nothing else is required.

## 7. Add a workflow/prompt

WORKFLOWS/ = operator runbooks; PROMPTS/ = session bootstraps. Keep each
progressive-loading compliant (≤ 3 knowledge cards, context-pack only).

## 8. Versioning discipline

Bump VERSION keys when behavior changes: `analyzer` (analysis outputs),
`naming` (name scheme), `embedding` (vector layout → clear embeddings dir),
`knowledge` (pattern catalog), `schema` (DB DDL → migration needed).
`engine` tracks releases. The analyzer fingerprint auto-invalidates caches
on config/taxonomy bumps.
