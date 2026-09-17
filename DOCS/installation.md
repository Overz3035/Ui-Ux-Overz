# Installation

## Requirements

- Windows 10/11 with Windows Terminal, PowerShell 5.1+, or CMD
  (the engine is Windows-first; nothing prevents other OSes — tools.search_paths
  in CONFIG covers unix bins)
- Python 3.10+
- Pillow + numpy (hard), PyYAML (recommended; a built-in mini-YAML parser
  covers the shipped configs without it)
- Optional: ffmpeg/ffprobe (video), Tesseract + pytesseract (OCR),
  sentence-transformers + torch (neural text embeddings)

## Steps

```powershell
cd UIUX-ENGINE
powershell -ExecutionPolicy Bypass -File SCRIPTS\install.ps1
# optional: add uiux to PATH for this user
powershell -ExecutionPolicy Bypass -File SCRIPTS\install.ps1 -AddPath
```

The installer verifies Python and packages, probes optional tools (no
downloads, per security policy), writes the `uiux.cmd` shim to
`%LOCALAPPDATA%\uiux-engine\bin`, and runs `uiux doctor`.

CMD equivalent: `SCRIPTS\install.bat`.

## First run

```powershell
uiux doctor     # capability report; writes INDEX/resource-state.json
uiux status     # index state
```

## Pinning tools (non-PATH installs)

CONFIG/config.yaml:

```yaml
tools:
  ffmpeg: "C:/ffmpeg/bin/ffmpeg.exe"
  ffprobe: "C:/ffmpeg/bin/ffprobe.exe"
  tesseract: ""
```

## Portability

Copy the engine folder anywhere; run the installer on the new machine. No
absolute paths are baked in: the CLI resolves the engine root from
`UIUX_ENGINE_HOME` (optional) or its own location (CLI/uiux/__init__.py).
