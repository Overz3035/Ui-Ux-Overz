@echo off
REM UIUX ENGINE launcher (CMD). Works in place OR copied standalone:
REM falls back to UIUX_ENGINE_HOME and known install paths.
setlocal enabledelayedexpansion
set "UIUX_ROOT="
if defined UIUX_ENGINE_HOME if exist "%UIUX_ENGINE_HOME%\CLI\uiux\cli.py" set "UIUX_ROOT=%UIUX_ENGINE_HOME%"
if not defined UIUX_ROOT (
    set "CAND=%~dp0.."
    if exist "!CAND!\CLI\uiux\cli.py" set "UIUX_ROOT=!CAND!"
)
if not defined UIUX_ROOT if exist "%USERPROFILE%\Desktop\UIUX_ENGINE\CLI\uiux\cli.py" set "UIUX_ROOT=%USERPROFILE%\Desktop\UIUX_ENGINE"
if not defined UIUX_ROOT if exist "%USERPROFILE%\UIUX_ENGINE\CLI\uiux\cli.py" set "UIUX_ROOT=%USERPROFILE%\UIUX_ENGINE"
if not defined UIUX_ROOT (
    echo uiux: engine not found. Set UIUX_ENGINE_HOME or run SCRIPTS\activate.ps1.
    exit /b 2
)
set "PYTHONPATH=%UIUX_ROOT%\CLI;%PYTHONPATH%"
where python >nul 2>nul
if errorlevel 1 (
    echo uiux: python not found on PATH. Run SCRIPTS\install.ps1 first.
    exit /b 2
)
python -m uiux %*
endlocal
