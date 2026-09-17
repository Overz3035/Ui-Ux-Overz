"""Discovery and safe invocation of optional external binaries.

The engine never downloads a binary and never executes anything it did not
find on the local machine (build spec §38). Everything here is optional: when a
tool is missing the caller records a capability gap and continues.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from .config import get, resolve_path

_WIN_SUFFIXES = (".exe", ".cmd", ".bat", "")


@lru_cache(maxsize=None)
def find_tool(name: str) -> str | None:
    """Locate ``name``: explicit config pin, then PATH, then configured dirs."""
    pinned = get(f"tools.{name}", "") or ""
    if pinned:
        p = resolve_path(pinned)
        if p.is_file():
            return str(p)
        # A pinned bare command name is still worth trying on PATH.
        which = shutil.which(pinned)
        if which:
            return which

    which = shutil.which(name)
    if which:
        return which

    for raw_dir in get("tools.search_paths", []) or []:
        d = Path(str(raw_dir)).expanduser()
        if not d.is_dir():
            continue
        for suffix in _WIN_SUFFIXES:
            cand = d / f"{name}{suffix}"
            if cand.is_file():
                return str(cand)
    return None


def have(name: str) -> bool:
    return find_tool(name) is not None


def run(argv: list[str], timeout: int = 120, binary: bool = False):
    """Run a command with no shell, returning (ok, stdout, stderr).

    ``argv`` is always a list, so values interpolated from filenames cannot be
    reinterpreted as shell syntax.
    """
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            timeout=timeout,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
    except FileNotFoundError:
        return False, b"" if binary else "", "binary not found"
    except subprocess.TimeoutExpired:
        return False, b"" if binary else "", f"timeout after {timeout}s"
    except OSError as exc:  # pragma: no cover - platform specific
        return False, b"" if binary else "", str(exc)

    if binary:
        return proc.returncode == 0, proc.stdout, proc.stderr.decode("utf-8", "replace")
    return (
        proc.returncode == 0,
        proc.stdout.decode("utf-8", "replace"),
        proc.stderr.decode("utf-8", "replace"),
    )


def ffprobe_available() -> bool:
    setting = str(get("video_analysis.enabled", "auto")).lower()
    if setting in ("false", "0", "no", "off"):
        return False
    return have("ffprobe")


def ffmpeg_available() -> bool:
    setting = str(get("video_analysis.enabled", "auto")).lower()
    if setting in ("false", "0", "no", "off"):
        return False
    return have("ffmpeg")


def ocr_available() -> bool:
    setting = str(get("image_analysis.ocr.enabled", "auto")).lower()
    if setting in ("false", "0", "no", "off"):
        return False
    if not have("tesseract"):
        return False
    try:
        import pytesseract  # noqa: F401
    except ImportError:
        return False
    return True


def python_package(name: str) -> str | None:
    """Return an installed package version, or None when unusable."""
    try:
        import importlib.metadata as md

        return md.version(name)
    except Exception:
        return None


def importable(module: str) -> tuple[bool, str]:
    """Try to import ``module``; return (ok, detail).

    Used by ``uiux doctor`` to distinguish "not installed" from "installed but
    broken" (e.g. a transformers/huggingface-hub version conflict).
    """
    try:
        __import__(module)
        return True, "ok"
    except ImportError as exc:
        return False, str(exc).split("\n")[0][:160]
    except Exception as exc:  # noqa: BLE001 - report anything that blocks import
        return False, f"{type(exc).__name__}: {str(exc).splitlines()[0][:140]}"
