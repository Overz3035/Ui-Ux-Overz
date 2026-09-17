# UIUX ENGINE installer (Windows: PowerShell 5.1+, Windows Terminal / CMD).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1           # verify + set up
#   powershell -ExecutionPolicy Bypass -File install.ps1 -AddPath  # also add to user PATH
#
# What it does:
#   1. Verifies Python 3.10+ and required packages (Pillow, numpy; PyYAML recommended)
#   2. Probes optional tools: ffmpeg/ffprobe (video), tesseract (OCR)
#   3. Creates the uiux.cmd shim in a user bin folder and optionally adds it to PATH
#   4. Runs `uiux doctor` to write INDEX/resource-state.json
#
# It never downloads binaries or executes remote code (security spec 38):
# missing optional tools are reported with install hints only.
# NOTE: kept ASCII-only on purpose - PowerShell 5.1 reads BOM-less files
# as ANSI and mis-decodes UTF-8 punctuation inside strings.

param(
    [switch]$AddPath
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$engineRoot = Resolve-Path (Join-Path $scriptDir "..")

Write-Host "UIUX ENGINE install - root: $engineRoot"

# --- 1. Python -------------------------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "  [FAIL] python not found on PATH." -ForegroundColor Red
    Write-Host "         Install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "         or: winget install Python.Python.3.12"
    exit 1
}
$pyVer = & $python.Source -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor)+'.'+str(sys.version_info.micro))"
& $python.Source -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] python $pyVer is too old (need 3.10+)." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK]   python $pyVer"

# --- 2. required packages ---------------------------------------------------
& $python.Source -c "import PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [....] installing Pillow (required)..."
    & $python.Source -m pip install --quiet Pillow
}
& $python.Source -c "import numpy" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [....] installing numpy (required)..."
    & $python.Source -m pip install --quiet numpy
}
& $python.Source -c "import yaml" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [....] installing PyYAML (recommended)..."
    & $python.Source -m pip install --quiet PyYAML
}
& $python.Source -c "import PIL, numpy" 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "  [OK]   Pillow + numpy importable" }
else { Write-Host "  [FAIL] Pillow/numpy still not importable - check pip output above." -ForegroundColor Red; exit 1 }

# --- 3. optional tool probes (no downloads) ---------------------------------
foreach ($tool in @("ffmpeg", "ffprobe", "tesseract")) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    $found = [bool]$cmd
    if (-not $found -and (Test-Path "C:\ffmpeg\bin\$tool.exe")) { $found = $true }
    if ($found) { Write-Host "  [OK]   $tool found" }
    else {
        Write-Host "  [--]   $tool not found (optional)" -ForegroundColor Yellow
        if ($tool -like "ff*") {
            Write-Host "         video analysis stays disabled until installed:"
            Write-Host "           winget install Gyan.FFmpeg   OR   choco install ffmpeg"
            Write-Host "         then pin it in CONFIG\config.yaml under tools:"
        }
        if ($tool -eq "tesseract") {
            Write-Host "         OCR stays disabled until installed:"
            Write-Host "           winget install UB-Mannheim.TesseractOCR"
        }
    }
}

# --- 4. uiux shim -----------------------------------------------------------
$binDir = Join-Path $env:LOCALAPPDATA "uiux-engine\bin"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
$shim = Join-Path $binDir "uiux.cmd"
$engineRootEscaped = "$engineRoot"
@"
@echo off
set "PYTHONPATH=$engineRootEscaped\CLI;%PYTHONPATH%"
python -m uiux %*
"@ | Set-Content -Encoding ASCII -Path $shim
Write-Host "  [OK]   shim written: $shim"

if ($AddPath) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
        Write-Host "  [OK]   added to user PATH (restart terminal to take effect)"
    } else {
        Write-Host "  [OK]   $binDir already on user PATH"
    }
} else {
    Write-Host "  [info] run with -AddPath to put 'uiux' on your PATH,"
    Write-Host "         or call the shim directly: `"$shim`" doctor"
}

# --- 5. doctor --------------------------------------------------------------
Write-Host ""
Write-Host "Running uiux doctor..."
$env:PYTHONPATH = "$engineRoot\CLI;" + $env:PYTHONPATH
& $python.Source -m uiux doctor
exit $LASTEXITCODE
