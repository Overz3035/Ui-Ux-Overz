# UIUX ENGINE - project activation.
#
# ONE command to bind the engine to ANY project. Run from anywhere:
#
#   powershell -ExecutionPolicy Bypass -File <engine>\SCRIPTS\activate.ps1
#   powershell -ExecutionPolicy Bypass -File <engine>\SCRIPTS\activate.ps1 -Project D:\work\my-app
#
# What it does (idempotent, re-run is safe):
#   1. verifies the engine + Python deps (uiux doctor)
#   2. runs `uiux init` on the project -> .uiux\ (design-dna.md, tokens.json)
#   3. writes a project-scoped agent skill into .claude\skills, .agents\skills
#      and a .kilo\command\uiux.md slash command - so ANY agent opened in this
#      project auto-activates the engine with no global setup
#   4. appends a managed rules block to AGENTS.md (created if missing)
#
# Remove the binding with:  activate.ps1 -Project <path> -Remove
#
# ASCII-only on purpose (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Project = (Get-Location).Path,
    [string]$Engine = "",
    [switch]$Remove,
    [switch]$SkipDoctor
)

$ErrorActionPreference = "Stop"

# --- locate the engine -------------------------------------------------------
# Works BOTH in place (SCRIPTS\ inside the engine) AND as a single copied
# file inside any project: engine order = -Engine param > UIUX_ENGINE_HOME >
# this script's parent (in-engine) > known install paths.
$candidates = @()
if ($Engine) { $candidates += $Engine }
if ($env:UIUX_ENGINE_HOME) { $candidates += $env:UIUX_ENGINE_HOME }
$candidates += (Join-Path $PSScriptRoot "..")                       # in-engine
$candidates += "C:\Users\SRS\Desktop\UIUX_ENGINE"                   # known
$candidates += (Join-Path $env:USERPROFILE "UIUX_ENGINE")           # known
$candidates += (Join-Path $env:USERPROFILE "Desktop\UIUX_ENGINE")   # known
$candidates += (Join-Path (Get-Location).Path "UIUX_ENGINE")        # sibling

$engineRoot = $null
foreach ($c in $candidates) {
    if ($c -and (Test-Path (Join-Path $c "CLI\uiux\cli.py"))) {
        $engineRoot = (Resolve-Path $c).Path
        break
    }
}
if (-not $engineRoot) {
    Write-Host "  [FAIL] engine not found. Pass it explicitly:" -ForegroundColor Red
    Write-Host '         activate.ps1 -Engine "C:\path\to\UIUX_ENGINE"'
    exit 1
}
$project = (Resolve-Path $Project).Path
Write-Host "UIUX ENGINE activation"
Write-Host "  engine : $engineRoot"
Write-Host "  project: $project"

$env:PYTHONPATH = "$engineRoot\CLI;" + $env:PYTHONPATH
$python = (Get-Command python).Source
$managed = "<!-- uiux-engine:managed -->"

# --- remove mode --------------------------------------------------------------
if ($Remove) {
    foreach ($rel in @(".claude\skills\uiux-engine", ".agents\skills\uiux-engine",
                       ".kilo\command\uiux.md")) {
        $p = Join-Path $project $rel
        if (Test-Path $p) { Remove-Item -Recurse -Force $p; Write-Host "  [OK]   removed $rel" }
    }
    $agents = Join-Path $project "AGENTS.md"
    if (Test-Path $agents) {
        $text = Get-Content $agents -Raw
        if ($text.Contains($managed)) {
            $text = $text -replace "(?s)$managed.*?<!-- /uiux-engine:managed -->\r?\n?", ""
            Set-Content -Encoding UTF8 -Path $agents -Value $text
            Write-Host "  [OK]   AGENTS.md block removed"
        }
    }
    Write-Host "  (index/.uiux data kept; run activate again to rebind)"
    exit 0
}

# --- 1. health check -----------------------------------------------------------
if (-not $SkipDoctor) {
    Write-Host "  [....] uiux doctor"
    & $python -m uiux doctor | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [warn] doctor reported failures - continuing (details: uiux doctor)" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK]   doctor clean"
    }
}

# --- 2. attach project (detect + design DNA) ------------------------------------
Write-Host "  [....] uiux init (framework detection + Design DNA)"
& $python -m uiux init $project
if ($LASTEXITCODE -ne 0) { Write-Host "  [FAIL] uiux init" -ForegroundColor Red; exit 1 }

# --- 3. project-scoped agent skill ----------------------------------------------
# single-quoted here-string: nothing interpolates; ENGINE_ROOT_PLACEHOLDER and
# DOTDNA markers are replaced explicitly (backticks survive as literals).
$skillMd = @'
---
name: uiux-engine
description: UIUX ENGINE is bound to THIS project. Use for every UI/UX task in this repo - design work, components, pages, motion, review. Reads .uiux\design-dna.md as the visual law and runs the engine CLI.
---

# UIUX ENGINE (project binding)

The engine root for this project: ENGINE_ROOT_PLACEHOLDER

## Non-negotiables

1. `.uiux\design-dna.md` in this project is the visual LAW. Read it before
   any UI work; conflicts resolve by `ENGINE_ROOT_PLACEHOLDER\ENGINE\priority-hierarchy.md`
   (user > project > audience > accessibility > existing system > engine).
2. References: `ENGINE_ROOT_PLACEHOLDER\SCRIPTS\uiux.cmd search "<concept>" --context-pack`
   is the ONLY authorized reference payload. Never open INDEX\*.json, INBOX
   media, or the whole KNOWLEDGE tree. Max 3 knowledge cards per task.
3. Methodology skills installed globally: emil-design-eng / animate /
   review-animations (animation craft), cast + paint (Genjutsu pipelines),
   design-taste-frontend, frontend-design, motion-design,
   web-design-guidelines. Load at most 3 per task.

## Commands (via `ENGINE_ROOT_PLACEHOLDER\SCRIPTS\uiux.cmd` or PYTHONPATH=ENGINE_ROOT_PLACEHOLDER\CLI + python -m uiux)

| Task | Command |
|---|---|
| references | `uiux search "<concept>" --context-pack -n 8` |
| refresh DNA | `uiux init <project>` (never overwrites existing DNA) |
| quality gate | `uiux review <project>` then `uiux polish <project>` - fix all P0 |
| index new refs | `uiux update` (only in the engine folder) |

## Definition of done (UI tasks)

- tokens from the DNA only (alias existing project tokens, never fork values)
- focus-visible + hover + active + disabled + reduced-motion on every
  interactive element; touch targets >= 44px
- responsive by adaptation (320/768/1024/1440), not desktop shrinkage
- `uiux review` clean of P0 findings
'@
$skillMd = $skillMd -replace 'ENGINE_ROOT_PLACEHOLDER', $engineRoot

foreach ($base in @(".claude\skills\uiux-engine", ".agents\skills\uiux-engine")) {
    $dir = Join-Path $project $base
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Set-Content -Encoding UTF8 -Path (Join-Path $dir "SKILL.md") -Value $skillMd
    Write-Host "  [OK]   $base\SKILL.md"
}

$kiloDir = Join-Path $project ".kilo\command"
New-Item -ItemType Directory -Force -Path $kiloDir | Out-Null
@'
---
description: Run the UIUX ENGINE design pipeline (references + DNA + plan) for this project.
---
# UIUX Design Pipeline

Engine root: ENGINE_ROOT_PLACEHOLDER

1. Read .uiux/design-dna.md (visual law). If missing, run
   `python -m uiux init <project>` with PYTHONPATH=ENGINE_ROOT_PLACEHOLDER\CLI.
2. Retrieve references: `uiux search "$ARGUMENTS" --context-pack -n 8`.
3. Route methodology skills (max 3): emil-design-eng / animate / cast /
   design-taste-frontend / frontend-design / motion-design /
   web-design-guidelines.
4. Produce a design plan citing DNA axes, then implement, then
   `uiux review <project>` - fix all P0 findings before finishing.
'@ -replace 'ENGINE_ROOT_PLACEHOLDER', $engineRoot |
    Set-Content -Encoding UTF8 -Path (Join-Path $kiloDir "uiux.md")
Write-Host "  [OK]   .kilo\command\uiux.md"

# --- 4. AGENTS.md managed block --------------------------------------------------
$agents = Join-Path $project "AGENTS.md"
$block = @"
$managed
## UIUX ENGINE (managed - do not edit between these markers)

- Visual law: .uiux/design-dna.md (regenerate via uiux init; never overwrite)
- Priority order: user > project > audience > accessibility > existing
  system > brand > technical > engine > external skills > references
- References: $engineRoot\SCRIPTS\uiux.cmd search "<concept>" --context-pack
- Quality gate: $engineRoot\SCRIPTS\uiux.cmd review . (fix all P0)
- Full contract: .claude/skills/uiux-engine/SKILL.md
<!-- /uiux-engine:managed -->
"@
if (Test-Path $agents) {
    $text = Get-Content $agents -Raw
    if (-not $text.Contains($managed)) {
        Add-Content -Encoding UTF8 -Path $agents -Value "`n$block"
        Write-Host "  [OK]   AGENTS.md block appended"
    } else {
        Write-Host "  [skip] AGENTS.md already bound"
    }
} else {
    Set-Content -Encoding UTF8 -Path $agents -Value "# $([IO.Path]::GetFileName($project))`n`n$block"
    Write-Host "  [OK]   AGENTS.md created"
}

Write-Host ""
Write-Host "  Bound. Open an agent in this project and describe what to design -"
Write-Host "  the pipeline (references -> DNA -> implement -> review) runs automatically."
