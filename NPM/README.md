# uiux-overz

UIUX ENGINE design skills for any project — no GitHub, no zip, no heavy download.

## Install (one command, inside your project folder)

```bash
npx uiux-overz init
```

What it does (idempotent, re-run is safe):

| Creates | Purpose |
|---|---|
| `.agents/skills/*` | all 46 vendored skills (motion, design, workflow) |
| `.claude/skills/uiux-engine/SKILL.md` | Claude Code binding |
| `.kilo/command/uiux.md` | Kilo Code slash command |
| `AGENTS.md` (managed block) | rules for AGENTS.md-aware agents |
| `INBOX-OverzStyleUIUX/images/` + `videos/` | project media folders (with `.gitkeep`) |
| `.gitignore` rules | keeps committed media light |

Options:

```bash
npx uiux-overz init --dir ./my-app   # target another folder
npx uiux-overz init --minimal        # binder only, no 46-skill copy
npx uiux-overz --help
```

After that, open any agent in the project and describe what to design.
