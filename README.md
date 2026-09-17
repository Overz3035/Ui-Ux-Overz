# UIUX ENGINE

A portable, reusable **design intelligence engine** — not a template
generator. It ingests your local reference library (images/videos), turns
it into inspectable knowledge, generates a unique Design DNA per project,
routes external resources intelligently, and reviews implementations —
all locally, with minimal token consumption.

## Core ideas

| Principle | Implementation |
|---|---|
| Design intelligence, not templates | 8-direction DNA generator seeded per project; references supply principles only |
| Two projects never look alike | every axis (palette/typography/spacing/density/radius/motion/layout) derived from project inputs |
| Priority hierarchy | user > project > audience > accessibility > UX > existing system > brand > technical > engine > skills > libraries > references |
| Local-first | classification, dedup, naming, search, patterns: zero model calls; media never leaves disk |
| Token efficiency | `uiux search --context-pack` = the only model-facing reference payload (≤ 12 compact entries) |
| Annotate-only dedup | originals never deleted; duplicate_of / similar_to / cluster_id |
| Progressive loading | orchestrator routes; ≤ 3 knowledge cards per task |

## Quick start

```powershell
git init 2>nul & cd UIUX-ENGINE
powershell -ExecutionPolicy Bypass -File SCRIPTS\install.ps1 -AddPath

uiux doctor                                  # capabilities
uiux ingest                                  # index INBOX references
uiux search "premium enterprise dashboard"   # hybrid semantic search
uiux init .\my-project                       # attach project + Design DNA
uiux review .\my-project                     # quality report + polish plan
```

## One command, full design pipeline

```powershell
uiux build "premium industrial control dashboard with dense data" --project .\my-app
```

This runs the entire local pipeline in one shot: context pack from your
reference library + UI UX Pro Max design-system intelligence + Design DNA
generation + a routed implementation plan (`.uiux/design-plan.md`). The
`uiux-engine` skill (installed in `~\.kilo\skills\uiux-engine`) makes agents
execute this flow automatically when you ask for a design in any project —
including review and P0 fixes.

## Bind any project (one command) — shareable

```powershell
powershell -ExecutionPolicy Bypass -File SCRIPTS\activate.ps1 -Project D:\work\my-app
```

Writes `.uiux/` (Design DNA), project-scoped agent skills, and a managed
AGENTS.md block — so every future agent session in that project runs the
design pipeline automatically. Unbind with `-Remove`.
**Sharing with someone else**: send the folder + 2 commands.
See `SHARING.md`.

## Commands

`init` · `ingest` · `update` · `search` · `analyze` · `design` · `review` ·
`polish` · `status` · `doctor` · `version` — all support `--json`.
See DOCS/cli.md.

## Layout

INBOX (raw) → SOURCES (metadata) → REFERENCES (renamed hardlinks) →
INDEX (SQLite + embeddings + exports) → KNOWLEDGE (patterns/cards) →
ENGINE (orchestrator + 8 engine contracts) → ADAPTERS (Claude Code,
OpenCode, KiloCode, UI UX Pro Max). Full map: DOCS/architecture.md.

## Status of external resources

Classified in CONFIG/resources.yaml from RESOURCE-LIST.md with confidence
levels. Live detection via `uiux doctor`. UI UX Pro Max: installed here and
invoked through its native CLI (ADAPTERS/ui-ux-pro-max/). Unresolved
identities (e.g. "Genjutsu") are marked UNKNOWN and the router never acts
on them.

## Security

No downloads, no remote execution, no network in pipelines (config
`security.allow_network=false`). External resources are
classified → inspected → stored → approved before any activation.

## Docs

installation · architecture · cli · configuration · ingestion ·
design-dna · resource routing (ENGINE/resource-router.md) · adapters ·
troubleshooting · extending — see DOCS/.
