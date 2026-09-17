# UI UX Pro Max Adapter (§19)

**Role:** detect the external UI UX Pro Max engine, preserve its native
behavior, route appropriate tasks to it, and degrade honestly when absent.

## Detection (implemented in CLI/uiux/promax.py, run by `uiux doctor`)

Probes, in order, across skill homes
(`~/.kilo/skills`, `~/.claude/skills`, `~/.agents/skills`, engine vendor dir):

1. skill folder with `SKILL.md` (names: ui-ux-pro-max / uiux-pro-max / ui_ux_pro_max)
2. its native CLI: `src/ui-ux-pro-max/scripts/search.py`

Verified on this machine: **installed** at `~/.kilo/skills/ui-ux-pro-max`
with a working search CLI. `uiux doctor` writes the result to
`INDEX/resource-state.json`; `CONFIG/resources.yaml` merges it at runtime.

## Native interface (verified)

```bash
python <skill>/src/ui-ux-pro-max/scripts/search.py "<query>" \
  --domain <product|style|typography|color|landing|chart|ux|icons|react|web|google-fonts|gsap> \
  [-n N] [--design-system --variance 1-10 --motion 1-10 --density 1-10] \
  [--stack html-tailwind|react|nextjs|...|threejs]
```

Domains auto-detect when omitted. The engine invokes it argv-style (no
shell) via `promax.invoke()` and summarizes output into the task plan —
never forwarding raw dumps into model context.

## Routing policy (ENGINE/resource-router.md §4)

| Task kind | When installed | When absent |
|---|---|---|
| design-system-generation | route to native CLI (`--design-system` dials) | `ENGINE/design-dna-engine.md` |
| ui-ux-audit | route; merge with `uiux review` | `ENGINE/quality-engine.md` |
| product-design-guidance | route with `--domain` matching the question | internal KNOWLEDGE cards |
| component-spec | route with `--stack` + `--domain` | `ENGINE/frontend-engine.md` |

Everything else stays with the engine's own modules.

## Guarantees

- No fabricated commands: every flag used here is verified against the
  installed SKILL.md; `promax.invoke()` omits unsupported flags.
- The adapter never modifies the skill; it calls it read-only.
- `route()` returns the explicit fallback paths when not installed, so
  agents never dead-end.
