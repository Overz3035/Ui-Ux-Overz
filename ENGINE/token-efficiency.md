# ENGINE — Token Efficiency (§29)

The engine exists to keep the reference library OUT of the language model.
This card is the contract every adapter and workflow follows.

## Pipeline

```
INBOX → local analysis → metadata (SQLite) → embeddings
      → index → uiux search (local) → TOP-N context pack → project context → model
```

## Rules

1. **Local before model.** Classification, dedup, naming, search, and
   pattern extraction run without any model call. The model sees results.
2. **The context pack is the interface.** `uiux search "<q>" --context-pack`
   returns ≤ `search.max_context_references` entries, each a few hundred
   bytes: generated name, type, category, layout, style, motion, 4 palette
   hexes, matched patterns.
3. **Never paste into model context:** INBOX media, INDEX/*.json exports,
   full DB dumps, video keyframes, OCR blobs, entire KNOWLEDGE/ trees.
4. **Knowledge cards are lazy.** An agent loads ≤ 3 cards per task, cited in
   its plan (orchestrator §4).
5. **External engines get summarized.** UI UX Pro Max output is distilled
   into the plan — not forwarded verbatim.
6. **Media stay on disk.** The model may receive *file paths* of reference
   thumbnails (the model host can attach images itself if the user asks);
   the engine never encodes base64 into prompts.

## Sizing guidance

| Task | Context budget |
|---|---|
| Reference lookup | 1 context pack (~0.5–1k tokens) |
| Design DNA generation | answers JSON + ≤ 2 knowledge cards |
| Implementation | DNA + relevant engine card + 1 context pack |
| Review | quality report + accessibility card |

If a task seems to need more, the task is under-decomposed — split it.
