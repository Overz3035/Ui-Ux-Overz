# KiloCode Adapter

KiloCode integrates through project commands and the CLI.

## Setup

1. `SCRIPTS\install.ps1` (engine-side; once per machine).
2. Copy the command files from `commands/` into the project's
   `.kilo/command/` directory (KiloCode loads them as slash commands), or
   into the global config `~/.config/kilo/command/`.
3. Run `uiux init <project>` to create `.uiux/` context + Design DNA.

## Provided commands (commands/)

| File | Slash command | Effect |
|---|---|---|
| uiux-search.md | /uiux-search | runs a context-pack search for a concept |
| uiux-dna.md | /uiux-dna | generates or reviews the project Design DNA |
| uiux-review.md | /uiux-review | runs the quality review flow |
| uiux-ingest.md | /uiux-ingest | ingests new INBOX assets |

## Behavior contract

- Commands shell out to the `uiux` shim (or `python -m uiux` with
  PYTHONPATH set to `<engine>/CLI`).
- Agents follow `.uiux/design-dna.md` as visual law and
  `ENGINE/orchestrator.md` for routing; progressive loading per
  `ENGINE/token-efficiency.md`.
