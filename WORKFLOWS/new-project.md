# WORKFLOW — New Project End-to-End

From zero to a designed, reviewed implementation.

```
[0] install once     SCRIPTS\install.ps1          (verify env, uiux shim)
[1] references       drop assets into INBOX\{sources,loose}
[2] index            uiux ingest                  (analyze, name, dedupe,
                                                   cluster, patterns, embed)
[3] attach project   uiux init <project>          (.uiux/ context + DNA)
[4] route            ENGINE/orchestrator.md       (classify task, pick modules)
[5] references       uiux search "<concept>" --context-pack
[6] design           apply design-dna.md + routed knowledge cards
[7] implement        ENGINE/frontend-engine.md    (tokens, components, pages)
[8] verify           uiux review <project>        (report + polish plan)
[9] maintain         uiux update                  (new INBOX assets only)
```

Failure modes and exits:

- `uiux doctor` fails a required check → fix env, re-run installer.
- Index empty → knowledge-only mode; engines still produce a DNA.
- UI UX Pro Max absent → internal DNA engine (adapter handles).
- Review HIGHs remain → do not declare the task complete.
