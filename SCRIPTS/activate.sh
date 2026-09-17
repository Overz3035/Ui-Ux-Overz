#!/usr/bin/env bash
# UIUX ENGINE - project activation (bash / Git Bash / WSL variant).
#
# Copy THIS file alone into any project and run:
#   bash activate.sh
# Or run from the engine:  SCRIPTS/activate.sh -p /path/to/project
#
# Same behavior as activate.ps1: verifies the engine, runs `uiux init`
# (Design DNA + .uiux/), writes project-scoped agent bindings
# (.claude/skills, .agents/skills, .kilo/command, AGENTS.md block).
#
# Remove:  bash activate.sh --remove
#
# Engine resolution order: --engine > $UIUX_ENGINE_HOME > this script's
# parent (in-engine) > known install paths.

set -euo pipefail

PROJECT="$(pwd)"
ENGINE=""
REMOVE=0
SKIP_DOCTOR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--project)  PROJECT="$2"; shift 2 ;;
    -e|--engine)   ENGINE="$2"; shift 2 ;;
    --remove)      REMOVE=1; shift ;;
    --skip-doctor) SKIP_DOCTOR=1; shift ;;
    -h|--help)
      echo "usage: bash activate.sh [-p project] [-e engine] [--remove] [--skip-doctor]"
      exit 0 ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac
done

# --- locate the engine --------------------------------------------------------
CANDIDATES=()
[[ -n "$ENGINE" ]] && CANDIDATES+=("$ENGINE")
[[ -n "${UIUX_ENGINE_HOME:-}" ]] && CANDIDATES+=("$UIUX_ENGINE_HOME")
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATES+=("$(dirname "$SELF_DIR")")                       # in-engine
CANDIDATES+=("$HOME/Desktop/UIUX_ENGINE")
CANDIDATES+=("$HOME/UIUX_ENGINE")
CANDIDATES+=("$(pwd)/UIUX_ENGINE")

ENGINE_ROOT=""
for c in "${CANDIDATES[@]}"; do
  if [[ -n "$c" && -f "$c/CLI/uiux/cli.py" ]]; then ENGINE_ROOT="$(cd "$c" && pwd)"; break; fi
done
if [[ -z "$ENGINE_ROOT" ]]; then
  echo "  [FAIL] engine not found. Pass it explicitly:" >&2
  echo "         bash activate.sh --engine /path/to/UIUX_ENGINE" >&2
  exit 1
fi
PROJECT="$(cd "$PROJECT" && pwd)"
echo "UIUX ENGINE activation"
echo "  engine : $ENGINE_ROOT"
echo "  project: $PROJECT"

export PYTHONPATH="$ENGINE_ROOT/CLI${PYTHONPATH:+:$PYTHONPATH}"
MANAGED="<!-- uiux-engine:managed -->"

# --- remove mode -----------------------------------------------------------------
if [[ "$REMOVE" == "1" ]]; then
  for rel in ".claude/skills/uiux-engine" ".agents/skills/uiux-engine" ".kilo/command/uiux.md"; do
    p="$PROJECT/$rel"
    if [[ -e "$p" ]]; then rm -rf "$p"; echo "  [OK]   removed $rel"; fi
  done
  if [[ -f "$PROJECT/AGENTS.md" ]] && grep -q "$MANAGED" "$PROJECT/AGENTS.md"; then
    python - "$PROJECT/AGENTS.md" <<'PYEOF'
import sys, re
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t = re.sub(r"(?s)<!-- uiux-engine:managed -->.*?<!-- /uiux-engine:managed -->\n?", "", t)
open(p, "w", encoding="utf-8", newline="\n").write(t)
PYEOF
    echo "  [OK]   AGENTS.md block removed"
  fi
  echo "  (index/.uiux data kept; run again to rebind)"
  exit 0
fi

# --- 1. health check -----------------------------------------------------------------
if [[ "$SKIP_DOCTOR" != "1" ]]; then
  echo "  [....] uiux doctor"
  python -m uiux doctor >/dev/null 2>&1 || echo "  [warn] doctor reported failures - continuing" >&2
  echo "  [OK]   doctor"
fi

# --- 2. attach project -----------------------------------------------------------------
echo "  [....] uiux init (framework detection + Design DNA)"
python -m uiux init "$PROJECT"

# --- 3. project-scoped agent skill -------------------------------------------------------
SKILL="$PROJECT/.claude/skills/uiux-engine"
mkdir -p "$SKILL" "$PROJECT/.agents/skills/uiux-engine" "$PROJECT/.kilo/command"
cat > "$SKILL/SKILL.md" <<SKILLEOF
---
name: uiux-engine
description: UIUX ENGINE is bound to THIS project. Use for every UI/UX task in this repo - design work, components, pages, motion, review. Reads .uiux/design-dna.md as the visual law and runs the engine CLI.
---

# UIUX ENGINE (project binding)

The engine root for this project: $ENGINE_ROOT

## Non-negotiables

1. \`.uiux/design-dna.md\` in this project is the visual LAW. Read it before
   any UI work; conflicts resolve by \`$ENGINE_ROOT/ENGINE/priority-hierarchy.md\`
   (user > project > audience > accessibility > existing system > engine).
2. References: \`$ENGINE_ROOT/SCRIPTS/uiux.sh search "<concept>" --context-pack\`
   is the ONLY authorized reference payload. Never open INDEX/*.json, INBOX
   media, or the whole KNOWLEDGE tree. Max 3 knowledge cards per task.
3. Methodology skills installed globally: emil-design-eng / animate /
   review-animations (animation craft), cast + paint (Genjutsu pipelines),
   design-taste-frontend, frontend-design, motion-design,
   web-design-guidelines. Load at most 3 per task.

## Commands (PYTHONPATH=$ENGINE_ROOT/CLI python -m uiux)

| Task | Command |
|---|---|
| references | \`uiux search "<concept>" --context-pack -n 8\` |
| refresh DNA | \`uiux init <project>\` (never overwrites existing DNA) |
| quality gate | \`uiux review <project>\` then \`uiux polish <project>\` - fix all P0 |
| index new refs | \`uiux update\` (only in the engine folder) |

## Definition of done (UI tasks)

- tokens from the DNA only (alias existing project tokens, never fork values)
- focus-visible + hover + active + disabled + reduced-motion on every
  interactive element; touch targets >= 44px
- responsive by adaptation (320/768/1024/1440), not desktop shrinkage
- \`uiux review\` clean of P0 findings
SKILLEOF
cp "$SKILL/SKILL.md" "$PROJECT/.agents/skills/uiux-engine/SKILL.md"
echo "  [OK]   .claude/skills/uiux-engine/SKILL.md"
echo "  [OK]   .agents/skills/uiux-engine/SKILL.md"

cat > "$PROJECT/.kilo/command/uiux.md" <<KILOEOF
---
description: Run the UIUX ENGINE design pipeline (references + DNA + plan) for this project.
---
# UIUX Design Pipeline

Engine root: $ENGINE_ROOT

1. Read .uiux/design-dna.md (visual law). If missing, run
   \`PYTHONPATH=$ENGINE_ROOT/CLI python -m uiux init <project>\`.
2. Retrieve references: \`uiux search "\$ARGUMENTS" --context-pack -n 8\`.
3. Route methodology skills (max 3): emil-design-eng / animate / cast /
   design-taste-frontend / frontend-design / motion-design /
   web-design-guidelines.
4. Produce a design plan citing DNA axes, then implement, then
   \`uiux review <project>\` - fix all P0 findings before finishing.
KILOEOF
echo "  [OK]   .kilo/command/uiux.md"

# --- 4. AGENTS.md managed block -------------------------------------------------------------
AGENTS="$PROJECT/AGENTS.md"
if [[ -f "$AGENTS" ]] && grep -q "$MANAGED" "$AGENTS"; then
  echo "  [skip] AGENTS.md already bound"
elif [[ -f "$AGENTS" ]]; then
  cat >> "$AGENTS" <<AGENTSEOF

$MANAGED
## UIUX ENGINE (managed - do not edit between these markers)

- Visual law: .uiux/design-dna.md (regenerate via uiux init; never overwrite)
- Priority order: user > project > audience > accessibility > existing
  system > brand > technical > engine > external skills > references
- References: $ENGINE_ROOT/SCRIPTS/uiux.sh search "<concept>" --context-pack
- Quality gate: $ENGINE_ROOT/SCRIPTS/uiux.sh review . (fix all P0)
- Full contract: .claude/skills/uiux-engine/SKILL.md
<!-- /uiux-engine:managed -->
AGENTSEOF
  echo "  [OK]   AGENTS.md block appended"
else
  cat > "$AGENTS" <<AGENTSEOF
# $(basename "$PROJECT")

$MANAGED
## UIUX ENGINE (managed - do not edit between these markers)

- Visual law: .uiux/design-dna.md (regenerate via uiux init; never overwrite)
- Priority order: user > project > audience > accessibility > existing
  system > brand > technical > engine > external skills > references
- References: $ENGINE_ROOT/SCRIPTS/uiux.sh search "<concept>" --context-pack
- Quality gate: $ENGINE_ROOT/SCRIPTS/uiux.sh review . (fix all P0)
- Full contract: .claude/skills/uiux-engine/SKILL.md
<!-- /uiux-engine:managed -->
AGENTSEOF
  echo "  [OK]   AGENTS.md created"
fi

echo ""
echo "  Bound. Open an agent in this project and describe what to design -"
echo "  the pipeline (references -> DNA -> implement -> review) runs automatically."
