# UIUX ENGINE launcher for PowerShell / Windows Terminal.
# Works in place OR copied standalone: falls back to UIUX_ENGINE_HOME
# and known install paths.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$candidates = @()
if ($env:UIUX_ENGINE_HOME) { $candidates += $env:UIUX_ENGINE_HOME }
$candidates += (Join-Path $scriptDir "..")
$candidates += (Join-Path $env:USERPROFILE "Desktop\UIUX_ENGINE")
$candidates += (Join-Path $env:USERPROFILE "UIUX_ENGINE")
$engineRoot = $null
foreach ($c in $candidates) {
    if ($c -and (Test-Path (Join-Path $c "CLI\uiux\cli.py"))) {
        $engineRoot = (Resolve-Path $c).Path
        break
    }
}
if (-not $engineRoot) {
    Write-Error "uiux: engine not found. Set UIUX_ENGINE_HOME or run SCRIPTS\activate.ps1."
    exit 2
}
$env:PYTHONPATH = "$engineRoot\CLI;" + $env:PYTHONPATH
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "uiux: python not found on PATH. Run SCRIPTS\install.ps1 first."
    exit 2
}
& $python.Source -m uiux @args
exit $LASTEXITCODE
