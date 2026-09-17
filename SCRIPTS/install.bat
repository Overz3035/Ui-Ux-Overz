@echo off
REM UIUX ENGINE installer (CMD variant). Forwards to install.ps1.
REM Usage: install.bat [-AddPath]
setlocal
set "SCRIPT_DIR=%~dp0"
where powershell >nul 2>nul
if errorlevel 1 (
    echo install.bat: powershell.exe not found. Use Windows PowerShell to run SCRIPTS\install.ps1 directly.
    exit /b 2
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install.ps1" %*
endlocal
