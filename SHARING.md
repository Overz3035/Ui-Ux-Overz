# SHARING — giving the engine to someone else

The whole engine is ONE portable folder. No installer, no npm, no registry.

## The 2-command share

1. **Zip and send** the `UIUX-ENGINE` folder (any channel: USB, cloud, git).
   `INDEX\` (your index/embeddings/cache) can be excluded to shrink it — the
   friend can rebuild it from their own INBOX, or inherit yours.
2. **Friend unzips anywhere** and runs once:

   ```powershell
   powershell -ExecutionPolicy Bypass -File SCRIPTS\install.ps1 -AddPath
   ```

   (Requires Python 3.10+; installs Pillow/numpy, writes the `uiux` shim,
   probes ffmpeg/tesseract — never downloads anything.)
3. **Friend binds a project** — from anywhere:

   ```powershell
   powershell -ExecutionPolicy Bypass -File <engine>\SCRIPTS\activate.ps1 -Project D:\work\their-project
   ```

That's it. From then on, any agent opened inside that project automatically
uses the engine: `.uiux\design-dna.md` is the visual law, `.claude\skills\`,
`.agents\skills\` and `.kilo\command\` carry the binding, and `AGENTS.md`
holds a managed rules block.

## Single-file mode (copy activate into the project)

`SCRIPTS\activate.ps1` (PowerShell) and `SCRIPTS\activate.sh` (bash/Git
Bash) are **self-contained**: copy just that one file into any project and
run it there — it finds the engine via `UIUX_ENGINE_HOME` or the known
install paths:

```bash
# Git Bash / WSL: copy activate.sh into the project, then
bash activate.sh              # binds the current directory
bash activate.sh --remove     # unbinds (keeps .uiux data)
```

If the engine isn't installed on the machine yet, the script says so
clearly (`-Engine` flag points it at the unzipped folder).

## What activate creates in a project

| File | Purpose |
|---|---|
| `.uiux\design-dna.md` | generated Design DNA (never overwritten; updates go to `design-dna.proposed.md`) |
| `.uiux\tokens.json`, `motion.json`, `context.json` | machine-readable DNA |
| `.claude\skills\uiux-engine\SKILL.md` | Claude Code binding |
| `.agents\skills\uiux-engine\SKILL.md` | universal agents binding |
| `.kilo\command\uiux.md` | Kilo Code slash command |
| `AGENTS.md` (managed block) | rules for AGENTS.md-aware agents |

## Notes

- `activate` writes the engine's absolute path into the project files.
  If the engine folder later moves, re-run activate once.
- Global methodology skills (Emil Kowalski, Genjutsu, taste,
  frontend-design, motion-design, web-design-guidelines, UI UX Pro Max) are
  installed on the friend's machine by the same skills commands if they want
  the full toolbox — see CONFIG\resources.yaml `install:` fields for each.
  The engine degrades gracefully without them.
- To share references too: send your `INBOX\` folder; the friend runs
  `uiux ingest` once (~1-3 min for a few hundred assets).
