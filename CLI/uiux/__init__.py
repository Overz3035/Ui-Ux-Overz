"""UIUX ENGINE — local design intelligence engine.

Public entry point is :func:`uiux.cli.main`. Everything in this package is
pure Python; only Pillow and numpy are hard requirements and both are checked
by ``uiux doctor``. Every optional capability degrades instead of failing.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["VERSIONS", "engine_root", "__version__"]


def _read_versions() -> dict:
    """Parse the repo-root VERSION file (key=value lines)."""
    out = {
        "engine": "0.0.0",
        "analyzer": "0",
        "index": "0",
        "schema": "0",
        "naming": "0",
        "embedding": "0",
        "knowledge": "0",
    }
    vf = engine_root() / "VERSION"
    try:
        for line in vf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    except OSError:
        pass
    return out


def engine_root() -> Path:
    """Locate the engine root portably.

    Resolution order:
      1. ``UIUX_ENGINE_HOME`` environment variable (explicit override)
      2. two levels up from this file (CLI/uiux/__init__.py -> root)

    No absolute path is ever baked in, so the folder can be copied anywhere
    (build spec §34).
    """
    env = os.environ.get("UIUX_ENGINE_HOME")
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p.resolve()
    return Path(__file__).resolve().parents[2]


VERSIONS = _read_versions()
__version__ = VERSIONS["engine"]
