# UIUX ENGINE - per-project library installer (RESOURCE-LIST sections 2-4).
#
# Libraries from the resource registry are PROJECT dependencies, never
# machine-global. This script installs the right ones into a target project
# based on its detected framework + the capabilities the design needs.
#
# Usage:
#   .\install-libs.ps1 -Project <path> -Motion            # motion (motion / framer-motion / css)
#   .\install-libs.ps1 -Project <path> -Scroll -Motion    # + GSAP scroll choreography
#   .\install-libs.ps1 -Project <path> -ThreeD            # three.js / @react-three/fiber
#   .\install-libs.ps1 -Project <path> -Shader            # + @shadergradient/react
#   .\install-libs.ps1 -Project <path> -Tailwind          # + tailwindcss
#   .\install-libs.ps1 -Project <path> -All               # everything the stack allows
#
# Guardrails (build spec 20/23/38):
#   - CSS-first: if a one-property transition solves it, nothing is installed.
#   - Never installs into a project whose package.json is absent unless -Force.
#   - Uses the CANONICAL package names verified 2026-09 in
#     CONFIG\resources.yaml (motion, not framer-motion, for new projects).

param(
    [Parameter(Mandatory = $true)][string]$Project,
    [switch]$Motion,
    [switch]$Scroll,
    [switch]$ThreeD,
    [switch]$Shader,
    [switch]$Tailwind,
    [switch]$All,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path $Project
$pkg = Join-Path $root "package.json"
$engine = $null
$cand = Join-Path $PSScriptRoot ".."
if (Test-Path (Join-Path $cand "CONFIG\resources.yaml")) { $engine = (Resolve-Path $cand).Path }

if (-not (Test-Path $pkg) -and -not $Force) {
    Write-Host "  [skip] $root has no package.json - install manually or pass -Force"
    exit 0
}
Set-Location $root

# --- detect stack -----------------------------------------------------------
$framework = "vanilla"
$pkgMgr = "npm"
if (Test-Path $pkg) {
    $json = Get-Content $pkg -Raw -Encoding UTF8 | ConvertFrom-Json
    $deps = @{}; $json.dependencies.PSObject.Properties | ForEach-Object { $deps[$_.Name] = $_.Value }
    $dev = @{}; if ($json.devDependencies) { $json.devDependencies.PSObject.Properties | ForEach-Object { $dev[$_.Name] = $_.Value } }
    $all = $deps + $dev
    if ($all.ContainsKey("next")) { $framework = "next" }
    elseif ($all.ContainsKey("nuxt")) { $framework = "nuxt" }
    elseif ($all.ContainsKey("@remix-run/react")) { $framework = "remix" }
    elseif ($all.ContainsKey("astro")) { $framework = "astro" }
    elseif ($all.ContainsKey("react") -or $all.ContainsKey("react-dom")) { $framework = "react" }
    elseif ($all.ContainsKey("vue")) { $framework = "vue" }
    elseif ($all.ContainsKey("svelte")) { $framework = "svelte" }
    if (Test-Path (Join-Path $root "pnpm-lock.yaml")) { $pkgMgr = "pnpm" }
    elseif (Test-Path (Join-Path $root "yarn.lock")) { $pkgMgr = "yarn" }
    elseif (Test-Path (Join-Path $root "bun.lock") -or (Test-Path (Join-Path $root "bun.lockb"))) { $pkgMgr = "bun" }
}
$isReact = $framework -in @("next", "react", "remix", "astro")

$addCmd = switch ($pkgMgr) {
    "pnpm" { "pnpm add" }
    "yarn" { "yarn add" }
    "bun"  { "bun add" }
    default { "npm install" }
}

Write-Host "UIUX ENGINE library installer - $root"
Write-Host "  framework: $framework | pkg mgr: $pkgMgr"
$installed = @()

function Add-Pkg([string]$pkgs, [string]$why) {
    Write-Host "  [....] installing $pkgs ($why)"
    Invoke-Expression "$addCmd $pkgs"
    if ($LASTEXITCODE -eq 0) { Write-Host "  [OK]   $pkgs" } else { Write-Host "  [FAIL] $pkgs" -ForegroundColor Red }
}

# --- motion (canonical: `motion`; keep existing framer-motion untouched) ----
if ($All -or $Motion) {
    $already = $false
    if (Test-Path $pkg) {
        $cur = (Get-Content $pkg -Raw -Encoding UTF8 | ConvertFrom-Json)
        if ($cur.dependencies.PSObject.Properties.Name -contains "framer-motion") {
            Write-Host "  [skip] framer-motion already present (existing alias wins; do not migrate mid-feature)"
            $already = $true
        }
    }
    if (-not $already) {
        if ($isReact) { Add-Pkg "motion" "Motion for React (declarative + layout + gestures)" ; $installed += "motion" }
        else { Write-Host "  [info] non-React stack ($framework): use CSS transitions + the motion-design skill; `motion` has a vanilla `motion` mini API if needed" }
    }
}

# --- scroll choreography (GSAP, framework-agnostic) --------------------------
if ($All -or $Scroll) {
    Add-Pkg "gsap" "ScrollTrigger/timelines - only for real choreography" ; $installed += "gsap"
}

# --- 3D -----------------------------------------------------------------------
if ($All -or $ThreeD) {
    if ($isReact) {
        Add-Pkg "three @react-three/fiber @react-three/drei" "R3F declarative WebGL" ; $installed += "three", "react-three-fiber"
    } else {
        Add-Pkg "three" "vanilla WebGL scene graph" ; $installed += "three"
    }
    if ($All -or $Shader) {
        if ($isReact) { Add-Pkg "@shadergradient/react" "ambient shader gradient surfaces" ; $installed += "shadergradient" }
    }
}
if ((-not $All -and $Shader) -and -not $ThreeD) {
    Write-Host "  [info] -Shader implies 3D peer deps; pass -ThreeD too"
}

# --- tailwind -----------------------------------------------------------------
if ($All -or $Tailwind) {
    $hasTw = $false
    if (Test-Path $pkg) {
        $cur = (Get-Content $pkg -Raw -Encoding UTF8 | ConvertFrom-Json)
        $names = @($cur.dependencies.PSObject.Properties.Name) + @($cur.devDependencies.PSObject.Properties.Name)
        $hasTw = $names -contains "tailwindcss"
    }
    if ($hasTw) { Write-Host "  [skip] tailwindcss already present" }
    else { Add-Pkg "tailwindcss @tailwindcss/vite" "utility CSS + token mapping" ; $installed += "tailwindcss" }
}

# --- component sources (consult-class: never auto-installed) ------------------
if ($All) {
    Write-Host ""
    Write-Host "  [consult] Component sources are NOT auto-installed (registry activation=consult):"
    Write-Host "    - React Bits      https://reactbits.dev        (animated components, copy-paste)"
    Write-Host "    - 21st.dev        https://21st.dev             (shadcn-registry components)"
    Write-Host "    - Uiverse         https://uiverse.io           (CSS technique inspiration only)"
    Write-Host "    - Lightswind      https://lightswind.com       (npx i lightswind - review licence first)"
    Write-Host "    - shadcn/ui       https://ui.shadcn.com        (npx shadcn@latest add <component>)"
}

Write-Host ""
if ($installed.Count) { Write-Host "  installed: $($installed -join ', ')" }
else { Write-Host "  nothing installed (CSS-first guard, or already present)" }
Write-Host "  next: map Design DNA tokens (see .uiux\design-dna.md), then `uiux review <project>`"
