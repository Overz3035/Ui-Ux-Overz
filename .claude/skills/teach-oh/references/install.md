# Teach-OH Install Reference

Load only after AGENTS.md context is drafted and the user wants optional OMP or Claude Code integration.

Set `<ref>` to a release tag or commit SHA for the skills version being installed. Do not fetch from a floating branch such as `master`. If a checksum is published for a downloaded file, verify it after download before installing.

## OMP Phase-Aware Hook

Offer only if OMP is detected (`.omp/` exists or `omp` is on PATH).

Ask:
> "Install the phase-aware skills hook? It reads `.oh/` session files and suggests the right OH skill at the right moment."

If accepted, fetch the canonical hook from:
`https://raw.githubusercontent.com/open-horizon-labs/skills/<ref>/hooks-omp/oh-skills-phase.ts`

Write it to `.omp/hooks/oh-skills-phase.ts`.
Optional checksum: `<sha256>`

Do not fabricate or rewrite the hook.

## OMP Phase Agents

Offer only after the hook step if OMP is detected.

Fetch canonical files from:
`https://raw.githubusercontent.com/open-horizon-labs/skills/<ref>/agents-omp/`

Files:
- `oh-aim.md`
- `oh-problem-space.md`
- `oh-problem-weave.md` (optional multi-layer framing gate)
- `oh-problem-statement.md`
- `oh-solution-space.md`
- `oh-execute.md`
- `oh-ship.md`

Reference files required by those agents:
- `references/framing.md`
- `references/depth.md`
- `references/drift-boundaries.md`
- `references/reality-contact.md`

Write agent files to `.omp/agents/`. Also fetch the required `references/` files from `agents-omp/references/` into `.omp/agents/references/`.

## Claude Code Phase Agents

Offer only if Claude Code is detected.

Fetch canonical files from:
`https://raw.githubusercontent.com/open-horizon-labs/skills/<ref>/agents-claude/`

Write to `.claude/agents/`.

Also fetch the same `references/` files from `agents-claude/references/` into `.claude/agents/references/`.

Pre-packaged Claude Code agents already include MCP preambles. Do not append custom preambles.
