#!/usr/bin/env bash
# UIUX ENGINE CLI launcher (bash / Git Bash / WSL).
# Works in place (inside the engine) OR copied standalone: falls back to
# UIUX_ENGINE_HOME and known install paths.
ENGINE_ROOT=""
CANDIDATES=()
[[ -n "${UIUX_ENGINE_HOME:-}" ]] && CANDIDATES+=("$UIUX_ENGINE_HOME")
CANDIDATES+=("$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)")
CANDIDATES+=("$HOME/Desktop/UIUX_ENGINE")
CANDIDATES+=("$HOME/UIUX_ENGINE")
for c in "${CANDIDATES[@]}"; do
  if [[ -f "$c/CLI/uiux/cli.py" ]]; then ENGINE_ROOT="$c"; break; fi
done
if [[ -z "$ENGINE_ROOT" ]]; then
  echo "uiux: engine not found. Set UIUX_ENGINE_HOME or use -e/--engine in activate." >&2
  exit 2
fi
export PYTHONPATH="$ENGINE_ROOT/CLI${PYTHONPATH:+:$PYTHONPATH}"
exec python -m uiux "$@"
