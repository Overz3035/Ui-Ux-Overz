# Claude Code Adapter

## Setup

1. Run `SCRIPTS\install.ps1` once (verifies Python deps, writes the `uiux`
   shim, executes `uiux doctor`).
2. Install the master skill globally (done once, works in every project):

   ```powershell
   # the engine ships the skill; mirror it into the global skill homes
   Copy-Item -Recurse -Force SKILLS\uiux-engine ~/.claude/skills/uiux-engine
   ```

   The same folder already lives in `~\.kilo\skills\uiux-engine` and
   `~\.agents\skills\uiux-engine` on this machine.
3. Per-project: `uiux init <project>` creates `.uiux/` with the Design DNA
   and agent contract — or just say "design me X" and the skill runs the
   whole pipeline (`uiux build` included) automatically.

## Progressive loading contract

Claude Code sessions must NOT read the whole engine. The load order is:

1. `ENGINE/orchestrator.md` — always, it is short and routes everything.
2. `.uiux/design-dna.md` in the project — the visual law of that project.
3. On demand: the single ENGINE/<name>.md the orchestrator routes to.
4. References: `uiux search "<concept>" --context-pack` (compact JSON only).

Never read: INBOX media, INDEX/*.json exports, the full KNOWLEDGE/ tree, or
more than three knowledge cards per task.

## Command surface

| Task | Command |
|---|---|
| attach project, generate DNA | `uiux init <project>` |
| index reference assets | `uiux ingest` / `uiux update` |
| find references | `uiux search "<concept>" [-n 6] [--context-pack]` |
| generate a DNA standalone | `uiux design --answers '<json>' --out <path>` |
| quality report | `uiux review <project>` |
| prioritized fixes | `uiux polish <project>` |
| capabilities | `uiux doctor` |

## Session behavior

- Before UI work in an attached project: read its `design-dna.md`; follow
  the priority hierarchy for conflicts (`ENGINE/priority-hierarchy.md`).
- The DNA never overrides explicit user requirements or the project's
  existing design system.
- New visual decisions made during the session get appended to the DNA
  (changelog line), keeping it the single source of truth.
