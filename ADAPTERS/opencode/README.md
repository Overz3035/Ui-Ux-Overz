# OpenCode Adapter

OpenCode sessions can use the engine through its CLI plus AGENTS.md rules.

## Setup

1. `SCRIPTS\install.ps1` (adds the `uiux` shim, writes INDEX/resource-state.json).
2. Append the content of `AGENTS-OPENCODE.md` below to the project's
   `AGENTS.md` (or OpenCode's global instructions file):

## AGENTS-OPENCODE.md (copy into your AGENTS.md)

```markdown
## UIUX ENGINE rules

- Engine root: <path to UIUX-ENGINE folder> (UIUX_ENGINE_HOME).
- For any UI/UX task, first read <engine>/ENGINE/orchestrator.md and follow
  its routing. Do not read other engine files unless routed to them.
- Project design law: .uiux/design-dna.md (created by `uiux init`).
- Reference retrieval: run `uiux search "<concept>" --context-pack` from the
  engine folder; treat its JSON as the only reference context.
- Reviews: `uiux review <project>` then `uiux polish <project>`; fix HIGH
  findings before completing UI tasks.
- Priority conflicts: <engine>/ENGINE/priority-hierarchy.md.
```

## Notes

- OpenCode has no native skill format dependency here; the CLI is the
  interface, the orchestrator card is the routing brain.
- All commands are read-only regarding project sources except `.uiux/`.
